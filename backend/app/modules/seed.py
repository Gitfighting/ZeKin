from copy import deepcopy

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import AdminProfile, TeacherProfile, User
from app.modules.checkin_types.models import CheckinType
from app.modules.groups.models import Group, GroupTeacher
from app.modules.rule_templates.models import RuleTemplate
from app.shared.enums import UserType

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DEFAULT_RULE_SNAPSHOT = {
    "timeRule": {
        "mode": "single",
        "startTime": "21:30",
        "endTime": "22:30",
        "allowLate": False,
        "allowMakeup": True,
        "makeupNeedReview": True,
    },
    "locationRule": {
        "mode": "fixed_area",
        "placeName": "3号宿舍楼",
        "longitude": 120.000001,
        "latitude": 30.000001,
        "radius": 300,
        "allowExceptionSubmit": True,
    },
    "verificationRule": {"methods": ["location"]},
    "submitRule": {
        "fields": [
            {
                "key": "remark",
                "label": "情况说明",
                "type": "textarea",
                "required": False,
            }
        ]
    },
    "reviewRule": {"mode": "exception_only"},
    "reminderRule": {
        "beforeStartMinutes": 10,
        "beforeEndMinutes": 5,
        "notifyTeacherAfterEnd": True,
    },
    "faceRule": {"enabled": False, "provider": "placeholder"},
}


def seed_reference_data(db: Session) -> None:
    _ensure_admin(db)
    teacher = _ensure_teacher(db)
    checkin_type = _ensure_checkin_type(db)
    group = _ensure_group(db)
    _ensure_group_teacher(db, group.id, teacher.teacher_profile.id)
    _ensure_rule_template(db, checkin_type.id, teacher.id)
    db.commit()


def _ensure_admin(db: Session) -> None:
    if db.scalar(select(User).where(User.account == "admin")) is not None:
        return
    user = User(
        account="admin",
        phone="13800000000",
        password_hash=pwd_context.hash("admin123456"),
        user_type=UserType.ADMIN.value,
        display_name="系统管理员",
    )
    db.add(user)
    db.flush()
    db.add(AdminProfile(user_id=user.id, department="学工处", scope="全校"))


def _ensure_teacher(db: Session) -> User:
    teacher = db.scalar(select(User).where(User.account == "teacher"))
    if teacher is not None:
        return teacher
    teacher = User(
        account="teacher",
        phone="13800000002",
        password_hash=pwd_context.hash("teacher123456"),
        user_type=UserType.TEACHER.value,
        display_name="李老师",
    )
    db.add(teacher)
    db.flush()
    db.add(
        TeacherProfile(
            user_id=teacher.id,
            teacher_no="T2026001",
            name="李老师",
            phone="13800000002",
            department="软件学院",
        )
    )
    db.flush()
    return teacher


def _ensure_checkin_type(db: Session) -> CheckinType:
    checkin_type = db.scalar(select(CheckinType).where(CheckinType.name == "晚间查寝"))
    if checkin_type is not None:
        return checkin_type
    checkin_type = CheckinType(name="晚间查寝", description="宿舍晚间查寝")
    db.add(checkin_type)
    db.flush()
    return checkin_type


def _ensure_group(db: Session) -> Group:
    group = db.scalar(select(Group).where(Group.name == "软件2601"))
    if group is not None:
        return group
    group = Group(name="软件2601", group_type="class")
    db.add(group)
    db.flush()
    return group


def _ensure_group_teacher(db: Session, group_id: int, teacher_profile_id: int) -> None:
    existing = db.scalar(
        select(GroupTeacher).where(
            GroupTeacher.group_id == group_id,
            GroupTeacher.teacher_profile_id == teacher_profile_id,
        )
    )
    if existing is None:
        db.add(GroupTeacher(group_id=group_id, teacher_profile_id=teacher_profile_id))


def _ensure_rule_template(db: Session, type_id: int, created_by_user_id: int) -> None:
    existing = db.scalar(select(RuleTemplate).where(RuleTemplate.name == "晚间查寝模板"))
    if existing is None:
        db.add(
            RuleTemplate(
                name="晚间查寝模板",
                type_id=type_id,
                created_by_user_id=created_by_user_id,
                status="active",
                usage_count=0,
                rules_jsonb=deepcopy(DEFAULT_RULE_SNAPSHOT),
            )
        )
