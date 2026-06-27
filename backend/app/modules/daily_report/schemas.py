from pydantic import BaseModel, Field


class SubmitDailyReportRequest(BaseModel):
    task_id: int | None = None
    report_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    content: str = Field(..., min_length=10, max_length=2000)
    work_hours: float | None = Field(None, ge=0, le=24)
    mood: str | None = Field(None, pattern=r"^(good|normal|bad)$")
    photo_urls: list[str] = Field(default_factory=list)


class TeacherCommentRequest(BaseModel):
    comment: str = Field(..., min_length=1, max_length=500)
