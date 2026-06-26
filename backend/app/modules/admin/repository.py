from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, TeacherProfile
from app.modules.checkin_types.models import CheckinType
from app.modules.exceptions.models import CheckinException
from app.modules.face_recognition.models import FaceEncoding
from app.modules.groups.models import Group, GroupMember
from app.modules.groups.models import GroupTeacher
from app.modules.records.models import CheckinRecord
from app.modules.rule_templates.models import RuleTemplate
from app.modules.tasks.models import CheckinTask, CheckinTaskGroup


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
        return list(
            self.db.scalars(select(CheckinException).order_by(CheckinException.id))
        )

    def list_groups_for_student(self, student_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.student_profile_id == student_profile_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def list_teachers_for_student(
        self, student_profile_id: int
    ) -> list[TeacherProfile]:
        statement = (
            select(TeacherProfile)
            .join(GroupTeacher, GroupTeacher.teacher_profile_id == TeacherProfile.id)
            .join(GroupMember, GroupMember.group_id == GroupTeacher.group_id)
            .where(GroupMember.student_profile_id == student_profile_id)
            .order_by(TeacherProfile.id)
        )
        return list(self.db.scalars(statement).unique())

    def list_groups_for_teacher(self, teacher_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupTeacher, GroupTeacher.group_id == Group.id)
            .where(GroupTeacher.teacher_profile_id == teacher_profile_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def list_students_for_teacher(
        self, teacher_profile_id: int
    ) -> list[StudentProfile]:
        statement = (
            select(StudentProfile)
            .join(GroupMember, GroupMember.student_profile_id == StudentProfile.id)
            .join(GroupTeacher, GroupTeacher.group_id == GroupMember.group_id)
            .where(GroupTeacher.teacher_profile_id == teacher_profile_id)
            .order_by(StudentProfile.id)
        )
        return list(self.db.scalars(statement).unique())

    def list_students_for_group(self, group_id: int) -> list[StudentProfile]:
        statement = (
            select(StudentProfile)
            .join(GroupMember, GroupMember.student_profile_id == StudentProfile.id)
            .where(GroupMember.group_id == group_id)
            .order_by(StudentProfile.id)
        )
        return list(self.db.scalars(statement))

    def list_teachers_for_group(self, group_id: int) -> list[TeacherProfile]:
        statement = (
            select(TeacherProfile)
            .join(GroupTeacher, GroupTeacher.teacher_profile_id == TeacherProfile.id)
            .where(GroupTeacher.group_id == group_id)
            .order_by(TeacherProfile.id)
        )
        return list(self.db.scalars(statement))

    def list_groups_for_task(self, task_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(CheckinTaskGroup, CheckinTaskGroup.group_id == Group.id)
            .where(CheckinTaskGroup.task_id == task_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def list_tasks_for_group_ids(self, group_ids: list[int]) -> list[CheckinTask]:
        if not group_ids:
            return []
        statement = (
            select(CheckinTask)
            .join(CheckinTaskGroup, CheckinTaskGroup.task_id == CheckinTask.id)
            .where(CheckinTaskGroup.group_id.in_(group_ids))
            .order_by(CheckinTask.id)
        )
        return list(self.db.scalars(statement).unique())

    def list_students_for_task(self, task_id: int) -> list[StudentProfile]:
        statement = (
            select(StudentProfile)
            .join(GroupMember, GroupMember.student_profile_id == StudentProfile.id)
            .join(CheckinTaskGroup, CheckinTaskGroup.group_id == GroupMember.group_id)
            .where(CheckinTaskGroup.task_id == task_id)
            .order_by(StudentProfile.id)
        )
        return list(self.db.scalars(statement).unique())

    def list_records_for_task(self, task_id: int) -> list[CheckinRecord]:
        statement = (
            select(CheckinRecord)
            .where(CheckinRecord.task_id == task_id)
            .order_by(CheckinRecord.id)
        )
        return list(self.db.scalars(statement))

    def list_exceptions_for_task(self, task_id: int) -> list[CheckinException]:
        statement = (
            select(CheckinException)
            .where(CheckinException.task_id == task_id)
            .order_by(CheckinException.id)
        )
        return list(self.db.scalars(statement))

    def get_record(self, record_id: int) -> CheckinRecord | None:
        return self.db.get(CheckinRecord, record_id)

    def get_student_profile(self, student_profile_id: int) -> StudentProfile | None:
        return self.db.get(StudentProfile, student_profile_id)

    def get_task(self, task_id: int) -> CheckinTask | None:
        return self.db.get(CheckinTask, task_id)

    def get_teacher_profile_by_user_id(self, user_id: int) -> TeacherProfile | None:
        statement = select(TeacherProfile).where(TeacherProfile.user_id == user_id)
        return self.db.scalar(statement)

    def get_rule_template(self, template_id: int) -> RuleTemplate | None:
        return self.db.get(RuleTemplate, template_id)

    def get_group_by_name(self, name: str) -> Group | None:
        statement = select(Group).where(Group.name == name)
        return self.db.scalar(statement)

    def find_student_by_student_no(self, student_no: str) -> StudentProfile | None:
        statement = select(StudentProfile).where(
            StudentProfile.student_no == student_no
        )
        return self.db.scalar(statement)

    def add_group_member(self, group_member: GroupMember) -> None:
        self.db.add(group_member)

    def list_active_face_student_ids(self) -> set[int]:
        statement = select(FaceEncoding.student_profile_id).where(
            FaceEncoding.is_active.is_(True)
        )
        return set(self.db.scalars(statement))
