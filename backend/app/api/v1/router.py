from fastapi import APIRouter

from app.api.v1 import auth, checkins, teacher, system

api_router = APIRouter()
api_router.include_router(system.router, tags=["System"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Checkins"])
api_router.include_router(teacher.router, prefix="/teacher", tags=["Teacher"])
