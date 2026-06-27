from fastapi import APIRouter, Depends, Header, HTTPException, status
import logging
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    BindWechatRequest,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    SendCodeRequest,
    StudentActivateRequest,
)
from app.modules.auth.service import AuthError, AuthService
from app.shared.response import success_response

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger("zeKin.auth.register")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    authorization: str = Header(default=""),
    service: AuthService = Depends(get_auth_service),
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        user_id = service.decode_token(token)
        user = service.repository.get_user_by_id(user_id)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    return user


@router.post("/login")
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        result = service.authenticate(account=payload.account, password=payload.password, user_type=payload.user_type)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.post("/register")
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    logger.info(
        "[register-flow] 路由层 收到请求 account=%s phone=%s password_len=%s",
        payload.account.strip(),
        payload.phone.strip(),
        len(payload.password),
    )
    try:
        result = service.register(payload)
    except AuthError as exc:
        logger.warning("[register-flow] 路由层 业务校验失败: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    logger.info(
        "[register-flow] 路由层 注册成功 user_id=%s display_name=%s",
        result.user.id,
        result.user.display_name,
    )
    return success_response(result)


@router.post("/student/activate")
def activate_student(payload: StudentActivateRequest, service: AuthService = Depends(get_auth_service)):
    try:
        result = service.activate_student(payload)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.post("/send-code")
def send_code(payload: SendCodeRequest, service: AuthService = Depends(get_auth_service)):
    return success_response(service.send_code(payload.phone))


@router.post("/bind-wechat")
def bind_wechat(
    payload: BindWechatRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return success_response(service.bind_wechat(current_user=current_user, openid=payload.openid))


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    result: MeResponse = service.get_me(current_user.id)
    return success_response(result)
