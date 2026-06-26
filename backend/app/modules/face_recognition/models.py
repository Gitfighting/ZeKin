from sqlalchemy import Boolean, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin


class FaceEncoding(Base, TimestampMixin):
    __tablename__ = "face_encodings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_profile_id: Mapped[int | None] = mapped_column(ForeignKey("student_profiles.id"), index=True, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    encoding: Mapped[bytes] = mapped_column(LargeBinary)
    dimension: Mapped[int] = mapped_column(Integer, default=128)
    model_name: Mapped[str] = mapped_column(String(64), default="face_recognition")
    source: Mapped[str] = mapped_column(String(64), default="admin_upload")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    quality_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT, default=dict)
