from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin


class CheckinRecord(Base, TimestampMixin):
    __tablename__ = "checkin_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("checkin_tasks.id"))
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
    submitted_at: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column(String(32))
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
    dynamic_code_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
    face_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
    submit_payload_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
    evaluation_messages_jsonb: Mapped[list] = mapped_column(JSON_VARIANT)
    need_review: Mapped[bool] = mapped_column(default=False)


class CheckinRecordAttachment(Base, TimestampMixin):
    __tablename__ = "checkin_record_attachments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("checkin_records.id"))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))


class Appeal(Base, TimestampMixin):
    __tablename__ = "appeals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("checkin_records.id"))
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
    reason: Mapped[str] = mapped_column(Text)
    attachment_ids_jsonb: Mapped[list] = mapped_column(JSON_VARIANT)
    status: Mapped[str] = mapped_column(String(32), default="appeal_pending")
