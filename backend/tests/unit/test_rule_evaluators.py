from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.records.evaluators import LocationRuleEvaluator, TimeRuleEvaluator


def test_time_rule_evaluator_passes_within_window() -> None:
    result = TimeRuleEvaluator().evaluate(
        now=datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
        rule={"startTime": "21:30", "endTime": "22:30", "allowLate": False},
    )

    assert result.passed is True
    assert result.status == "normal"
    assert result.exception_types == []


def test_time_rule_evaluator_marks_late_outside_window() -> None:
    result = TimeRuleEvaluator().evaluate(
        now=datetime(2026, 6, 24, 22, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
        rule={"startTime": "21:30", "endTime": "22:30", "allowLate": False},
    )

    assert result.passed is False
    assert result.status == "exception"
    assert result.exception_types == ["late"]


def test_location_rule_evaluator_passes_within_radius() -> None:
    result = LocationRuleEvaluator().evaluate(
        longitude=120.000001,
        latitude=30.000001,
        rule={
            "mode": "fixed_area",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 300,
        },
    )

    assert result.passed is True
    assert result.status == "normal"
    assert result.exception_types == []


def test_location_rule_evaluator_fails_outside_radius() -> None:
    result = LocationRuleEvaluator().evaluate(
        longitude=120.01,
        latitude=30.01,
        rule={
            "mode": "fixed_area",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 100,
        },
    )

    assert result.passed is False
    assert result.status == "exception"
    assert result.exception_types == ["location_error"]
