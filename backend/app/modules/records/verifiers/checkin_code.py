"""签到码校验器：学生输入与老师配置的固定码比对。"""
from __future__ import annotations

from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType


class CheckinCodeVerifier(CheckinVerifier):
    method = "checkin_code"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        payload = ctx.payload
        submitted = (
            getattr(payload, "checkin_code", None)
            or getattr(payload, "dynamic_code", None)
        )
        submitted = str(submitted or "").strip()

        expected = str(self.config.get("code", "")).strip()
        case_sensitive = bool(self.config.get("caseSensitive", False))

        if not expected:
            return self._fail("任务未配置签到码，请联系老师")
        if not submitted:
            return self._fail("请输入老师公布的签到码")

        if not case_sensitive:
            submitted = submitted.upper()
            expected = expected.upper()

        if submitted != expected:
            return self._fail("签到码错误，请核对老师公布的签到码后重试")

        return VerifierResult(
            method=self.method,
            passed=True,
            message="签到码校验通过",
        )

    def _fail(self, message: str) -> VerifierResult:
        return VerifierResult(
            method=self.method,
            passed=False,
            message=message,
            need_review=True,
            exception_type=ExceptionType.DYNAMIC_CODE_ERROR.value,
        )
