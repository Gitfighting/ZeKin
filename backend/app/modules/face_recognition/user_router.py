from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.router import get_current_user
from app.modules.face_recognition.service import (
    FaceImageError,
    FaceRecognitionLibraryMissing,
    FaceRecognitionService,
)
from app.shared.response import success_response


class FaceImagePayload(BaseModel):
    face_image: str  # base64 data URL


router = APIRouter(prefix="/api/face", tags=["face-test"])


def get_face_service(db: Session = Depends(get_db)) -> FaceRecognitionService:
    return FaceRecognitionService(db)


@router.post("/register")
def register_face(
    payload: FaceImagePayload,
    current_user: User = Depends(get_current_user),
    service: FaceRecognitionService = Depends(get_face_service),
):
    try:
        image_bytes = _decode_base64(payload.face_image)
        result = service.register_user_face(current_user.id, image_bytes)
    except FaceRecognitionLibraryMissing as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except FaceImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{type(exc).__name__}: {exc}") from exc
    return success_response(result)


@router.post("/verify")
def verify_face(
    payload: FaceImagePayload,
    current_user: User = Depends(get_current_user),
    service: FaceRecognitionService = Depends(get_face_service),
):
    try:
        image_bytes = _decode_base64(payload.face_image)
        result = service.verify_user_face(current_user.id, image_bytes)
    except FaceRecognitionLibraryMissing as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{type(exc).__name__}: {exc}") from exc
    return success_response(result)


def _decode_base64(value: str) -> bytes:
    import base64

    payload = value.split(",", 1)[1] if "," in value else value
    return base64.b64decode(payload, validate=True)
