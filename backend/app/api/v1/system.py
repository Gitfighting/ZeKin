from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def api_health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
