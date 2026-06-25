from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.router import get_current_user
from app.modules.records.service import RecordService
from app.shared.enums import UserType
from app.shared.response import success_response

router = APIRouter(prefix="/api/teacher", tags=["exceptions"])


class ReviewRequest(BaseModel):
    decision: str
    comment: str


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.TEACHER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return current_user


def get_record_service(db: Session = Depends(get_db)) -> RecordService:
    return RecordService(db)


@router.get("/exceptions")
def list_exceptions(current_user: User = Depends(require_teacher), service: RecordService = Depends(get_record_service)):
    return success_response(service.list_teacher_exceptions(current_user))


@router.post("/exceptions/{exception_id}/review")
def review_exception(
    exception_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(require_teacher),
    service: RecordService = Depends(get_record_service),
):
    try:
        result = service.review_exception(current_user=current_user, exception_id=exception_id, payload=payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)
