from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, TeacherProfile
from app.modules.checkin_types.models import CheckinType
from app.modules.exceptions.models import CheckinException
from app.modules.groups.models import Group, GroupMember, GroupTeacher
from app.modules.records.models import CheckinRecord
from app.modules.rule_templates.models import RuleTemplate
from app.modules.tasks.models import (
    CheckinTask,
    CheckinTaskGroup,
    CheckinTaskOccurrence,
)


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, entity: object) -> None:
        self.db.add(entity)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def get_task(self, task_id: int) -> CheckinTask | None:
        return self.db.get(CheckinTask, task_id)

    def get_checkin_type(self, type_id: int) -> CheckinType | None:
        return self.db.get(CheckinType, type_id)

    def get_rule_template_for_type(self, type_id: int) -> RuleTemplate | None:
        statement = (
            select(RuleTemplate)
            .where(RuleTemplate.type_id == type_id)
            .order_by(RuleTemplate.id)
        )
        return self.db.scalar(statement)

    def list_tasks_by_teacher(self, teacher_user_id: int) -> list[CheckinTask]:
        statement = (
            select(CheckinTask)
            .where(CheckinTask.teacher_user_id == teacher_user_id)
            .order_by(CheckinTask.id)
        )
        return list(self.db.scalars(statement))

    def list_group_ids_for_task(self, task_id: int) -> list[int]:
        statement = select(CheckinTaskGroup.group_id).where(
            CheckinTaskGroup.task_id == task_id
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

    def list_students_for_task(self, task_id: int) -> list[StudentProfile]:
        statement = (
            select(StudentProfile)
            .join(GroupMember, GroupMember.student_profile_id == StudentProfile.id)
            .join(CheckinTaskGroup, CheckinTaskGroup.group_id == GroupMember.group_id)
            .where(CheckinTaskGroup.task_id == task_id)
            .order_by(StudentProfile.id)
        )
        return list(self.db.scalars(statement).unique())

    def get_student_profile(self, student_profile_id: int) -> StudentProfile | None:
        return self.db.get(StudentProfile, student_profile_id)

    def get_record_for_student_task(
        self, task_id: int, student_profile_id: int
    ) -> CheckinRecord | None:
        statement = (
            select(CheckinRecord)
            .where(
                CheckinRecord.task_id == task_id,
                CheckinRecord.student_profile_id == student_profile_id,
            )
            .order_by(CheckinRecord.id.desc())
        )
        return self.db.scalar(statement)

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

    def list_group_ids_for_student(self, student_profile_id: int) -> list[int]:
        statement = select(GroupMember.group_id).where(
            GroupMember.student_profile_id == student_profile_id
        )
        return list(self.db.scalars(statement))

    def list_students_for_group(self, group_id: int) -> list[StudentProfile]:
        statement = (
            select(StudentProfile)
            .join(GroupMember, GroupMember.student_profile_id == StudentProfile.id)
            .where(GroupMember.group_id == group_id)
            .order_by(StudentProfile.id)
        )
        return list(self.db.scalars(statement))

    def list_group_ids_for_teacher_profile(self, teacher_profile_id: int) -> list[int]:
        statement = select(GroupTeacher.group_id).where(
            GroupTeacher.teacher_profile_id == teacher_profile_id
        )
        return list(self.db.scalars(statement))

    def list_groups_for_teacher_profile(self, teacher_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupTeacher, GroupTeacher.group_id == Group.id)
            .where(GroupTeacher.teacher_profile_id == teacher_profile_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def list_groups_for_student_profile(self, student_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.student_profile_id == student_profile_id)
            .order_by(Group.id)
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

    def get_group(self, group_id: int) -> Group | None:
        return self.db.get(Group, group_id)

    def get_group_by_invite_code(self, invite_code: str) -> Group | None:
        statement = select(Group).where(Group.invite_code == invite_code)
        return self.db.scalar(statement)

    def invite_code_exists(self, invite_code: str) -> bool:
        statement = select(Group.id).where(Group.invite_code == invite_code)
        return self.db.scalar(statement) is not None

    def group_member_exists(self, group_id: int, student_profile_id: int) -> bool:
        statement = select(GroupMember.id).where(
            GroupMember.group_id == group_id,
            GroupMember.student_profile_id == student_profile_id,
        )
        return self.db.scalar(statement) is not None

    def list_records_for_student(self, student_profile_id: int) -> list[CheckinRecord]:
        statement = (
            select(CheckinRecord)
            .where(CheckinRecord.student_profile_id == student_profile_id)
            .order_by(CheckinRecord.id)
        )
        return list(self.db.scalars(statement))

    def map_records_for_student_tasks(
        self, student_profile_id: int, task_ids: list[int]
    ) -> dict[tuple[int, str], CheckinRecord]:
        if not task_ids:
            return {}
        statement = select(CheckinRecord).where(
            CheckinRecord.student_profile_id == student_profile_id,
            CheckinRecord.task_id.in_(task_ids),
        )
        indexed: dict[tuple[int, str], CheckinRecord] = {}
        for record in self.db.scalars(statement):
            indexed[(record.task_id, record.occurrence_date or "")] = record
        return indexed

    def get_exception_by_record_id(self, record_id: int) -> CheckinException | None:
        statement = select(CheckinException).where(
            CheckinException.record_id == record_id
        )
        return self.db.scalar(statement)

    def list_exceptions_for_teacher_task_ids(
        self, task_ids: list[int]
    ) -> list[CheckinException]:
        if not task_ids:
            return []
        statement = (
            select(CheckinException)
            .where(CheckinException.task_id.in_(task_ids))
            .order_by(CheckinException.id)
        )
        return list(self.db.scalars(statement))

    def get_student_profile_by_user_id(self, user_id: int) -> StudentProfile | None:
        statement = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return self.db.scalar(statement)

    # ── 定时任务实例（occurrence） ──────────────────────────────────────
    def get_occurrence(
        self, task_id: int, occurrence_date: str
    ) -> CheckinTaskOccurrence | None:
        statement = select(CheckinTaskOccurrence).where(
            CheckinTaskOccurrence.task_id == task_id,
            CheckinTaskOccurrence.occurrence_date == occurrence_date,
        )
        return self.db.scalar(statement)

    def list_occurrences_for_task(self, task_id: int) -> list[CheckinTaskOccurrence]:
        statement = (
            select(CheckinTaskOccurrence)
            .where(CheckinTaskOccurrence.task_id == task_id)
            .order_by(CheckinTaskOccurrence.occurrence_date)
        )
        return list(self.db.scalars(statement))

    def list_tasks_pending_scheduled_publish(
        self, before: datetime
    ) -> list[CheckinTask]:
        statement = (
            select(CheckinTask)
            .where(
                CheckinTask.is_published.is_(False),
                CheckinTask.scheduled_publish_at.isnot(None),
                CheckinTask.scheduled_publish_at <= before,
            )
            .order_by(CheckinTask.scheduled_publish_at)
        )
        return list(self.db.scalars(statement))
