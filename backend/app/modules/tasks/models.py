from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin
from app.shared.enums import ScheduleMode, TaskStatus


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
    scheduled_publish_at: Mapped[datetime | None] = mapped_column(nullable=True)
    rules_snapshot_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
    # ── 任务周期：一次任务 / 定时循环任务
    schedule_mode: Mapped[str] = mapped_column(
        String(20), default=ScheduleMode.ONE_TIME.value
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # ── 二维码签到：当前有效 token（启用 qr_code 时由教师刷新写入）
    current_qr_token: Mapped[str | None] = mapped_column(Text, nullable=True)


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


class CheckinTaskOccurrence(Base, TimestampMixin):
    """定时任务的每日实例（物化）。一次任务也会生成单条记录。"""

    __tablename__ = "checkin_task_occurrences"
    __table_args__ = (UniqueConstraint("task_id", "occurrence_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("checkin_tasks.id"), index=True)
    occurrence_date: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.NOT_STARTED.value)
