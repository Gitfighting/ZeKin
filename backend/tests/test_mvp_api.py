from fastapi.testclient import TestClient

from app.main import app


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_student_checkin_teacher_review_and_stats_flow():
    with TestClient(app) as client:
        student_payload = {
            "username": "student001",
            "password": "Passw0rd!",
            "real_name": "王同学",
            "role": "student",
            "class_name": "软件一班",
            "phone": "13800000001",
        }
        teacher_payload = {
            "username": "teacher001",
            "password": "Passw0rd!",
            "real_name": "华老师",
            "role": "teacher",
            "class_name": "软件一班",
            "phone": "13800000002",
        }

        assert client.post("/api/auth/register", json=student_payload).status_code == 201
        assert client.post("/api/auth/register", json=teacher_payload).status_code == 201

        student_login = client.post(
            "/api/auth/login",
            json={"username": "student001", "password": "Passw0rd!"},
        )
        assert student_login.status_code == 200
        student_token = student_login.json()["data"]["access_token"]

        teacher_login = client.post(
            "/api/auth/login",
            json={"username": "teacher001", "password": "Passw0rd!"},
        )
        assert teacher_login.status_code == 200
        teacher_token = teacher_login.json()["data"]["access_token"]

        me = client.get("/api/auth/me", headers=auth_headers(student_token))
        assert me.status_code == 200
        assert me.json()["data"]["role"] == "student"

        checkin = client.post(
            "/api/checkins",
            json={
                "type": "dorm",
                "content": "今天按时完成查寝打卡，宿舍情况正常。",
                "photo_url": "https://example.com/photo.jpg",
                "lat": 30.2741,
                "lng": 120.1551,
            },
            headers=auth_headers(student_token),
        )
        assert checkin.status_code == 201
        checkin_id = checkin.json()["data"]["id"]
        assert checkin.json()["data"]["status"] == "pending"

        history = client.get("/api/checkins/my", headers=auth_headers(student_token))
        assert history.status_code == 200
        assert len(history.json()["data"]["items"]) == 1

        teacher_list = client.get(
            "/api/teacher/checkins",
            headers=auth_headers(teacher_token),
        )
        assert teacher_list.status_code == 200
        assert teacher_list.json()["data"]["items"][0]["id"] == checkin_id

        review = client.post(
            "/api/teacher/reviews",
            json={
                "checkin_id": checkin_id,
                "action": "approved",
                "comment": "记录完整，通过。",
            },
            headers=auth_headers(teacher_token),
        )
        assert review.status_code == 201
        assert review.json()["data"]["action"] == "approved"

        stats = client.get("/api/stats/overview", headers=auth_headers(teacher_token))
        assert stats.status_code == 200
        assert stats.json()["data"]["total_checkins"] == 1
        assert stats.json()["data"]["approved_checkins"] == 1


def test_student_cannot_access_teacher_review_api():
    with TestClient(app) as client:
        client.post(
            "/api/auth/register",
            json={
                "username": "student002",
                "password": "Passw0rd!",
                "real_name": "赵同学",
                "role": "student",
                "class_name": "软件二班",
                "phone": "13800000003",
            },
        )
        login = client.post(
            "/api/auth/login",
            json={"username": "student002", "password": "Passw0rd!"},
        )
        token = login.json()["data"]["access_token"]

        response = client.get("/api/teacher/checkins", headers=auth_headers(token))

        assert response.status_code == 403
        assert response.json()["message"] == "权限不足"

