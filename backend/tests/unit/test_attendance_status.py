"""考勤状态解析单元测试。"""
from datetime import datetime

from app.modules.exceptions.models import CheckinException
from app.modules.records.models import CheckinRecord
from app.shared.attendance import resolve_attendance_status
from app.shared.enums import AttendanceStatus, ExceptionType, RecordStatus


def _record(**kwargs) -> CheckinRecord:
    defaults = {
        "task_id": 1,
        "student_profile_id": 1,
        "submitted_at": datetime(2026, 6, 26, 21, 40),
        "occurrence_date": "2026-06-26",
        "status": RecordStatus.NORMAL.value,
        "verification_results_jsonb": {},
        "enabled_methods_jsonb": [],
        "submit_payload_jsonb": {},
    }
    defaults.update(kwargs)
    return CheckinRecord(**defaults)


def test_resolve_attendance_status_manual_leave() -> None:
    record = _record(manual_status=AttendanceStatus.LEAVE.value)
    assert resolve_attendance_status(record=record) == AttendanceStatus.LEAVE.value


def test_resolve_attendance_status_late_from_record_status() -> None:
    record = _record(status=RecordStatus.LATE.value)
    assert resolve_attendance_status(record=record) == AttendanceStatus.LATE.value


def test_resolve_attendance_status_early_leave_from_exception() -> None:
    record = _record(status=RecordStatus.EXCEPTION.value)
    exception = CheckinException(
        record_id=1,
        task_id=1,
        student_profile_id=1,
        exception_types_jsonb=[ExceptionType.EARLY_LEAVE.value],
        messages_jsonb=["早退"],
        status=RecordStatus.EXCEPTION.value,
    )
    assert (
        resolve_attendance_status(record=record, exception=exception)
        == AttendanceStatus.EARLY_LEAVE.value
    )


def test_resolve_attendance_status_absent_when_no_record() -> None:
    assert resolve_attendance_status(record=None) == AttendanceStatus.ABSENT.value
