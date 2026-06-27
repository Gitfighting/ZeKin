"""校验流水线与 QR token 单元测试。"""
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.modules.qr_code.service import QrTokenError, generate_token, verify_token
from app.modules.records.verifiers import CheckinContext, CheckinPipeline


@dataclass
class _Task:
    id: int = 1


@dataclass
class _Payload:
    longitude: float | None = None
    latitude: float | None = None
    face_image: str | None = None
    qr_payload: str | None = None
    checkin_code: str | None = None
    dynamic_code: str | None = None
    attachment: dict | None = None
    gesture: dict | None = None
    occurrence_date: str | None = None


def _ctx(payload: _Payload) -> CheckinContext:
    return CheckinContext(
        db=None,
        task=_Task(),
        student_profile_id=1,
        now=datetime(2026, 6, 26, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
        payload=payload,
        occurrence_date="2026-06-26",
    )


def test_pipeline_assembles_only_enabled_methods() -> None:
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {
            "methods": ["location", "attachment"],
            "order": ["location", "attachment"],
            "location": {"longitude": 120.0, "latitude": 30.0, "radius": 300},
            "attachment": {"required": True, "minTextLength": 5},
        },
    }
    pipeline = CheckinPipeline(rules)
    assert pipeline.methods == ["location", "attachment"]

    payload = _Payload(
        longitude=120.0,
        latitude=30.0,
        attachment={"text": "今天一切正常", "files": []},
    )
    result = pipeline.run(_ctx(payload))
    assert result.passed is True
    assert result.status == "normal"
    assert set(result.verification_results) >= {"time", "location", "attachment"}


def test_pipeline_fails_when_attachment_missing() -> None:
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {
            "methods": ["attachment"],
            "attachment": {"required": True, "minTextLength": 20},
        },
    }
    result = CheckinPipeline(rules).run(_ctx(_Payload(attachment={"text": "太短"})))
    assert result.passed is False
    assert "attachment_missing" in result.exception_types


def test_pipeline_qr_code_pass_and_fail() -> None:
    token, _ = generate_token(1, occurrence_date="2026-06-26", expire_seconds=120)
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {"methods": ["qr_code"], "qr_code": {"expireSeconds": 120}},
    }
    ok = CheckinPipeline(rules).run(_ctx(_Payload(qr_payload=token)))
    assert ok.passed is True

    bad = CheckinPipeline(rules).run(_ctx(_Payload(qr_payload="forged.signature")))
    assert bad.passed is False
    assert "qr_failed" in bad.exception_types


def test_gesture_matches_preset_pattern() -> None:
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {
            "methods": ["gesture"],
            "gesture": {"mode": "preset", "presetPattern": "Z"},
        },
    }
    ok = CheckinPipeline(rules).run(
        _ctx(_Payload(gesture={"pattern_id": "Z", "points": [[0, 0], [1, 0], [0, 1], [1, 1]]}))
    )
    assert ok.passed is True

    wrong = CheckinPipeline(rules).run(_ctx(_Payload(gesture={"pattern_id": "N"})))
    assert wrong.passed is False
    assert "gesture_failed" in wrong.exception_types


def test_pipeline_checkin_code_pass_and_fail() -> None:
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {
            "methods": ["checkin_code"],
            "checkin_code": {"code": "ABC123", "caseSensitive": False},
        },
    }
    ok = CheckinPipeline(rules).run(_ctx(_Payload(checkin_code="abc123")))
    assert ok.passed is True

    missing = CheckinPipeline(rules).run(_ctx(_Payload()))
    assert missing.passed is False
    assert "dynamic_code_error" in missing.exception_types

    wrong = CheckinPipeline(rules).run(_ctx(_Payload(checkin_code="WRONG1")))
    assert wrong.passed is False
    assert "dynamic_code_error" in wrong.exception_types


def test_pipeline_checkin_code_legacy_dynamic_code_field() -> None:
    rules = {
        "timeRule": {"startTime": "21:30", "endTime": "23:00"},
        "verificationRule": {
            "methods": ["checkin_code"],
            "checkin_code": {"code": "888888"},
        },
    }
    ok = CheckinPipeline(rules).run(_ctx(_Payload(dynamic_code="888888")))
    assert ok.passed is True


def test_qr_token_expiry_and_task_mismatch(monkeypatch) -> None:
    token, token_obj = generate_token(1, expire_seconds=120)
    assert verify_token(token, expected_task_id=1).task_id == 1

    with pytest.raises(QrTokenError):
        verify_token(token, expected_task_id=999)

    # 模拟时间快进到过期之后
    monkeypatch.setattr(
        "app.modules.qr_code.service.time.time",
        lambda: token_obj.expires_at + 1,
    )
    with pytest.raises(QrTokenError):
        verify_token(token, expected_task_id=1)
