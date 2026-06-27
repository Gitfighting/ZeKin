"""校验流水线：根据规则动态组装签到方式校验器并依次执行。

兼容两种规则结构：
- 新结构：rules["verificationRule"]["methods"] = ["face", "location", ...]
  每种方式的参数在 rules["verificationRule"][method] 中。
- 旧结构（向后兼容）：
  - location：默认启用，除非 locationRule.mode == "none"
  - face：faceRule.enabled == True 时启用
  - attachment：submitRule.fields 非空时启用（可选）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.records.verifiers.attachment import AttachmentVerifier
from app.modules.records.verifiers.base import CheckinContext, CheckinVerifier, VerifierResult
from app.modules.records.verifiers.checkin_code import CheckinCodeVerifier
from app.modules.records.verifiers.face import FaceVerifier
from app.modules.records.verifiers.gesture import GestureVerifier
from app.modules.records.verifiers.location import LocationVerifier
from app.modules.records.verifiers.qr_code import QrCodeVerifier
from app.modules.records.verifiers.time_window import TimeWindowVerifier
from app.shared.enums import CheckinMethod, ExceptionType, RecordStatus

VERIFIER_REGISTRY: dict[str, type[CheckinVerifier]] = {
    CheckinMethod.FACE.value: FaceVerifier,
    CheckinMethod.LOCATION.value: LocationVerifier,
    CheckinMethod.QR_CODE.value: QrCodeVerifier,
    CheckinMethod.CHECKIN_CODE.value: CheckinCodeVerifier,
    CheckinMethod.ATTACHMENT.value: AttachmentVerifier,
    CheckinMethod.GESTURE.value: GestureVerifier,
}


@dataclass(slots=True)
class PipelineResult:
    passed: bool
    status: str
    enabled_methods: list[str]
    verification_results: dict[str, dict[str, Any]]
    exception_types: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    need_review: bool = False


class CheckinPipeline:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules or {}
        self.time_verifier = TimeWindowVerifier(self.rules.get("timeRule", {}))
        self.methods, self.verifiers = self._build(self.rules)

    # ── 构建 ──────────────────────────────────────────────────────────────

    def _build(self, rules: dict) -> tuple[list[str], list[CheckinVerifier]]:
        vr = rules.get("verificationRule", {}) or {}
        methods = self._resolve_methods(rules, vr)

        verifiers: list[CheckinVerifier] = []
        for method in methods:
            verifier_cls = VERIFIER_REGISTRY[method]
            config = self._resolve_config(method, rules, vr)
            verifiers.append(verifier_cls(config))
        return methods, verifiers

    def _resolve_methods(self, rules: dict, vr: dict) -> list[str]:
        # 新结构优先
        methods = vr.get("methods")
        if methods:
            order = vr.get("order") or methods
            ordered = [m for m in order if m in methods]
            ordered += [m for m in methods if m not in ordered]
            resolved = [m for m in ordered if m in VERIFIER_REGISTRY]
            # 兼容旧 faceRule.enabled 触发：未显式声明 face 时按需补充
            if (
                rules.get("faceRule", {}).get("enabled")
                and CheckinMethod.FACE.value not in resolved
            ):
                resolved.append(CheckinMethod.FACE.value)
            return resolved

        # 旧结构兼容推断
        legacy: list[str] = []
        location_rule = rules.get("locationRule", {})
        if location_rule and location_rule.get("mode") != "none":
            legacy.append(CheckinMethod.LOCATION.value)
        if rules.get("faceRule", {}).get("enabled"):
            legacy.append(CheckinMethod.FACE.value)
        return legacy

    def _resolve_config(self, method: str, rules: dict, vr: dict) -> dict:
        # 新结构：verificationRule[method]
        if method in vr and isinstance(vr.get(method), dict):
            return vr[method]
        # 旧结构回退
        if method == CheckinMethod.LOCATION.value:
            return rules.get("locationRule", {})
        if method == CheckinMethod.FACE.value:
            return rules.get("faceRule", {})
        if method == CheckinMethod.ATTACHMENT.value:
            return rules.get("attachmentRule", {})
        return {}

    # ── 执行 ──────────────────────────────────────────────────────────────

    def run(self, ctx: CheckinContext) -> PipelineResult:
        results: dict[str, dict[str, Any]] = {}
        exception_types: list[str] = []
        messages: list[str] = []
        need_review = False
        passed = True

        # 1. 时间窗口（始终校验）
        time_result = self.time_verifier.evaluate(ctx)
        results[time_result.method] = time_result.to_dict()
        self._accumulate(time_result, exception_types, messages)
        if not time_result.passed:
            passed = False
            need_review = need_review or time_result.need_review

        # 2. 依次执行启用的签到方式
        for verifier in self.verifiers:
            result = verifier.evaluate(ctx)
            results[result.method] = result.to_dict()
            self._accumulate(result, exception_types, messages)
            if not result.passed:
                passed = False
                need_review = need_review or result.need_review

        status = RecordStatus.NORMAL.value if passed else RecordStatus.EXCEPTION.value
        if ExceptionType.LATE.value in exception_types:
            status = RecordStatus.LATE.value
        return PipelineResult(
            passed=passed,
            status=status,
            enabled_methods=list(self.methods),
            verification_results=results,
            exception_types=exception_types,
            messages=messages,
            need_review=need_review,
        )

    @staticmethod
    def _accumulate(
        result: VerifierResult, exception_types: list[str], messages: list[str]
    ) -> None:
        if result.passed:
            return
        if result.message:
            messages.append(result.message)
        if result.exception_type:
            exception_types.append(result.exception_type)
