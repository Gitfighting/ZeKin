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


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminRepository(db)

    def dashboard(self) -> dict:
        students = self.repository.list_students()
        tasks = self.repository.list_tasks()
        exceptions = self.repository.list_exceptions()
        return {
            "student_count": len(students),
            "task_count": len(tasks),
            "exception_count": len(exceptions),
        }

    def org_tree(self) -> list[dict]:
        groups = self.repository.list_groups()
        return [{"id": group.id, "name": group.name, "type": group.group_type} for group in groups]

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
            self.repository.add_group_member(GroupMember(group_id=group.id, student_profile_id=profile.id))
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
        items = [self._student_item(profile) for profile in self.repository.list_students()]
        return {"items": items, "total": len(items)}

    def list_teachers(self) -> dict:
        items = [
            {
                "id": profile.id,
                "teacher_no": profile.teacher_no,
                "name": profile.name,
                "phone": profile.phone,
                "department": profile.department,
            }
            for profile in self.repository.list_teachers()
        ]
        return {"items": items, "total": len(items)}

    def list_groups(self) -> dict:
        items = [{"id": group.id, "name": group.name, "group_type": group.group_type} for group in self.repository.list_groups()]
        return {"items": items, "total": len(items)}

    def list_checkin_types(self) -> dict:
        items = [{"id": item.id, "name": item.name, "description": item.description} for item in self.repository.list_checkin_types()]
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

    def update_rule_template(self, template_id: int, payload: RuleTemplateUpdateRequest) -> dict:
        template = self.repository.get_rule_template(template_id)
        if template is None:
            raise ValueError("规则模板不存在")
        template.name = payload.name
        template.rules_jsonb = payload.rules_snapshot
        self.repository.commit()
        return {"updated": True, "id": template.id}

    def list_tasks(self) -> dict:
        items = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "starts_at": task.starts_at.isoformat(),
                "ends_at": task.ends_at.isoformat(),
            }
            for task in self.repository.list_tasks()
        ]
        return {"items": items, "total": len(items)}

    def list_exceptions(self) -> dict:
        items = [
            {
                "id": item.id,
                "record_id": item.record_id,
                "task_id": item.task_id,
                "status": item.status,
                "exception_types": item.exception_types_jsonb,
            }
            for item in self.repository.list_exceptions()
        ]
        return {"items": items, "total": len(items)}

    def _student_item(self, profile: StudentProfile) -> dict:
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
        }
