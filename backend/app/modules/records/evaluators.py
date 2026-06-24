from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from math import asin, cos, radians, sin, sqrt

from app.shared.enums import ExceptionType, RecordStatus


@dataclass(slots=True)
class EvaluationResult:
    passed: bool
    status: str
    exception_types: list[str]
    messages: list[str]
    need_review: bool


def _normal_result() -> EvaluationResult:
    return EvaluationResult(True, RecordStatus.NORMAL.value, [], [], False)


class TimeRuleEvaluator:
    def evaluate(self, *, now: datetime, rule: dict) -> EvaluationResult:
        start_time = time.fromisoformat(rule["startTime"])
        end_time = time.fromisoformat(rule["endTime"])
        current_time = now.timetz().replace(tzinfo=None)

        if start_time <= current_time <= end_time:
            return _normal_result()

        return EvaluationResult(
            False,
            RecordStatus.EXCEPTION.value,
            [ExceptionType.LATE.value],
            ["当前时间不在打卡窗口内"],
            True,
        )


class LocationRuleEvaluator:
    EARTH_RADIUS_METERS = 6371000

    def evaluate(self, *, longitude: float, latitude: float, rule: dict) -> EvaluationResult:
        if rule.get("mode") == "none":
            return _normal_result()

        distance = self._haversine_distance(
            longitude,
            latitude,
            float(rule["longitude"]),
            float(rule["latitude"]),
        )
        if distance <= float(rule["radius"]):
            return _normal_result()

        return EvaluationResult(
            False,
            RecordStatus.EXCEPTION.value,
            [ExceptionType.LOCATION_ERROR.value],
            ["当前位置不在有效范围内"],
            True,
        )

    def _haversine_distance(
        self,
        longitude_a: float,
        latitude_a: float,
        longitude_b: float,
        latitude_b: float,
    ) -> float:
        lon_a, lat_a, lon_b, lat_b = map(radians, [longitude_a, latitude_a, longitude_b, latitude_b])
        delta_lon = lon_b - lon_a
        delta_lat = lat_b - lat_a
        haversine = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
        return 2 * self.EARTH_RADIUS_METERS * asin(sqrt(haversine))
