from collections import Counter, defaultdict
from datetime import date, timedelta

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.modules.admin.repository import AdminRepository
from app.modules.admin.scenario_analytics import ScenarioAnalyticsBuilder
from app.modules.admin.schemas import (
    GroupImportRequest,
    RuleTemplateUpdateRequest,
    StudentImportRequest,
    TeacherImportRequest,
)
from app.modules.auth.models import StudentProfile, TeacherProfile, User
from app.modules.groups.invite import generate_unique_invite_code
from app.modules.groups.models import Group, GroupMember
from app.modules.records.models import CheckinRecord
from app.modules.tasks.lifecycle import TaskLifecycleService
from app.modules.tasks.models import CheckinTask
from app.shared.enums import ExceptionType, RecordStatus, UserType

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
DEFAULT_STUDENT_PASSWORD = "123456"


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminRepository(db)
        self.task_lifecycle = TaskLifecycleService(db)

    def _ensure_tasks_fresh(self, tasks: list[CheckinTask]) -> None:
        self.task_lifecycle.refresh_tasks(tasks)

    def dashboard(self) -> dict:
        students = self.repository.list_students()
        tasks = self.repository.list_tasks()
        self._ensure_tasks_fresh(tasks)
        exceptions = self.repository.list_exceptions()
        submitted_count = sum(
            len(
                {
                    record.student_profile_id
                    for record in self.repository.list_records_for_task(task.id)
                }
            )
            for task in tasks
        )
        expected_count = sum(
            len(self.repository.list_students_for_task(task.id)) for task in tasks
        )
        completion_rate = self._completion_rate(submitted_count, expected_count)
        pending_appeal_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        return {
            "student_count": len(students),
            "task_count": len(tasks),
            "exception_count": len(exceptions),
            "pending_appeal_count": pending_appeal_count,
            "completion_rate": completion_rate,
        }

    def scenario_analytics(
        self,
        scenario: str = "all",
        range_key: str = "week",
        college: str | None = None,
        major: str | None = None,
        class_name: str | None = None,
        grade: str | None = None,
    ) -> dict:
        return ScenarioAnalyticsBuilder(self.db, self.repository).build(
            scenario=scenario,
            range_key=range_key,
            college=college,
            major=major,
            class_name=class_name,
            grade=grade,
        )

    def analytics(self) -> dict:
        students = self.repository.list_students()
        groups = self.repository.list_groups()
        tasks = self.repository.list_tasks()
        exceptions = self.repository.list_exceptions()
        task_items = [self._task_item(task) for task in tasks]
        records_by_task = {
            task.id: self.repository.list_records_for_task(task.id) for task in tasks
        }
        expected_total = sum(item["student_count"] for item in task_items)
        submitted_total = sum(item["submitted_count"] for item in task_items)
        pending_appeal_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        return {
            "summary": {
                "expected_students": len(students),
                "checked_students": len(
                    {
                        record.student_profile_id
                        for records in records_by_task.values()
                        for record in records
                    }
                ),
                "completion_rate": self._completion_rate(submitted_total, expected_total),
                "exception_count": len(exceptions),
                "pending_appeal_count": pending_appeal_count,
                "task_count": len(tasks),
                "covered_class_count": len(groups),
                "checkin_count": sum(len(records) for records in records_by_task.values()),
            },
            "trend": self._analytics_trend(tasks, records_by_task),
            "college_rates": self._analytics_college_rates(students, tasks, records_by_task),
            "exception_types": self._analytics_exception_types(exceptions),
            "class_exception_ranking": self._analytics_class_exception_ranking(exceptions),
            "overview": {
                "task_count": len(tasks),
                "covered_class_count": len(groups),
                "covered_student_count": len(students),
                "checkin_count": sum(len(records) for records in records_by_task.values()),
                "exception_count": len(exceptions),
                "appeal_count": pending_appeal_count,
            },
        }

    def org_tree(self) -> list[dict]:
        groups = self.repository.list_groups()
        return [
            {"id": group.id, "name": group.name, "type": group.group_type}
            for group in groups
        ]

    def import_students(self, payload: StudentImportRequest) -> dict:
        created = 0
        for item in payload.students:
            existing = self.repository.find_student_by_student_no(item.student_no)
            if existing is not None:
                continue
            password = item.password or DEFAULT_STUDENT_PASSWORD
            user = User(
                account=item.student_no,
                phone=item.phone,
                password_hash=pwd_context.hash(password),
                user_type=UserType.STUDENT.value,
                display_name=item.name,
            )
            profile = StudentProfile(
                user=user,
                student_no=item.student_no,
                name=item.name,
                phone=item.phone,
                college=item.college,
                major=item.major,
                grade=item.grade,
                class_name=item.class_name,
                dormitory=item.dormitory,
                dormitory_longitude=item.dormitory_longitude,
                dormitory_latitude=item.dormitory_latitude,
                dormitory_address=item.dormitory_address,
                internship_company=item.internship_company,
                internship_longitude=item.internship_longitude,
                internship_latitude=item.internship_latitude,
                internship_address=item.internship_address,
                activated=True,
                status="active",
            )
            self.repository.add(user)
            self.repository.add(profile)
            self.repository.flush()
            group = self.repository.get_group_by_name(item.class_name)
            if group is None:
                group = Group(
                    name=item.class_name,
                    group_type="class",
                    invite_code=generate_unique_invite_code(self.db),
                )
                self.repository.add(group)
                self.repository.flush()
            self.repository.add_group_member(
                GroupMember(group_id=group.id, student_profile_id=profile.id)
            )
            created += 1
        self.repository.commit()
        return {"imported": created}

    def import_teachers(self, payload: TeacherImportRequest) -> dict:
        created = 0
        for item in payload.teachers:
            user = User(
                account=item.teacher_no,
                phone=item.phone,
                password_hash="",
                user_type="teacher",
                display_name=item.name,
            )
            profile = TeacherProfile(
                user=user,
                teacher_no=item.teacher_no,
                name=item.name,
                phone=item.phone,
                department=item.department,
            )
            self.repository.add(user)
            self.repository.add(profile)
            created += 1
        self.repository.commit()
        return {"imported": created}

    def import_groups(self, payload: GroupImportRequest) -> dict:
        created = 0
        for item in payload.groups:
            if self.repository.get_group_by_name(item.name) is None:
                self.repository.add(
                    Group(
                        name=item.name,
                        group_type=item.group_type,
                        invite_code=generate_unique_invite_code(self.db),
                    )
                )
                created += 1
        self.repository.commit()
        return {"imported": created}

    def list_students(self) -> dict:
        face_student_ids = self.repository.list_active_face_student_ids()
        items = [
            self._student_item(profile, face_student_ids)
            for profile in self.repository.list_students()
        ]
        return {"items": items, "total": len(items)}

    def list_teachers(self) -> dict:
        items = [
            self._teacher_item(profile) for profile in self.repository.list_teachers()
        ]
        return {"items": items, "total": len(items)}

    def list_groups(self) -> dict:
        items = [self._group_item(group) for group in self.repository.list_groups()]
        return {"items": items, "total": len(items)}

    def list_checkin_types(self) -> dict:
        items = [
            {"id": item.id, "name": item.name, "description": item.description}
            for item in self.repository.list_checkin_types()
        ]
        return {"items": items, "total": len(items)}

    def list_rule_templates(self) -> dict:
        items = [
            {
                "id": template.id,
                "name": template.name,
                "type_id": template.type_id,
                "rules_snapshot": template.rules_jsonb,
            }
            for template in self.repository.list_rule_templates()
        ]
        return {"items": items, "total": len(items)}

    def update_rule_template(
        self, template_id: int, payload: RuleTemplateUpdateRequest
    ) -> dict:
        template = self.repository.get_rule_template(template_id)
        if template is None:
            raise ValueError("规则模板不存在")
        template.name = payload.name
        template.rules_jsonb = payload.rules_snapshot
        self.repository.commit()
        return {"updated": True, "id": template.id}

    def list_tasks(self) -> dict:
        tasks = self.repository.list_tasks()
        self._ensure_tasks_fresh(tasks)
        items = [self._task_item(task) for task in tasks]
        return {"items": items, "total": len(items)}

    def list_exceptions(self) -> dict:
        items = [
            self._exception_item(item) for item in self.repository.list_exceptions()
        ]
        return {"items": items, "total": len(items)}

    def _student_item(
        self, profile: StudentProfile, face_student_ids: set[int] | None = None
    ) -> dict:
        face_student_ids = face_student_ids or set()
        groups = self.repository.list_groups_for_student(profile.id)
        teachers = self.repository.list_teachers_for_student(profile.id)
        return {
            "id": profile.id,
            "student_no": profile.student_no,
            "name": profile.name,
            "phone": profile.phone,
            "college": profile.college,
            "major": profile.major,
            "grade": profile.grade,
            "class_name": profile.class_name,
            "dormitory": profile.dormitory,
            "dormitory_longitude": profile.dormitory_longitude,
            "dormitory_latitude": profile.dormitory_latitude,
            "dormitory_address": profile.dormitory_address,
            "dormitory_location_configured": (
                profile.dormitory_longitude is not None
                and profile.dormitory_latitude is not None
            ),
            "internship_company": profile.internship_company,
            "internship_longitude": profile.internship_longitude,
            "internship_latitude": profile.internship_latitude,
            "internship_address": profile.internship_address,
            "internship_location_configured": (
                profile.internship_longitude is not None
                and profile.internship_latitude is not None
            ),
            "activated": profile.activated,
            "status": profile.status,
            "user_id": profile.user_id,
            "face_registered": profile.id in face_student_ids,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "teacher_ids": [teacher.id for teacher in teachers],
            "teacher_names": [teacher.name for teacher in teachers],
        }

    def _teacher_item(self, profile: TeacherProfile) -> dict:
        groups = self.repository.list_groups_for_teacher(profile.id)
        students = self.repository.list_students_for_teacher(profile.id)
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "account": profile.user.account,
            "teacher_no": profile.teacher_no,
            "name": profile.name,
            "phone": profile.phone,
            "department": profile.department,
            "group_ids": [group.id for group in groups],
            "groups": [group.name for group in groups],
            "group_names": [group.name for group in groups],
            "student_count": len(students),
        }

    def _group_item(self, group: Group) -> dict:
        students = self.repository.list_students_for_group(group.id)
        teachers = self.repository.list_teachers_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "student_count": len(students),
            "teacher_count": len(teachers),
            "teacher_ids": [teacher.id for teacher in teachers],
            "teacher_names": [teacher.name for teacher in teachers],
            "task_count": len(tasks),
        }

    def _task_item(self, task: CheckinTask) -> dict:
        groups = self.repository.list_groups_for_task(task.id)
        records = self.repository.list_records_for_task(task.id)
        exceptions = self.repository.list_exceptions_for_task(task.id)
        students = self.repository.list_students_for_task(task.id)
        teacher = self.repository.get_teacher_profile_by_user_id(task.teacher_user_id)
        submitted_count = len({record.student_profile_id for record in records})
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "teacher_user_id": task.teacher_user_id,
            "teacher_id": teacher.id if teacher else None,
            "teacher_name": teacher.name if teacher else None,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "student_count": len(students),
            "submitted_count": submitted_count,
            "completion_rate": self._completion_rate(submitted_count, len(students)),
            "exception_count": len(exceptions),
            "pending_review_count": sum(
                1
                for item in exceptions
                if item.status == RecordStatus.PENDING_REVIEW.value
            ),
        }

    def _exception_item(self, item) -> dict:
        student = self.repository.get_student_profile(item.student_profile_id)
        task = self.repository.get_task(item.task_id)
        record = self.repository.get_record(item.record_id)
        groups = self.repository.list_groups_for_task(item.task_id)
        teacher = (
            self.repository.get_teacher_profile_by_user_id(task.teacher_user_id)
            if task
            else None
        )
        return {
            "id": item.id,
            "record_id": item.record_id,
            "task_id": item.task_id,
            "student_id": item.student_profile_id,
            "student_name": student.name if student else None,
            "student_no": student.student_no if student else None,
            "task_title": task.title if task else None,
            "teacher_id": teacher.id if teacher else None,
            "teacher_name": teacher.name if teacher else None,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups],
            "status": item.status,
            "record_status": record.status if record else None,
            "submitted_at": record.submitted_at.isoformat() if record else None,
            "exception_types": item.exception_types_jsonb,
            "messages": item.messages_jsonb,
        }

    def _completion_rate(self, submitted_count: int, expected_count: int) -> int:
        if expected_count == 0:
            return 0
        return round(submitted_count / expected_count * 100)

    def _analytics_trend(
        self,
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
    ) -> list[dict]:
        today = date.today()
        days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        result = []
        for day in days:
            day_tasks = [task for task in tasks if task.starts_at.date() == day]
            expected = sum(
                len(self.repository.list_students_for_task(task.id)) for task in day_tasks
            )
            checked = sum(
                len({record.student_profile_id for record in records_by_task.get(task.id, [])})
                for task in day_tasks
            )
            result.append(
                {
                    "date": day.isoformat(),
                    "label": f"{day.month}/{day.day}",
                    "expected": expected,
                    "checked": checked,
                    "completion_rate": self._completion_rate(checked, expected),
                }
            )
        return result

    def _analytics_college_rates(
        self,
        students: list[StudentProfile],
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
    ) -> list[dict]:
        student_by_id = {student.id: student for student in students}
        expected_by_college: Counter[str] = Counter()
        checked_by_college: Counter[str] = Counter()
        for task in tasks:
            for student in self.repository.list_students_for_task(task.id):
                expected_by_college[student.college or "未设置学院"] += 1
            checked_student_ids = {
                record.student_profile_id for record in records_by_task.get(task.id, [])
            }
            for student_id in checked_student_ids:
                student = student_by_id.get(student_id)
                if student is not None:
                    checked_by_college[student.college or "未设置学院"] += 1
        if not expected_by_college:
            expected_by_college.update(
                Counter(student.college or "未设置学院" for student in students)
            )
        rows = [
            {
                "name": college,
                "expected": expected,
                "checked": checked_by_college[college],
                "completion_rate": self._completion_rate(
                    checked_by_college[college], expected
                ),
            }
            for college, expected in expected_by_college.items()
        ]
        return sorted(rows, key=lambda item: item["completion_rate"], reverse=True)[:6]

    def _analytics_exception_types(self, exceptions: list) -> list[dict]:
        label_map = {
            ExceptionType.MISSING.value: "未打卡",
            ExceptionType.LATE.value: "迟到",
            ExceptionType.LOCATION_ERROR.value: "位置异常",
            ExceptionType.DYNAMIC_CODE_ERROR.value: "验证码异常",
            ExceptionType.FACE_FAILED.value: "人脸失败",
            ExceptionType.SAFETY_RISK.value: "安全风险",
            ExceptionType.LOG_MISSING.value: "缺卡",
            ExceptionType.APPEAL_PENDING.value: "申诉中",
        }
        counter: Counter[str] = Counter()
        for item in exceptions:
            for exception_type in item.exception_types_jsonb or ["unknown"]:
                counter[label_map.get(exception_type, str(exception_type))] += 1
        total = sum(counter.values())
        if total == 0:
            return []
        return [
            {
                "label": label,
                "value": value,
                "percent": round(value / total * 100, 1),
            }
            for label, value in counter.most_common()
        ]

    def _analytics_class_exception_ranking(self, exceptions: list) -> list[dict]:
        count_by_group: Counter[str] = Counter()
        student_ids_by_group: dict[str, set[int]] = defaultdict(set)
        for item in exceptions:
            groups = self.repository.list_groups_for_task(item.task_id)
            group_names = [group.name for group in groups] or ["未关联班级"]
            for group_name in group_names:
                count_by_group[group_name] += 1
                student_ids_by_group[group_name].add(item.student_profile_id)
        rows = []
        for group_name, count in count_by_group.most_common(5):
            student_count = len(student_ids_by_group[group_name])
            group = self.repository.get_group_by_name(group_name)
            total_students = (
                len(self.repository.list_students_for_group(group.id)) if group else count
            )
            rows.append(
                {
                    "rank": len(rows) + 1,
                    "class_name": group_name,
                    "exception_count": count,
                    "exception_student_count": student_count,
                    "exception_rate": self._completion_rate(student_count, total_students),
                }
            )
        return rows
