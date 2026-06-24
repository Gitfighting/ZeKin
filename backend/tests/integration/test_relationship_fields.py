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


def _import_student(
    client: TestClient, admin_token: str, *, student_no: str, name: str, phone: str
) -> None:
    response = client.post(
        "/api/admin/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "students": [
                {
                    "student_no": student_no,
                    "name": name,
                    "phone": phone,
                    "college": "软件学院",
                    "major": "软件工程",
                    "grade": "2026",
                    "class_name": "软件2601",
                    "dormitory": "3号楼301",
                }
            ]
        },
    )
    assert response.status_code == 200


def _activate_student(
    client: TestClient, *, student_no: str, name: str, phone: str
) -> str:
    response = client.post(
        "/api/auth/student/activate",
        json={
            "name": name,
            "student_no": student_no,
            "phone": phone,
            "code": "000000",
            "password": "student123456",
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _create_task(client: TestClient, teacher_token: str) -> int:
    response = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "晚间查寝",
            "type_id": 1,
            "group_ids": [1],
            "starts_at": "2026-06-24T21:30:00+08:00",
            "ends_at": "2026-06-24T22:30:00+08:00",
            "rules_snapshot": DEFAULT_RULE_SNAPSHOT,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


def _seed_relationship_scenario(client: TestClient) -> dict[str, int | str]:
    admin_token = _login(client, "admin", "admin123456", "admin")
    teacher_token = _login(client, "teacher", "teacher123456", "teacher")
    students = [
        ("20260001", "张三", "13800000001"),
        ("20260002", "李四", "13800000004"),
        ("20260003", "王五", "13800000005"),
    ]
    for student_no, name, phone in students:
        _import_student(
            client, admin_token, student_no=student_no, name=name, phone=phone
        )

    normal_student_token = _activate_student(
        client, student_no="20260001", name="张三", phone="13800000001"
    )
    exception_student_token = _activate_student(
        client, student_no="20260002", name="李四", phone="13800000004"
    )
    task_id = _create_task(client, teacher_token)

    normal_checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {normal_student_token}"},
        json={
            "longitude": 120.000001,
            "latitude": 30.000001,
            "dynamic_code": "",
            "submit_payload": {"remark": "已在宿舍"},
        },
    )
    assert normal_checkin.status_code == 200
    exception_checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {exception_student_token}"},
        json={
            "longitude": 120.01,
            "latitude": 30.01,
            "dynamic_code": "",
            "submit_payload": {"remark": "定位偏移"},
        },
    )
    assert exception_checkin.status_code == 200

    return {
        "admin_token": admin_token,
        "teacher_token": teacher_token,
        "task_id": task_id,
    }


def test_teacher_relationship_fields_include_counts_progress_students_and_exceptions(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = TestClient(app)
    scenario = _seed_relationship_scenario(client)
    teacher_headers = {"Authorization": f"Bearer {scenario['teacher_token']}"}

    groups_response = client.get("/api/teacher/groups", headers=teacher_headers)
    assert groups_response.status_code == 200
    group = groups_response.json()["data"]["items"][0]
    assert group["id"] == 1
    assert group["student_count"] == 3
    assert group["studentCount"] == 3
    assert group["recent_task_count"] == 1
    assert group["recentTaskCount"] == 1

    tasks_response = client.get("/api/teacher/tasks", headers=teacher_headers)
    assert tasks_response.status_code == 200
    task = tasks_response.json()["data"]["items"][0]
    assert task["student_count"] == 3
    assert task["submitted_count"] == 2
    assert task["completion_rate"] == 67
    assert task["completionRate"] == 67
    assert task["exception_count"] == 1
    assert task["pending_review_count"] == 1
    assert task["group_names"] == ["软件2601"]
    assert task["groupName"] == "软件2601"

    detail_response = client.get(
        f"/api/teacher/tasks/{scenario['task_id']}", headers=teacher_headers
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()["data"]
    assert detail["id"] == scenario["task_id"]
    assert detail["task"]["completionRate"] == 67
    assert [student["name"] for student in detail["students"]] == [
        "张三",
        "李四",
        "王五",
    ]
    assert {student["name"]: student["status"] for student in detail["students"]} == {
        "张三": "submitted",
        "李四": "pending_review",
        "王五": "missing",
    }
    assert detail["exceptions"][0]["studentName"] == "李四"
    assert detail["exceptions"][0]["taskTitle"] == "晚间查寝"
    assert detail["exceptions"][0]["groupName"] == "软件2601"
    assert detail["exceptions"][0]["reason"] == "当前位置不在有效范围内"

    exceptions_response = client.get("/api/teacher/exceptions", headers=teacher_headers)
    assert exceptions_response.status_code == 200
    exception = exceptions_response.json()["data"]["items"][0]
    assert exception["student_name"] == "李四"
    assert exception["studentName"] == "李四"
    assert exception["task_title"] == "晚间查寝"
    assert exception["taskTitle"] == "晚间查寝"
    assert exception["group_name"] == "软件2601"
    assert exception["groupName"] == "软件2601"
    assert exception["submitted_at"].startswith("2026-06-24T21:45:00")


def test_admin_relationship_fields_include_student_teacher_group_task_and_exception_links(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = TestClient(app)
    scenario = _seed_relationship_scenario(client)
    admin_headers = {"Authorization": f"Bearer {scenario['admin_token']}"}

    dashboard_response = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()["data"]
    assert dashboard["student_count"] == 3
    assert dashboard["task_count"] == 1
    assert dashboard["exception_count"] == 1
    assert dashboard["pending_appeal_count"] == 1
    assert dashboard["completion_rate"] == 67

    students_response = client.get("/api/admin/students", headers=admin_headers)
    assert students_response.status_code == 200
    student = students_response.json()["data"]["items"][0]
    assert student["student_no"] == "20260001"
    assert student["group_ids"] == [1]
    assert student["group_names"] == ["软件2601"]
    assert student["teacher_names"] == ["李老师"]

    teachers_response = client.get("/api/admin/teachers", headers=admin_headers)
    assert teachers_response.status_code == 200
    teacher = teachers_response.json()["data"]["items"][0]
    assert teacher["name"] == "李老师"
    assert teacher["group_ids"] == [1]
    assert teacher["groups"] == ["软件2601"]
    assert teacher["student_count"] == 3

    groups_response = client.get("/api/admin/groups", headers=admin_headers)
    assert groups_response.status_code == 200
    group = groups_response.json()["data"]["items"][0]
    assert group["name"] == "软件2601"
    assert group["student_count"] == 3
    assert group["teacher_count"] == 1
    assert group["teacher_names"] == ["李老师"]

    tasks_response = client.get("/api/admin/tasks", headers=admin_headers)
    assert tasks_response.status_code == 200
    task = tasks_response.json()["data"]["items"][0]
    assert task["title"] == "晚间查寝"
    assert task["teacher_name"] == "李老师"
    assert task["group_names"] == ["软件2601"]
    assert task["student_count"] == 3
    assert task["submitted_count"] == 2
    assert task["completion_rate"] == 67
    assert task["exception_count"] == 1

    exceptions_response = client.get("/api/admin/exceptions", headers=admin_headers)
    assert exceptions_response.status_code == 200
    exception = exceptions_response.json()["data"]["items"][0]
    assert exception["student_name"] == "李四"
    assert exception["student_no"] == "20260002"
    assert exception["task_title"] == "晚间查寝"
    assert exception["teacher_name"] == "李老师"
    assert exception["group_names"] == ["软件2601"]
    assert exception["record_status"] == "exception"
