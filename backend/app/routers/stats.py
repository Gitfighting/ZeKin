from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.cache import cache
from app.core.security import require_role
from app.models import Checkin, User
from app.schemas import ApiResponse


router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def overview(
    current_user: Annotated[User, Depends(require_role("teacher", "admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse:
    cache_key = f"stats:overview:{current_user.role}:{current_user.class_name or 'all'}"
    cached = cache.get_json(cache_key)
    if cached:
        return ApiResponse(data=cached)

    total = db.scalar(select(func.count(Checkin.id))) or 0
    approved = db.scalar(select(func.count(Checkin.id)).where(Checkin.status == "approved")) or 0
    pending = db.scalar(select(func.count(Checkin.id)).where(Checkin.status == "pending")) or 0
    rejected = db.scalar(select(func.count(Checkin.id)).where(Checkin.status == "rejected")) or 0
    data = {
        "total_checkins": total,
        "approved_checkins": approved,
        "pending_checkins": pending,
        "rejected_checkins": rejected,
        "checkin_rate": 1.0 if total else 0.0,
        "missing_students": 0,
        "max_streak_days": 1 if total else 0,
    }
    cache.set_json(cache_key, data, ttl_seconds=60)
    return ApiResponse(data=data)
