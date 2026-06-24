from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, TeacherProfile
from app.modules.checkin_types.models import CheckinType
from app.modules.exceptions.models import CheckinException
from app.modules.groups.models import Group, GroupMember
from app.modules.rule_templates.models import RuleTemplate
from app.modules.tasks.models import CheckinTask


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, entity: object) -> None:
        self.db.add(entity)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def list_students(self) -> list[StudentProfile]:
        return list(self.db.scalars(select(StudentProfile).order_by(StudentProfile.id)))

    def list_teachers(self) -> list[TeacherProfile]:
        return list(self.db.scalars(select(TeacherProfile).order_by(TeacherProfile.id)))

    def list_groups(self) -> list[Group]:
        return list(self.db.scalars(select(Group).order_by(Group.id)))

    def list_checkin_types(self) -> list[CheckinType]:
        return list(self.db.scalars(select(CheckinType).order_by(CheckinType.id)))

    def list_rule_templates(self) -> list[RuleTemplate]:
        return list(self.db.scalars(select(RuleTemplate).order_by(RuleTemplate.id)))

    def list_tasks(self) -> list[CheckinTask]:
        return list(self.db.scalars(select(CheckinTask).order_by(CheckinTask.id)))

    def list_exceptions(self) -> list[CheckinException]:
        return list(self.db.scalars(select(CheckinException).order_by(CheckinException.id)))

    def get_rule_template(self, template_id: int) -> RuleTemplate | None:
        return self.db.get(RuleTemplate, template_id)

    def get_group_by_name(self, name: str) -> Group | None:
        statement = select(Group).where(Group.name == name)
        return self.db.scalar(statement)

    def find_student_by_student_no(self, student_no: str) -> StudentProfile | None:
        statement = select(StudentProfile).where(StudentProfile.student_no == student_no)
        return self.db.scalar(statement)

    def add_group_member(self, group_member: GroupMember) -> None:
        self.db.add(group_member)
