from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginResponse,
    LoginUser,
    MeResponse,
    StudentActivateRequest,
    StudentActivateResponse,
)
from app.shared.enums import UserType

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuthRepository(db)
        self.settings = get_settings()

    def authenticate(self, *, account: str, password: str, user_type: UserType) -> LoginResponse:
        user = self.repository.get_user_by_account(account=account, user_type=user_type.value)
        if user is None or not pwd_context.verify(password, user.password_hash):
            raise AuthError("账号或密码错误")
        return self._build_login_response(user)

    def activate_student(self, payload: StudentActivateRequest) -> StudentActivateResponse:
        profile = self.repository.get_student_profile_for_activation(
            name=payload.name,
            student_no=payload.student_no,
            phone=payload.phone,
        )
        if profile is None:
            raise AuthError("学生档案不存在")
        if payload.code != "000000":
            raise AuthError("验证码错误")

        user = profile.user
        if user is None:
            user = User(
                account=payload.student_no,
                phone=payload.phone,
                password_hash=pwd_context.hash(payload.password),
                user_type=UserType.STUDENT.value,
                display_name=payload.name,
            )
            self.repository.add(user)
            self.db.flush()
            profile.user_id = user.id
        else:
            user.password_hash = pwd_context.hash(payload.password)

        profile.activated = True
        profile.status = "active"
        self.repository.save()
        return StudentActivateResponse(activated=True, access_token=self._create_token(user))

    def send_code(self, phone: str) -> dict[str, str | bool]:
        return {"sent": True, "code": "000000", "phone": phone}

    def bind_wechat(self, *, current_user: User, openid: str) -> dict[str, bool]:
        current_user.wechat_openid = openid
        self.repository.save()
        return {"bound": True}

    def get_me(self, user_id: int) -> MeResponse:
        user = self.repository.get_user_by_id(user_id)
        if user is None:
            raise AuthError("用户不存在")
        return MeResponse(
            id=user.id,
            account=user.account,
            user_type=UserType(user.user_type),
            display_name=user.display_name,
        )

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self.settings.jwt_secret_key, algorithms=[self.settings.jwt_algorithm])
        except JWTError as exc:
            raise AuthError("无效令牌") from exc
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id.isdigit():
            raise AuthError("无效令牌")
        return int(user_id)

    def _build_login_response(self, user: User) -> LoginResponse:
        return LoginResponse(
            access_token=self._create_token(user),
            user=LoginUser(
                id=user.id,
                user_type=UserType(user.user_type),
                display_name=user.display_name,
            ),
        )

    def _create_token(self, user: User) -> str:
        return jwt.encode(
            {"sub": str(user.id), "user_type": user.user_type},
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )
