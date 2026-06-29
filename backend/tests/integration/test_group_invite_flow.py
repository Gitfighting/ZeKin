"""Integration tests for group invite code flow."""

from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_teacher_create_group_and_student_join() -> None:
    client = TestClient(app)
    teacher_token = _login(client, "20261001", "123456", "teacher")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    create_response = client.post(
        "/api/teacher/groups",
        headers=teacher_headers,
        json={"name": "测试邀请码班级"},
    )
    assert create_response.status_code == 200, create_response.text
    group = create_response.json()["data"]
    assert group["name"] == "测试邀请码班级"
    invite_code = group["invite_code"]
    assert invite_code
    group_id = group["id"]

    detail_response = client.get(
        f"/api/teacher/groups/{group_id}",
        headers=teacher_headers,
    )
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()["data"]
    assert detail["group"]["invite_code"] == invite_code
    assert detail["students"] == []

    student_token = _login(client, "20260001", "123456", "student")
    student_headers = {"Authorization": f"Bearer {student_token}"}

    join_response = client.post(
        "/api/student/groups/join",
        headers=student_headers,
        json={"invite_code": invite_code},
    )
    assert join_response.status_code == 200, join_response.text
    joined = join_response.json()["data"]
    assert joined["group"]["id"] == group_id
    assert joined["already_member"] is False

    detail_after_join = client.get(
        f"/api/teacher/groups/{group_id}",
        headers=teacher_headers,
    )
    assert detail_after_join.status_code == 200, detail_after_join.text
    students = detail_after_join.json()["data"]["students"]
    assert len(students) == 1
    assert students[0]["name"] == "张三"

    join_again = client.post(
        "/api/student/groups/join",
        headers=student_headers,
        json={"invite_code": invite_code},
    )
    assert join_again.status_code == 200, join_again.text
    assert join_again.json()["data"]["already_member"] is True

    list_response = client.get(
        "/api/student/groups",
        headers=student_headers,
    )
    assert list_response.status_code == 200, list_response.text
    items = list_response.json()["data"]["items"]
    matched = next((item for item in items if item["id"] == group_id), None)
    assert matched is not None


def test_student_group_attendance_detail() -> None:
    client = TestClient(app)
    student_token = _login(client, "20260001", "123456", "student")
    student_headers = {"Authorization": f"Bearer {student_token}"}

    list_response = client.get("/api/student/groups", headers=student_headers)
    assert list_response.status_code == 200, list_response.text
    items = list_response.json()["data"]["items"]
    assert items, "seed 数据应包含学生已加入的班级"
    group_id = items[0]["id"]

    attendance_response = client.get(
        f"/api/student/groups/{group_id}/attendance",
        headers=student_headers,
    )
    assert attendance_response.status_code == 200, attendance_response.text
    payload = attendance_response.json()["data"]
    assert payload["group"]["id"] == group_id
    assert "summary" in payload
    assert "checked_in_count" in payload["summary"] or "checkedInCount" in payload["summary"]
    assert isinstance(payload["tasks"], list)
    assert isinstance(payload["timeline"], list)
    if payload["timeline"]:
        first = payload["timeline"][0]
        assert "status_label" in first or "statusLabel" in first
        assert "occurred_at" in first or "occurredAt" in first
