"""Integration tests for open account registration."""

from fastapi.testclient import TestClient

from app.main import app


def test_register_creates_user_and_student_profile() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/auth/register",
        json={
            "account": "20268888",
            "phone": "13900008888",
            "password": "123456",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["access_token"]
    assert data["user"]["display_name"] == "用户20268888"

    login_response = client.post(
        "/api/auth/login",
        json={
            "account": "20268888",
            "password": "123456",
            "user_type": "student",
        },
    )
    assert login_response.status_code == 200, login_response.text


def test_register_rejects_existing_demo_student() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/auth/register",
        json={
            "account": "20260001",
            "phone": "13800000001",
            "password": "123456",
        },
    )
    assert response.status_code == 400
    assert "已注册" in response.json()["detail"]
