from pydantic import BaseModel


class CheckinRequest(BaseModel):
    longitude: float
    latitude: float
    dynamic_code: str
    face_image: str | None = None
    submit_payload: dict


class AppealRequest(BaseModel):
    reason: str
    attachment_ids: list[int]
