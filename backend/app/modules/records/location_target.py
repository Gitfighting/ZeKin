from __future__ import annotations

from typing import Any

from app.modules.auth.models import StudentProfile

PER_STUDENT_LOCATION_MODES = frozenset({"student_dorm", "student_internship"})

_PROFILE_LOCATION_BINDINGS: dict[str, dict[str, str]] = {
    "student_dorm": {
        "lng": "dormitory_longitude",
        "lat": "dormitory_latitude",
        "name": "dormitory",
        "address": "dormitory_address",
        "default_name": "本人寝室",
        "source": "student_dorm",
        "missing_message": "未录入寝室位置，请联系管理员或在个人信息中完善寝室定位",
    },
    "student_internship": {
        "lng": "internship_longitude",
        "lat": "internship_latitude",
        "name": "internship_company",
        "address": "internship_address",
        "default_name": "实习单位",
        "source": "student_internship",
        "missing_message": "未录入实习单位位置，请联系管理员完善实习地信息",
    },
}


def get_location_mode(rules: dict[str, Any] | None) -> str | None:
    rules = rules or {}
    location_rule = rules.get("locationRule") or {}
    verification = rules.get("verificationRule") or {}
    location_cfg = verification.get("location") or {}
    mode = location_cfg.get("mode") or location_rule.get("mode")
    if mode in PER_STUDENT_LOCATION_MODES:
        return str(mode)
    return str(mode) if mode else None


def is_student_dorm_location_mode(rules: dict[str, Any] | None) -> bool:
    return get_location_mode(rules) == "student_dorm"


def is_student_internship_location_mode(rules: dict[str, Any] | None) -> bool:
    return get_location_mode(rules) == "student_internship"


def is_per_student_location_mode(rules: dict[str, Any] | None) -> bool:
    return get_location_mode(rules) in PER_STUDENT_LOCATION_MODES


def _radius_from_rules(rules: dict[str, Any] | None, default: float) -> float:
    rules = rules or {}
    location_rule = rules.get("locationRule") or {}
    verification = rules.get("verificationRule") or {}
    location_cfg = verification.get("location") or {}
    return float(location_cfg.get("radius") or location_rule.get("radius") or default)


def resolve_student_profile_location_target(
    mode: str,
    rules: dict[str, Any] | None,
    profile: StudentProfile,
) -> dict[str, Any]:
    binding = _PROFILE_LOCATION_BINDINGS[mode]
    place_name = getattr(profile, binding["name"]) or binding["default_name"]
    default_radius = 200.0 if mode == "student_dorm" else 500.0
    radius = _radius_from_rules(rules, default_radius)
    return {
        "mode": "fixed_area",
        "placeName": place_name,
        "longitude": getattr(profile, binding["lng"]),
        "latitude": getattr(profile, binding["lat"]),
        "radius": radius,
        "source": binding["source"],
    }


def resolve_student_dorm_target(
    rules: dict[str, Any] | None,
    profile: StudentProfile,
) -> dict[str, Any]:
    return resolve_student_profile_location_target("student_dorm", rules, profile)


def resolve_student_internship_target(
    rules: dict[str, Any] | None,
    profile: StudentProfile,
) -> dict[str, Any]:
    return resolve_student_profile_location_target("student_internship", rules, profile)


def resolve_location_config_for_student(
    rules: dict[str, Any] | None,
    profile: StudentProfile | None,
) -> dict[str, Any]:
    rules = rules or {}
    location_rule = rules.get("locationRule") or {}
    verification = rules.get("verificationRule") or {}
    location_cfg = dict(verification.get("location") or location_rule or {})
    mode = get_location_mode(rules)

    if mode in PER_STUDENT_LOCATION_MODES:
        if profile is None:
            return {**location_cfg, "mode": mode}
        return resolve_student_profile_location_target(mode, rules, profile)

    resolved_mode = location_cfg.get("mode") or location_rule.get("mode") or "fixed_area"
    return {
        **location_rule,
        **location_cfg,
        "mode": resolved_mode,
    }


def resolve_profile_location_for_mode(
    mode: str,
    profile: StudentProfile,
) -> tuple[float | None, float | None, str, str | None]:
    """返回 (lng, lat, place_name, missing_message)。"""
    binding = _PROFILE_LOCATION_BINDINGS[mode]
    lng = getattr(profile, binding["lng"])
    lat = getattr(profile, binding["lat"])
    place_name = getattr(profile, binding["name"]) or binding["default_name"]
    missing_message = binding["missing_message"] if lng is None or lat is None else None
    return lng, lat, place_name, missing_message
