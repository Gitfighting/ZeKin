"""种子数据：账号 + 班级群组 + 任务模板（可组合签到方式）。

设计依据：docs/checkin-task-template-design.md
- 群组（Group）为任务发布单位：班级 / 寝室班 / 课程班 / 实习班
- 模板（RuleTemplate）差异仅在 verificationRule.methods 组合与各方式参数
- DEFAULT_RULE_SNAPSHOT 为查寝默认（位置签到），保持向后兼容
"""
from copy import deepcopy

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import AdminProfile, StudentProfile, TeacherProfile, User
from app.modules.checkin_types.models import CheckinType
from app.modules.groups.invite import generate_unique_invite_code
from app.modules.groups.models import Group, GroupMember, GroupTeacher
from app.modules.rule_templates.models import RuleTemplate
from app.shared.enums import UserType
from app.shared.student_default_locations import (
    DEFAULT_DORMITORY_ADDRESS,
    DEFAULT_DORMITORY_LABEL,
    DEFAULT_DORMITORY_LATITUDE,
    DEFAULT_DORMITORY_LONGITUDE,
    DEFAULT_INTERNSHIP_ADDRESS,
    DEFAULT_INTERNSHIP_COMPANY,
    DEFAULT_INTERNSHIP_LATITUDE,
    DEFAULT_INTERNSHIP_LONGITUDE,
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
DEFAULT_PASSWORD = "123456"
DEFAULT_STUDENT_PASSWORD = DEFAULT_PASSWORD
DEFAULT_TEACHER_ACCOUNT = "20261001"
DEFAULT_TEACHER_PASSWORD = DEFAULT_PASSWORD

DEMO_STUDENTS = [
    ("20260001", "张三", "13800000001"),
    ("20260002", "李四", "13800000004"),
    ("20260003", "王五", "13800000005"),
]

# ─────────────────────────────────────────────────────────────
# 默认模板（位置签到，向后兼容旧 schema）
# ─────────────────────────────────────────────────────────────

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
    "verificationRule": {
        "methods": ["location"],
        "location": {
            "placeName": "3号宿舍楼",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 300,
        },
    },
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

# ─────────────────────────────────────────────────────────────
# 可组合签到方式模板（新 schema：verificationRule.methods 自由组合）
# ─────────────────────────────────────────────────────────────

DORM_RULE_SNAPSHOT = {
    "timeRule": {"startTime": "21:30", "endTime": "23:00", "allowLate": False, "allowMakeup": True},
    "locationRule": {
        "mode": "student_dorm",
        "placeName": "学生寝室",
        "radius": 200,
        "allowExceptionSubmit": True,
    },
    "verificationRule": {
        "methods": ["face", "location"],
        "order": ["face", "location"],
        "face": {"tolerance": 0.6, "detectionModel": "hog"},
        "location": {
            "mode": "student_dorm",
            "radius": 200,
        },
    },
    "reviewRule": {"mode": "exception_only"},
    "reminderRule": {"beforeStartMinutes": 10, "beforeEndMinutes": 5},
}

COURSE_RULE_SNAPSHOT = {
    "timeRule": {"startTime": "08:00", "endTime": "08:15", "allowLate": True, "allowMakeup": False},
    "verificationRule": {
        "methods": ["qr_code", "face"],
        "order": ["qr_code", "face"],
        "qr_code": {"refreshIntervalSeconds": 60, "expireSeconds": 120, "allowReuse": False},
        "face": {"tolerance": 0.6, "detectionModel": "hog"},
    },
    "reviewRule": {"mode": "exception_only"},
    "reminderRule": {"beforeStartMinutes": 5, "beforeEndMinutes": 2},
}

INTERNSHIP_RULE_SNAPSHOT = {
    "timeRule": {"startTime": "08:30", "endTime": "10:00", "allowLate": True, "allowMakeup": True},
    "locationRule": {
        "mode": "student_internship",
        "placeName": "实习单位",
        "radius": 500,
        "allowExceptionSubmit": True,
    },
    "verificationRule": {
        "methods": ["face", "location", "attachment"],
        "order": ["face", "location", "attachment"],
        "face": {"tolerance": 0.65, "detectionModel": "hog"},
        "location": {
            "mode": "student_internship",
            "radius": 500,
        },
        "attachment": {
            "required": True,
            "acceptTypes": ["text", "image"],
            "minTextLength": 20,
            "maxFileCount": 3,
            "maxFileSizeMb": 10,
            "label": "今日工作日志",
        },
    },
    "reviewRule": {"mode": "all"},
    "reminderRule": {"beforeStartMinutes": 15, "beforeEndMinutes": 10},
}


# ─────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────


def seed_reference_data(db: Session) -> None:
    _ensure_admin(db)
    teacher = _ensure_teacher(db)

    # 默认班级（id=1），与导入学生 class_name 对应，保持既有行为
    default_type = _ensure_checkin_type(db, "晚间查寝", "宿舍晚间查寝")
    default_group = _ensure_group(db, "软件2601", "class")
    _ensure_group_teacher(db, default_group.id, teacher.teacher_profile.id)
    _ensure_rule_template(db, "晚间查寝模板", default_type.id, teacher.id, DEFAULT_RULE_SNAPSHOT)
    _ensure_demo_students(db, default_group)
    _apply_default_student_locations(db)

    # 演示用：三类班级群组 + 三套可组合签到模板
    dorm_type = _ensure_checkin_type(db, "查寝打卡", "宿舍查寝场景")
    course_type = _ensure_checkin_type(db, "课程打卡", "课程出勤场景")
    internship_type = _ensure_checkin_type(db, "实习打卡", "实习日报场景")

    _ensure_group(db, "3号寝室班", "dorm")
    _ensure_group(db, "软工导论A202班", "course")
    _ensure_group(db, "XX公司实习班", "internship")

    _ensure_rule_template(db, "晚间查寝模板（人脸+位置）", dorm_type.id, teacher.id, DORM_RULE_SNAPSHOT)
    _ensure_rule_template(db, "课程签到模板（二维码+人脸）", course_type.id, teacher.id, COURSE_RULE_SNAPSHOT)
    _ensure_rule_template(db, "实习日报模板（人脸+位置+附件）", internship_type.id, teacher.id, INTERNSHIP_RULE_SNAPSHOT)

    _sync_demo_passwords(db)
    db.commit()


def _sync_demo_passwords(db: Session) -> None:
    """每次 seed 都将演示账号密码同步为 DEFAULT_PASSWORD，避免改密后旧库无法登录。"""
    demo_accounts = [
        ("admin", DEFAULT_PASSWORD),
        (DEFAULT_TEACHER_ACCOUNT, DEFAULT_TEACHER_PASSWORD),
        *[(student_no, DEFAULT_STUDENT_PASSWORD) for student_no, _, _ in DEMO_STUDENTS],
    ]
    for account, password in demo_accounts:
        user = db.scalar(select(User).where(User.account == account))
        if user is not None:
            user.password_hash = pwd_context.hash(password)

    legacy_teacher = db.scalar(select(User).where(User.account == "teacher"))
    if legacy_teacher is not None:
        legacy_teacher.password_hash = pwd_context.hash(DEFAULT_TEACHER_PASSWORD)


# ─────────────────────────────────────────────────────────────
# 账号
# ─────────────────────────────────────────────────────────────


def _ensure_admin(db: Session) -> None:
    if db.scalar(select(User).where(User.account == "admin")) is not None:
        return
    user = User(
        account="admin",
        phone="13800000000",
        password_hash=pwd_context.hash(DEFAULT_PASSWORD),
        user_type=UserType.ADMIN.value,
        display_name="系统管理员",
    )
    db.add(user)
    db.flush()
    db.add(AdminProfile(user_id=user.id, department="学工处", scope="全校"))


def _ensure_teacher(db: Session) -> User:
    teacher = db.scalar(select(User).where(User.account == DEFAULT_TEACHER_ACCOUNT))
    if teacher is not None:
        return teacher

    # 兼容旧种子：account=teacher → 20261001
    legacy = db.scalar(select(User).where(User.account == "teacher"))
    if legacy is not None:
        legacy.account = DEFAULT_TEACHER_ACCOUNT
        if legacy.teacher_profile is not None:
            legacy.teacher_profile.teacher_no = DEFAULT_TEACHER_ACCOUNT
        db.flush()
        return legacy

    teacher = User(
        account=DEFAULT_TEACHER_ACCOUNT,
        phone="13800000002",
        password_hash=pwd_context.hash(DEFAULT_TEACHER_PASSWORD),
        user_type=UserType.TEACHER.value,
        display_name="李老师",
    )
    db.add(teacher)
    db.flush()
    db.add(
        TeacherProfile(
            user_id=teacher.id,
            teacher_no=DEFAULT_TEACHER_ACCOUNT,
            name="李老师",
            phone="13800000002",
            department="软件学院",
        )
    )
    db.flush()
    return teacher


def _apply_default_student_locations(db: Session) -> None:
    """为全部学生写入默认寝室/实习坐标（查寝、实习打卡按档案校验）。"""
    profiles = db.scalars(select(StudentProfile)).all()
    for profile in profiles:
        profile.dormitory = DEFAULT_DORMITORY_LABEL
        profile.dormitory_longitude = DEFAULT_DORMITORY_LONGITUDE
        profile.dormitory_latitude = DEFAULT_DORMITORY_LATITUDE
        profile.dormitory_address = DEFAULT_DORMITORY_ADDRESS
        profile.internship_company = DEFAULT_INTERNSHIP_COMPANY
        profile.internship_longitude = DEFAULT_INTERNSHIP_LONGITUDE
        profile.internship_latitude = DEFAULT_INTERNSHIP_LATITUDE
        profile.internship_address = DEFAULT_INTERNSHIP_ADDRESS


def _ensure_demo_students(db: Session, group: Group) -> None:
    """预置可登录学生（学号即账号，默认密码 123456）。"""
    for student_no, name, phone in DEMO_STUDENTS:
        existing = db.scalar(select(StudentProfile).where(StudentProfile.student_no == student_no))
        if existing is not None:
            continue
        user = User(
            account=student_no,
            phone=phone,
            password_hash=pwd_context.hash(DEFAULT_STUDENT_PASSWORD),
            user_type=UserType.STUDENT.value,
            display_name=name,
        )
        profile = StudentProfile(
            user=user,
            student_no=student_no,
            name=name,
            phone=phone,
            college="软件学院",
            major="软件工程",
            grade="2026",
            class_name=group.name,
            dormitory=DEFAULT_DORMITORY_LABEL,
            dormitory_longitude=DEFAULT_DORMITORY_LONGITUDE,
            dormitory_latitude=DEFAULT_DORMITORY_LATITUDE,
            dormitory_address=DEFAULT_DORMITORY_ADDRESS,
            internship_company=DEFAULT_INTERNSHIP_COMPANY,
            internship_longitude=DEFAULT_INTERNSHIP_LONGITUDE,
            internship_latitude=DEFAULT_INTERNSHIP_LATITUDE,
            internship_address=DEFAULT_INTERNSHIP_ADDRESS,
            activated=True,
            status="active",
        )
        db.add(user)
        db.add(profile)
        db.flush()
        db.add(GroupMember(group_id=group.id, student_profile_id=profile.id))


# ─────────────────────────────────────────────────────────────
# 基础数据
# ─────────────────────────────────────────────────────────────


def _ensure_checkin_type(db: Session, name: str, description: str) -> CheckinType:
    checkin_type = db.scalar(select(CheckinType).where(CheckinType.name == name))
    if checkin_type is not None:
        return checkin_type
    checkin_type = CheckinType(name=name, description=description)
    db.add(checkin_type)
    db.flush()
    return checkin_type


def _ensure_group(db: Session, name: str, group_type: str) -> Group:
    group = db.scalar(select(Group).where(Group.name == name))
    if group is not None:
        if not group.invite_code:
            group.invite_code = generate_unique_invite_code(db)
            db.flush()
        return group
    group = Group(
        name=name,
        group_type=group_type,
        invite_code=generate_unique_invite_code(db),
    )
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


def _ensure_rule_template(
    db: Session, name: str, type_id: int, created_by_user_id: int, rules: dict
) -> None:
    existing = db.scalar(select(RuleTemplate).where(RuleTemplate.name == name))
    if existing is None:
        db.add(
            RuleTemplate(
                name=name,
                type_id=type_id,
                created_by_user_id=created_by_user_id,
                status="active",
                usage_count=0,
                rules_jsonb=deepcopy(rules),
            )
        )


if __name__ == "__main__":
    from app.core.database import SessionLocal, engine
    from app.core.schema_patch import ensure_student_location_columns

    ensure_student_location_columns(engine)
    with SessionLocal() as session:
        seed_reference_data(session)
    print("Seed completed. Demo account passwords synced to 123456.")
