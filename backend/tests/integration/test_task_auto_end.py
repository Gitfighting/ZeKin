from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app

BEIJING = ZoneInfo("Asia/Shanghai")


def _login(client: TestClient, account: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": "123456", "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_task_auto_ends_after_end_time(monkeypatch) -> None:
    client = TestClient(app)
    teacher_token = _login(client, "20261001", "teacher")
    student_token = _login(client, "20260001", "student")

    create = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "自动结束测试",
            "type_id": 1,
            "group_ids": [1],
            "starts_at": "2026-06-28T08:00:00+08:00",
            "ends_at": "2026-06-28T09:00:00+08:00",
            "schedule_mode": "one_time",
            "rules_snapshot": {
                "reviewRule": {"autoEnd": True},
                "verificationRule": {"methods": ["location"]},
                "locationRule": {
                    "mode": "fixed_area",
                    "placeName": "教室",
                    "longitude": 0,
                    "latitude": 0,
                    "radius": 300,
                },
            },
        },
    )
    assert create.status_code == 200
    task_id = create.json()["data"]["id"]

    publish = client.post(
        f"/api/teacher/tasks/{task_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert publish.status_code == 200

    monkeypatch.setattr(
        "app.modules.tasks.lifecycle.get_beijing_now",
        lambda: datetime(2026, 6, 28, 10, 0, tzinfo=BEIJING),
    )
    monkeypatch.setattr(
        "app.modules.records.service.get_beijing_now",
        lambda: datetime(2026, 6, 28, 10, 0, tzinfo=BEIJING),
    )

    teacher_tasks = client.get(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert teacher_tasks.status_code == 200
    teacher_item = next(
        item for item in teacher_tasks.json()["data"]["items"] if item["id"] == task_id
    )
    assert teacher_item["status"] == "ended"

    student_tasks = client.get(
        "/api/student/tasks",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert student_tasks.status_code == 200
    student_item = next(
        item for item in student_tasks.json()["data"]["items"] if item["id"] == task_id
    )
    assert student_item["task_status"] == "ended"
    assert student_item["status"] == "in_progress"
    assert student_item["checked_in"] is False

    checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"longitude": 0, "latitude": 0},
    )
    assert checkin.status_code == 400
    assert "任务已结束" in str(checkin.json()["detail"])
