from sqlalchemy import select
import logging
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, TeacherProfile, User
from app.shared.enums import UserType

logger = logging.getLogger("zeKin.auth.register")


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_account(self, *, account: str, user_type: str | None) -> User | None:
        statement = select(User).where(User.account == account)
        if user_type is None:
            statement = statement.where(
                User.user_type.in_([UserType.STUDENT.value, UserType.TEACHER.value])
            )
        else:
            statement = statement.where(User.user_type == user_type)
        return self.db.scalar(statement)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_user_by_phone(self, phone: str) -> User | None:
        statement = select(User).where(User.phone == phone)
        return self.db.scalar(statement)

    def get_student_by_student_no(self, student_no: str) -> StudentProfile | None:
        statement = select(StudentProfile).where(StudentProfile.student_no == student_no)
        return self.db.scalar(statement)

    def get_student_profile_for_activation(
        self,
        *,
        name: str,
        student_no: str,
        phone: str,
    ) -> StudentProfile | None:
        statement = select(StudentProfile).where(
            StudentProfile.name == name,
            StudentProfile.student_no == student_no,
            StudentProfile.phone == phone,
        )
        return self.db.scalar(statement)

    def get_student_by_no_and_phone(
        self, student_no: str, phone: str
    ) -> StudentProfile | None:
        statement = select(StudentProfile).where(
            StudentProfile.student_no == student_no,
            StudentProfile.phone == phone,
        )
        return self.db.scalar(statement)

    def get_teacher_by_no_and_phone(
        self, teacher_no: str, phone: str
    ) -> TeacherProfile | None:
        statement = select(TeacherProfile).where(
            TeacherProfile.teacher_no == teacher_no,
            TeacherProfile.phone == phone,
        )
        return self.db.scalar(statement)

    def save(self) -> None:
        logger.info("[register-flow] 仓储层 db.commit() 开始")
        self.db.commit()
        logger.info("[register-flow] 仓储层 db.commit() 完成")

    def add(self, entity: object) -> None:
        self.db.add(entity)
