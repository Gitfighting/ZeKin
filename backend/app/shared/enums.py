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


class RecordStatus(StrEnum):
    NORMAL = "normal"
    LATE = "late"
    EXCEPTION = "exception"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class ExceptionType(StrEnum):
    MISSING = "missing"
    LATE = "late"
    LOCATION_ERROR = "location_error"
    DYNAMIC_CODE_ERROR = "dynamic_code_error"
    FACE_FAILED = "face_failed"
    SAFETY_RISK = "safety_risk"
    LOG_MISSING = "log_missing"
    APPEAL_PENDING = "appeal_pending"
