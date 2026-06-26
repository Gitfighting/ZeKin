from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app
from app.modules.seed import DEFAULT_RULE_SNAPSHOT


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_checkin_with_enabled_face_rule_requires_registered_face(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = TestClient(app)
    admin_token = _login(client, "admin", "admin123456", "admin")
    teacher_token = _login(client, "teacher", "teacher123456", "teacher")

    student_payload = {
        "student_no": "20260001",
        "name": "张三",
        "phone": "13800000001",
        "college": "软件学院",
        "major": "软件工程",
        "grade": "2026",
        "class_name": "软件2601",
        "dormitory": "3号楼301",
    }
    import_response = client.post(
        "/api/admin/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"students": [student_payload]},
    )
    assert import_response.status_code == 200

    activate_response = client.post(
        "/api/auth/student/activate",
        json={
            "name": "张三",
            "student_no": "20260001",
            "phone": "13800000001",
            "code": "000000",
            "password": "student123456",
        },
    )
    assert activate_response.status_code == 200
    student_token = activate_response.json()["data"]["access_token"]

    rules = deepcopy(DEFAULT_RULE_SNAPSHOT)
    rules["faceRule"] = {
        "enabled": True,
        "provider": "face_recognition",
        "tolerance": 0.6,
    }
    create_task_response = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "晚间查寝",
            "type_id": 1,
            "group_ids": [1],
            "starts_at": "2026-06-24T21:30:00+08:00",
            "ends_at": "2026-06-24T22:30:00+08:00",
            "rules_snapshot": rules,
        },
    )
    assert create_task_response.status_code == 200
    task_id = create_task_response.json()["data"]["id"]

    checkin_response = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "longitude": 120.000001,
            "latitude": 30.000001,
            "dynamic_code": "",
            "face_image": "aW1hZ2UtYnl0ZXM=",
            "submit_payload": {"remark": "已在宿舍"},
        },
    )

    assert checkin_response.status_code == 200
    result = checkin_response.json()["data"]
    assert result["status"] == "exception"
    assert result["exception_types"] == ["face_failed"]
    assert result["need_review"] is True
