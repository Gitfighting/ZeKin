from pydantic import BaseModel

from app.shared.enums import UserType


class LoginRequest(BaseModel):
    account: str
    password: str
    user_type: UserType | None = None


class LoginUser(BaseModel):
    id: int
    user_type: UserType
    display_name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUser


class StudentActivateRequest(BaseModel):
    name: str
    student_no: str
    phone: str
    code: str
    password: str
    dormitory_longitude: float | None = None
    dormitory_latitude: float | None = None
    dormitory_address: str | None = None


class RegisterRequest(BaseModel):
    account: str
    phone: str
    password: str


class StudentActivateResponse(BaseModel):
    activated: bool
    access_token: str


class SendCodeRequest(BaseModel):
    phone: str


class SendCodeResponse(BaseModel):
    sent: bool
    code: str


class BindWechatRequest(BaseModel):
    openid: str


class MeResponse(BaseModel):
    id: int
    account: str
    user_type: UserType
    display_name: str
