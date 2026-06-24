from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.router import get_current_user
from app.modules.records.schemas import AppealRequest, CheckinRequest
from app.modules.records.service import RecordService
from app.shared.enums import UserType
from app.shared.response import success_response

router = APIRouter(prefix="/api/student", tags=["student"])


def require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return current_user


def get_record_service(db: Session = Depends(get_db)) -> RecordService:
    return RecordService(db)


@router.get("/dashboard")
def dashboard(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.student_dashboard(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks")
def tasks(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.list_student_tasks(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks/{task_id}")
def task_detail(task_id: int, current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.get_student_task(current_user, task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.post("/tasks/{task_id}/checkin")
def checkin(
    task_id: int,
    payload: CheckinRequest,
    current_user: User = Depends(require_student),
    service: RecordService = Depends(get_record_service),
):
    try:
        result = service.submit_checkin(current_user=current_user, task_id=task_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/records")
def records(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.list_student_records(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.post("/records/{record_id}/appeal")
def appeal(
    record_id: int,
    payload: AppealRequest,
    current_user: User = Depends(require_student),
    service: RecordService = Depends(get_record_service),
):
    try:
        result = service.submit_appeal(current_user=current_user, record_id=record_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/messages")
def messages(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    return success_response(service.list_messages(current_user))


@router.get("/profile")
def profile(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.profile(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/growth-summary")
def growth_summary(current_user: User = Depends(require_student), service: RecordService = Depends(get_record_service)):
    try:
        result = service.growth_summary(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)
