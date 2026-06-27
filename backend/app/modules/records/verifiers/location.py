"""地理位置（围栏）校验器。"""
from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from app.modules.records.verifiers.base import (
    CheckinContext,
    CheckinVerifier,
    VerifierResult,
)
from app.shared.enums import ExceptionType

EARTH_RADIUS_METERS = 6371000


def haversine_distance(lon_a: float, lat_a: float, lon_b: float, lat_b: float) -> float:
    """计算两 GPS 坐标间距离（米）。"""
    lon_a, lat_a, lon_b, lat_b = map(radians, [lon_a, lat_a, lon_b, lat_b])
    delta_lon = lon_b - lon_a
    delta_lat = lat_b - lat_a
    h = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * asin(sqrt(h))


class LocationVerifier(CheckinVerifier):
    method = "location"

    def evaluate(self, ctx: CheckinContext) -> VerifierResult:
        rule = self.config
        payload = ctx.payload

        # mode == none 视为不校验（兼容旧 schema）
        if rule.get("mode") == "none":
            return VerifierResult(self.method, True, "无需位置校验")

        if payload.longitude is None or payload.latitude is None:
            return VerifierResult(
                method=self.method,
                passed=False,
                message="缺少定位信息，请先获取当前位置",
                need_review=True,
                exception_type=ExceptionType.LOCATION_ERROR.value,
            )

        distance = haversine_distance(
            payload.longitude,
            payload.latitude,
            float(rule["longitude"]),
            float(rule["latitude"]),
        )
        radius = float(rule["radius"])
        if distance <= radius:
            return VerifierResult(
                method=self.method,
                passed=True,
                message="在围栏内",
                detail={"distance_m": round(distance, 1)},
            )

        return VerifierResult(
            method=self.method,
            passed=False,
            message="当前位置不在签到范围内，请到指定地点后重新定位",
            need_review=True,
            exception_type=ExceptionType.LOCATION_ERROR.value,
            detail={"distance_m": round(distance, 1)},
        )
