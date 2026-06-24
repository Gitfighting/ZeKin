from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_account(self, *, account: str, user_type: str) -> User | None:
        statement = select(User).where(User.account == account, User.user_type == user_type)
        return self.db.scalar(statement)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

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

    def save(self) -> None:
        self.db.commit()

    def add(self, entity: object) -> None:
        self.db.add(entity)
