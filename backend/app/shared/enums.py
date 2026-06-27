from enum import StrEnum


class UserType(StrEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class TaskStatus(StrEnum):
    DRAFT = "draft"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"


class ScheduleMode(StrEnum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"


class CheckinMethod(StrEnum):
    FACE = "face"
    LOCATION = "location"
    QR_CODE = "qr_code"
    CHECKIN_CODE = "checkin_code"
    ATTACHMENT = "attachment"
    GESTURE = "gesture"


class RecordStatus(StrEnum):
    NORMAL = "normal"
    LATE = "late"
    EXCEPTION = "exception"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class AttendanceStatus(StrEnum):
    """考勤状态：签到 / 迟到 / 早退 / 未签到 / 请假。"""

    PRESENT = "present"
    LATE = "late"
    EARLY_LEAVE = "early_leave"
    ABSENT = "absent"
    LEAVE = "leave"


class ExceptionType(StrEnum):
    MISSING = "missing"
    LATE = "late"
    EARLY_LEAVE = "early_leave"
    LOCATION_ERROR = "location_error"
    DYNAMIC_CODE_ERROR = "dynamic_code_error"
    QR_FAILED = "qr_failed"
    FACE_FAILED = "face_failed"
    GESTURE_FAILED = "gesture_failed"
    ATTACHMENT_MISSING = "attachment_missing"
    SAFETY_RISK = "safety_risk"
    LOG_MISSING = "log_missing"
    APPEAL_PENDING = "appeal_pending"
