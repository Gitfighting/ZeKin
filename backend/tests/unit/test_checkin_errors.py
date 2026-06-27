"""阻断类签到失败单元测试。"""
from app.modules.records.checkin_errors import get_blocking_checkin_failure
from app.modules.records.verifiers.pipeline import PipelineResult


def test_get_blocking_checkin_failure_returns_face_message() -> None:
    result = PipelineResult(
        passed=False,
        status="exception",
        enabled_methods=["face"],
        verification_results={
            "face": {"passed": False, "message": "人脸比对未通过，请重新拍摄"},
        },
        exception_types=["face_failed"],
        messages=["人脸比对未通过，请重新拍摄"],
    )
    assert get_blocking_checkin_failure(result) == "人脸比对未通过，请重新拍摄"


def test_get_blocking_checkin_failure_returns_location_message() -> None:
    result = PipelineResult(
        passed=False,
        status="exception",
        enabled_methods=["location"],
        verification_results={
            "location": {
                "passed": False,
                "message": "当前位置不在签到范围内，请到指定地点后重新定位",
            },
        },
        exception_types=["location_error"],
        messages=["当前位置不在签到范围内，请到指定地点后重新定位"],
    )
    assert (
        get_blocking_checkin_failure(result)
        == "当前位置不在签到范围内，请到指定地点后重新定位"
    )


def test_get_blocking_checkin_failure_returns_none_for_soft_exception() -> None:
    result = PipelineResult(
        passed=False,
        status="exception",
        enabled_methods=["attachment"],
        verification_results={},
        exception_types=["attachment_missing"],
        messages=["附件缺失"],
    )
    assert get_blocking_checkin_failure(result) is None
