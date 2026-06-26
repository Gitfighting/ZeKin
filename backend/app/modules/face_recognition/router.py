from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.router import require_admin
from app.modules.auth.models import User
from app.modules.face_recognition.service import (
    FaceImageError,
    FaceRecognitionLibraryMissing,
    FaceRecognitionService,
)
from app.shared.response import success_response

router = APIRouter(prefix="/api/admin/students", tags=["face-recognition"])


def get_face_service(db: Session = Depends(get_db)) -> FaceRecognitionService:
    return FaceRecognitionService(db)


@router.get("/{student_profile_id}/face")
def face_status(
    student_profile_id: int,
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    return success_response(service.get_profile_status(student_profile_id))


@router.post("/{student_profile_id}/face")
async def register_face(
    student_profile_id: int,
    photo: UploadFile = File(...),
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    try:
        result = service.register_face(student_profile_id, await photo.read())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FaceRecognitionLibraryMissing as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except FaceImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return success_response(result)
