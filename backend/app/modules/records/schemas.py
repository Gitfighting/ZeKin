from pydantic import BaseModel, Field


class CheckinRequest(BaseModel):
    # 位置
    longitude: float | None = None
    latitude: float | None = None
    # 人脸
    face_image: str | None = None
    # 二维码（扫码回传的签名 token）
    qr_payload: str | None = None
    # 附件 / 日志：{"text": str, "files": [str]}
    attachment: dict | None = None
    # 手势：{"pattern_id": str, "points": [[x, y], ...]}
    gesture: dict | None = None
    # 定时任务的当日实例日期 YYYY-MM-DD
    occurrence_date: str | None = None
    # 签到码（兼容旧字段 dynamic_code）
    checkin_code: str | None = None
    dynamic_code: str | None = None
    submit_payload: dict = Field(default_factory=dict)


class AppealRequest(BaseModel):
    reason: str
    attachment_ids: list[int]


class DormitoryLocationUpdateRequest(BaseModel):
    longitude: float
    latitude: float
    address: str | None = None


class InternshipLocationUpdateRequest(BaseModel):
    longitude: float
    latitude: float
    company: str | None = None
    address: str | None = None
