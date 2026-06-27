from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    group_type: Mapped[str] = mapped_column(String(50), default="class")
    invite_code: Mapped[str] = mapped_column(String(8), unique=True, index=True)


class GroupMember(Base, TimestampMixin):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "student_profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    student_profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))


class GroupTeacher(Base, TimestampMixin):
    __tablename__ = "group_teachers"
    __table_args__ = (UniqueConstraint("group_id", "teacher_profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    teacher_profile_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"))
