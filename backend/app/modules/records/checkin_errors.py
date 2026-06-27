"""签到硬性校验失败：写入异常记录供申诉，并返回 record_id。"""
from __future__ import annotations

from app.modules.records.verifiers.pipeline import PipelineResult
from app.shared.enums import ExceptionType

BLOCKING_CHECKIN_EXCEPTIONS = frozenset(
    {
        ExceptionType.FACE_FAILED.value,
        ExceptionType.LOCATION_ERROR.value,
        ExceptionType.DYNAMIC_CODE_ERROR.value,
    }
)

_EXCEPTION_METHOD = {
    ExceptionType.FACE_FAILED.value: "face",
    ExceptionType.LOCATION_ERROR.value: "location",
    ExceptionType.DYNAMIC_CODE_ERROR.value: "checkin_code",
}

_DEFAULT_MESSAGES = {
    ExceptionType.FACE_FAILED.value: "人脸识别未通过，请重新拍摄后重试",
    ExceptionType.LOCATION_ERROR.value: "当前位置不在签到范围内，请到指定地点后重新定位",
    ExceptionType.DYNAMIC_CODE_ERROR.value: "签到码错误，请核对老师公布的签到码后重试",
}


class CheckinBlockedError(ValueError):
    def __init__(self, message: str, record_id: int) -> None:
        super().__init__(message)
        self.record_id = record_id


def get_blocking_checkin_failure(result: PipelineResult) -> str | None:
    """若存在阻断类校验失败，返回面向学生的错误文案。"""
    for exc_type in result.exception_types:
        if exc_type not in BLOCKING_CHECKIN_EXCEPTIONS:
            continue
        method = _EXCEPTION_METHOD.get(exc_type)
        if method:
            detail = result.verification_results.get(method, {})
            message = detail.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        for message in result.messages:
            if isinstance(message, str) and message.strip():
                return message.strip()
        return _DEFAULT_MESSAGES.get(exc_type, "签到校验未通过，请检查后重试")
    return None
