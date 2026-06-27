"""二维码签到校验器。"""
from __future__ import annotations

from app.modules.qr_code.service import QrTokenError, verify_token
from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType


class QrCodeVerifier(CheckinVerifier):
    method = "qr_code"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        payload = ctx.payload
        qr_payload = getattr(payload, "qr_payload", None)

        if not qr_payload:
            return self._fail("请扫描教师展示的签到二维码")

        try:
            token = verify_token(qr_payload, expected_task_id=ctx.task.id)
        except QrTokenError as exc:
            return self._fail(str(exc))

        # 可选：校验 occurrence_date 一致性，防跨日复用
        if (
            ctx.occurrence_date is not None
            and token.occurrence_date is not None
            and token.occurrence_date != ctx.occurrence_date
        ):
            return self._fail("二维码非本次打卡日期，请扫描最新二维码")

        return VerifierResult(
            method=self.method,
            passed=True,
            message="二维码校验通过",
            detail={"nonce": token.nonce},
        )

    def _fail(self, message: str) -> VerifierResult:
        return VerifierResult(
            method=self.method,
            passed=False,
            message=message,
            need_review=True,
            exception_type=ExceptionType.QR_FAILED.value,
        )
