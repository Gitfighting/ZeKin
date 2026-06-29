from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.schema_patch import ensure_student_location_columns, ensure_task_scheduled_publish_column
from app.core.logging_config import setup_logging
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.daily_report.router import router as daily_report_router
from app.modules.exceptions.router import router as exceptions_router
from app.modules.face_recognition.router import router as face_recognition_router
from app.modules.face_recognition.user_router import router as face_test_router
from app.modules.seed import seed_reference_data
from app.modules.statistics.router import router as statistics_router
from app.modules.student.router import router as student_router
from app.modules.tasks.router import router as teacher_router
import app.modules.all_models  # noqa: F401

settings = get_settings()
logger = logging.getLogger("zeKin.app")


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_student_location_columns(engine)
    ensure_task_scheduled_publish_column(engine)
    with SessionLocal() as session:
        seed_reference_data(session)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_file = db_url.replace("sqlite:///", "", 1)
        db_exists = Path(db_file).exists()
        logger.info(
            "database: url=%s file_exists=%s file_size=%s",
            db_url,
            db_exists,
            Path(db_file).stat().st_size if db_exists else 0,
        )
    else:
        logger.info("database: url=%s", db_url)
    initialize_database()
    auth_routes = [
        f"{','.join(sorted(route.methods))} {route.path}"
        for route in app.routes
        if hasattr(route, "path") and route.path.startswith("/api/auth")
    ]
    logger.info("auth routes: %s", auth_routes)
    student_group_routes = [
        f"{','.join(sorted(route.methods))} {route.path}"
        for route in app.routes
        if hasattr(route, "path") and route.path.startswith("/api/student/groups")
    ]
    logger.info("student group routes: %s", student_group_routes)
    has_student_group_list = any(
        hasattr(route, "path")
        and route.path == "/api/student/groups"
        and "GET" in getattr(route, "methods", set())
        for route in app.routes
    )
    has_student_group_attendance = any(
        hasattr(route, "path")
        and "/api/student/groups/" in route.path
        and route.path.endswith("/attendance")
        and "GET" in getattr(route, "methods", set())
        for route in app.routes
    )
    if not has_student_group_list:
        logger.warning("GET /api/student/groups 未注册，学生班级列表将返回 404，请重启 backend")
    if not has_student_group_attendance:
        logger.warning(
            "GET /api/student/groups/{id}/attendance 未注册，班级详情将返回 404，请重启 backend"
        )
    if not any("/api/auth/register" in item for item in auth_routes):
        logger.warning("POST /api/auth/register 未注册，小程序注册将返回 404，请确认已部署最新 backend 代码")
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(face_recognition_router)
app.include_router(face_test_router)
app.include_router(teacher_router)
app.include_router(exceptions_router)
app.include_router(student_router)
app.include_router(daily_report_router)
app.include_router(statistics_router)


@app.middleware("http")
async def log_auth_register_requests(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/auth"):
        logger.info("[register-flow] HTTP 进入 %s %s", request.method, path)
    response = await call_next(request)
    if path.startswith("/api/auth"):
        logger.info(
            "[register-flow] HTTP 返回 %s %s -> status=%s",
            request.method,
            path,
            response.status_code,
        )
    return response


@app.get("/health")
def health() -> dict[str, object]:
    db_url = settings.database_url
    info: dict[str, object] = {
        "status": "ok",
        "database_url": db_url,
        "features": {
            "student_group_attendance": True,
        },
    }
    if db_url.startswith("sqlite:///"):
        db_file = Path(db_url.replace("sqlite:///", "", 1))
        info["database_file_exists"] = db_file.exists()
        if db_file.exists():
            info["database_file_size"] = db_file.stat().st_size
    return info
