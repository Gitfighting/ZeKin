from sqlalchemy.orm import Session

from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    GroupImportRequest,
    RuleTemplateUpdateRequest,
    StudentImportRequest,
    TeacherImportRequest,
)
from app.modules.auth.models import StudentProfile, TeacherProfile, User
from app.modules.groups.models import Group, GroupMember
from app.modules.tasks.models import CheckinTask
from app.shared.enums import RecordStatus


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminRepository(db)

    def dashboard(self) -> dict:
        students = self.repository.list_students()
        tasks = self.repository.list_tasks()
        exceptions = self.repository.list_exceptions()
        submitted_count = sum(
            len(
                {
                    record.student_profile_id
                    for record in self.repository.list_records_for_task(task.id)
                }
            )
            for task in tasks
        )
        expected_count = sum(
            len(self.repository.list_students_for_task(task.id)) for task in tasks
        )
        completion_rate = self._completion_rate(submitted_count, expected_count)
        pending_appeal_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        return {
            "student_count": len(students),
            "task_count": len(tasks),
            "exception_count": len(exceptions),
            "pending_appeal_count": pending_appeal_count,
            "completion_rate": completion_rate,
        }

    def org_tree(self) -> list[dict]:
        groups = self.repository.list_groups()
        return [
            {"id": group.id, "name": group.name, "type": group.group_type}
            for group in groups
        ]

    def import_students(self, payload: StudentImportRequest) -> dict:
        created = 0
        for item in payload.students:
            existing = self.repository.find_student_by_student_no(item.student_no)
            if existing is not None:
                continue
            profile = StudentProfile(**item.model_dump())
            self.repository.add(profile)
            self.repository.flush()
            group = self.repository.get_group_by_name(item.class_name)
            if group is None:
                group = Group(name=item.class_name, group_type="class")
                self.repository.add(group)
                self.repository.flush()
            self.repository.add_group_member(
                GroupMember(group_id=group.id, student_profile_id=profile.id)
            )
            created += 1
        self.repository.commit()
        return {"imported": created}

    def import_teachers(self, payload: TeacherImportRequest) -> dict:
        created = 0
        for item in payload.teachers:
            user = User(
                account=item.teacher_no,
                phone=item.phone,
                password_hash="",
                user_type="teacher",
                display_name=item.name,
            )
            profile = TeacherProfile(
                user=user,
                teacher_no=item.teacher_no,
                name=item.name,
                phone=item.phone,
                department=item.department,
            )
            self.repository.add(user)
            self.repository.add(profile)
            created += 1
        self.repository.commit()
        return {"imported": created}

    def import_groups(self, payload: GroupImportRequest) -> dict:
        created = 0
        for item in payload.groups:
            if self.repository.get_group_by_name(item.name) is None:
                self.repository.add(Group(name=item.name, group_type=item.group_type))
                created += 1
        self.repository.commit()
        return {"imported": created}

    def list_students(self) -> dict:
        items = [
            self._student_item(profile) for profile in self.repository.list_students()
        ]
        return {"items": items, "total": len(items)}

    def list_teachers(self) -> dict:
        items = [
            self._teacher_item(profile) for profile in self.repository.list_teachers()
        ]
        return {"items": items, "total": len(items)}

    def list_groups(self) -> dict:
        items = [self._group_item(group) for group in self.repository.list_groups()]
        return {"items": items, "total": len(items)}

    def list_checkin_types(self) -> dict:
        items = [
            {"id": item.id, "name": item.name, "description": item.description}
            for item in self.repository.list_checkin_types()
        ]
        return {"items": items, "total": len(items)}

    def list_rule_templates(self) -> dict:
        items = [
            {
                "id": template.id,
                "name": template.name,
                "type_id": template.type_id,
                "rules_snapshot": template.rules_jsonb,
            }
            for template in self.repository.list_rule_templates()
        ]
        return {"items": items, "total": len(items)}

    def update_rule_template(
        self, template_id: int, payload: RuleTemplateUpdateRequest
    ) -> dict:
        template = self.repository.get_rule_template(template_id)
        if template is None:
            raise ValueError("规则模板不存在")
        template.name = payload.name
        template.rules_jsonb = payload.rules_snapshot
        self.repository.commit()
        return {"updated": True, "id": template.id}

    def list_tasks(self) -> dict:
        items = [self._task_item(task) for task in self.repository.list_tasks()]
        return {"items": items, "total": len(items)}

    def list_exceptions(self) -> dict:
        items = [
            self._exception_item(item) for item in self.repository.list_exceptions()
        ]
        return {"items": items, "total": len(items)}

    def _student_item(self, profile: StudentProfile) -> dict:
        groups = self.repository.list_groups_for_student(profile.id)
        teachers = self.repository.list_teachers_for_student(profile.id)
        return {
            "id": profile.id,
            "student_no": profile.student_no,
            "name": profile.name,
            "phone": profile.phone,
            "college": profile.college,
            "major": profile.major,
            "grade": profile.grade,
            "class_name": profile.class_name,
            "dormitory": profile.dormitory,
            "activated": profile.activated,
            "status": profile.status,
            "user_id": profile.user_id,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "teacher_ids": [teacher.id for teacher in teachers],
            "teacher_names": [teacher.name for teacher in teachers],
        }

    def _teacher_item(self, profile: TeacherProfile) -> dict:
        groups = self.repository.list_groups_for_teacher(profile.id)
        students = self.repository.list_students_for_teacher(profile.id)
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "teacher_no": profile.teacher_no,
            "name": profile.name,
            "phone": profile.phone,
            "department": profile.department,
            "group_ids": [group.id for group in groups],
            "groups": [group.name for group in groups],
            "group_names": [group.name for group in groups],
            "student_count": len(students),
        }

    def _group_item(self, group: Group) -> dict:
        students = self.repository.list_students_for_group(group.id)
        teachers = self.repository.list_teachers_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "student_count": len(students),
            "teacher_count": len(teachers),
            "teacher_ids": [teacher.id for teacher in teachers],
            "teacher_names": [teacher.name for teacher in teachers],
            "task_count": len(tasks),
        }

    def _task_item(self, task: CheckinTask) -> dict:
        groups = self.repository.list_groups_for_task(task.id)
        records = self.repository.list_records_for_task(task.id)
        exceptions = self.repository.list_exceptions_for_task(task.id)
        students = self.repository.list_students_for_task(task.id)
        teacher = self.repository.get_teacher_profile_by_user_id(task.teacher_user_id)
        submitted_count = len({record.student_profile_id for record in records})
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "teacher_user_id": task.teacher_user_id,
            "teacher_id": teacher.id if teacher else None,
            "teacher_name": teacher.name if teacher else None,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "student_count": len(students),
            "submitted_count": submitted_count,
            "completion_rate": self._completion_rate(submitted_count, len(students)),
            "exception_count": len(exceptions),
            "pending_review_count": sum(
                1
                for item in exceptions
                if item.status == RecordStatus.PENDING_REVIEW.value
            ),
        }

    def _exception_item(self, item) -> dict:
        student = self.repository.get_student_profile(item.student_profile_id)
        task = self.repository.get_task(item.task_id)
        record = self.repository.get_record(item.record_id)
        groups = self.repository.list_groups_for_task(item.task_id)
        teacher = (
            self.repository.get_teacher_profile_by_user_id(task.teacher_user_id)
            if task
            else None
        )
        return {
            "id": item.id,
            "record_id": item.record_id,
            "task_id": item.task_id,
            "student_id": item.student_profile_id,
            "student_name": student.name if student else None,
            "student_no": student.student_no if student else None,
            "task_title": task.title if task else None,
            "teacher_id": teacher.id if teacher else None,
            "teacher_name": teacher.name if teacher else None,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "status": item.status,
            "record_status": record.status if record else None,
            "submitted_at": record.submitted_at.isoformat() if record else None,
            "exception_types": item.exception_types_jsonb,
            "messages": item.messages_jsonb,
        }

    def _completion_rate(self, submitted_count: int, expected_count: int) -> int:
        if expected_count == 0:
            return 0
        return round(submitted_count / expected_count * 100)
