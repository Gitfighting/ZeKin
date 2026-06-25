from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin


class CheckinException(Base, TimestampMixin):
    __tablename__ = "checkin_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("checkin_records.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("checkin_tasks.id"))
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
    exception_types_jsonb: Mapped[list] = mapped_column(JSON_VARIANT)
    messages_jsonb: Mapped[list] = mapped_column(JSON_VARIANT)
    status: Mapped[str] = mapped_column(String(32), default="pending_review")


class ReviewLog(Base, TimestampMixin):
    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("checkin_records.id"))
    reviewer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(Text)
