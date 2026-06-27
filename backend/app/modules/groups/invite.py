import secrets
import string

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.groups.models import Group


def generate_unique_invite_code(db: Session, length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        existing = db.scalar(select(Group.id).where(Group.invite_code == code))
        if existing is None:
            return code
