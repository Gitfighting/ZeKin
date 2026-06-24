from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSON_VARIANT, TimestampMixin


class RuleTemplate(Base, TimestampMixin):
    __tablename__ = "rule_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    type_id: Mapped[int | None] = mapped_column(ForeignKey("checkin_types.id"), nullable=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    usage_count: Mapped[int] = mapped_column(default=0)
    rules_jsonb: Mapped[dict] = mapped_column(JSON_VARIANT)
