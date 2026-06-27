from jose import JWTError, jwt
import logging
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.auth.models import StudentProfile, User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginResponse,
    LoginUser,
    MeResponse,
    RegisterRequest,
    StudentActivateRequest,
    StudentActivateResponse,
)
from app.shared.enums import UserType

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
logger = logging.getLogger("zeKin.auth.register")


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuthRepository(db)
        self.settings = get_settings()

    def authenticate(
        self,
        *,
        account: str,
        password: str,
        user_type: UserType | None,
    ) -> LoginResponse:
        user = self.repository.get_user_by_account(
            account=account,
            user_type=user_type.value if user_type is not None else None,
        )
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

    def register(self, payload: RegisterRequest) -> LoginResponse:
        account = payload.account.strip()
        phone = payload.phone.strip()
        password = payload.password

        logger.info("[register-flow] 服务层 开始校验 account=%s phone=%s", account, phone)

        if not account or not phone:
            logger.warning("[register-flow] 服务层 校验失败: 缺少学号/工号或手机号")
            raise AuthError("请填写学号/工号和手机号")
        if len(password) < 6:
            logger.warning("[register-flow] 服务层 校验失败: 密码长度不足")
            raise AuthError("密码至少 6 位")

        existing_user = self.repository.get_user_by_account(account=account, user_type=None)
        if existing_user is not None:
            logger.warning("[register-flow] 服务层 校验失败: 账号已存在 user_id=%s", existing_user.id)
            raise AuthError("该学号/工号已注册，请直接登录")

        existing_phone = self.repository.get_user_by_phone(phone)
        if existing_phone is not None:
            logger.warning("[register-flow] 服务层 校验失败: 手机号已存在 user_id=%s", existing_phone.id)
            raise AuthError("该手机号已注册")

        existing_profile = self.repository.get_student_by_student_no(account)
        if existing_profile is not None:
            logger.warning(
                "[register-flow] 服务层 校验失败: 学号档案已存在 profile_id=%s",
                existing_profile.id,
            )
            raise AuthError("该学号/工号已注册，请直接登录")

        display_name = f"用户{account}"
        logger.info("[register-flow] 服务层 校验通过，准备写入数据库 display_name=%s", display_name)

        user = User(
            account=account,
            phone=phone,
            password_hash=pwd_context.hash(password),
            user_type=UserType.STUDENT.value,
            display_name=display_name,
        )
        profile = StudentProfile(
            user=user,
            student_no=account,
            name=display_name,
            phone=phone,
            college="未填写",
            major="未填写",
            grade="2026",
            class_name="未分班",
            dormitory="未填写",
            activated=True,
            status="active",
        )
        self.repository.add(user)
        logger.info("[register-flow] 服务层 已 add User（待 flush）")
        self.repository.add(profile)
        logger.info("[register-flow] 服务层 已 add StudentProfile（待 commit）")
        self.repository.save()
        logger.info(
            "[register-flow] 服务层 数据库 commit 成功 user_id=%s student_no=%s",
            user.id,
            profile.student_no,
        )
        response = self._build_login_response(user)
        logger.info("[register-flow] 服务层 已生成 token，准备返回")
        return response

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
