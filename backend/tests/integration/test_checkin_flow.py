from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app


def test_checkin_flow_and_rule_snapshot_is_immutable(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = TestClient(app)

    admin_login = client.post(
        "/api/auth/login",
        json={"account": "admin", "password": "admin123456", "user_type": "admin"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["data"]["access_token"]

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

    teacher_login = client.post(
        "/api/auth/login",
        json={"account": "teacher", "password": "teacher123456", "user_type": "teacher"},
    )
    assert teacher_login.status_code == 200
    teacher_token = teacher_login.json()["data"]["access_token"]

    rules_snapshot = {
        "timeRule": {
            "mode": "single",
            "startTime": "21:30",
            "endTime": "22:30",
            "allowLate": False,
            "allowMakeup": True,
            "makeupNeedReview": True,
        },
        "locationRule": {
            "mode": "fixed_area",
            "placeName": "3号宿舍楼",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 300,
            "allowExceptionSubmit": True,
        },
        "verificationRule": {"methods": ["location"]},
        "submitRule": {
            "fields": [
                {
                    "key": "remark",
                    "label": "情况说明",
                    "type": "textarea",
                    "required": False,
                }
            ]
        },
        "reviewRule": {"mode": "exception_only"},
        "reminderRule": {
            "beforeStartMinutes": 10,
            "beforeEndMinutes": 5,
            "notifyTeacherAfterEnd": True,
        },
        "faceRule": {"enabled": False, "provider": "placeholder"},
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
            "rules_snapshot": rules_snapshot,
        },
    )
    assert create_task_response.status_code == 200
    task_data = create_task_response.json()["data"]
    task_id = task_data["id"]
    snapshot_before_template_update = deepcopy(task_data["rules_snapshot"])

    template_list_response = client.get(
        "/api/admin/rule-templates",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert template_list_response.status_code == 200
    rule_template_id = template_list_response.json()["data"]["items"][0]["id"]

    update_template_response = client.post(
        f"/api/admin/rule-templates/{rule_template_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "晚间查寝模板",
            "rules_snapshot": {
                **rules_snapshot,
                "locationRule": {
                    **rules_snapshot["locationRule"],
                    "radius": 500,
                },
            },
        },
    )
    assert update_template_response.status_code == 200

    task_detail_response = client.get(
        f"/api/teacher/tasks/{task_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert task_detail_response.status_code == 200
    assert task_detail_response.json()["data"]["rules_snapshot"] == snapshot_before_template_update

    checkin_response = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "longitude": 120.000001,
            "latitude": 30.000001,
            "dynamic_code": "",
            "submit_payload": {"remark": "已在宿舍"},
        },
    )
    assert checkin_response.status_code == 200
    assert checkin_response.json()["data"]["status"] == "normal"
