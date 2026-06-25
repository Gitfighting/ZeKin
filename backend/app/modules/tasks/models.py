from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin
from app.shared.enums import TaskStatus


class CheckinTask(Base, TimestampMixin):
    __tablename__ = "checkin_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("checkin_types.id"))
    teacher_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.DRAFT.value)
    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()
    is_published: Mapped[bool] = mapped_column(default=False)
    rules_snapshot_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)


class CheckinTaskGroup(Base, TimestampMixin):
    __tablename__ = "checkin_task_groups"
    __table_args__ = (UniqueConstraint("task_id", "group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("checkin_tasks.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))


class CheckinTaskStudent(Base, TimestampMixin):
    __tablename__ = "checkin_task_students"
    __table_args__ = (UniqueConstraint("task_id", "student_profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("checkin_tasks.id"))
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
