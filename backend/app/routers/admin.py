from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_role
from app.models import Checkin, User
from app.routers.checkins import to_checkin_out
from app.schemas import ApiResponse, UserOut


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(
    _: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
    keyword: str | None = Query(default=None),
    role: str | None = Query(default=None),
) -> ApiResponse:
    query = select(User).order_by(desc(User.created_at), desc(User.id))
    if role:
        query = query.where(User.role == role)
    if keyword:
        like = f"%{keyword}%"
        query = query.where(
            or_(User.username.like(like), User.real_name.like(like), User.phone.like(like))
        )
    users = db.scalars(query).all()
    return ApiResponse(data={"items": [UserOut.model_validate(user).model_dump() for user in users]})


@router.get("/checkins")
def list_checkins(
    _: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    type: str | None = Query(default=None),
) -> ApiResponse:
    query = select(Checkin).options(joinedload(Checkin.user)).order_by(
        desc(Checkin.created_at),
        desc(Checkin.id),
    )
    if status:
        query = query.where(Checkin.status == status)
    if type:
        query = query.where(Checkin.type == type)
    if keyword:
        like = f"%{keyword}%"
        query = query.join(User).where(or_(User.real_name.like(like), User.class_name.like(like)))
    items = db.scalars(query).all()
    return ApiResponse(data={"items": [to_checkin_out(item) for item in items]})

