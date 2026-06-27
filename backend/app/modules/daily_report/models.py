"""日报模型：学生每日实习/任务日志记录。"""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin


class DailyReport(Base, TimestampMixin):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), index=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("checkin_tasks.id"), nullable=True, index=True)
    report_date: Mapped[str] = mapped_column(String(10))   # YYYY-MM-DD
    content: Mapped[str] = mapped_column(Text)
    work_hours: Mapped[float | None] = mapped_column(nullable=True)
    mood: Mapped[str | None] = mapped_column(String(20), nullable=True)  # good/normal/bad
    photo_urls_jsonb: Mapped[list] = mapped_column(JSON_VARIANT, default=list)
    status: Mapped[str] = mapped_column(String(20), default="submitted")  # submitted/reviewed
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
