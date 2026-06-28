from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.shared.enums import UserType


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    user_type: Mapped[str] = mapped_column(String(20), default=UserType.STUDENT.value)
    display_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="active")
    wechat_openid: Mapped[str | None] = mapped_column(String(128), nullable=True)

    student_profile: Mapped["StudentProfile | None"] = relationship(back_populates="user")
    teacher_profile: Mapped["TeacherProfile | None"] = relationship(back_populates="user")
    admin_profile: Mapped["AdminProfile | None"] = relationship(back_populates="user")


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    student_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    college: Mapped[str] = mapped_column(String(100))
    major: Mapped[str] = mapped_column(String(100))
    grade: Mapped[str] = mapped_column(String(20))
    class_name: Mapped[str] = mapped_column(String(100))
    dormitory: Mapped[str] = mapped_column(String(100))
    dormitory_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    dormitory_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    dormitory_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    internship_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    internship_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    internship_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    internship_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activated: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(20), default="imported")

    user: Mapped[User | None] = relationship(back_populates="student_profile")


class TeacherProfile(Base, TimestampMixin):
    __tablename__ = "teacher_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    teacher_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped[User] = relationship(back_populates="teacher_profile")


class AdminProfile(Base, TimestampMixin):
    __tablename__ = "admin_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped[User] = relationship(back_populates="admin_profile")
