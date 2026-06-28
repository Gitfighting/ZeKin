from fastapi.testclient import TestClient

from app.main import app


def test_admin_analytics_returns_dashboard_payload() -> None:
    client = TestClient(app)
    login_response = client.post(
        "/api/auth/login",
        json={"account": "admin", "password": "123456", "user_type": "admin"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/api/admin/analytics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data) == {
        "summary",
        "trend",
        "college_rates",
        "exception_types",
        "class_exception_ranking",
        "overview",
    }
    assert set(data["summary"]) >= {
        "expected_students",
        "checked_students",
        "completion_rate",
        "exception_count",
        "pending_appeal_count",
        "task_count",
    }
    assert len(data["trend"]) == 7
