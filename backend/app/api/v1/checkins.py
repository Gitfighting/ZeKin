"""Checkin API — 实现见 Sprint 1 FEAT-002."""
from fastapi import APIRouter

router = APIRouter()


@router.post("")
def create_checkin():
    return {"code": 501, "message": "Not implemented — see specs/features/FEAT-002-checkin.md", "data": None}


@router.get("")
def list_checkins():
    return {"code": 501, "message": "Not implemented", "data": None}


@router.get("/today")
def today_status():
    return {
        "code": 501,
        "message": "Not implemented",
        "data": {"dorm": "pending", "class": "pending", "internship": "not_required"},
    }
