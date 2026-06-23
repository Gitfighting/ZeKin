from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["student", "teacher", "admin"]
CheckinType = Literal["dorm", "class", "internship"]
CheckinStatus = Literal["pending", "approved", "rejected"]
ReviewAction = Literal["approved", "rejected"]


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: object | None = None


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    real_name: str = Field(min_length=1, max_length=64)
    role: Role
    class_name: str | None = Field(default=None, max_length=64)
    phone: str = Field(min_length=6, max_length=20)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    class_name: str | None
    phone: str

    model_config = {"from_attributes": True}


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CheckinCreate(BaseModel):
    type: CheckinType
    content: str = Field(min_length=1, max_length=280)
    photo_url: str | None = None
    lat: float | None = None
    lng: float | None = None


class CheckinOut(BaseModel):
    id: int
    user_id: int
    type: str
    content: str
    photo_url: str | None
    lat: float | None
    lng: float | None
    status: str
    created_at: datetime | None = None
    student_name: str | None = None
    class_name: str | None = None

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    checkin_id: int
    action: ReviewAction
    comment: str | None = Field(default=None, max_length=200)


class ReviewOut(BaseModel):
    id: int
    checkin_id: int
    reviewer_id: int
    action: str
    comment: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

