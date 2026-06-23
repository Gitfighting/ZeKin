from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_role
from app.models import Checkin, Review, User
from app.routers.checkins import to_checkin_out
from app.schemas import ApiResponse, ReviewCreate, ReviewOut


router = APIRouter(prefix="/api/teacher", tags=["teacher"])


@router.get("/checkins")
def teacher_checkins(
    current_user: Annotated[User, Depends(require_role("teacher", "admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse:
    query = select(Checkin).options(joinedload(Checkin.user)).order_by(
        desc(Checkin.created_at),
        desc(Checkin.id),
    )
    if current_user.role == "teacher" and current_user.class_name:
        query = query.join(User).where(User.class_name == current_user.class_name)
    items = db.scalars(query).all()
    return ApiResponse(data={"items": [to_checkin_out(item) for item in items]})


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: Annotated[User, Depends(require_role("teacher", "admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse:
    checkin = db.get(Checkin, payload.checkin_id)
    if checkin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡记录不存在")
    if payload.action == "rejected" and not payload.comment:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="拒绝必须填写评语")
    review = Review(
        checkin_id=payload.checkin_id,
        reviewer_id=current_user.id,
        action=payload.action,
        comment=payload.comment,
    )
    checkin.status = payload.action
    db.add(review)
    db.commit()
    db.refresh(review)
    return ApiResponse(data=ReviewOut.model_validate(review).model_dump())

