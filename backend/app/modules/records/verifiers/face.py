"""人脸识别校验器（复用 FaceRecognitionService）。"""
from __future__ import annotations

import logging

from app.modules.face_recognition.service import (
    FaceImageError,
    FaceRecognitionLibraryMissing,
    FaceRecognitionService,
    FaceVerificationInput,
    decode_image_payload,
)
from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType

logger = logging.getLogger("zeKin.face_recognition")


class FaceVerifier(CheckinVerifier):
    method = "face"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        rule = self.config
        payload = ctx.payload
        logger.info(
            "FaceVerifier 开始校验 task_id=%s student_profile_id=%s tolerance=%s detection_model=%s",
            ctx.task.id,
            ctx.student_profile_id,
            rule.get("tolerance", 0.6),
            rule.get("detectionModel", "hog"),
        )

        try:
            image_bytes = decode_image_payload(getattr(payload, "face_image", None))
        except FaceImageError as exc:
            return self._fail(str(exc))

        if image_bytes is None:
            logger.warning(
                "FaceVerifier 缺少人脸照片 task_id=%s student_profile_id=%s",
                ctx.task.id,
                ctx.student_profile_id,
            )
            return self._fail("请先完成人脸核验")

        logger.info(
            "FaceVerifier 收到人脸照片 task_id=%s student_profile_id=%s image_bytes=%s",
            ctx.task.id,
            ctx.student_profile_id,
            len(image_bytes),
        )

        service = FaceRecognitionService(ctx.db)
        try:
            result = service.verify_face(
                ctx.student_profile_id,
                FaceVerificationInput(
                    image_bytes=image_bytes,
                    tolerance=float(rule.get("tolerance", 0.6)),
                    detection_model=str(rule.get("detectionModel", "hog")),
                ),
            )
        except FaceRecognitionLibraryMissing as exc:
            return self._fail(str(exc))

        if result.passed:
            logger.info(
                "FaceVerifier 校验通过 task_id=%s student_profile_id=%s distance=%s",
                ctx.task.id,
                ctx.student_profile_id,
                result.distance,
            )
            return VerifierResult(
                method=self.method,
                passed=True,
                message=result.message,
                detail={"distance": result.distance, "tolerance": result.tolerance},
            )
        logger.warning(
            "FaceVerifier 校验失败 task_id=%s student_profile_id=%s message=%s distance=%s",
            ctx.task.id,
            ctx.student_profile_id,
            result.message,
            result.distance,
        )
        return self._fail(result.message, distance=result.distance)

    def _fail(self, message: str, distance: float | None = None) -> VerifierResult:
        detail = {"distance": distance} if distance is not None else {}
        return VerifierResult(
            method=self.method,
            passed=False,
            message=message,
            need_review=True,
            exception_type=ExceptionType.FACE_FAILED.value,
            detail=detail,
        )
