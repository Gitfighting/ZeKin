from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class CheckinType(Base, TimestampMixin):
    __tablename__ = "checkin_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
