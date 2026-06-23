from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models import User
from app.schemas import ApiResponse, LoginOut, LoginRequest, RegisterRequest, UserOut


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> ApiResponse:
    existing = db.scalar(
        select(User).where(or_(User.username == payload.username, User.phone == payload.phone))
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户已存在")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        real_name=payload.real_name,
        role=payload.role,
        class_name=payload.class_name,
        phone=payload.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(data=UserOut.model_validate(user).model_dump())


@router.post("/login")
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> ApiResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="手机号或密码错误")
    token = create_access_token(user)
    return ApiResponse(
        data=LoginOut(access_token=token, user=UserOut.model_validate(user)).model_dump()
    )


@router.get("/me")
def me(current_user: Annotated[User, Depends(get_current_user)]) -> ApiResponse:
    return ApiResponse(data=UserOut.model_validate(current_user).model_dump())

