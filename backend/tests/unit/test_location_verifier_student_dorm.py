"""查寝模式：按学生档案寝室坐标校验位置。"""
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from app.modules.records.verifiers.location import LocationVerifier


@dataclass
class _Payload:
    longitude: float | None = None
    latitude: float | None = None


@dataclass
class _Task:
    id: int = 1


def _ctx(*, db, payload: _Payload, profile_id: int = 1):
    from app.modules.records.verifiers.base import CheckinContext

    return CheckinContext(
        db=db,
        task=_Task(),
        student_profile_id=profile_id,
        now=datetime(2026, 6, 26, 22, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
        payload=payload,
        occurrence_date="2026-06-26",
    )


def _profile(**overrides):
    profile = MagicMock()
    profile.dormitory = overrides.get("dormitory", "3号楼301")
    profile.dormitory_longitude = overrides.get("dormitory_longitude", 120.0)
    profile.dormitory_latitude = overrides.get("dormitory_latitude", 30.0)
    return profile


def test_student_dorm_location_passes_within_radius() -> None:
    db = MagicMock()
    db.get.return_value = _profile()
    verifier = LocationVerifier({"mode": "student_dorm", "radius": 300})
    result = verifier.evaluate(_ctx(db=db, payload=_Payload(longitude=120.0001, latitude=30.0001)))
    assert result.passed is True
    assert "3号楼301" in result.message


def test_student_dorm_location_fails_outside_radius() -> None:
    db = MagicMock()
    db.get.return_value = _profile()
    verifier = LocationVerifier({"mode": "student_dorm", "radius": 50})
    result = verifier.evaluate(_ctx(db=db, payload=_Payload(longitude=120.01, latitude=30.01)))
    assert result.passed is False
    assert result.need_review is True


def test_student_dorm_location_missing_profile_coords() -> None:
    db = MagicMock()
    db.get.return_value = _profile(dormitory_longitude=None, dormitory_latitude=None)
    verifier = LocationVerifier({"mode": "student_dorm", "radius": 200})
    result = verifier.evaluate(_ctx(db=db, payload=_Payload(longitude=120.0, latitude=30.0)))
    assert result.passed is False
    assert "未录入寝室位置" in result.message


def test_student_internship_location_passes_within_radius() -> None:
    db = MagicMock()
    profile = MagicMock()
    profile.internship_company = "XX科技有限公司"
    profile.internship_longitude = 121.5
    profile.internship_latitude = 31.2
    db.get.return_value = profile
    verifier = LocationVerifier({"mode": "student_internship", "radius": 500})
    result = verifier.evaluate(_ctx(db=db, payload=_Payload(longitude=121.5001, latitude=31.2001)))
    assert result.passed is True
    assert "XX科技有限公司" in result.message


def test_student_internship_location_missing_coords() -> None:
    db = MagicMock()
    profile = MagicMock()
    profile.internship_company = "XX科技有限公司"
    profile.internship_longitude = None
    profile.internship_latitude = None
    db.get.return_value = profile
    verifier = LocationVerifier({"mode": "student_internship", "radius": 500})
    result = verifier.evaluate(_ctx(db=db, payload=_Payload(longitude=121.5, latitude=31.2)))
    assert result.passed is False
    assert "实习单位位置" in result.message
