from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app, initialize_database
from app.modules.auth.models import StudentProfile, TeacherProfile, User
from app.modules.groups.models import Group, GroupTeacher
from app.modules.seed import DEFAULT_RULE_SNAPSHOT, pwd_context
from app.shared.enums import UserType


def _client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _import_and_activate_student(client: TestClient, admin_token: str) -> str:
    response = client.post(
        "/api/admin/students/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "students": [
                {
                    "student_no": "20260001",
                    "name": "张三",
                    "phone": "13800000001",
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
    activate = client.post(
        "/api/auth/student/activate",
        json={
            "name": "张三",
            "student_no": "20260001",
            "phone": "13800000001",
            "code": "000000",
            "password": "123456",
        },
    )
    assert activate.status_code == 200
    return activate.json()["data"]["access_token"]


def _create_task(
    client: TestClient, teacher_token: str, group_ids: list[int] | None = None
) -> int:
    response = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "晚间查寝",
            "type_id": 1,
            "group_ids": group_ids or [1],
            "starts_at": "2026-06-24T21:30:00+08:00",
            "ends_at": "2026-06-24T22:30:00+08:00",
            "rules_snapshot": DEFAULT_RULE_SNAPSHOT,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


def _add_second_teacher_and_group() -> tuple[int, int]:
    with SessionLocal() as session:
        teacher = User(
            account="20261002",
            phone="13800000003",
            password_hash=pwd_context.hash("123456"),
            user_type=UserType.TEACHER.value,
            display_name="王老师",
        )
        session.add(teacher)
        session.flush()
        profile = TeacherProfile(
            user_id=teacher.id,
            teacher_no="20261002",
            name="王老师",
            phone="13800000003",
            department="软件学院",
        )
        session.add(profile)
        session.flush()
        group = Group(
            name="软件2602",
            group_type="class",
            invite_code="TEST02",
        )
        session.add(group)
        session.flush()
        session.add(GroupTeacher(group_id=group.id, teacher_profile_id=profile.id))
        session.commit()
        return teacher.id, group.id


def test_initialize_database_does_not_delete_existing_data() -> None:
    with SessionLocal() as session:
        session.add(
            StudentProfile(
                student_no="KEEP001",
                name="保留学生",
                phone="13900000001",
                college="软件学院",
                major="软件工程",
                grade="2026",
                class_name="软件2609",
                dormitory="9号楼901",
            )
        )
        session.commit()

    initialize_database()

    with SessionLocal() as session:
        assert (
            session.query(StudentProfile).filter_by(student_no="KEEP001").one_or_none()
            is not None
        )


def test_roleless_login_resolves_mini_app_users_but_not_admins() -> None:
    client = _client()

    teacher_login = client.post(
        "/api/auth/login",
        json={"account": "20261001", "password": "123456"},
    )
    assert teacher_login.status_code == 200
    assert teacher_login.json()["data"]["user"]["user_type"] == "teacher"

    admin_login = client.post(
        "/api/auth/login",
        json={"account": "admin", "password": "123456"},
    )
    assert admin_login.status_code == 400


def test_teacher_groups_come_from_database_memberships() -> None:
    _, group_id = _add_second_teacher_and_group()
    client = _client()
    teacher2_token = _login(client, "20261002", "123456", "teacher")

    response = client.get(
        "/api/teacher/groups", headers={"Authorization": f"Bearer {teacher2_token}"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    item = data["items"][0]
    assert item["id"] == group_id
    assert item["name"] == "软件2602"
    assert item["group_type"] == "class"
    assert item["student_count"] == 0
    assert item["studentCount"] == 0
    assert item["recent_task_count"] == 0
    assert item["recentTaskCount"] == 0


def test_appeal_and_review_create_student_messages(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 22, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    client = _client()
    admin_token = _login(client, "admin", "123456", "admin")
    student_token = _import_and_activate_student(client, admin_token)
    teacher_token = _login(client, "20261001", "123456", "teacher")
    task_id = _create_task(client, teacher_token)
    checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "longitude": 120.000001,
            "latitude": 30.000001,
            "dynamic_code": "",
            "submit_payload": {"remark": "定位偏移"},
        },
    )
    assert checkin.status_code == 200
    record_id = checkin.json()["data"]["record_id"]

    appeal = client.post(
        f"/api/student/records/{record_id}/appeal",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"reason": "定位偏移，实际在宿舍楼内", "attachment_ids": []},
    )
    assert appeal.status_code == 200
    messages = client.get(
        "/api/student/messages", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert messages.status_code == 200
    assert any(
        "申诉已提交" in item["title"] for item in messages.json()["data"]["items"]
    )

    exceptions = client.get(
        "/api/teacher/exceptions", headers={"Authorization": f"Bearer {teacher_token}"}
    )
    exception_id = exceptions.json()["data"]["items"][0]["id"]
    review = client.post(
        f"/api/teacher/exceptions/{exception_id}/review",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"decision": "approve", "comment": "申诉通过"},
    )
    assert review.status_code == 200
    reviewed_messages = client.get(
        "/api/student/messages", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert any(
        "申诉审核结果" in item["title"] or "审核结果" in item["title"]
        for item in reviewed_messages.json()["data"]["items"]
    )


def test_teacher_cannot_publish_end_or_review_out_of_scope_task(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 22, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    _add_second_teacher_and_group()
    client = _client()
    admin_token = _login(client, "admin", "123456", "admin")
    student_token = _import_and_activate_student(client, admin_token)
    teacher_token = _login(client, "20261001", "123456", "teacher")
    teacher2_token = _login(client, "20261002", "123456", "teacher")
    task_id = _create_task(client, teacher_token)

    assert (
        client.post(
            f"/api/teacher/tasks/{task_id}/publish",
            headers={"Authorization": f"Bearer {teacher2_token}"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/teacher/tasks/{task_id}/end",
            headers={"Authorization": f"Bearer {teacher2_token}"},
        ).status_code
        == 403
    )

    checkin = client.post(
        f"/api/student/tasks/{task_id}/checkin",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "longitude": 120.01,
            "latitude": 30.01,
            "dynamic_code": "",
            "submit_payload": {"remark": "定位偏移"},
        },
    )
    assert checkin.status_code == 200
    exceptions = client.get(
        "/api/teacher/exceptions", headers={"Authorization": f"Bearer {teacher_token}"}
    )
    exception_id = exceptions.json()["data"]["items"][0]["id"]

    review = client.post(
        f"/api/teacher/exceptions/{exception_id}/review",
        headers={"Authorization": f"Bearer {teacher2_token}"},
        json={"decision": "approve", "comment": "越权审核"},
    )

    assert review.status_code == 403
