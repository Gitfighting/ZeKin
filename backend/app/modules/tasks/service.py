from copy import deepcopy
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User
from app.modules.exceptions.models import CheckinException
from app.modules.groups.models import Group
from app.modules.records.models import CheckinRecord
from app.modules.tasks.models import CheckinTask, CheckinTaskGroup
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import CreateTaskRequest
from app.shared.enums import RecordStatus, TaskStatus


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TaskRepository(db)

    def create_task(self, *, teacher_user: User, payload: CreateTaskRequest) -> dict:
        self._require_teacher_group_scope(teacher_user, payload.group_ids)
        task = CheckinTask(
            title=payload.title,
            type_id=payload.type_id,
            teacher_user_id=teacher_user.id,
            status=TaskStatus.DRAFT.value,
            starts_at=datetime.fromisoformat(payload.starts_at),
            ends_at=datetime.fromisoformat(payload.ends_at),
            rules_snapshot_jsonb=deepcopy(payload.rules_snapshot),
        )
        self.repository.add(task)
        self.repository.flush()
        for group_id in payload.group_ids:
            self.repository.add(CheckinTaskGroup(task_id=task.id, group_id=group_id))
        self.repository.commit()
        return self.serialize_task(task)

    def list_teacher_tasks(self, teacher_user_id: int) -> dict:
        items = [
            self.serialize_task(task)
            for task in self.repository.list_tasks_by_teacher(teacher_user_id)
        ]
        return {"items": items, "total": len(items)}

    def get_task_detail(self, task_id: int, teacher_user: User | None = None) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        if teacher_user is not None:
            self._require_task_owner(task, teacher_user)
        task_item = self.serialize_task(task)
        return {
            **task_item,
            "task": {**task_item, "published": task.is_published, "published_at": None},
            "students": self._serialize_task_students(task.id),
            "exceptions": self._serialize_task_exceptions(task.id),
        }

    def publish_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        task.is_published = True
        task.status = TaskStatus.NOT_STARTED.value
        self.repository.commit()
        return {"published": True, "status": task.status}

    def end_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        task.status = TaskStatus.ENDED.value
        self.repository.commit()
        return {"ended": True, "status": task.status}

    def teacher_dashboard(self, teacher_user_id: int) -> dict:
        tasks = self.repository.list_tasks_by_teacher(teacher_user_id)
        task_ids = [task.id for task in tasks]
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        pending_reviews = [
            item
            for item in exceptions
            if item.status == RecordStatus.PENDING_REVIEW.value
        ]
        today_tasks = len(tasks)
        return {
            "task_count": len(tasks),
            "exception_count": len(exceptions),
            "pending_review_count": len(pending_reviews),
            "todayTasks": today_tasks,
            "exceptions": len(exceptions),
            "pendingReviews": len(pending_reviews),
            "quickCreateCount": 0,
        }

    def list_teacher_groups(self, teacher_user: User) -> dict:
        if teacher_user.teacher_profile is None:
            return {"items": [], "total": 0}
        groups = self.repository.list_groups_for_teacher_profile(
            teacher_user.teacher_profile.id
        )
        items = [self._serialize_teacher_group(group) for group in groups]
        return {"items": items, "total": len(items)}

    def serialize_task(self, task: CheckinTask) -> dict:
        checkin_type = self.repository.get_checkin_type(task.type_id)
        rule_template = self.repository.get_rule_template_for_type(task.type_id)
        groups = self.repository.list_groups_for_task(task.id)
        group_ids = [group.id for group in groups]
        group_names = [group.name for group in groups]
        records = self.repository.list_records_for_task(task.id)
        exceptions = self.repository.list_exceptions_for_task(task.id)
        student_count = len(self.repository.list_students_for_task(task.id))
        submitted_count = len({record.student_profile_id for record in records})
        exception_count = len(exceptions)
        pending_review_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        completion_rate = self._completion_rate(submitted_count, student_count)
        return {
            "id": task.id,
            "title": task.title,
            "type_id": task.type_id,
            "type_name": checkin_type.name if checkin_type else None,
            "taskType": checkin_type.name if checkin_type else "custom",
            "templateName": rule_template.name if rule_template else "",
            "description": task.description,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "startsAt": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "endsAt": task.ends_at.isoformat(),
            "group_ids": group_ids,
            "group_names": group_names,
            "groupName": " / ".join(group_names),
            "student_count": student_count,
            "studentCount": student_count,
            "submitted_count": submitted_count,
            "submittedCount": submitted_count,
            "completion_rate": completion_rate,
            "completionRate": completion_rate,
            "exception_count": exception_count,
            "exceptionCount": exception_count,
            "pending_review_count": pending_review_count,
            "pendingReviewCount": pending_review_count,
            "rules_snapshot": deepcopy(task.rules_snapshot_jsonb),
        }

    def _require_task_owner(self, task: CheckinTask, teacher_user: User) -> None:
        if task.teacher_user_id != teacher_user.id:
            raise PermissionError("无权操作该任务")

    def _require_teacher_group_scope(
        self, teacher_user: User, group_ids: list[int]
    ) -> None:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        allowed_group_ids = set(
            self.repository.list_group_ids_for_teacher_profile(
                teacher_user.teacher_profile.id
            )
        )
        if not set(group_ids).issubset(allowed_group_ids):
            raise PermissionError("无权向所选分组发布任务")

    def _serialize_teacher_group(self, group: Group) -> dict:
        students = self._students_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        recent_task_count = len(tasks)
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "student_count": len(students),
            "studentCount": len(students),
            "recent_task_count": recent_task_count,
            "recentTaskCount": recent_task_count,
        }

    def _serialize_task_students(self, task_id: int) -> list[dict]:
        records = {
            record.student_profile_id: record
            for record in self.repository.list_records_for_task(task_id)
        }
        exceptions = {
            item.student_profile_id: item
            for item in self.repository.list_exceptions_for_task(task_id)
        }
        items = []
        for student in self.repository.list_students_for_task(task_id):
            record = records.get(student.id)
            exception = exceptions.get(student.id)
            items.append(
                {
                    "id": student.id,
                    "student_no": student.student_no,
                    "studentNo": student.student_no,
                    "name": student.name,
                    "status": self._student_task_status(record, exception),
                    "submitted_at": record.submitted_at.isoformat() if record else None,
                    "submittedAt": record.submitted_at.isoformat() if record else None,
                }
            )
        return items

    def _serialize_task_exceptions(self, task_id: int) -> list[dict]:
        groups = self.repository.list_groups_for_task(task_id)
        group_name = " / ".join(group.name for group in groups)
        task = self.repository.get_task(task_id)
        records = {
            record.id: record
            for record in self.repository.list_records_for_task(task_id)
        }
        students = {
            student.id: student
            for student in self.repository.list_students_for_task(task_id)
        }
        return [
            self._serialize_exception(
                item,
                student=students.get(item.student_profile_id),
                task=task,
                record=records.get(item.record_id),
                group_name=group_name,
            )
            for item in self.repository.list_exceptions_for_task(task_id)
        ]

    def _serialize_exception(
        self,
        item: CheckinException,
        *,
        student: StudentProfile | None,
        task: CheckinTask | None,
        record: CheckinRecord | None,
        group_name: str,
    ) -> dict:
        reason = " / ".join(item.messages_jsonb) if item.messages_jsonb else "异常"
        submitted_at = record.submitted_at.isoformat() if record else None
        status = (
            "pending"
            if item.status == RecordStatus.PENDING_REVIEW.value
            else item.status
        )
        return {
            "id": item.id,
            "record_id": item.record_id,
            "recordId": item.record_id,
            "task_id": item.task_id,
            "taskId": item.task_id,
            "student_id": item.student_profile_id,
            "studentId": item.student_profile_id,
            "student_name": student.name if student else None,
            "studentName": student.name if student else "",
            "task_title": task.title if task else None,
            "taskTitle": task.title if task else "",
            "group_name": group_name,
            "groupName": group_name,
            "submitted_at": submitted_at,
            "submittedAt": submitted_at,
            "reason": reason,
            "status": status,
            "exception_types": item.exception_types_jsonb,
            "exceptionTypes": item.exception_types_jsonb,
            "messages": item.messages_jsonb,
        }

    def _students_for_group(self, group_id: int) -> list[StudentProfile]:
        return self.repository.list_students_for_group(group_id)

    def _student_task_status(
        self, record: CheckinRecord | None, exception: CheckinException | None
    ) -> str:
        if record is None:
            return "missing"
        if exception is None:
            return "submitted"
        if exception.status == RecordStatus.PENDING_REVIEW.value:
            return "pending_review"
        return exception.status

    def _completion_rate(self, submitted_count: int, student_count: int) -> int:
        if student_count == 0:
            return 0
        return round(submitted_count / student_count * 100)
