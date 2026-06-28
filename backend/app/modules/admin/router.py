from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.schemas import (
    GroupImportRequest,
    RuleTemplateUpdateRequest,
    StudentImportRequest,
    TeacherImportRequest,
)
from app.modules.admin.service import AdminService
from app.modules.auth.router import get_current_user
from app.modules.auth.models import User
from app.shared.enums import UserType
from app.shared.response import success_response

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    return current_user


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)


@router.get("/dashboard")
def dashboard(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.dashboard())


@router.get("/analytics")
def analytics(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.analytics())


@router.get("/analytics/scenario")
def scenario_analytics(
    scenario: str = Query("all"),
    range: str = Query("week", alias="range"),
    college: str | None = Query(None),
    major: str | None = Query(None),
    class_name: str | None = Query(None),
    grade: str | None = Query(None),
    _: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return success_response(
        service.scenario_analytics(
            scenario=scenario,
            range_key=range,
            college=college,
            major=major,
            class_name=class_name,
            grade=grade,
        )
    )


@router.get("/org/tree")
def org_tree(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.org_tree())


@router.post("/students/import")
def import_students(
    payload: StudentImportRequest,
    _: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return success_response(service.import_students(payload))


@router.post("/teachers/import")
def import_teachers(
    payload: TeacherImportRequest,
    _: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return success_response(service.import_teachers(payload))


@router.post("/groups/import")
def import_groups(
    payload: GroupImportRequest,
    _: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return success_response(service.import_groups(payload))


@router.get("/students")
def students(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_students())


@router.get("/teachers")
def teachers(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_teachers())


@router.get("/groups")
def groups(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_groups())


@router.get("/checkin-types")
def checkin_types(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_checkin_types())


@router.get("/rule-templates")
def rule_templates(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_rule_templates())


@router.post("/rule-templates/{template_id}")
def update_rule_template(
    template_id: int,
    payload: RuleTemplateUpdateRequest,
    _: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    try:
        result = service.update_rule_template(template_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return success_response(result)


@router.get("/tasks")
def tasks(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_tasks())


@router.get("/exceptions")
def exceptions(_: User = Depends(require_admin), service: AdminService = Depends(get_admin_service)):
    return success_response(service.list_exceptions())
