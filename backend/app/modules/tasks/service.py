from copy import deepcopy
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User
from app.modules.exceptions.models import CheckinException
from app.modules.groups.invite import generate_unique_invite_code
from app.modules.groups.models import Group, GroupMember, GroupTeacher
from app.modules.messages.models import Message
from app.modules.records.models import CheckinRecord
from app.modules.tasks.models import (
    CheckinTask,
    CheckinTaskGroup,
    CheckinTaskOccurrence,
)
from app.modules.tasks.repository import TaskRepository
from app.modules.qr_code.service import generate_token, render_qr_data_url
from app.modules.tasks.schemas import CreateTaskRequest
from app.shared.attendance import resolve_attendance_status
from app.shared.datetime_utils import get_beijing_now
from app.shared.enums import (
    AttendanceStatus,
    RecordStatus,
    ScheduleMode,
    TaskStatus,
)

MAX_MATERIALIZED_DAYS = 90

CHECKIN_METHOD_LABELS = {
    "face": "人脸识别",
    "location": "地理位置",
    "qr_code": "二维码",
    "checkin_code": "签到码",
    "attachment": "附件/日志",
    "gesture": "手势签到",
}


def _resolve_task_method_labels(rules: dict | None) -> list[str]:
    snapshot = rules or {}
    verification = snapshot.get("verificationRule") or {}
    methods = verification.get("methods") or []
    labels = [
        CHECKIN_METHOD_LABELS.get(str(method), str(method))
        for method in methods
        if method
    ]
    if labels:
        return labels

    legacy: list[str] = []
    if (snapshot.get("faceRule") or {}).get("enabled"):
        legacy.append(CHECKIN_METHOD_LABELS["face"])
    location_rule = snapshot.get("locationRule") or {}
    if location_rule.get("mode") not in (None, "", "none"):
        legacy.append(CHECKIN_METHOD_LABELS["location"])
    return legacy


def _format_task_notify_message(
    task: CheckinTask, *, group_names: list[str] | None = None
) -> tuple[str, str]:
    window = (
        f"{task.starts_at.strftime('%m-%d %H:%M')} - "
        f"{task.ends_at.strftime('%H:%M')}"
    )
    methods = _resolve_task_method_labels(task.rules_snapshot_jsonb)
    methods_text = "、".join(methods) if methods else "按任务要求"
    group_text = " / ".join(group_names) if group_names else ""
    description = (task.description or "").strip() or (
        "您有一条新的签到任务，请在规定时间内完成签到。"
    )
    lines = [
        f"课群名称：{group_text}" if group_text else None,
        f"任务说明：{description}",
        f"打卡方式：{methods_text}",
        f"打卡时间：{window}",
    ]
    content = "\n".join(line for line in lines if line)
    return task.title, content


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TaskRepository(db)

    def create_task(self, *, teacher_user: User, payload: CreateTaskRequest) -> dict:
        self._require_teacher_group_scope(teacher_user, payload.group_ids)
        schedule_mode = ScheduleMode(payload.schedule_mode)
        is_recurring = schedule_mode == ScheduleMode.RECURRING
        task = CheckinTask(
            title=payload.title,
            type_id=payload.type_id,
            teacher_user_id=teacher_user.id,
            status=TaskStatus.DRAFT.value,
            starts_at=datetime.fromisoformat(payload.starts_at),
            ends_at=datetime.fromisoformat(payload.ends_at),
            rules_snapshot_jsonb=deepcopy(payload.rules_snapshot),
            schedule_mode=schedule_mode.value,
            is_recurring=is_recurring,
            recurrence_rule=payload.recurrence_rule
            or ("FREQ=DAILY" if is_recurring else None),
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
            "occurrences": self._serialize_occurrences(task.id),
        }

    def _serialize_occurrences(self, task_id: int) -> list[dict]:
        return [
            {
                "id": occ.id,
                "occurrence_date": occ.occurrence_date,
                "occurrenceDate": occ.occurrence_date,
                "starts_at": occ.starts_at.isoformat(),
                "ends_at": occ.ends_at.isoformat(),
                "status": occ.status,
            }
            for occ in self.repository.list_occurrences_for_task(task_id)
        ]

    def publish_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        task.is_published = True
        task.status = TaskStatus.NOT_STARTED.value
        self.repository.flush()

        occurrences = self._materialize_occurrences(task)
        notified = self._notify_group_members(task)
        self.repository.commit()
        return {
            "published": True,
            "status": task.status,
            "notified_count": notified,
            "occurrence_count": len(occurrences),
        }

    def _materialize_occurrences(self, task: CheckinTask) -> list[CheckinTaskOccurrence]:
        """为任务生成 occurrence：一次任务一条；定时任务按日从开始到今天物化。"""
        created: list[CheckinTaskOccurrence] = []
        start_date = task.starts_at.date()
        is_recurring = task.schedule_mode == ScheduleMode.RECURRING.value

        if not is_recurring:
            dates = [start_date]
        else:
            today = datetime.now().date()
            cap_date = min(today, task.ends_at.date())
            if cap_date < start_date:
                cap_date = start_date
            dates = []
            cursor = start_date
            while cursor <= cap_date and len(dates) < MAX_MATERIALIZED_DAYS:
                dates.append(cursor)
                cursor += timedelta(days=1)

        for occurrence_date in dates:
            date_str = occurrence_date.isoformat()
            if self.repository.get_occurrence(task.id, date_str) is not None:
                continue
            if is_recurring:
                starts_at = datetime.combine(occurrence_date, task.starts_at.time())
                ends_at = datetime.combine(occurrence_date, task.ends_at.time())
            else:
                starts_at = task.starts_at
                ends_at = task.ends_at
            occurrence = CheckinTaskOccurrence(
                task_id=task.id,
                occurrence_date=date_str,
                starts_at=starts_at,
                ends_at=ends_at,
                status=TaskStatus.NOT_STARTED.value,
            )
            self.repository.add(occurrence)
            created.append(occurrence)
        self.repository.flush()
        return created

    def _notify_group_members(self, task: CheckinTask) -> int:
        """向任务所属群组的学生推送消息（类钉钉通知）。"""
        groups = self.repository.list_groups_for_task(task.id)
        group_names = [group.name for group in groups]
        title, content = _format_task_notify_message(task, group_names=group_names)
        count = 0
        seen_user_ids: set[int] = set()
        for student in self.repository.list_students_for_task(task.id):
            if student.user_id is None or student.user_id in seen_user_ids:
                continue
            seen_user_ids.add(student.user_id)
            self.repository.add(
                Message(
                    user_id=student.user_id,
                    title=title,
                    content=content,
                    created_at=get_beijing_now(),
                )
            )
            count += 1
        self.repository.flush()
        return count

    def end_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        task.status = TaskStatus.ENDED.value
        self.repository.commit()
        return {"ended": True, "status": task.status}

    def get_qr_code(
        self, *, task_id: int, teacher_user: User, refresh: bool = False
    ) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)

        rules = task.rules_snapshot_jsonb or {}
        vr = rules.get("verificationRule", {}) or {}
        if "qr_code" not in (vr.get("methods") or []):
            raise ValueError("该任务未启用二维码签到")

        qr_config = vr.get("qr_code", {}) or {}
        expire_seconds = int(qr_config.get("expireSeconds", 120))
        refresh_interval = int(qr_config.get("refreshIntervalSeconds", 60))

        token, token_obj = generate_token(
            task.id,
            occurrence_date=datetime.now().date().isoformat(),
            expire_seconds=expire_seconds,
        )
        task.current_qr_token = token
        self.repository.commit()

        return {
            "task_id": task.id,
            "qr_token": token,
            "qr_image": render_qr_data_url(token),
            "expires_at": token_obj.expires_at,
            "expire_seconds": expire_seconds,
            "refresh_interval_seconds": refresh_interval,
            "refreshed": refresh,
        }

    def set_student_attendance(
        self,
        *,
        task_id: int,
        student_profile_id: int,
        status: str,
        remark: str | None,
        teacher_user: User,
    ) -> dict:
        """教师手动设置某学生在该任务下的考勤（签到/迟到/早退/未签到/请假）。"""
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)

        try:
            attendance = AttendanceStatus(status)
        except ValueError as exc:
            raise ValueError("无效的考勤状态") from exc

        student = self.repository.get_student_profile(student_profile_id)
        if student is None:
            raise ValueError("学生不存在")

        record = self.repository.get_record_for_student_task(task_id, student_profile_id)
        if record is None:
            record = CheckinRecord(
                task_id=task_id,
                student_profile_id=student_profile_id,
                submitted_at=datetime.now(),
                occurrence_date=datetime.now().date().isoformat(),
                status=RecordStatus.NORMAL.value,
                verification_results_jsonb={},
                enabled_methods_jsonb=[],
                submit_payload_jsonb={"source": "teacher_manual"},
            )
            self.repository.add(record)

        record.manual_status = attendance.value
        record.manual_remark = remark or None
        # 手动标记后清除待复核占位
        record.need_review = False
        self.repository.commit()

        return {
            "task_id": task_id,
            "student_id": student_profile_id,
            "manual_status": attendance.value,
            "status": self._student_task_status(record, None),
        }

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

    def create_teacher_group(self, teacher_user: User, name: str) -> dict:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        trimmed = name.strip()
        if not trimmed:
            raise ValueError("班级名称不能为空")
        group = Group(
            name=trimmed,
            group_type="class",
            invite_code=generate_unique_invite_code(self.db),
        )
        self.repository.add(group)
        self.repository.flush()
        self.repository.add(
            GroupTeacher(
                group_id=group.id,
                teacher_profile_id=teacher_user.teacher_profile.id,
            )
        )
        self.repository.commit()
        return self._serialize_teacher_group(group)

    def get_teacher_group_detail(self, group_id: int, teacher_user: User) -> dict:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        group = self.repository.get_group(group_id)
        if group is None:
            raise ValueError("班级不存在")
        allowed_group_ids = set(
            self.repository.list_group_ids_for_teacher_profile(
                teacher_user.teacher_profile.id
            )
        )
        if group_id not in allowed_group_ids:
            raise PermissionError("无权查看该班级")

        students = self._students_for_group(group_id)
        tasks = self.repository.list_tasks_for_group_ids([group_id])
        task_ids = [task.id for task in tasks]
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        pending_review_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        total_records = sum(
            len(self.repository.list_records_for_task(task.id)) for task in tasks
        )
        total_students_in_tasks = sum(
            len(self.repository.list_students_for_task(task.id)) for task in tasks
        )
        attendance_rate = self._completion_rate(total_records, total_students_in_tasks)
        exception_rate = self._completion_rate(len(exceptions), max(total_records, 1))

        return {
            "group": self._serialize_teacher_group(group),
            "stats": {
                "attendance_rate": attendance_rate,
                "attendanceRate": attendance_rate,
                "exception_rate": exception_rate,
                "exceptionRate": exception_rate,
                "pending_review_count": pending_review_count,
                "pendingReviewCount": pending_review_count,
            },
            "students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "status": "joined",
                }
                for student in students
            ],
            "tasks": [self.serialize_task(task) for task in tasks],
        }

    def list_student_groups(self, student_user: User) -> dict:
        if student_user.student_profile is None:
            raise ValueError("学生档案不存在")
        groups = self.repository.list_groups_for_student_profile(
            student_user.student_profile.id
        )
        student_profile_id = student_user.student_profile.id
        items = [
            self._serialize_student_group(group, student_profile_id)
            for group in groups
        ]
        return {"items": items, "total": len(items)}

    def join_group_by_invite_code(self, student_user: User, invite_code: str) -> dict:
        if student_user.student_profile is None:
            raise ValueError("学生档案不存在")
        code = invite_code.strip().upper()
        if not code:
            raise ValueError("请输入班级邀请码")
        group = self.repository.get_group_by_invite_code(code)
        if group is None:
            raise ValueError("邀请码无效，请检查后重试")
        student_profile_id = student_user.student_profile.id
        already_member = self.repository.group_member_exists(
            group.id, student_profile_id
        )
        if not already_member:
            self.repository.add(
                GroupMember(
                    group_id=group.id,
                    student_profile_id=student_profile_id,
                )
            )
            self.repository.commit()
        return {
            "group": self._serialize_teacher_group(group),
            "already_member": already_member,
        }

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
            "schedule_mode": task.schedule_mode,
            "scheduleMode": task.schedule_mode,
            "is_recurring": task.is_recurring,
            "recurrence_rule": task.recurrence_rule,
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

    def _serialize_student_group(self, group: Group, student_profile_id: int) -> dict:
        students = self._students_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        teachers = self.repository.list_teachers_for_group(group.id)
        primary_teacher = teachers[0] if teachers else None
        teacher_names = [teacher.name for teacher in teachers]
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "groupType": group.group_type,
            "student_profile_id": student_profile_id,
            "studentProfileId": student_profile_id,
            "teacher_id": primary_teacher.id if primary_teacher else None,
            "teacherId": primary_teacher.id if primary_teacher else None,
            "teacher_name": primary_teacher.name if primary_teacher else "",
            "teacherName": primary_teacher.name if primary_teacher else "",
            "teacher_names": teacher_names,
            "teacherNames": teacher_names,
            "student_count": len(students),
            "studentCount": len(students),
            "recent_task_count": len(tasks),
            "recentTaskCount": len(tasks),
        }

    def _serialize_teacher_group(self, group: Group) -> dict:
        students = self._students_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        recent_task_count = len(tasks)
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "invite_code": group.invite_code,
            "inviteCode": group.invite_code,
            "student_count": len(students),
            "studentCount": len(students),
            "recent_task_count": recent_task_count,
            "recentTaskCount": recent_task_count,
            "course_name": group.group_type,
            "courseName": group.group_type,
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
            manual_status = record.manual_status if record else None
            items.append(
                {
                    "id": student.id,
                    "student_no": student.student_no,
                    "studentNo": student.student_no,
                    "name": student.name,
                    "status": self._student_task_status(record, exception),
                    "manual_status": manual_status,
                    "manualStatus": manual_status,
                    "manual_remark": record.manual_remark if record else None,
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
        status = resolve_attendance_status(record=record, exception=exception)
        if record is None:
            return "missing"
        if exception is not None and exception.status == RecordStatus.PENDING_REVIEW.value:
            if status not in {
                AttendanceStatus.PRESENT.value,
                AttendanceStatus.LATE.value,
                AttendanceStatus.EARLY_LEAVE.value,
                AttendanceStatus.LEAVE.value,
            }:
                return "pending_review"
        return status

    def _completion_rate(self, submitted_count: int, student_count: int) -> int:
        if student_count == 0:
            return 0
        return round(submitted_count / student_count * 100)
