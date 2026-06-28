from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
import logging
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
logger = logging.getLogger("zeKin.face_recognition")


def get_face_service(db: Session = Depends(get_db)) -> FaceRecognitionService:
    return FaceRecognitionService(db)


@router.get("/{student_profile_id}/face")
def face_status(
    student_profile_id: int,
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    logger.info("Admin 查询人脸状态 student_profile_id=%s", student_profile_id)
    result = service.get_profile_status(student_profile_id)
    logger.info(
        "Admin 人脸状态 student_profile_id=%s registered=%s encoding_count=%s",
        student_profile_id,
        result.get("registered"),
        result.get("encoding_count"),
    )
    return success_response(result)


@router.post("/faces/batch")
async def batch_register_faces(
    photos: list[UploadFile] = File(...),
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    if not photos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请至少上传一张照片")

    uploads: list[tuple[str, bytes]] = []
    for photo in photos:
        image_bytes = await photo.read()
        filename = photo.filename or "unknown.jpg"
        logger.info(
            "Admin 批量上传人脸 filename=%s content_type=%s size=%s",
            filename,
            photo.content_type,
            len(image_bytes),
        )
        uploads.append((filename, image_bytes))

    try:
        result = service.batch_register_faces(uploads)
    except FaceRecognitionLibraryMissing as exc:
        logger.error("Admin 批量人脸录入失败：依赖缺失 error=%s", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    logger.info(
        "Admin 批量人脸录入完成 total=%s success=%s failed=%s",
        result["total"],
        result["success_count"],
        result["failed_count"],
    )
    return success_response(result)


@router.post("/{student_profile_id}/face")
async def register_face(
    student_profile_id: int,
    photo: UploadFile = File(...),
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    image_bytes = await photo.read()
    logger.info(
        "Admin 上传人脸照片 student_profile_id=%s filename=%s content_type=%s size=%s",
        student_profile_id,
        photo.filename,
        photo.content_type,
        len(image_bytes),
    )
    try:
        result = service.register_face(student_profile_id, image_bytes)
    except ValueError as exc:
        logger.warning("Admin 人脸录入失败 student_profile_id=%s error=%s", student_profile_id, exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FaceRecognitionLibraryMissing as exc:
        logger.error("Admin 人脸录入失败：依赖缺失 student_profile_id=%s error=%s", student_profile_id, exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except FaceImageError as exc:
        logger.warning("Admin 人脸录入失败：图片无效 student_profile_id=%s error=%s", student_profile_id, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    logger.info("Admin 人脸录入成功 student_profile_id=%s result=%s", student_profile_id, result)
    return success_response(result)


@router.delete("/{student_profile_id}/face")
def clear_face(
    student_profile_id: int,
    _: User = Depends(require_admin),
    service: FaceRecognitionService = Depends(get_face_service),
):
    logger.info("Admin 清除学生人脸 student_profile_id=%s", student_profile_id)
    try:
        result = service.clear_face(student_profile_id)
    except ValueError as exc:
        logger.warning("Admin 清除人脸失败 student_profile_id=%s error=%s", student_profile_id, exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    logger.info("Admin 清除人脸成功 student_profile_id=%s result=%s", student_profile_id, result)
    return success_response(result)
