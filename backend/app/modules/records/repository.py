from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile
from app.modules.exceptions.models import CheckinException
from app.modules.groups.models import Group, GroupMember
from app.modules.messages.models import Message
from app.modules.records.models import CheckinRecord
from app.modules.tasks.models import CheckinTask, CheckinTaskGroup


class RecordRepository:
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

    def get_student_profile_by_user_id(self, user_id: int) -> StudentProfile | None:
        statement = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return self.db.scalar(statement)

    def list_task_ids_for_student(self, student_profile_id: int) -> list[int]:
        from app.modules.groups.models import GroupMember
        from app.modules.tasks.models import CheckinTaskGroup

        statement = (
            select(CheckinTaskGroup.task_id)
            .join(GroupMember, GroupMember.group_id == CheckinTaskGroup.group_id)
            .where(GroupMember.student_profile_id == student_profile_id)
        )
        return list(self.db.scalars(statement))

    def list_tasks_for_student(self, student_profile_id: int) -> list[CheckinTask]:
        task_ids = self.list_task_ids_for_student(student_profile_id)
        if not task_ids:
            return []
        statement = (
            select(CheckinTask)
            .where(CheckinTask.id.in_(task_ids))
            .order_by(CheckinTask.id)
        )
        return list(self.db.scalars(statement))

    def list_records_for_student(self, student_profile_id: int) -> list[CheckinRecord]:
        statement = (
            select(CheckinRecord)
            .where(CheckinRecord.student_profile_id == student_profile_id)
            .order_by(CheckinRecord.id)
        )
        return list(self.db.scalars(statement))

    def list_messages_for_user(self, user_id: int) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.id.desc())
        )
        return list(self.db.scalars(statement))

    def get_record(self, record_id: int) -> CheckinRecord | None:
        return self.db.get(CheckinRecord, record_id)

    def list_groups_for_task(self, task_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(CheckinTaskGroup, CheckinTaskGroup.group_id == Group.id)
            .where(CheckinTaskGroup.task_id == task_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def get_student_profile(self, student_profile_id: int) -> StudentProfile | None:
        return self.db.get(StudentProfile, student_profile_id)

    def list_groups_for_student(self, student_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.student_profile_id == student_profile_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def get_exception_by_record_id(self, record_id: int) -> CheckinException | None:
        statement = select(CheckinException).where(
            CheckinException.record_id == record_id
        )
        return self.db.scalar(statement)

    def list_exceptions_for_teacher(
        self, teacher_user_id: int
    ) -> list[CheckinException]:
        from app.modules.tasks.models import CheckinTask

        statement = (
            select(CheckinException)
            .join(CheckinTask, CheckinTask.id == CheckinException.task_id)
            .where(CheckinTask.teacher_user_id == teacher_user_id)
            .order_by(CheckinException.id)
        )
        return list(self.db.scalars(statement))

    def get_exception(self, exception_id: int) -> CheckinException | None:
        return self.db.get(CheckinException, exception_id)
