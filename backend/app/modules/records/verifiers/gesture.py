"""手势签到校验器。

前端在画布/九宫格上采集手势，本地完成图案识别后回传：
    payload.gesture = {"pattern_id": "Z", "points": [[x, y], ...]}

后端做轻量校验：
- preset 模式：比对 pattern_id 是否与模板预设一致，并要求最少采样点数；
- challenge 模式：比对 pattern_id 是否与本次下发的挑战图案一致。
"""
from __future__ import annotations

from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType

MIN_POINTS = 3


class GestureVerifier(CheckinVerifier):
    method = "gesture"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        rule = self.config
        payload = ctx.payload
        gesture = getattr(payload, "gesture", None) or {}

        if not isinstance(gesture, dict):
            return self._fail("手势数据格式错误")

        pattern_id = str(gesture.get("pattern_id", "")).strip()
        points = gesture.get("points") or []

        if not pattern_id and len(points) < MIN_POINTS:
            return self._fail("请完成手势绘制")

        expected = str(rule.get("presetPattern", "")).strip()
        if expected and pattern_id and pattern_id.upper() != expected.upper():
            return self._fail("手势不匹配，请重新绘制")

        if len(points) < MIN_POINTS and not expected:
            return self._fail("手势轨迹过短")

        return VerifierResult(
            method=self.method,
            passed=True,
            message="手势匹配",
            detail={"pattern_id": pattern_id, "point_count": len(points)},
        )

    def _fail(self, message: str) -> VerifierResult:
        return VerifierResult(
            method=self.method,
            passed=False,
            message=message,
            need_review=True,
            exception_type=ExceptionType.GESTURE_FAILED.value,
        )
