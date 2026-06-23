from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models import Checkin, User
from app.schemas import ApiResponse, CheckinCreate, CheckinOut


router = APIRouter(prefix="/api/checkins", tags=["checkins"])


def to_checkin_out(checkin: Checkin) -> dict:
    data = CheckinOut.model_validate(checkin).model_dump()
    if checkin.user:
        data["student_name"] = checkin.user.real_name
        data["class_name"] = checkin.user.class_name
    return data


@router.post("", status_code=status.HTTP_201_CREATED)
def create_checkin(
    payload: CheckinCreate,
    current_user: Annotated[User, Depends(require_role("student"))],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse:
    checkin = Checkin(
        user_id=current_user.id,
        type=payload.type,
        content=payload.content,
        photo_url=payload.photo_url,
        lat=payload.lat,
        lng=payload.lng,
        status="pending",
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    checkin.user = current_user
    return ApiResponse(data=to_checkin_out(checkin))


@router.get("/my")
def my_checkins(
    current_user: Annotated[User, Depends(require_role("student"))],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse:
    items = db.scalars(
        select(Checkin)
        .where(Checkin.user_id == current_user.id)
        .order_by(desc(Checkin.created_at), desc(Checkin.id))
    ).all()
    for item in items:
        item.user = current_user
    return ApiResponse(data={"items": [to_checkin_out(item) for item in items]})

