from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User
from app.modules.exceptions.models import CheckinException
from app.modules.groups.invite import generate_unique_invite_code
from app.modules.groups.models import Group, GroupMember, GroupTeacher
from app.modules.messages.models import Message
from app.modules.records.models import CheckinRecord
from app.modules.tasks.models import (
    CheckinTask,
    CheckinTaskGroup,
    CheckinTaskOccurrence,
)
from app.modules.tasks.lifecycle import TaskLifecycleService
from app.modules.tasks.repository import TaskRepository
from app.modules.qr_code.service import generate_token, render_qr_data_url
from app.modules.tasks.schemas import CreateTaskRequest
from app.shared.attendance import resolve_attendance_status
from app.shared.datetime_utils import as_beijing_datetime, get_beijing_now, to_beijing_iso
from app.shared.enums import (
    AttendanceStatus,
    RecordStatus,
    ScheduleMode,
    TaskStatus,
)

MAX_MATERIALIZED_DAYS = 90

PUBLISHED_TASK_STATUSES = frozenset({
    TaskStatus.NOT_STARTED.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.ENDED.value,
})
CHECKED_IN_ATTENDANCE_STATUSES = frozenset({
    AttendanceStatus.PRESENT.value,
    AttendanceStatus.LATE.value,
    AttendanceStatus.EARLY_LEAVE.value,
})

logger = logging.getLogger("zeKin.tasks")

CHECKIN_METHOD_LABELS = {
    "face": "人脸识别",
    "location": "地理位置",
    "qr_code": "二维码",
    "checkin_code": "签到码",
    "attachment": "附件/日志",
    "gesture": "手势签到",
}


def _resolve_task_method_labels(rules: dict | None) -> list[str]:
    snapshot = rules or {}
    verification = snapshot.get("verificationRule") or {}
    methods = verification.get("methods") or []
    labels = [
        CHECKIN_METHOD_LABELS.get(str(method), str(method))
        for method in methods
        if method
    ]
    if labels:
        return labels

    legacy: list[str] = []
    if (snapshot.get("faceRule") or {}).get("enabled"):
        legacy.append(CHECKIN_METHOD_LABELS["face"])
    location_rule = snapshot.get("locationRule") or {}
    if location_rule.get("mode") not in (None, "", "none"):
        legacy.append(CHECKIN_METHOD_LABELS["location"])
    return legacy


def _format_task_notify_message(
    task: CheckinTask, *, group_names: list[str] | None = None
) -> tuple[str, str]:
    window = (
        f"{task.starts_at.strftime('%m-%d %H:%M')} - "
        f"{task.ends_at.strftime('%H:%M')}"
    )
    methods = _resolve_task_method_labels(task.rules_snapshot_jsonb)
    methods_text = "、".join(methods) if methods else "按任务要求"
    group_text = " / ".join(group_names) if group_names else ""
    description = (task.description or "").strip() or (
        "您有一条新的签到任务，请在规定时间内完成签到。"
    )
    lines = [
        f"课群名称：{group_text}" if group_text else None,
        f"任务说明：{description}",
        f"打卡方式：{methods_text}",
        f"打卡时间：{window}",
    ]
    content = "\n".join(line for line in lines if line)
    return task.title, content


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TaskRepository(db)
        self.lifecycle = TaskLifecycleService(db)

    def _ensure_task_fresh(self, task: CheckinTask) -> None:
        if self.lifecycle.refresh_task(task):
            self.repository.commit()

    def _ensure_tasks_fresh(self, tasks: list[CheckinTask]) -> None:
        self._process_scheduled_publishes()
        self.lifecycle.refresh_tasks(tasks)

    def _parse_task_datetime(self, value: str) -> datetime:
        normalized = value.strip().replace(" ", "T")
        if "+" not in normalized and len(normalized) >= 16:
            normalized = f"{normalized}+08:00"
        return datetime.fromisoformat(normalized)

    def _process_scheduled_publishes(self) -> None:
        now = get_beijing_now()
        pending = self.repository.list_tasks_pending_scheduled_publish(now)
        if not pending:
            return
        for task in pending:
            self._apply_publish(task)
        self.repository.commit()

    def create_task(self, *, teacher_user: User, payload: CreateTaskRequest) -> dict:
        self._require_teacher_group_scope(teacher_user, payload.group_ids)
        schedule_mode = ScheduleMode(payload.schedule_mode)
        is_recurring = schedule_mode == ScheduleMode.RECURRING
        scheduled_publish_at = None
        if payload.scheduled_publish_at:
            scheduled_publish_at = self._parse_task_datetime(payload.scheduled_publish_at)
            if scheduled_publish_at <= get_beijing_now():
                raise ValueError("定时发放时间须晚于当前时间")
        task = CheckinTask(
            title=payload.title,
            type_id=payload.type_id,
            teacher_user_id=teacher_user.id,
            status=TaskStatus.DRAFT.value,
            starts_at=self._parse_task_datetime(payload.starts_at),
            ends_at=self._parse_task_datetime(payload.ends_at),
            rules_snapshot_jsonb=deepcopy(payload.rules_snapshot),
            schedule_mode=schedule_mode.value,
            is_recurring=is_recurring,
            recurrence_rule=payload.recurrence_rule
            or ("FREQ=DAILY" if is_recurring else None),
            scheduled_publish_at=scheduled_publish_at,
        )
        self.repository.add(task)
        self.repository.flush()
        for group_id in payload.group_ids:
            self.repository.add(CheckinTaskGroup(task_id=task.id, group_id=group_id))
        self.repository.commit()
        return self.serialize_task(task)

    def list_teacher_tasks(self, teacher_user_id: int) -> dict:
        tasks = self.repository.list_tasks_by_teacher(teacher_user_id)
        self._ensure_tasks_fresh(tasks)
        items = [self.serialize_task(task) for task in tasks]
        return {"items": items, "total": len(items)}

    def get_task_detail(self, task_id: int, teacher_user: User | None = None) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        if teacher_user is not None:
            self._require_task_owner(task, teacher_user)
        self._ensure_task_fresh(task)
        task_item = self.serialize_task(task)
        return {
            **task_item,
            "task": {**task_item, "published": task.is_published, "published_at": None},
            "students": self._serialize_task_students(task.id),
            "exceptions": self._serialize_task_exceptions(task.id),
            "occurrences": self._serialize_occurrences(task.id),
        }

    def _serialize_occurrences(self, task_id: int) -> list[dict]:
        return [
            {
                "id": occ.id,
                "occurrence_date": occ.occurrence_date,
                "occurrenceDate": occ.occurrence_date,
                "starts_at": occ.starts_at.isoformat(),
                "ends_at": occ.ends_at.isoformat(),
                "status": occ.status,
            }
            for occ in self.repository.list_occurrences_for_task(task_id)
        ]

    def publish_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        if task.is_published:
            raise ValueError("任务已发布")
        result = self._apply_publish(task)
        self.repository.commit()
        return result

    def _apply_publish(self, task: CheckinTask) -> dict:
        task.is_published = True
        task.scheduled_publish_at = None
        task.status = TaskStatus.NOT_STARTED.value
        self.repository.flush()

        occurrences = self._materialize_occurrences(task)
        notified = self._notify_group_members(task)
        return {
            "published": True,
            "status": task.status,
            "notified_count": notified,
            "occurrence_count": len(occurrences),
        }

    def _materialize_occurrences(self, task: CheckinTask) -> list[CheckinTaskOccurrence]:
        """为任务生成 occurrence：一次任务一条；定时任务按日从开始到今天物化。"""
        created: list[CheckinTaskOccurrence] = []
        start_date = task.starts_at.date()
        is_recurring = task.schedule_mode == ScheduleMode.RECURRING.value

        if not is_recurring:
            dates = [start_date]
        else:
            today = datetime.now().date()
            cap_date = min(today, task.ends_at.date())
            if cap_date < start_date:
                cap_date = start_date
            dates = []
            cursor = start_date
            while cursor <= cap_date and len(dates) < MAX_MATERIALIZED_DAYS:
                dates.append(cursor)
                cursor += timedelta(days=1)

        for occurrence_date in dates:
            date_str = occurrence_date.isoformat()
            if self.repository.get_occurrence(task.id, date_str) is not None:
                continue
            if is_recurring:
                starts_at = datetime.combine(occurrence_date, task.starts_at.time())
                ends_at = datetime.combine(occurrence_date, task.ends_at.time())
            else:
                starts_at = task.starts_at
                ends_at = task.ends_at
            occurrence = CheckinTaskOccurrence(
                task_id=task.id,
                occurrence_date=date_str,
                starts_at=starts_at,
                ends_at=ends_at,
                status=TaskStatus.NOT_STARTED.value,
            )
            self.repository.add(occurrence)
            created.append(occurrence)
        self.repository.flush()
        return created

    def _notify_group_members(self, task: CheckinTask) -> int:
        """向任务所属群组的学生推送消息（类钉钉通知）。"""
        groups = self.repository.list_groups_for_task(task.id)
        group_names = [group.name for group in groups]
        title, content = _format_task_notify_message(task, group_names=group_names)
        count = 0
        seen_user_ids: set[int] = set()
        for student in self.repository.list_students_for_task(task.id):
            if student.user_id is None or student.user_id in seen_user_ids:
                continue
            seen_user_ids.add(student.user_id)
            self.repository.add(
                Message(
                    user_id=student.user_id,
                    title=title,
                    content=content,
                    created_at=get_beijing_now(),
                )
            )
            count += 1
        self.repository.flush()
        return count

    def end_task(self, *, task_id: int, teacher_user: User) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)
        self._ensure_task_fresh(task)
        if task.status == TaskStatus.ENDED.value:
            return {"ended": True, "status": task.status}
        task.status = TaskStatus.ENDED.value
        self.repository.commit()
        return {"ended": True, "status": task.status}

    def get_qr_code(
        self, *, task_id: int, teacher_user: User, refresh: bool = False
    ) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)

        rules = task.rules_snapshot_jsonb or {}
        vr = rules.get("verificationRule", {}) or {}
        if "qr_code" not in (vr.get("methods") or []):
            raise ValueError("该任务未启用二维码签到")

        qr_config = vr.get("qr_code", {}) or {}
        expire_seconds = int(qr_config.get("expireSeconds", 120))
        refresh_interval = int(qr_config.get("refreshIntervalSeconds", 60))

        token, token_obj = generate_token(
            task.id,
            occurrence_date=datetime.now().date().isoformat(),
            expire_seconds=expire_seconds,
        )
        task.current_qr_token = token
        self.repository.commit()

        return {
            "task_id": task.id,
            "qr_token": token,
            "qr_image": render_qr_data_url(token),
            "expires_at": token_obj.expires_at,
            "expire_seconds": expire_seconds,
            "refresh_interval_seconds": refresh_interval,
            "refreshed": refresh,
        }

    def set_student_attendance(
        self,
        *,
        task_id: int,
        student_profile_id: int,
        status: str,
        remark: str | None,
        teacher_user: User,
    ) -> dict:
        """教师手动设置某学生在该任务下的考勤（签到/迟到/早退/未签到/请假）。"""
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        self._require_task_owner(task, teacher_user)

        try:
            attendance = AttendanceStatus(status)
        except ValueError as exc:
            raise ValueError("无效的考勤状态") from exc

        student = self.repository.get_student_profile(student_profile_id)
        if student is None:
            raise ValueError("学生不存在")

        record = self.repository.get_record_for_student_task(task_id, student_profile_id)
        if record is None:
            record = CheckinRecord(
                task_id=task_id,
                student_profile_id=student_profile_id,
                submitted_at=datetime.now(),
                occurrence_date=datetime.now().date().isoformat(),
                status=RecordStatus.NORMAL.value,
                verification_results_jsonb={},
                enabled_methods_jsonb=[],
                submit_payload_jsonb={"source": "teacher_manual"},
            )
            self.repository.add(record)

        record.manual_status = attendance.value
        record.manual_remark = remark or None
        # 手动标记后清除待复核占位
        record.need_review = False
        self.repository.commit()

        return {
            "task_id": task_id,
            "student_id": student_profile_id,
            "manual_status": attendance.value,
            "status": self._student_task_status(record, None),
        }

    def teacher_dashboard(self, teacher_user_id: int) -> dict:
        tasks = self.repository.list_tasks_by_teacher(teacher_user_id)
        self._ensure_tasks_fresh(tasks)
        task_ids = [task.id for task in tasks]
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        pending_reviews = [
            item
            for item in exceptions
            if item.status == RecordStatus.PENDING_REVIEW.value
        ]
        today_tasks = len(tasks)
        return {
            "task_count": len(tasks),
            "exception_count": len(exceptions),
            "pending_review_count": len(pending_reviews),
            "todayTasks": today_tasks,
            "exceptions": len(exceptions),
            "pendingReviews": len(pending_reviews),
            "quickCreateCount": 0,
        }

    def list_teacher_groups(self, teacher_user: User) -> dict:
        if teacher_user.teacher_profile is None:
            return {"items": [], "total": 0}
        groups = self.repository.list_groups_for_teacher_profile(
            teacher_user.teacher_profile.id
        )
        items = [self._serialize_teacher_group(group) for group in groups]
        return {"items": items, "total": len(items)}

    def create_teacher_group(self, teacher_user: User, name: str) -> dict:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        trimmed = name.strip()
        if not trimmed:
            raise ValueError("班级名称不能为空")
        group = Group(
            name=trimmed,
            group_type="class",
            invite_code=generate_unique_invite_code(self.db),
        )
        self.repository.add(group)
        self.repository.flush()
        self.repository.add(
            GroupTeacher(
                group_id=group.id,
                teacher_profile_id=teacher_user.teacher_profile.id,
            )
        )
        self.repository.commit()
        return self._serialize_teacher_group(group)

    def get_teacher_group_detail(self, group_id: int, teacher_user: User) -> dict:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        group = self.repository.get_group(group_id)
        if group is None:
            raise ValueError("班级不存在")
        allowed_group_ids = set(
            self.repository.list_group_ids_for_teacher_profile(
                teacher_user.teacher_profile.id
            )
        )
        if group_id not in allowed_group_ids:
            raise PermissionError("无权查看该班级")

        students = self._students_for_group(group_id)
        tasks = self.repository.list_tasks_for_group_ids([group_id])
        self._ensure_tasks_fresh(tasks)
        task_ids = [task.id for task in tasks]
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        pending_review_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        total_records = sum(
            len(self.repository.list_records_for_task(task.id)) for task in tasks
        )
        total_students_in_tasks = sum(
            len(self.repository.list_students_for_task(task.id)) for task in tasks
        )
        attendance_rate = self._completion_rate(total_records, total_students_in_tasks)
        exception_rate = self._completion_rate(len(exceptions), max(total_records, 1))

        return {
            "group": self._serialize_teacher_group(group),
            "stats": {
                "attendance_rate": attendance_rate,
                "attendanceRate": attendance_rate,
                "exception_rate": exception_rate,
                "exceptionRate": exception_rate,
                "pending_review_count": pending_review_count,
                "pendingReviewCount": pending_review_count,
            },
            "students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "status": "joined",
                }
                for student in students
            ],
            "tasks": [self.serialize_task(task) for task in tasks],
        }

    def list_student_groups(self, student_user: User) -> dict:
        if student_user.student_profile is None:
            raise ValueError("学生档案不存在")
        groups = self.repository.list_groups_for_student_profile(
            student_user.student_profile.id
        )
        student_profile_id = student_user.student_profile.id
        items = [
            self._serialize_student_group(group, student_profile_id)
            for group in groups
        ]
        return {"items": items, "total": len(items)}

    def get_student_group_attendance(
        self, group_id: int, student_user: User
    ) -> dict:
        if student_user.student_profile is None:
            raise ValueError("学生档案不存在")
        student_profile_id = student_user.student_profile.id
        group = self.repository.get_group(group_id)
        if group is None:
            raise ValueError("班级不存在")
        if not self.repository.group_member_exists(group_id, student_profile_id):
            raise PermissionError("无权查看该班级")

        attendance = self._compute_group_attendance(group_id, student_profile_id)
        teachers = self.repository.list_teachers_for_group(group_id)
        primary_teacher = teachers[0] if teachers else None
        return {
            "group": {
                "id": group.id,
                "name": group.name,
                "teacher_name": primary_teacher.name if primary_teacher else "",
                "teacherName": primary_teacher.name if primary_teacher else "",
            },
            "summary": attendance["summary"],
            "tasks": attendance["tasks"],
            "timeline": attendance["timeline"],
        }

    def join_group_by_invite_code(self, student_user: User, invite_code: str) -> dict:
        if student_user.student_profile is None:
            raise ValueError("学生档案不存在")
        code = invite_code.strip().upper()
        if not code:
            raise ValueError("请输入班级邀请码")
        group = self.repository.get_group_by_invite_code(code)
        if group is None:
            raise ValueError("邀请码无效，请检查后重试")
        student_profile_id = student_user.student_profile.id
        already_member = self.repository.group_member_exists(
            group.id, student_profile_id
        )
        if not already_member:
            self.repository.add(
                GroupMember(
                    group_id=group.id,
                    student_profile_id=student_profile_id,
                )
            )
            self.repository.commit()
        return {
            "group": self._serialize_teacher_group(group),
            "already_member": already_member,
        }

    def serialize_task(self, task: CheckinTask) -> dict:
        checkin_type = self.repository.get_checkin_type(task.type_id)
        rule_template = self.repository.get_rule_template_for_type(task.type_id)
        groups = self.repository.list_groups_for_task(task.id)
        group_ids = [group.id for group in groups]
        group_names = [group.name for group in groups]
        records = self.repository.list_records_for_task(task.id)
        exceptions = self.repository.list_exceptions_for_task(task.id)
        student_count = len(self.repository.list_students_for_task(task.id))
        submitted_count = len({record.student_profile_id for record in records})
        exception_count = len(exceptions)
        pending_review_count = sum(
            1 for item in exceptions if item.status == RecordStatus.PENDING_REVIEW.value
        )
        completion_rate = self._completion_rate(submitted_count, student_count)
        return {
            "id": task.id,
            "title": task.title,
            "type_id": task.type_id,
            "type_name": checkin_type.name if checkin_type else None,
            "taskType": checkin_type.name if checkin_type else "custom",
            "templateName": rule_template.name if rule_template else "",
            "description": task.description,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "startsAt": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "endsAt": task.ends_at.isoformat(),
            "is_published": task.is_published,
            "published": task.is_published,
            "scheduled_publish_at": (
                task.scheduled_publish_at.isoformat() if task.scheduled_publish_at else None
            ),
            "scheduledPublishAt": (
                task.scheduled_publish_at.isoformat() if task.scheduled_publish_at else None
            ),
            "schedule_mode": task.schedule_mode,
            "scheduleMode": task.schedule_mode,
            "is_recurring": task.is_recurring,
            "recurrence_rule": task.recurrence_rule,
            "group_ids": group_ids,
            "group_names": group_names,
            "groupName": " / ".join(group_names),
            "student_count": student_count,
            "studentCount": student_count,
            "submitted_count": submitted_count,
            "submittedCount": submitted_count,
            "completion_rate": completion_rate,
            "completionRate": completion_rate,
            "exception_count": exception_count,
            "exceptionCount": exception_count,
            "pending_review_count": pending_review_count,
            "pendingReviewCount": pending_review_count,
            "rules_snapshot": deepcopy(task.rules_snapshot_jsonb),
        }

    def _require_task_owner(self, task: CheckinTask, teacher_user: User) -> None:
        if task.teacher_user_id != teacher_user.id:
            raise PermissionError("无权操作该任务")

    def _require_teacher_group_scope(
        self, teacher_user: User, group_ids: list[int]
    ) -> None:
        if teacher_user.teacher_profile is None:
            raise PermissionError("教师档案不存在")
        allowed_group_ids = set(
            self.repository.list_group_ids_for_teacher_profile(
                teacher_user.teacher_profile.id
            )
        )
        if not set(group_ids).issubset(allowed_group_ids):
            raise PermissionError("无权向所选分组发布任务")

    def _serialize_student_group(self, group: Group, student_profile_id: int) -> dict:
        students = self._students_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        teachers = self.repository.list_teachers_for_group(group.id)
        primary_teacher = teachers[0] if teachers else None
        teacher_names = [teacher.name for teacher in teachers]
        attendance = self._compute_group_attendance(group.id, student_profile_id)
        summary = attendance["summary"]
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "groupType": group.group_type,
            "student_profile_id": student_profile_id,
            "studentProfileId": student_profile_id,
            "teacher_id": primary_teacher.id if primary_teacher else None,
            "teacherId": primary_teacher.id if primary_teacher else None,
            "teacher_name": primary_teacher.name if primary_teacher else "",
            "teacherName": primary_teacher.name if primary_teacher else "",
            "teacher_names": teacher_names,
            "teacherNames": teacher_names,
            "student_count": len(students),
            "studentCount": len(students),
            "recent_task_count": len(tasks),
            "recentTaskCount": len(tasks),
            "checked_in_count": summary["checked_in_count"],
            "checkedInCount": summary["checked_in_count"],
            "published_count": summary["published_count"],
            "publishedCount": summary["published_count"],
        }

    def _teacher_display_name(self, teacher_user_id: int) -> str:
        user = self.repository.db.get(User, teacher_user_id)
        if user is None:
            return ""
        if user.teacher_profile is not None and user.teacher_profile.name:
            return user.teacher_profile.name
        return user.display_name or ""

    def _leave_category(self, record: CheckinRecord | None) -> str:
        if record is None:
            return "personal"
        remark = (record.manual_remark or "").strip()
        if "病" in remark:
            return "sick"
        if "公" in remark:
            return "official"
        return "personal"

    def _attendance_display_label(
        self,
        attendance: str,
        record: CheckinRecord | None,
        is_expired: bool,
    ) -> str:
        if is_expired:
            return "已过期"
        if attendance == AttendanceStatus.LEAVE.value:
            category = self._leave_category(record)
            if category == "sick":
                return "病假"
            if category == "official":
                return "公假"
            return "事假"
        labels = {
            AttendanceStatus.PRESENT.value: "出勤",
            AttendanceStatus.LATE.value: "迟到",
            AttendanceStatus.EARLY_LEAVE.value: "早退",
            AttendanceStatus.ABSENT.value: "缺勤",
        }
        return labels.get(attendance, "缺勤")

    def _compute_group_attendance(
        self, group_id: int, student_profile_id: int
    ) -> dict:
        tasks = self.repository.list_tasks_for_group_ids([group_id])
        published_tasks = [
            task for task in tasks if task.status in PUBLISHED_TASK_STATUSES
        ]
        self._ensure_tasks_fresh(published_tasks)
        task_ids = [task.id for task in published_tasks]
        records_index = self.repository.map_records_for_student_tasks(
            student_profile_id, task_ids
        )
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        logger.info(
            "compute_group_attendance group_id=%s student_profile_id=%s "
            "tasks_in_group=%s published_tasks=%s record_index_size=%s task_ids=%s",
            group_id,
            student_profile_id,
            len(tasks),
            len(published_tasks),
            len(records_index),
            task_ids,
        )
        exception_by_record: dict[int, CheckinException] = {}
        for item in exceptions:
            if item.record_id is not None:
                exception_by_record[item.record_id] = item

        published_count = 0
        checked_in_count = 0
        present_count = 0
        late_count = 0
        early_leave_count = 0
        absent_count = 0
        expired_count = 0
        sick_leave_count = 0
        personal_leave_count = 0
        official_leave_count = 0
        task_items: list[dict] = []
        timeline: list[dict] = []
        teacher_name_cache: dict[int, str] = {}
        now = get_beijing_now()

        for task in sorted(published_tasks, key=lambda item: item.ends_at, reverse=True):
            teacher_name = teacher_name_cache.get(task.teacher_user_id)
            if teacher_name is None:
                teacher_name = self._teacher_display_name(task.teacher_user_id)
                teacher_name_cache[task.teacher_user_id] = teacher_name

            occurrences = self.repository.list_occurrences_for_task(task.id)
            occ_by_date = {occ.occurrence_date: occ for occ in occurrences}
            if occurrences:
                occurrence_dates = [occ.occurrence_date for occ in occurrences]
            else:
                occurrence_dates = [
                    as_beijing_datetime(task.ends_at).date().isoformat()
                ]

            task_published = len(occurrence_dates)
            task_checked = 0
            last_attendance = AttendanceStatus.ABSENT.value

            for occurrence_date in occurrence_dates:
                published_count += 1
                record = records_index.get((task.id, occurrence_date))
                if record is None:
                    record = records_index.get((task.id, ""))
                exception = (
                    exception_by_record.get(record.id) if record is not None else None
                )
                occ = occ_by_date.get(occurrence_date)
                ends_at = occ.ends_at if occ is not None else task.ends_at
                ends_at_bj = as_beijing_datetime(ends_at)
                is_past = ends_at_bj <= now
                is_expired = record is None and is_past

                if is_expired:
                    attendance = AttendanceStatus.ABSENT.value
                    expired_count += 1
                else:
                    attendance = resolve_attendance_status(
                        record=record, exception=exception
                    )
                    if attendance == AttendanceStatus.PRESENT.value:
                        present_count += 1
                    elif attendance == AttendanceStatus.LATE.value:
                        late_count += 1
                    elif attendance == AttendanceStatus.EARLY_LEAVE.value:
                        early_leave_count += 1
                    elif attendance == AttendanceStatus.LEAVE.value:
                        leave_category = self._leave_category(record)
                        if leave_category == "sick":
                            sick_leave_count += 1
                        elif leave_category == "official":
                            official_leave_count += 1
                        else:
                            personal_leave_count += 1
                    elif attendance == AttendanceStatus.ABSENT.value:
                        absent_count += 1

                last_attendance = attendance
                if attendance in CHECKED_IN_ATTENDANCE_STATUSES:
                    checked_in_count += 1
                    task_checked += 1

                status_label = self._attendance_display_label(
                    attendance, record, is_expired
                )
                if record is not None and record.submitted_at is not None:
                    occurred_at = record.submitted_at
                elif occ is not None:
                    occurred_at = occ.starts_at
                else:
                    occurred_at = ends_at
                occurred_iso = to_beijing_iso(occurred_at)

                timeline.append(
                    {
                        "task_id": task.id,
                        "taskId": task.id,
                        "task_title": task.title,
                        "taskTitle": task.title,
                        "occurrence_date": occurrence_date,
                        "occurrenceDate": occurrence_date,
                        "occurred_at": occurred_iso,
                        "occurredAt": occurred_iso,
                        "initiator_name": teacher_name,
                        "initiatorName": teacher_name,
                        "attendance_status": attendance,
                        "attendanceStatus": attendance,
                        "status_label": status_label,
                        "statusLabel": status_label,
                        "is_expired": is_expired,
                        "isExpired": is_expired,
                    }
                )

            if task_published == 1:
                display_attendance = last_attendance
            elif task_checked == 0:
                display_attendance = AttendanceStatus.ABSENT.value
            elif task_checked >= task_published:
                display_attendance = AttendanceStatus.PRESENT.value
            else:
                display_attendance = "partial"

            task_items.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "task_status": task.status,
                    "taskStatus": task.status,
                    "starts_at": task.starts_at.isoformat(),
                    "startsAt": task.starts_at.isoformat(),
                    "ends_at": task.ends_at.isoformat(),
                    "endsAt": task.ends_at.isoformat(),
                    "is_recurring": task.is_recurring,
                    "isRecurring": task.is_recurring,
                    "occurrence_count": task_published,
                    "occurrenceCount": task_published,
                    "checked_in_count": task_checked,
                    "checkedInCount": task_checked,
                    "checked_in": task_checked > 0,
                    "checkedIn": task_checked > 0,
                    "attendance_status": display_attendance,
                    "attendanceStatus": display_attendance,
                }
            )

        timeline.sort(key=lambda item: item.get("occurred_at") or "", reverse=True)

        leave_count = sick_leave_count + personal_leave_count + official_leave_count
        logger.info(
            "compute_group_attendance done group_id=%s published=%s checked_in=%s timeline=%s summary=%s",
            group_id,
            published_count,
            checked_in_count,
            len(timeline),
            {
                "present": present_count,
                "late": late_count,
                "absent": absent_count,
                "expired": expired_count,
                "leave": leave_count,
            },
        )

        summary = {
            "checked_in_count": checked_in_count,
            "checkedInCount": checked_in_count,
            "published_count": published_count,
            "publishedCount": published_count,
            "present_count": present_count,
            "presentCount": present_count,
            "late_count": late_count,
            "lateCount": late_count,
            "early_leave_count": early_leave_count,
            "earlyLeaveCount": early_leave_count,
            "absent_count": absent_count,
            "absentCount": absent_count,
            "expired_count": expired_count,
            "expiredCount": expired_count,
            "sick_leave_count": sick_leave_count,
            "sickLeaveCount": sick_leave_count,
            "personal_leave_count": personal_leave_count,
            "personalLeaveCount": personal_leave_count,
            "official_leave_count": official_leave_count,
            "officialLeaveCount": official_leave_count,
            "leave_count": leave_count,
            "leaveCount": leave_count,
        }
        return {"summary": summary, "tasks": task_items, "timeline": timeline}

    def _group_student_meta(self, students: list[StudentProfile]) -> dict[str, str]:
        if not students:
            return {"grade": "", "major": ""}
        grades = Counter(student.grade for student in students if student.grade)
        majors = Counter(student.major for student in students if student.major)
        return {
            "grade": grades.most_common(1)[0][0] if grades else "",
            "major": majors.most_common(1)[0][0] if majors else "",
        }

    def _serialize_teacher_group(self, group: Group) -> dict:
        students = self._students_for_group(group.id)
        tasks = self.repository.list_tasks_for_group_ids([group.id])
        recent_task_count = len(tasks)
        meta = self._group_student_meta(students)
        created_at = group.created_at
        created_iso = created_at.isoformat() if created_at else None
        return {
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "invite_code": group.invite_code,
            "inviteCode": group.invite_code,
            "student_count": len(students),
            "studentCount": len(students),
            "recent_task_count": recent_task_count,
            "recentTaskCount": recent_task_count,
            "course_name": group.group_type,
            "courseName": group.group_type,
            "grade": meta["grade"],
            "major": meta["major"],
            "created_at": created_iso,
            "createdAt": created_iso,
        }

    def _serialize_task_students(self, task_id: int) -> list[dict]:
        records = {
            record.student_profile_id: record
            for record in self.repository.list_records_for_task(task_id)
        }
        exceptions = {
            item.student_profile_id: item
            for item in self.repository.list_exceptions_for_task(task_id)
        }
        items = []
        for student in self.repository.list_students_for_task(task_id):
            record = records.get(student.id)
            exception = exceptions.get(student.id)
            manual_status = record.manual_status if record else None
            items.append(
                {
                    "id": student.id,
                    "student_no": student.student_no,
                    "studentNo": student.student_no,
                    "name": student.name,
                    "status": self._student_task_status(record, exception),
                    "manual_status": manual_status,
                    "manualStatus": manual_status,
                    "manual_remark": record.manual_remark if record else None,
                    "submitted_at": record.submitted_at.isoformat() if record else None,
                    "submittedAt": record.submitted_at.isoformat() if record else None,
                }
            )
        return items

    def _serialize_task_exceptions(self, task_id: int) -> list[dict]:
        groups = self.repository.list_groups_for_task(task_id)
        group_name = " / ".join(group.name for group in groups)
        task = self.repository.get_task(task_id)
        records = {
            record.id: record
            for record in self.repository.list_records_for_task(task_id)
        }
        students = {
            student.id: student
            for student in self.repository.list_students_for_task(task_id)
        }
        return [
            self._serialize_exception(
                item,
                student=students.get(item.student_profile_id),
                task=task,
                record=records.get(item.record_id),
                group_name=group_name,
            )
            for item in self.repository.list_exceptions_for_task(task_id)
        ]

    def _serialize_exception(
        self,
        item: CheckinException,
        *,
        student: StudentProfile | None,
        task: CheckinTask | None,
        record: CheckinRecord | None,
        group_name: str,
    ) -> dict:
        reason = " / ".join(item.messages_jsonb) if item.messages_jsonb else "异常"
        submitted_at = record.submitted_at.isoformat() if record else None
        status = (
            "pending"
            if item.status == RecordStatus.PENDING_REVIEW.value
            else item.status
        )
        return {
            "id": item.id,
            "record_id": item.record_id,
            "recordId": item.record_id,
            "task_id": item.task_id,
            "taskId": item.task_id,
            "student_id": item.student_profile_id,
            "studentId": item.student_profile_id,
            "student_name": student.name if student else None,
            "studentName": student.name if student else "",
            "task_title": task.title if task else None,
            "taskTitle": task.title if task else "",
            "group_name": group_name,
            "groupName": group_name,
            "submitted_at": submitted_at,
            "submittedAt": submitted_at,
            "reason": reason,
            "status": status,
            "exception_types": item.exception_types_jsonb,
            "exceptionTypes": item.exception_types_jsonb,
            "messages": item.messages_jsonb,
        }

    def _students_for_group(self, group_id: int) -> list[StudentProfile]:
        return self.repository.list_students_for_group(group_id)

    def _student_task_status(
        self, record: CheckinRecord | None, exception: CheckinException | None
    ) -> str:
        status = resolve_attendance_status(record=record, exception=exception)
        if record is None:
            return "missing"
        if exception is not None and exception.status == RecordStatus.PENDING_REVIEW.value:
            if status not in {
                AttendanceStatus.PRESENT.value,
                AttendanceStatus.LATE.value,
                AttendanceStatus.EARLY_LEAVE.value,
                AttendanceStatus.LEAVE.value,
            }:
                return "pending_review"
        return status

    def _completion_rate(self, submitted_count: int, student_count: int) -> int:
        if student_count == 0:
            return 0
        return round(submitted_count / student_count * 100)
