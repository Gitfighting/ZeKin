"""日报路由：学生提交 & 查询，教师查看 & 点评。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.router import get_current_user
from app.modules.daily_report.schemas import SubmitDailyReportRequest, TeacherCommentRequest
from app.modules.daily_report.service import DailyReportService
from app.shared.enums import UserType
from app.shared.response import success_response

router = APIRouter(tags=["daily_report"])


def _require_role(role: str):
    def dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.user_type != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
        return current_user

    return dep


def _get_service(db: Session = Depends(get_db)) -> DailyReportService:
    return DailyReportService(db)


# ── 学生端 ────────────────────────────────────────────────────────────────

@router.post("/api/student/daily-reports")
def student_submit_report(
    payload: SubmitDailyReportRequest,
    current_user: User = Depends(_require_role(UserType.STUDENT.value)),
    service: DailyReportService = Depends(_get_service),
):
    try:
        result = service.submit_report(current_user=current_user, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/api/student/daily-reports")
def student_list_reports(
    current_user: User = Depends(_require_role(UserType.STUDENT.value)),
    service: DailyReportService = Depends(_get_service),
):
    try:
        result = service.list_student_reports(current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


# ── 教师端 ────────────────────────────────────────────────────────────────

@router.get("/api/teacher/tasks/{task_id}/daily-reports")
def teacher_list_task_reports(
    task_id: int,
    _: User = Depends(_require_role(UserType.TEACHER.value)),
    service: DailyReportService = Depends(_get_service),
):
    return success_response(service.list_task_reports(task_id=task_id))


@router.post("/api/teacher/daily-reports/{report_id}/comment")
def teacher_add_comment(
    report_id: int,
    payload: TeacherCommentRequest,
    current_user: User = Depends(_require_role(UserType.TEACHER.value)),
    service: DailyReportService = Depends(_get_service),
):
    try:
        result = service.add_comment(
            report_id=report_id, teacher_user=current_user, payload=payload
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)
