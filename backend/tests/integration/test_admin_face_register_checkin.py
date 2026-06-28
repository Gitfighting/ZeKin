from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app
from app.modules.face_recognition.service import FaceRecognitionExtractor
from app.modules.seed import DEFAULT_RULE_SNAPSHOT

SHARED_FACE_ENCODING = [0.12, 0.34, 0.56, 0.78]


def _login(client: TestClient, account: str, password: str, user_type: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"account": account, "password": password, "user_type": user_type},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _student_profile_id(client: TestClient, admin_token: str, student_no: str) -> int:
    response = client.get(
        "/api/admin/students",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    profile = next(item for item in items if item["student_no"] == student_no)
    return profile["id"]


def test_admin_register_face_then_student_checkin_passes(monkeypatch) -> None:
    def fake_extract(self, image_bytes: bytes, detection_model: str = "hog") -> list[float]:
        assert image_bytes
        assert detection_model in {"hog", "cnn"}
        return SHARED_FACE_ENCODING

    monkeypatch.setattr(
        FaceRecognitionExtractor,
        "extract_single_encoding",
        fake_extract,
    )
    monkeypatch.setattr(
        "app.modules.records.service.get_current_time",
        lambda: datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )

    client = TestClient(app)
    admin_token = _login(client, "admin", "123456", "admin")
    teacher_token = _login(client, "20261001", "123456", "teacher")
    student_token = _login(client, "20260001", "123456", "student")
    student_profile_id = _student_profile_id(client, admin_token, "20260001")

    register_response = client.post(
        f"/api/admin/students/{student_profile_id}/face",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"photo": ("face.jpg", b"admin-face-image", "image/jpeg")},
    )
    assert register_response.status_code == 200
    register_data = register_response.json()["data"]
    assert register_data["encoding_count"] == 1
    assert register_data["dimension"] == len(SHARED_FACE_ENCODING)

    status_response = client.get(
        f"/api/admin/students/{student_profile_id}/face",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["data"]["registered"] is True

    rules = deepcopy(DEFAULT_RULE_SNAPSHOT)
    rules["faceRule"] = {
        "enabled": True,
        "provider": "face_recognition",
        "tolerance": 0.6,
    }
    rules["verificationRule"] = {
        "methods": ["face", "location"],
        "face": {"tolerance": 0.6, "detectionModel": "hog"},
        "location": rules["locationRule"],
    }
    create_task_response = client.post(
        "/api/teacher/tasks",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "人脸打卡联调",
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
            "occurrence_date": "2026-06-24",
            "dynamic_code": "",
            "face_image": "data:image/jpeg;base64,YWRtaW4tZmFjZS1pbWFnZQ==",
            "submit_payload": {"remark": "人脸联调测试"},
        },
    )

    assert checkin_response.status_code == 200
    body = checkin_response.json()["data"]
    assert body["record_id"]
    assert body["status"] in {"normal", "pending_review", "exception"}
    assert body["verification_results"]["face"]["passed"] is True


def test_admin_clear_face_removes_registered_status(monkeypatch) -> None:
    def fake_extract(self, image_bytes: bytes, detection_model: str = "hog") -> list[float]:
        return SHARED_FACE_ENCODING

    monkeypatch.setattr(FaceRecognitionExtractor, "extract_single_encoding", fake_extract)

    client = TestClient(app)
    admin_token = _login(client, "admin", "123456", "admin")
    student_profile_id = _student_profile_id(client, admin_token, "20260001")

    register_response = client.post(
        f"/api/admin/students/{student_profile_id}/face",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"photo": ("face.jpg", b"admin-face-image", "image/jpeg")},
    )
    assert register_response.status_code == 200

    clear_response = client.delete(
        f"/api/admin/students/{student_profile_id}/face",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert clear_response.status_code == 200
    assert clear_response.json()["data"]["registered"] is False

    status_response = client.get(
        f"/api/admin/students/{student_profile_id}/face",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status_response.json()["data"]["registered"] is False
