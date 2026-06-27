from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.router import get_current_user
from app.modules.tasks.schemas import CreateGroupRequest, CreateTaskRequest, SetAttendanceRequest
from app.modules.tasks.service import TaskService
from app.shared.enums import UserType
from app.shared.response import success_response

router = APIRouter(prefix="/api/teacher", tags=["teacher"])


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.TEACHER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return current_user


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("/dashboard")
def dashboard(current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    return success_response(service.teacher_dashboard(current_user.id))


@router.get("/groups")
def groups(current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    return success_response(service.list_teacher_groups(current_user))


@router.post("/groups")
def create_group(
    payload: CreateGroupRequest,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.create_teacher_group(current_user, payload.name)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)


@router.get("/groups/{group_id}")
def get_group(
    group_id: int,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.get_teacher_group_detail(group_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks")
def list_tasks(current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    return success_response(service.list_teacher_tasks(current_user.id))


@router.post("/tasks")
def create_task(
    payload: CreateTaskRequest,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.create_task(teacher_user=current_user, payload=payload)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks/{task_id}")
def get_task(task_id: int, current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    try:
        result = service.get_task_detail(task_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.post("/tasks/{task_id}/publish")
def publish_task(task_id: int, current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    try:
        result = service.publish_task(task_id=task_id, teacher_user=current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks/{task_id}/qr-code")
def get_qr_code(
    task_id: int,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.get_qr_code(task_id=task_id, teacher_user=current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.post("/tasks/{task_id}/qr-code/refresh")
def refresh_qr_code(
    task_id: int,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.get_qr_code(
            task_id=task_id, teacher_user=current_user, refresh=True
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.post("/tasks/{task_id}/students/{student_id}/attendance")
def set_student_attendance(
    task_id: int,
    student_id: int,
    payload: SetAttendanceRequest,
    current_user: User = Depends(require_teacher),
    service: TaskService = Depends(get_task_service),
):
    try:
        result = service.set_student_attendance(
            task_id=task_id,
            student_profile_id=student_id,
            status=payload.status.value,
            remark=payload.remark,
            teacher_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.post("/tasks/{task_id}/end")
def end_task(task_id: int, current_user: User = Depends(require_teacher), service: TaskService = Depends(get_task_service)):
    try:
        result = service.end_task(task_id=task_id, teacher_user=current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)
