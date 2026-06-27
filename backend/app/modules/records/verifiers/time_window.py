"""时间窗口校验器（始终执行，不属于可选签到方式）。"""
from __future__ import annotations

from datetime import time

from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType


class TimeWindowVerifier(CheckinVerifier):
    method = "time"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        rule = self.config
        if not rule or not rule.get("startTime") or not rule.get("endTime"):
            # 未配置时间窗口则视为通过
            return VerifierResult(self.method, True, "无时间限制")

        start_time = time.fromisoformat(rule["startTime"])
        end_time = time.fromisoformat(rule["endTime"])
        current_time = ctx.now.timetz().replace(tzinfo=None)

        if current_time < start_time:
            return VerifierResult(self.method, True, "提前签到")

        if start_time <= current_time <= end_time:
            return VerifierResult(self.method, True, "在打卡窗口内")

        return VerifierResult(
            method=self.method,
            passed=False,
            message="超过打卡截止时间，记为迟到",
            need_review=True,
            exception_type=ExceptionType.LATE.value,
        )
