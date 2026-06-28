"""地理位置（围栏）校验器。"""
from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from app.modules.auth.models import StudentProfile
from app.modules.records.location_target import (
    PER_STUDENT_LOCATION_MODES,
    resolve_profile_location_for_mode,
)
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
        rule = dict(self.config)
        if rule.get("mode") == "none":
            return VerifierResult(self.method, True, "无需位置校验")

        payload = ctx.payload
        if payload.longitude is None or payload.latitude is None:
            return VerifierResult(
                method=self.method,
                passed=False,
                message="缺少定位信息，请先获取当前位置",
                need_review=True,
                exception_type=ExceptionType.LOCATION_ERROR.value,
            )

        mode = rule.get("mode", "fixed_area")
        if mode in PER_STUDENT_LOCATION_MODES:
            if ctx.db is None:
                return VerifierResult(
                    method=self.method,
                    passed=False,
                    message="无法读取学生档案位置",
                    need_review=True,
                    exception_type=ExceptionType.LOCATION_ERROR.value,
                )
            profile = ctx.db.get(StudentProfile, ctx.student_profile_id)
            if profile is None:
                return VerifierResult(
                    method=self.method,
                    passed=False,
                    message="学生档案不存在，无法校验签到位置",
                    need_review=True,
                    exception_type=ExceptionType.LOCATION_ERROR.value,
                )
            target_lng, target_lat, place_name, missing_message = resolve_profile_location_for_mode(
                mode,
                profile,
            )
            if missing_message:
                return VerifierResult(
                    method=self.method,
                    passed=False,
                    message=missing_message,
                    need_review=True,
                    exception_type=ExceptionType.LOCATION_ERROR.value,
                )
            target_lng = float(target_lng)
            target_lat = float(target_lat)
            retry_hint = "请到实习单位附近后重新定位" if mode == "student_internship" else "请到寝室附近后重新定位"
        else:
            if rule.get("longitude") is None or rule.get("latitude") is None:
                return VerifierResult(
                    method=self.method,
                    passed=False,
                    message="任务未配置有效签到位置",
                    need_review=True,
                    exception_type=ExceptionType.LOCATION_ERROR.value,
                )
            target_lng = float(rule["longitude"])
            target_lat = float(rule["latitude"])
            place_name = str(rule.get("placeName") or "签到地点")
            retry_hint = "请到指定地点附近后重新定位"

        distance = haversine_distance(
            payload.longitude,
            payload.latitude,
            target_lng,
            target_lat,
        )
        radius = float(rule.get("radius") or 300)
        if distance <= radius:
            return VerifierResult(
                method=self.method,
                passed=True,
                message=f"已在{place_name}打卡范围内",
                detail={"distance_m": round(distance, 1), "place_name": place_name},
            )

        return VerifierResult(
            method=self.method,
            passed=False,
            message=f"当前位置不在{place_name}签到范围内，{retry_hint}，也可提交异常申诉",
            need_review=True,
            exception_type=ExceptionType.LOCATION_ERROR.value,
            detail={"distance_m": round(distance, 1), "place_name": place_name},
        )
