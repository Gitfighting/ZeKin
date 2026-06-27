"""发布任务：消息推送 + 定时任务 occurrence 物化。"""
from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_publish_notifies_members_and_materializes_occurrences() -> None:
    client = TestClient(app)
    admin_token = _login(client, "admin", "123456", "admin")
    teacher_token = _login(client, "20261001", "123456", "teacher")

    client.post(
        "/api/admin/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "students": [
                {
                    "student_no": "20260201",
                    "name": "孙八",
                    "phone": "13800003001",
                    "college": "软件学院",
                    "major": "软件工程",
                    "grade": "2026",
                    "class_name": "软件2601",
                    "dormitory": "3号楼301",
                }
            ]
        },
    )
    activate = client.post(
        "/api/auth/student/activate",
        json={
            "name": "孙八",
            "student_no": "20260201",
            "phone": "13800003001",
            "code": "000000",
            "password": "123456",
        },
    )
    student_token = activate.json()["data"]["access_token"]

    rules = {
        "timeRule": {"startTime": "08:30", "endTime": "10:00"},
        "verificationRule": {"methods": ["location"], "location": {"longitude": 120.0, "latitude": 30.0, "radius": 300}},
    }
    create = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "实习每日打卡",
            "type_id": 1,
            "group_ids": [1],
            "schedule_mode": "recurring",
            "recurrence_rule": "FREQ=DAILY",
            "starts_at": "2026-06-26T08:30:00+08:00",
            "ends_at": "2026-06-26T10:00:00+08:00",
            "rules_snapshot": rules,
        },
    )
    assert create.status_code == 200
    task_id = create.json()["data"]["id"]
    assert create.json()["data"]["schedule_mode"] == "recurring"

    publish = client.post(
        f"/api/teacher/tasks/{task_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert publish.status_code == 200
    data = publish.json()["data"]
    assert data["published"] is True
    assert data["notified_count"] >= 1
    assert data["occurrence_count"] >= 1

    # 任务详情包含 occurrences
    detail = client.get(
        f"/api/teacher/tasks/{task_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert detail.status_code == 200
    assert len(detail.json()["data"]["occurrences"]) >= 1

    # 学生收到发布通知消息
    messages = client.get(
        "/api/student/messages",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert messages.status_code == 200
    items = messages.json()["data"]["items"]
    assert any(item.get("title") == "实习每日打卡" for item in items)
