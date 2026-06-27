"""统一解析考勤/签到状态。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.shared.enums import AttendanceStatus, ExceptionType, RecordStatus

if TYPE_CHECKING:
    from app.modules.exceptions.models import CheckinException
    from app.modules.records.models import CheckinRecord


def resolve_attendance_status(
    *,
    record: CheckinRecord | None,
    exception: CheckinException | None = None,
) -> str:
    """返回 present / late / early_leave / absent / leave。"""
    if record is not None and record.manual_status:
        return record.manual_status

    if record is None:
        return AttendanceStatus.ABSENT.value

    exception_types = (
        exception.exception_types_jsonb if exception is not None else []
    ) or []

    if record.status == RecordStatus.LATE.value:
        return AttendanceStatus.LATE.value
    if ExceptionType.LATE.value in exception_types:
        return AttendanceStatus.LATE.value
    if ExceptionType.EARLY_LEAVE.value in exception_types:
        return AttendanceStatus.EARLY_LEAVE.value

    if record.status == RecordStatus.NORMAL.value:
        return AttendanceStatus.PRESENT.value

    if record.status in {
        RecordStatus.EXCEPTION.value,
        RecordStatus.REJECTED.value,
    }:
        return AttendanceStatus.ABSENT.value

    if exception is not None and exception.status == RecordStatus.PENDING_REVIEW.value:
        if ExceptionType.LATE.value in exception_types:
            return AttendanceStatus.LATE.value
        return AttendanceStatus.ABSENT.value

    return AttendanceStatus.PRESENT.value
