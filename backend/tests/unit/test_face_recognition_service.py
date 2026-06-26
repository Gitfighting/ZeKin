from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile
from app.modules.face_recognition.service import (
    FaceEncodingUnavailable,
    FaceRecognitionService,
    FaceVerificationInput,
)


@dataclass
class StubExtractor:
    next_encoding: list[float]

    def extract_single_encoding(
        self, image_bytes: bytes, detection_model: str = "hog"
    ) -> list[float]:
        assert image_bytes
        assert detection_model in {"hog", "cnn"}
        return self.next_encoding


def _student(db: Session) -> StudentProfile:
    profile = StudentProfile(
        student_no="20260001",
        name="张三",
        phone="13800000001",
        college="软件学院",
        major="软件工程",
        grade="2026",
        class_name="软件2601",
        dormitory="3号楼301",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_register_face_stores_single_encoding_as_blob(db_session: Session) -> None:
    student = _student(db_session)
    extractor = StubExtractor([0.1, 0.2, 0.3])
    service = FaceRecognitionService(db_session, extractor=extractor)

    result = service.register_face(student.id, b"image-bytes")

    assert result == {
        "student_profile_id": student.id,
        "encoding_count": 1,
        "dimension": 3,
        "model": "face_recognition",
    }
    status = service.get_profile_status(student.id)
    assert status["registered"] is True
    assert status["encoding_count"] == 1


def test_verify_face_returns_passed_with_distance_below_tolerance(
    db_session: Session,
) -> None:
    student = _student(db_session)
    service = FaceRecognitionService(
        db_session,
        extractor=StubExtractor([0.1, 0.2, 0.3]),
    )
    service.register_face(student.id, b"known")
    service.extractor = StubExtractor([0.1, 0.21, 0.3])

    result = service.verify_face(
        student.id,
        FaceVerificationInput(image_bytes=b"unknown", tolerance=0.6),
    )

    assert result.passed is True
    assert result.distance == 0.01
    assert result.message == "人脸验证通过"


def test_verify_face_returns_failed_when_distance_exceeds_tolerance(
    db_session: Session,
) -> None:
    student = _student(db_session)
    service = FaceRecognitionService(
        db_session,
        extractor=StubExtractor([0.1, 0.2, 0.3]),
    )
    service.register_face(student.id, b"known")
    service.extractor = StubExtractor([1.1, 1.2, 1.3])

    result = service.verify_face(
        student.id,
        FaceVerificationInput(image_bytes=b"unknown", tolerance=0.6),
    )

    assert result.passed is False
    assert result.distance > 1.7
    assert result.message == "人脸验证失败，请确认是否本人操作"


def test_verify_face_requires_registered_encoding(db_session: Session) -> None:
    student = _student(db_session)
    service = FaceRecognitionService(
        db_session,
        extractor=StubExtractor([0.1, 0.2, 0.3]),
    )

    result = service.verify_face(
        student.id,
        FaceVerificationInput(image_bytes=b"unknown", tolerance=0.6),
    )

    assert result.passed is False
    assert result.reason == FaceEncodingUnavailable.NOT_REGISTERED
    assert result.message == "该学生尚未录入人脸"
