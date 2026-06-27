"""日报业务逻辑：学生提交日报、查询日报，教师查看并点评。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User
from app.modules.daily_report.models import DailyReport
from app.modules.daily_report.schemas import SubmitDailyReportRequest, TeacherCommentRequest


class DailyReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ─── 学生端 ──────────────────────────────────────────────────────────

    def submit_report(self, *, current_user: User, payload: SubmitDailyReportRequest) -> dict:
        profile = self._require_student_profile(current_user.id)
        report = DailyReport(
            student_profile_id=profile.id,
            task_id=payload.task_id,
            report_date=payload.report_date,
            content=payload.content,
            work_hours=payload.work_hours,
            mood=payload.mood,
            photo_urls_jsonb=payload.photo_urls,
            status="submitted",
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return self._serialize(report)

    def list_student_reports(self, *, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        rows = list(
            self.db.scalars(
                select(DailyReport)
                .where(DailyReport.student_profile_id == profile.id)
                .order_by(DailyReport.report_date.desc())
            )
        )
        return {"items": [self._serialize(r) for r in rows], "total": len(rows)}

    # ─── 教师端 ──────────────────────────────────────────────────────────

    def list_task_reports(self, *, task_id: int) -> dict:
        """列出某任务下所有学生的日报。"""
        rows = list(
            self.db.scalars(
                select(DailyReport)
                .where(DailyReport.task_id == task_id)
                .order_by(DailyReport.report_date.desc())
            )
        )
        items = []
        for r in rows:
            item = self._serialize(r)
            profile = self.db.get(StudentProfile, r.student_profile_id)
            item["student_name"] = profile.name if profile else None
            item["student_no"] = profile.student_no if profile else None
            items.append(item)
        return {"items": items, "total": len(items)}

    def add_comment(self, *, report_id: int, teacher_user: User, payload: TeacherCommentRequest) -> dict:
        report = self.db.get(DailyReport, report_id)
        if report is None:
            raise ValueError("日报不存在")
        report.teacher_comment = payload.comment
        report.status = "reviewed"
        self.db.commit()
        self.db.refresh(report)
        return self._serialize(report)

    # ─── 内部工具 ────────────────────────────────────────────────────────

    def _require_student_profile(self, user_id: int) -> StudentProfile:
        profile = self.db.scalar(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        if profile is None:
            raise ValueError("学生档案不存在")
        return profile

    def _serialize(self, report: DailyReport) -> dict:
        return {
            "id": report.id,
            "student_profile_id": report.student_profile_id,
            "task_id": report.task_id,
            "report_date": report.report_date,
            "content": report.content,
            "work_hours": report.work_hours,
            "mood": report.mood,
            "photo_urls": report.photo_urls_jsonb or [],
            "status": report.status,
            "teacher_comment": report.teacher_comment,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
