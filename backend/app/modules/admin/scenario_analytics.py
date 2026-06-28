from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.modules.admin.repository import AdminRepository
from app.modules.auth.models import StudentProfile
from app.modules.exceptions.models import CheckinException
from app.modules.records.models import Appeal, CheckinRecord
from app.modules.tasks.models import CheckinTask
from app.shared.enums import ExceptionType

SCENARIO_LABELS = {
    "all": "综合洞察",
    "classroom": "课堂签到",
    "dorm": "查寝签到",
    "internship": "实习签到",
    "custom": "自定义签到",
}

CLASSROOM_KEYWORDS = ("课程", "课堂", "上课")
DORM_KEYWORDS = ("查寝", "晚间")
INTERNSHIP_KEYWORDS = ("实习",)

GROUP_TYPE_BY_SCENARIO = {
    "classroom": {"course"},
    "dorm": {"dorm"},
    "internship": {"internship"},
}

RANGE_DAYS = {
    "today": 1,
    "week": 7,
    "month": 30,
    "semester": 120,
}

VERIFICATION_LABELS = {
    "location": "位置校验",
    "face": "人脸校验",
    "qr_code": "二维码校验",
    "checkin_code": "签到码校验",
    "attachment": "附件校验",
    "gesture": "手势校验",
}

EXCEPTION_LABELS = {
    ExceptionType.MISSING.value: "未打卡",
    ExceptionType.LATE.value: "迟到",
    ExceptionType.LOCATION_ERROR.value: "位置异常",
    ExceptionType.DYNAMIC_CODE_ERROR.value: "验证码异常",
    ExceptionType.FACE_FAILED.value: "人脸失败",
    ExceptionType.SAFETY_RISK.value: "安全风险",
    ExceptionType.LOG_MISSING.value: "缺卡",
    ExceptionType.APPEAL_PENDING.value: "申诉中",
    ExceptionType.QR_FAILED.value: "二维码失败",
    ExceptionType.GESTURE_FAILED.value: "手势失败",
    ExceptionType.ATTACHMENT_MISSING.value: "附件缺失",
    ExceptionType.EARLY_LEAVE.value: "早退",
}


class ScenarioAnalyticsBuilder:
    def __init__(self, db: Session, repository: AdminRepository) -> None:
        self.db = db
        self.repository = repository
        self._type_name_cache: dict[int, str | None] = {}

    def build(
        self,
        scenario: str = "all",
        range_key: str = "week",
        college: str | None = None,
        major: str | None = None,
        class_name: str | None = None,
        grade: str | None = None,
    ) -> dict:
        scenario = scenario if scenario in SCENARIO_LABELS else "all"
        range_key = range_key if range_key in RANGE_DAYS else "week"
        today = date.today()
        days = RANGE_DAYS[range_key]
        start_date = today - timedelta(days=days - 1)

        all_students = self.repository.list_students()
        filtered_students = [
            student
            for student in all_students
            if self._matches_student(student, college, major, class_name, grade)
        ]
        student_ids = {student.id for student in filtered_students}
        student_by_id = {student.id: student for student in filtered_students}

        all_tasks = self.repository.list_tasks()
        filtered_tasks = [
            task
            for task in all_tasks
            if self._task_in_range(task, start_date, today)
            and self._matches_scenario(task, scenario)
        ]

        records_by_task = {
            task.id: [
                record
                for record in self.repository.list_records_for_task(task.id)
                if record.student_profile_id in student_ids
            ]
            for task in filtered_tasks
        }
        all_records = [
            record for records in records_by_task.values() for record in records
        ]
        all_exceptions = [
            item
            for item in self.repository.list_exceptions()
            if item.task_id in {task.id for task in filtered_tasks}
            and item.student_profile_id in student_ids
        ]
        pending_appeals = [
            appeal
            for appeal in self._list_appeals()
            if appeal.student_profile_id in student_ids
            and appeal.status == "appeal_pending"
        ]

        expected_total = 0
        checked_total = 0
        for task in filtered_tasks:
            task_students = [
                student
                for student in self.repository.list_students_for_task(task.id)
                if student.id in student_ids
            ]
            expected_total += len(task_students)
            checked_total += len(
                {
                    record.student_profile_id
                    for record in records_by_task.get(task.id, [])
                }
            )

        face_ids = self.repository.list_active_face_student_ids()
        face_registered = sum(1 for student in filtered_students if student.id in face_ids)
        verification_stats = self._verification_breakdown(all_records)

        return {
            "scenario": scenario,
            "scenario_label": SCENARIO_LABELS[scenario],
            "range": range_key,
            "filters": {
                "college": college or "",
                "major": major or "",
                "class_name": class_name or "",
                "grade": grade or "",
            },
            "filter_options": self._filter_options(all_students, college),
            "summary": {
                "expected_count": expected_total,
                "checked_count": checked_total,
                "completion_rate": self._completion_rate(checked_total, expected_total),
                "exception_count": len(all_exceptions),
                "exception_rate": self._completion_rate(
                    len(all_exceptions), max(expected_total, 1)
                ),
                "pending_appeal_count": len(pending_appeals),
                "task_count": len(filtered_tasks),
                "covered_student_count": len(filtered_students),
                "face_registration_rate": self._completion_rate(
                    face_registered, len(filtered_students)
                ),
                "location_pass_rate": verification_stats["location"]["pass_rate"],
                "face_pass_rate": verification_stats["face"]["pass_rate"],
            },
            "trend": self._build_trend(
                filtered_tasks, records_by_task, student_ids, start_date, today
            ),
            "major_rates": self._build_major_rates(
                filtered_tasks, records_by_task, student_by_id, student_ids
            ),
            "class_rates": self._build_class_rates(
                filtered_tasks, records_by_task, student_by_id, student_ids
            ),
            "exception_types": self._exception_types(all_exceptions),
            "verification_breakdown": list(verification_stats["items"]),
            "checkin_time_distribution": self._checkin_time_distribution(all_records),
            "class_exception_ranking": self._class_exception_ranking(
                all_exceptions, student_by_id
            ),
            "risk_students": self._risk_students(
                filtered_tasks, records_by_task, all_exceptions, student_by_id, student_ids
            ),
            "face_registration_by_major": self._face_registration_by_major(
                filtered_students, face_ids
            ),
        }

    def _list_appeals(self) -> list[Appeal]:
        from sqlalchemy import select

        return list(self.db.scalars(select(Appeal).order_by(Appeal.id)))

    def _type_name(self, type_id: int) -> str | None:
        if type_id not in self._type_name_cache:
            checkin_type = self.repository.get_checkin_type(type_id)
            self._type_name_cache[type_id] = (
                checkin_type.name if checkin_type else None
            )
        return self._type_name_cache[type_id]

    def _resolve_task_scenario(self, task: CheckinTask) -> str:
        type_name = self._type_name(task.type_id) or ""
        if any(keyword in type_name for keyword in CLASSROOM_KEYWORDS):
            return "classroom"
        if any(keyword in type_name for keyword in DORM_KEYWORDS):
            return "dorm"
        if any(keyword in type_name for keyword in INTERNSHIP_KEYWORDS):
            return "internship"

        group_types = {
            group.group_type for group in self.repository.list_groups_for_task(task.id)
        }
        for scenario, types in GROUP_TYPE_BY_SCENARIO.items():
            if group_types & types:
                return scenario
        return "custom"

    def _matches_scenario(self, task: CheckinTask, scenario: str) -> bool:
        if scenario == "all":
            return True
        return self._resolve_task_scenario(task) == scenario

    def _task_in_range(self, task: CheckinTask, start_date: date, end_date: date) -> bool:
        task_date = task.starts_at.date()
        return start_date <= task_date <= end_date

    def _matches_student(
        self,
        student: StudentProfile,
        college: str | None,
        major: str | None,
        class_name: str | None,
        grade: str | None,
    ) -> bool:
        if college and (student.college or "") != college:
            return False
        if major and (student.major or "") != major:
            return False
        if class_name and (student.class_name or "") != class_name:
            return False
        if grade and (student.grade or "") != grade:
            return False
        return True

    def _filter_options(
        self, students: list[StudentProfile], college: str | None
    ) -> dict:
        scoped = students
        if college:
            scoped = [student for student in students if (student.college or "") == college]
        return {
            "colleges": sorted({student.college or "未设置学院" for student in students}),
            "majors": sorted({student.major or "未设置专业" for student in scoped}),
            "classes": sorted({student.class_name or "未分班" for student in scoped}),
            "grades": sorted({student.grade or "未设置年级" for student in scoped}),
        }

    def _completion_rate(self, numerator: int, denominator: int) -> int:
        if denominator == 0:
            return 0
        return round(numerator / denominator * 100)

    def _build_trend(
        self,
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
        student_ids: set[int],
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        days = [
            start_date + timedelta(days=offset)
            for offset in range((end_date - start_date).days + 1)
        ]
        result = []
        for day in days:
            day_tasks = [task for task in tasks if task.starts_at.date() == day]
            expected = sum(
                len(
                    [
                        student
                        for student in self.repository.list_students_for_task(task.id)
                        if student.id in student_ids
                    ]
                )
                for task in day_tasks
            )
            checked = sum(
                len(
                    {
                        record.student_profile_id
                        for record in records_by_task.get(task.id, [])
                    }
                )
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

    def _build_major_rates(
        self,
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
        student_by_id: dict[int, StudentProfile],
        student_ids: set[int],
    ) -> list[dict]:
        expected_by_major: Counter[str] = Counter()
        checked_by_major: Counter[str] = Counter()
        for task in tasks:
            for student in self.repository.list_students_for_task(task.id):
                if student.id not in student_ids:
                    continue
                major = student.major or "未设置专业"
                expected_by_major[major] += 1
            for record in records_by_task.get(task.id, []):
                student = student_by_id.get(record.student_profile_id)
                if student is not None:
                    checked_by_major[student.major or "未设置专业"] += 1
        rows = [
            {
                "name": major,
                "expected": expected,
                "checked": checked_by_major[major],
                "completion_rate": self._completion_rate(
                    checked_by_major[major], expected
                ),
            }
            for major, expected in expected_by_major.items()
        ]
        return sorted(rows, key=lambda item: item["completion_rate"], reverse=True)[:8]

    def _build_class_rates(
        self,
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
        student_by_id: dict[int, StudentProfile],
        student_ids: set[int],
    ) -> list[dict]:
        expected_by_class: Counter[str] = Counter()
        checked_by_class: Counter[str] = Counter()
        for task in tasks:
            for student in self.repository.list_students_for_task(task.id):
                if student.id not in student_ids:
                    continue
                class_label = student.class_name or "未分班"
                expected_by_class[class_label] += 1
            for record in records_by_task.get(task.id, []):
                student = student_by_id.get(record.student_profile_id)
                if student is not None:
                    checked_by_class[student.class_name or "未分班"] += 1
        rows = [
            {
                "name": class_label,
                "expected": expected,
                "checked": checked_by_class[class_label],
                "completion_rate": self._completion_rate(
                    checked_by_class[class_label], expected
                ),
            }
            for class_label, expected in expected_by_class.items()
        ]
        return sorted(rows, key=lambda item: item["completion_rate"], reverse=True)[:10]

    def _exception_types(self, exceptions: list[CheckinException]) -> list[dict]:
        counter: Counter[str] = Counter()
        for item in exceptions:
            for exception_type in item.exception_types_jsonb or ["unknown"]:
                counter[
                    EXCEPTION_LABELS.get(exception_type, str(exception_type))
                ] += 1
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

    def _verification_breakdown(self, records: list[CheckinRecord]) -> dict:
        stats: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "failed": 0})
        for record in records:
            results = record.verification_results_jsonb or {}
            for method, detail in results.items():
                if method == "time_window":
                    continue
                if not isinstance(detail, dict):
                    continue
                bucket = stats[method]
                if detail.get("passed"):
                    bucket["passed"] += 1
                else:
                    bucket["failed"] += 1

        items = []
        for method in ("location", "face", "qr_code", "attachment", "checkin_code"):
            bucket = stats.get(method)
            if bucket is None:
                continue
            total = bucket["passed"] + bucket["failed"]
            if total == 0:
                continue
            items.append(
                {
                    "label": VERIFICATION_LABELS.get(method, method),
                    "method": method,
                    "passed": bucket["passed"],
                    "failed": bucket["failed"],
                    "pass_rate": self._completion_rate(bucket["passed"], total),
                }
            )

        location_rate = next(
            (item["pass_rate"] for item in items if item["method"] == "location"), 0
        )
        face_rate = next(
            (item["pass_rate"] for item in items if item["method"] == "face"), 0
        )
        return {"items": items, "location": {"pass_rate": location_rate}, "face": {"pass_rate": face_rate}}

    def _checkin_time_distribution(self, records: list[CheckinRecord]) -> list[dict]:
        counter: Counter[str] = Counter()
        for record in records:
            hour = record.submitted_at.hour
            label = f"{hour:02d}:00-{(hour + 1) % 24:02d}:00"
            counter[label] += 1
        if not counter:
            return []
        return [
            {"label": label, "count": counter[label]}
            for label in sorted(counter, key=lambda item: int(item[:2]))
        ]

    def _class_exception_ranking(
        self,
        exceptions: list[CheckinException],
        student_by_id: dict[int, StudentProfile],
    ) -> list[dict]:
        count_by_class: Counter[str] = Counter()
        student_ids_by_class: dict[str, set[int]] = defaultdict(set)
        for item in exceptions:
            student = student_by_id.get(item.student_profile_id)
            class_label = student.class_name if student else "未分班"
            if not class_label:
                class_label = "未分班"
            count_by_class[class_label] += 1
            student_ids_by_class[class_label].add(item.student_profile_id)
        rows = []
        for class_label, count in count_by_class.most_common(8):
            student_count = len(student_ids_by_class[class_label])
            rows.append(
                {
                    "rank": len(rows) + 1,
                    "class_name": class_label,
                    "exception_count": count,
                    "exception_student_count": student_count,
                    "exception_rate": self._completion_rate(student_count, max(count, 1)),
                }
            )
        return rows

    def _risk_students(
        self,
        tasks: list[CheckinTask],
        records_by_task: dict[int, list[CheckinRecord]],
        exceptions: list[CheckinException],
        student_by_id: dict[int, StudentProfile],
        student_ids: set[int],
    ) -> list[dict]:
        missing_by_student: Counter[int] = Counter()
        exception_by_student: Counter[int] = Counter()
        checked_by_student: dict[int, set[int]] = defaultdict(set)

        for task in tasks:
            task_student_ids = {
                student.id
                for student in self.repository.list_students_for_task(task.id)
                if student.id in student_ids
            }
            for record in records_by_task.get(task.id, []):
                checked_by_student[record.student_profile_id].add(task.id)
            for student_id in task_student_ids:
                if task.id not in checked_by_student[student_id]:
                    missing_by_student[student_id] += 1

        for item in exceptions:
            exception_by_student[item.student_profile_id] += 1

        rows = []
        for student_id in student_ids:
            missing_count = missing_by_student[student_id]
            exception_count = exception_by_student[student_id]
            if missing_count == 0 and exception_count == 0:
                continue
            student = student_by_id.get(student_id)
            if student is None:
                continue
            score = missing_count * 2 + exception_count
            if missing_count >= 3 or exception_count >= 3:
                risk_level = "high"
            elif missing_count >= 1 or exception_count >= 2:
                risk_level = "medium"
            else:
                risk_level = "low"
            rows.append(
                {
                    "student_no": student.student_no,
                    "name": student.name,
                    "major": student.major or "未设置专业",
                    "class_name": student.class_name or "未分班",
                    "missing_count": missing_count,
                    "exception_count": exception_count,
                    "risk_level": risk_level,
                    "risk_score": score,
                }
            )
        rows.sort(key=lambda item: item["risk_score"], reverse=True)
        return rows[:20]

    def _face_registration_by_major(
        self, students: list[StudentProfile], face_ids: set[int]
    ) -> list[dict]:
        totals: Counter[str] = Counter()
        registered: Counter[str] = Counter()
        for student in students:
            major = student.major or "未设置专业"
            totals[major] += 1
            if student.id in face_ids:
                registered[major] += 1
        return [
            {
                "name": major,
                "total": totals[major],
                "registered": registered[major],
                "rate": self._completion_rate(registered[major], totals[major]),
            }
            for major in sorted(totals)
        ]
