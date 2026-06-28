from fastapi.testclient import TestClient

from app.main import app


def _admin_headers(client: TestClient) -> dict[str, str]:
    login_response = client.post(
        "/api/auth/login",
        json={"account": "admin", "password": "123456", "user_type": "admin"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_scenario_analytics_returns_payload() -> None:
    client = TestClient(app)
    headers = _admin_headers(client)

    response = client.get(
        "/api/admin/analytics/scenario",
        params={"scenario": "classroom", "range": "week"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["scenario"] == "classroom"
    assert data["scenario_label"] == "课堂签到"
    assert set(data) >= {
        "summary",
        "trend",
        "major_rates",
        "class_rates",
        "exception_types",
        "verification_breakdown",
        "checkin_time_distribution",
        "class_exception_ranking",
        "risk_students",
        "face_registration_by_major",
        "filter_options",
    }
    assert set(data["summary"]) >= {
        "expected_count",
        "checked_count",
        "completion_rate",
        "face_registration_rate",
        "location_pass_rate",
        "face_pass_rate",
    }


def test_admin_scenario_analytics_supports_filters() -> None:
    client = TestClient(app)
    headers = _admin_headers(client)

    response = client.get(
        "/api/admin/analytics/scenario",
        params={
            "scenario": "dorm",
            "range": "month",
            "major": "软件工程",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["range"] == "month"
    assert data["filters"]["major"] == "软件工程"
