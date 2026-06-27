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
    occurrence_date: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32))
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    # 统一保存所有启用签到方式的逐项校验结果
    verification_results_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
    enabled_methods_jsonb: Mapped[list] = mapped_column(JSON_VARIANT, default=list)
    # 兼容字段（旧结构，便于平滑迁移）
    location_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
    dynamic_code_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
    face_result_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
    submit_payload_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
    evaluation_messages_jsonb: Mapped[list] = mapped_column(JSON_VARIANT, default=list)
    need_review: Mapped[bool] = mapped_column(default=False)
    # 教师手动考勤覆盖：present / absent / leave（为空表示按系统判定）
    manual_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    manual_remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


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
