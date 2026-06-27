"""校验器基类与上下文定义。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session


@dataclass(slots=True)
class CheckinContext:
    """一次打卡校验所需的全部上下文。"""

    db: Session
    task: Any                       # CheckinTask
    student_profile_id: int
    now: datetime
    payload: Any                    # CheckinRequest
    occurrence_date: str | None = None


@dataclass(slots=True)
class VerifierResult:
    """单个校验器的输出。"""

    method: str
    passed: bool
    message: str = ""
    need_review: bool = False
    exception_type: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "method": self.method,
            "passed": self.passed,
            "message": self.message,
        }
        data.update(self.detail)
        return data


class CheckinVerifier(ABC):
    """所有签到方式校验器的抽象基类（策略模式）。"""

    method: str = ""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    @abstractmethod
    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        """执行校验，返回结果。"""
        raise NotImplementedError
