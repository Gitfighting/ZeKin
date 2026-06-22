"""Auth API — 实现见 Sprint 1 FEAT-001."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
def register():
    return {"code": 501, "message": "Not implemented — see specs/features/FEAT-001-auth.md", "data": None}


@router.post("/login")
def login():
    return {"code": 501, "message": "Not implemented", "data": None}


@router.get("/me")
def me():
    return {"code": 501, "message": "Not implemented", "data": None}
