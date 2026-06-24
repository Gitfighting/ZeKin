from pydantic import BaseModel


class CheckinRequest(BaseModel):
    longitude: float
    latitude: float
    dynamic_code: str
    submit_payload: dict


class AppealRequest(BaseModel):
    reason: str
    attachment_ids: list[int]
