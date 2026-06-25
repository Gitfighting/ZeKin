from fastapi import APIRouter, Depends

from app.modules.admin.router import get_admin_service, require_admin
from app.modules.auth.models import User
from app.shared.response import success_response

router = APIRouter(tags=["statistics"])


@router.get("/api/admin/statistics")
def admin_statistics(_: User = Depends(require_admin), service=Depends(get_admin_service)):
    return success_response(service.dashboard())
