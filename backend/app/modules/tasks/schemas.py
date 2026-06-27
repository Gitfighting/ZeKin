from pydantic import BaseModel

from app.shared.enums import AttendanceStatus, ScheduleMode


class CreateTaskRequest(BaseModel):
    title: str
    type_id: int
    group_ids: list[int]
    starts_at: str
    ends_at: str
    rules_snapshot: dict
    schedule_mode: ScheduleMode = ScheduleMode.ONE_TIME
    recurrence_rule: str | None = None


class SetAttendanceRequest(BaseModel):
    status: AttendanceStatus
    remark: str | None = None


class CreateGroupRequest(BaseModel):
    name: str


class JoinGroupRequest(BaseModel):
    invite_code: str
