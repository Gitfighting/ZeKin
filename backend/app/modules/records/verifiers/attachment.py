"""附件/日志上传校验器（合并原 daily_report 能力）。"""
from __future__ import annotations

from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType


class AttachmentVerifier(CheckinVerifier):
    method = "attachment"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        rule = self.config
        payload = ctx.payload
        attachment = getattr(payload, "attachment", None) or {}

        text = (attachment.get("text") or "").strip() if isinstance(attachment, dict) else ""
        files = attachment.get("files") or [] if isinstance(attachment, dict) else []

        required = bool(rule.get("required", False))
        min_text_length = int(rule.get("minTextLength", 0))
        max_file_count = int(rule.get("maxFileCount", 9))

        if required and not text and not files:
            return self._fail("请填写日志或上传附件")

        if text and min_text_length and len(text) < min_text_length:
            return self._fail(f"日志内容不少于 {min_text_length} 个字")

        if len(files) > max_file_count:
            return self._fail(f"附件数量超过上限（最多 {max_file_count} 个）")

        return VerifierResult(
            method=self.method,
            passed=True,
            message="附件/日志已提交",
            detail={"text_length": len(text), "file_count": len(files)},
        )

    def _fail(self, message: str) -> VerifierResult:
        return VerifierResult(
            method=self.method,
            passed=False,
            message=message,
            need_review=True,
            exception_type=ExceptionType.ATTACHMENT_MISSING.value,
        )
