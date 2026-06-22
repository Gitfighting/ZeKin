"""Teacher API — 实现见 Sprint 1 FEAT-003."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/checkins")
def teacher_checkins():
    return {"code": 501, "message": "Not implemented — see specs/features/FEAT-003-teacher-review.md", "data": None}


@router.post("/reviews")
def create_review():
    return {"code": 501, "message": "Not implemented", "data": None}
