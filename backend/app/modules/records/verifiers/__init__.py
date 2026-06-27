"""签到校验器插件包。

每种签到方式实现为独立的 CheckinVerifier，由 CheckinPipeline 根据
任务规则中的 verificationRule.methods 动态组装并依次执行。
"""
from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.modules.records.verifiers.pipeline import CheckinPipeline, PipelineResult

__all__ = [
    "CheckinContext",
    "CheckinVerifier",
    "VerifierResult",
    "CheckinPipeline",
    "PipelineResult",
]
