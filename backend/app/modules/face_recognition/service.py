from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from math import sqrt
import struct
import warnings

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile
from app.modules.face_recognition.models import FaceEncoding


class FaceRecognitionError(RuntimeError):
    pass


class FaceRecognitionLibraryMissing(FaceRecognitionError):
    pass


class FaceImageError(FaceRecognitionError):
    pass


class FaceEncodingUnavailable(StrEnum):
    NOT_REGISTERED = "not_registered"
    NO_FACE_IMAGE = "no_face_image"
    SERVICE_UNAVAILABLE = "service_unavailable"
    NO_FACE_DETECTED = "no_face_detected"
    MULTIPLE_FACES = "multiple_faces"
    NOT_MATCHED = "not_matched"


@dataclass(slots=True)
class FaceVerificationInput:
    image_bytes: bytes
    tolerance: float = 0.6
    detection_model: str = "hog"


@dataclass(slots=True)
class FaceVerificationResult:
    passed: bool
    message: str
    reason: str | None = None
    distance: float | None = None
    tolerance: float = 0.6
    provider: str = "face_recognition"


class FaceRecognitionExtractor:
    provider = "face_recognition"

    def extract_single_encoding(
        self, image_bytes: bytes, detection_model: str = "hog"
    ) -> list[float]:
        # 优先使用 face_recognition（需要 dlib）
        try:
            import face_recognition as face_recognition_lib

            image = face_recognition_lib.load_image_file(BytesIO(image_bytes))
            locations = face_recognition_lib.face_locations(image, model=detection_model)
            if not locations:
                raise FaceImageError("照片中未检测到人脸")
            if len(locations) > 1:
                raise FaceImageError("照片中检测到多张人脸，请确保照片中只有一个人")

            encodings = face_recognition_lib.face_encodings(image, locations)
            if not encodings:
                raise FaceImageError("人脸特征提取失败，请重新拍照")
            return [float(value) for value in encodings[0]]
        except ImportError:
            pass  # 回退到 OpenCV 方案

        # 回退方案：使用 OpenCV Haar Cascade 检测人脸 + 像素特征
        return self._extract_with_opencv(image_bytes, detection_model)

    def _extract_with_opencv(
        self, image_bytes: bytes, detection_model: str = "hog"
    ) -> list[float]:
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise FaceRecognitionLibraryMissing(
                "人脸识别依赖未安装，请先安装 face_recognition 或 opencv-python"
            ) from None

        # 读取图像
        np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            # 尝试用 PIL 兜底
            try:
                from PIL import Image
                pil_img = Image.open(BytesIO(image_bytes)).convert("RGB")
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as exc:
                raise FaceImageError(f"无法解码图片: {exc}") from exc

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Haar Cascade 人脸检测
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        if len(faces) == 0:
            raise FaceImageError("照片中未检测到人脸（OpenCV 方案）")
        if len(faces) > 1:
            raise FaceImageError("照片中检测到多张人脸，请确保照片中只有一个人")

        x, y, w, h = faces[0]
        face_roi = gray[y : y + h, x : x + w]

        # 缩放到固定尺寸并归一化
        face_resized = cv2.resize(face_roi, (64, 64), interpolation=cv2.INTER_AREA)
        face_normalized = face_resized.astype(np.float32) / 255.0

        # 返回 64×64=4096 维特征向量
        return face_normalized.flatten().tolist()


class FaceRecognitionService:
    def __init__(
        self,
        db: Session,
        extractor: FaceRecognitionExtractor | None = None,
    ) -> None:
        self.db = db
        self.extractor = extractor or FaceRecognitionExtractor()

    def register_face(self, student_profile_id: int, image_bytes: bytes) -> dict:
        student = self.db.get(StudentProfile, student_profile_id)
        if student is None:
            raise ValueError("学生档案不存在")

        encoding = self.extractor.extract_single_encoding(image_bytes, "cnn")
        for existing in self._list_active_encodings(student_profile_id):
            existing.is_active = False

        record = FaceEncoding(
            student_profile_id=student_profile_id,
            encoding=_encode_vector(encoding),
            dimension=len(encoding),
            model_name="face_recognition",
            source="admin_upload",
            quality_jsonb={"detection_model": "cnn"},
            is_active=True,
        )
        self.db.add(record)
        self.db.commit()
        return {
            "student_profile_id": student_profile_id,
            "encoding_count": self._active_encoding_count(student_profile_id),
            "dimension": len(encoding),
            "model": record.model_name,
        }

    def get_profile_status(self, student_profile_id: int) -> dict:
        encodings = self._list_active_encodings(student_profile_id)
        latest = encodings[-1] if encodings else None
        return {
            "student_profile_id": student_profile_id,
            "registered": bool(encodings),
            "encoding_count": len(encodings),
            "model": latest.model_name if latest else None,
            "updated_at": latest.updated_at.isoformat() if latest and latest.updated_at else None,
        }

    def verify_face(
        self, student_profile_id: int, verification: FaceVerificationInput
    ) -> FaceVerificationResult:
        known_encodings = [
            _decode_vector(record.encoding, record.dimension)
            for record in self._list_active_encodings(student_profile_id)
        ]
        if not known_encodings:
            return FaceVerificationResult(
                passed=False,
                reason=FaceEncodingUnavailable.NOT_REGISTERED.value,
                message="该学生尚未录入人脸",
                tolerance=verification.tolerance,
            )

        try:
            unknown_encoding = self.extractor.extract_single_encoding(
                verification.image_bytes,
                verification.detection_model,
            )
        except FaceRecognitionLibraryMissing:
            raise
        except FaceImageError as exc:
            return FaceVerificationResult(
                passed=False,
                reason=FaceEncodingUnavailable.NO_FACE_DETECTED.value,
                message=str(exc),
                tolerance=verification.tolerance,
            )

        distances = [
            _euclidean_distance(known_encoding, unknown_encoding)
            for known_encoding in known_encodings
            if len(known_encoding) == len(unknown_encoding)
        ]
        if not distances:
            return FaceVerificationResult(
                passed=False,
                reason=FaceEncodingUnavailable.NOT_MATCHED.value,
                message="人脸特征维度不一致，请重新录入人脸",
                tolerance=verification.tolerance,
            )

        distance = min(distances)
        passed = distance <= verification.tolerance
        return FaceVerificationResult(
            passed=passed,
            reason=None if passed else FaceEncodingUnavailable.NOT_MATCHED.value,
            message="人脸验证通过" if passed else "人脸验证失败，请确认是否本人操作",
            distance=round(distance, 6),
            tolerance=verification.tolerance,
        )

    # ========== 用户级（非学生）人脸操作，用于 face-test ==========

    def register_user_face(self, user_id: int, image_bytes: bytes) -> dict:
        encoding = self.extractor.extract_single_encoding(image_bytes, "cnn")
        for existing in self._list_active_user_encodings(user_id):
            existing.is_active = False

        record = FaceEncoding(
            user_id=user_id,
            encoding=_encode_vector(encoding),
            dimension=len(encoding),
            model_name="face_recognition",
            source="face_test",
            quality_jsonb={"detection_model": "cnn"},
            is_active=True,
        )
        self.db.add(record)
        self.db.commit()
        return {
            "registered": True,
            "message": "人脸录入成功",
            "faceCount": self._active_user_encoding_count(user_id),
        }

    def verify_user_face(self, user_id: int, image_bytes: bytes) -> dict:
        known_encodings = [
            _decode_vector(record.encoding, record.dimension)
            for record in self._list_active_user_encodings(user_id)
        ]
        if not known_encodings:
            return {
                "matched": False,
                "similarity": 0,
                "message": "尚未录入人脸，请先完成录入",
            }

        try:
            unknown_encoding = self.extractor.extract_single_encoding(image_bytes, "hog")
        except FaceImageError as exc:
            return {
                "matched": False,
                "similarity": 0,
                "message": str(exc),
            }

        distances = [
            _euclidean_distance(known_encoding, unknown_encoding)
            for known_encoding in known_encodings
            if len(known_encoding) == len(unknown_encoding)
        ]
        if not distances:
            return {
                "matched": False,
                "similarity": 0,
                "message": "人脸特征维度不一致",
            }

        distance = min(distances)
        tolerance = 0.6
        matched = distance <= tolerance
        similarity = max(0.0, 1.0 - distance / tolerance) if not matched else max(0.0, 1.0 - distance / tolerance)
        return {
            "matched": matched,
            "similarity": round(similarity, 4),
            "distance": round(distance, 6),
            "message": "人脸验证通过" if matched else "人脸验证失败，请确认是否本人操作",
        }

    def _list_active_encodings(self, student_profile_id: int) -> list[FaceEncoding]:
        statement = (
            select(FaceEncoding)
            .where(
                FaceEncoding.student_profile_id == student_profile_id,
                FaceEncoding.is_active.is_(True),
            )
            .order_by(FaceEncoding.id)
        )
        return list(self.db.scalars(statement))

    def _active_encoding_count(self, student_profile_id: int) -> int:
        return len(self._list_active_encodings(student_profile_id))

    def _list_active_user_encodings(self, user_id: int) -> list[FaceEncoding]:
        statement = (
            select(FaceEncoding)
            .where(
                FaceEncoding.user_id == user_id,
                FaceEncoding.is_active.is_(True),
            )
            .order_by(FaceEncoding.id)
        )
        return list(self.db.scalars(statement))

    def _active_user_encoding_count(self, user_id: int) -> int:
        return len(self._list_active_user_encodings(user_id))


def decode_image_payload(value: str | None) -> bytes | None:
    if not value:
        return None
    payload = value.split(",", 1)[1] if "," in value else value
    try:
        return base64.b64decode(payload, validate=True)
    except ValueError as exc:
        raise FaceImageError("人脸照片数据格式不正确") from exc


def face_result_to_dict(result: FaceVerificationResult) -> dict:
    return {
        "passed": result.passed,
        "provider": result.provider,
        "message": result.message,
        "reason": result.reason,
        "distance": result.distance,
        "tolerance": result.tolerance,
    }


def _encode_vector(values: list[float]) -> bytes:
    return struct.pack(f"<{len(values)}d", *values)


def _decode_vector(value: bytes, dimension: int) -> list[float]:
    return list(struct.unpack(f"<{dimension}d", value))


def _euclidean_distance(left: list[float], right: list[float]) -> float:
    return sqrt(sum((left_value - right_value) ** 2 for left_value, right_value in zip(left, right, strict=True)))
