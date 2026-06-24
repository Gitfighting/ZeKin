from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile
from app.modules.exceptions.models import CheckinException
from app.modules.groups.models import Group, GroupMember, GroupTeacher
from app.modules.records.models import CheckinRecord
from app.modules.tasks.models import CheckinTask, CheckinTaskGroup


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

    def list_tasks_by_teacher(self, teacher_user_id: int) -> list[CheckinTask]:
        statement = select(CheckinTask).where(CheckinTask.teacher_user_id == teacher_user_id).order_by(CheckinTask.id)
        return list(self.db.scalars(statement))

    def list_group_ids_for_task(self, task_id: int) -> list[int]:
        statement = select(CheckinTaskGroup.group_id).where(CheckinTaskGroup.task_id == task_id)
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
        statement = select(GroupMember.group_id).where(GroupMember.student_profile_id == student_profile_id)
        return list(self.db.scalars(statement))

    def list_group_ids_for_teacher_profile(self, teacher_profile_id: int) -> list[int]:
        statement = select(GroupTeacher.group_id).where(GroupTeacher.teacher_profile_id == teacher_profile_id)
        return list(self.db.scalars(statement))

    def list_groups_for_teacher_profile(self, teacher_profile_id: int) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupTeacher, GroupTeacher.group_id == Group.id)
            .where(GroupTeacher.teacher_profile_id == teacher_profile_id)
            .order_by(Group.id)
        )
        return list(self.db.scalars(statement))

    def list_records_for_student(self, student_profile_id: int) -> list[CheckinRecord]:
        statement = select(CheckinRecord).where(CheckinRecord.student_profile_id == student_profile_id).order_by(CheckinRecord.id)
        return list(self.db.scalars(statement))

    def list_exceptions_for_teacher_task_ids(self, task_ids: list[int]) -> list[CheckinException]:
        if not task_ids:
            return []
        statement = select(CheckinException).where(CheckinException.task_id.in_(task_ids)).order_by(CheckinException.id)
        return list(self.db.scalars(statement))

    def get_student_profile_by_user_id(self, user_id: int) -> StudentProfile | None:
        statement = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return self.db.scalar(statement)
