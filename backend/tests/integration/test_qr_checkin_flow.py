"""二维码签到全链路集成测试：教师生成二维码 → 学生扫码提交。"""
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_qr_code_checkin_flow(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 26, 8, 5, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = TestClient(app)
    admin_token = _login(client, "admin", "123456", "admin")
    teacher_token = _login(client, "20261001", "123456", "teacher")

    client.post(
        "/api/admin/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "students": [
                {
                    "student_no": "20260101",
                    "name": "钱七",
                    "phone": "13800002001",
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
            "name": "钱七",
            "student_no": "20260101",
            "phone": "13800002001",
            "code": "000000",
            "password": "123456",
        },
    )
    student_token = activate.json()["data"]["access_token"]

    # 仅二维码签到的任务（避免人脸依赖），便于验证 QR 流程
    rules = {
        "timeRule": {"startTime": "08:00", "endTime": "08:15"},
        "verificationRule": {
            "methods": ["qr_code"],
            "qr_code": {"refreshIntervalSeconds": 60, "expireSeconds": 120},
        },
        "reviewRule": {"mode": "exception_only"},
    }
    create = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "课堂二维码签到",
            "type_id": 1,
            "group_ids": [1],
            "schedule_mode": "one_time",
            "starts_at": "2026-06-26T08:00:00+08:00",
            "ends_at": "2026-06-26T08:15:00+08:00",
            "rules_snapshot": rules,
        },
    )
    assert create.status_code == 200
    task_id = create.json()["data"]["id"]
    assert create.json()["data"]["schedule_mode"] == "one_time"

    # 教师生成二维码 token
    qr = client.get(
        f"/api/teacher/tasks/{task_id}/qr-code",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert qr.status_code == 200
    qr_token = qr.json()["data"]["qr_token"]
    assert qr_token

    # 学生扫码提交
    checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"qr_payload": qr_token, "occurrence_date": "2026-06-26"},
    )
    assert checkin.status_code == 200
    data = checkin.json()["data"]
    assert data["status"] == "normal"
    assert data["enabled_methods"] == ["qr_code"]
    assert data["verification_results"]["qr_code"]["passed"] is True

    # 伪造二维码 → 失败
    bad = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"qr_payload": "forged.token", "occurrence_date": "2026-06-26"},
    )
    assert bad.status_code == 200
    assert bad.json()["data"]["status"] == "exception"
    assert "qr_failed" in bad.json()["data"]["exception_types"]
