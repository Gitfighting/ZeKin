from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.exceptions.router import router as exceptions_router
from app.modules.seed import seed_reference_data
from app.modules.statistics.router import router as statistics_router
from app.modules.student.router import router as student_router
from app.modules.tasks.router import router as teacher_router
import app.modules.all_models  # noqa: F401

settings = get_settings()


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_reference_data(session)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
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
app.include_router(teacher_router)
app.include_router(exceptions_router)
app.include_router(student_router)
app.include_router(statistics_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
