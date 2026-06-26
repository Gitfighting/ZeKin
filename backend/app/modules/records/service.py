from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.modules.auth.models import StudentProfile, User
from app.modules.exceptions.models import CheckinException, ReviewLog
from app.modules.face_recognition.service import (
    FaceImageError,
    FaceRecognitionLibraryMissing,
    FaceRecognitionService,
    FaceVerificationInput,
    decode_image_payload,
)
from app.modules.messages.models import Message
from app.modules.records.evaluators import (
    EvaluationResult,
    LocationRuleEvaluator,
    TimeRuleEvaluator,
)
from app.modules.records.models import Appeal, CheckinRecord
from app.modules.records.repository import RecordRepository
from app.modules.records.schemas import AppealRequest, CheckinRequest
from app.shared.enums import RecordStatus
from app.shared.enums import ExceptionType


def get_current_time() -> datetime:
    return datetime.now(ZoneInfo("Asia/Shanghai"))


class RecordService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = RecordRepository(db)
        self.time_evaluator = TimeRuleEvaluator()
        self.location_evaluator = LocationRuleEvaluator()
        self.face_service = FaceRecognitionService(db)

    def student_dashboard(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        tasks = self.repository.list_tasks_for_student(profile.id)
        records = self.repository.list_records_for_student(profile.id)
        return {"task_count": len(tasks), "record_count": len(records)}

    def list_student_tasks(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        items = [
            self._serialize_task(task)
            for task in self.repository.list_tasks_for_student(profile.id)
        ]
        return {"items": items, "total": len(items)}

    def get_student_task(self, current_user: User, task_id: int) -> dict:
        profile = self._require_student_profile(current_user.id)
        tasks = {
            task.id: task for task in self.repository.list_tasks_for_student(profile.id)
        }
        task = tasks.get(task_id)
        if task is None:
            raise ValueError("任务不存在")
        return self._serialize_task(task)

    def submit_checkin(
        self, *, current_user: User, task_id: int, payload: CheckinRequest
    ) -> dict:
        profile = self._require_student_profile(current_user.id)
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")

        rules = deepcopy(task.rules_snapshot_jsonb)
        now = get_current_time()
        time_result = self.time_evaluator.evaluate(now=now, rule=rules["timeRule"])
        location_result = self.location_evaluator.evaluate(
            longitude=payload.longitude,
            latitude=payload.latitude,
            rule=rules["locationRule"],
        )
        face_result = self._evaluate_face(
            profile_id=profile.id,
            rule=rules.get("faceRule", {}),
            payload=payload,
        )
        result = self._merge_results(time_result, location_result, face_result)

        record = CheckinRecord(
            task_id=task.id,
            student_profile_id=profile.id,
            submitted_at=now,
            status=result.status,
            longitude=payload.longitude,
            latitude=payload.latitude,
            location_result_jsonb=self._result_dict(location_result),
            dynamic_code_result_jsonb={"passed": True, "code": payload.dynamic_code},
            face_result_jsonb=self._result_dict(face_result),
            submit_payload_jsonb=payload.submit_payload,
            evaluation_messages_jsonb=result.messages,
            need_review=result.need_review,
        )
        self.repository.add(record)
        self.repository.flush()

        if result.exception_types:
            exception = CheckinException(
                record_id=record.id,
                task_id=task.id,
                student_profile_id=profile.id,
                exception_types_jsonb=result.exception_types,
                messages_jsonb=result.messages,
                status=RecordStatus.PENDING_REVIEW.value
                if result.need_review
                else RecordStatus.EXCEPTION.value,
            )
            self.repository.add(exception)
        self.repository.commit()
        return {
            "record_id": record.id,
            "status": record.status,
            "exception_types": result.exception_types,
            "need_review": result.need_review,
        }

    def list_student_records(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        items = [
            {
                "id": record.id,
                "task_id": record.task_id,
                "status": record.status,
                "submitted_at": record.submitted_at.isoformat(),
                "need_review": record.need_review,
            }
            for record in self.repository.list_records_for_student(profile.id)
        ]
        return {"items": items, "total": len(items)}

    def submit_appeal(
        self, *, current_user: User, record_id: int, payload: AppealRequest
    ) -> dict:
        profile = self._require_student_profile(current_user.id)
        record = self.repository.get_record(record_id)
        if record is None:
            raise ValueError("记录不存在")
        appeal = Appeal(
            record_id=record.id,
            student_profile_id=profile.id,
            reason=payload.reason,
            attachment_ids_jsonb=payload.attachment_ids,
            status="appeal_pending",
        )
        record.status = "appeal_pending"
        self.repository.add(appeal)
        self.repository.add(
            Message(
                user_id=current_user.id,
                title="申诉已提交",
                content=f"记录 {record.id} 的申诉已提交，等待教师审核。",
            )
        )
        self.repository.commit()
        return {"appeal_id": appeal.id, "status": appeal.status}

    def list_messages(self, current_user: User) -> dict:
        messages = self.repository.list_messages_for_user(current_user.id)
        items = [
            {
                "id": message.id,
                "title": message.title,
                "content": message.content,
                "read_status": message.read_status,
                "created_at": message.created_at.isoformat()
                if message.created_at
                else None,
            }
            for message in messages
        ]
        return {"items": items, "total": len(items)}

    def profile(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        return {
            "student_no": profile.student_no,
            "name": profile.name,
            "college": profile.college,
            "major": profile.major,
            "grade": profile.grade,
            "class_name": profile.class_name,
            "dormitory": profile.dormitory,
        }

    def growth_summary(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        records = self.repository.list_records_for_student(profile.id)
        normal_count = sum(
            1 for record in records if record.status == RecordStatus.NORMAL.value
        )
        return {"normal_count": normal_count, "total_records": len(records)}

    def list_teacher_exceptions(self, current_user: User) -> dict:
        items = [
            self._serialize_teacher_exception(item)
            for item in self.repository.list_exceptions_for_teacher(current_user.id)
        ]
        return {"items": items, "total": len(items)}

    def review_exception(
        self, *, current_user: User, exception_id: int, payload: dict
    ) -> dict:
        exception = self.repository.get_exception(exception_id)
        if exception is None:
            raise ValueError("异常不存在")
        task = self.repository.get_task(exception.task_id)
        if task is None:
            raise ValueError("任务不存在")
        if task.teacher_user_id != current_user.id:
            raise PermissionError("无权审核该异常")
        record = self.repository.get_record(exception.record_id)
        if record is None:
            raise ValueError("记录不存在")

        decision = payload["decision"]
        if decision == "approve":
            record.status = RecordStatus.NORMAL.value
            exception.status = "approved"
        elif decision == "reject":
            record.status = RecordStatus.REJECTED.value
            exception.status = "rejected"
        else:
            record.status = RecordStatus.PENDING_REVIEW.value
            exception.status = "need_more"

        self.repository.add(
            ReviewLog(
                record_id=record.id,
                reviewer_user_id=current_user.id,
                decision=decision,
                comment=payload["comment"],
            )
        )
        student_profile = self.db.get(StudentProfile, exception.student_profile_id)
        if student_profile is not None and student_profile.user_id is not None:
            self.repository.add(
                Message(
                    user_id=student_profile.user_id,
                    title="审核结果",
                    content=f"记录 {record.id} 的审核结果为 {record.status}：{payload['comment']}",
                )
            )
        self.repository.commit()
        return {"reviewed": True, "record_status": record.status}

    def _require_student_profile(self, user_id: int):
        profile = self.repository.get_student_profile_by_user_id(user_id)
        if profile is None:
            raise ValueError("学生档案不存在")
        return profile

    def _merge_results(self, *results: EvaluationResult) -> EvaluationResult:
        passed = all(result.passed for result in results)
        exception_types: list[str] = []
        messages: list[str] = []
        need_review = False
        for result in results:
            exception_types.extend(result.exception_types)
            messages.extend(result.messages)
            need_review = need_review or result.need_review

        return EvaluationResult(
            passed=passed,
            status=RecordStatus.NORMAL.value
            if passed
            else RecordStatus.EXCEPTION.value,
            exception_types=exception_types,
            messages=messages,
            need_review=need_review,
        )

    def _evaluate_face(
        self, *, profile_id: int, rule: dict, payload: CheckinRequest
    ) -> EvaluationResult:
        if not rule.get("enabled"):
            return EvaluationResult(
                True,
                RecordStatus.NORMAL.value,
                [],
                [],
                False,
            )

        try:
            image_bytes = decode_image_payload(payload.face_image)
        except FaceImageError as exc:
            return EvaluationResult(
                False,
                RecordStatus.EXCEPTION.value,
                [ExceptionType.FACE_FAILED.value],
                [str(exc)],
                True,
            )
        if image_bytes is None:
            return EvaluationResult(
                False,
                RecordStatus.EXCEPTION.value,
                [ExceptionType.FACE_FAILED.value],
                ["请先完成人脸核验"],
                True,
            )

        try:
            result = self.face_service.verify_face(
                profile_id,
                FaceVerificationInput(
                    image_bytes=image_bytes,
                    tolerance=float(rule.get("tolerance", 0.6)),
                    detection_model=str(rule.get("detectionModel", "hog")),
                ),
            )
        except FaceRecognitionLibraryMissing as exc:
            return EvaluationResult(
                False,
                RecordStatus.EXCEPTION.value,
                [ExceptionType.FACE_FAILED.value],
                [str(exc)],
                True,
            )

        if result.passed:
            return EvaluationResult(
                True,
                RecordStatus.NORMAL.value,
                [],
                [result.message],
                False,
            )

        return EvaluationResult(
            False,
            RecordStatus.EXCEPTION.value,
            [ExceptionType.FACE_FAILED.value],
            [result.message],
            True,
        )

    def _result_dict(self, result: EvaluationResult) -> dict:
        return {
            "passed": result.passed,
            "status": result.status,
            "exception_types": result.exception_types,
            "messages": result.messages,
            "need_review": result.need_review,
        }

    def _serialize_task(self, task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "rules_snapshot": deepcopy(task.rules_snapshot_jsonb),
        }

    def _serialize_teacher_exception(self, item: CheckinException) -> dict:
        student = self.repository.get_student_profile(item.student_profile_id)
        task = self.repository.get_task(item.task_id)
        record = self.repository.get_record(item.record_id)
        groups = self.repository.list_groups_for_task(item.task_id)
        if not groups and student is not None:
            groups = self.repository.list_groups_for_student(student.id)
        group_name = " / ".join(group.name for group in groups)
        reason = " / ".join(item.messages_jsonb) if item.messages_jsonb else "异常"
        submitted_at = record.submitted_at.isoformat() if record else None
        teacher_status = (
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
            "student_no": student.student_no if student else None,
            "studentNo": student.student_no if student else "",
            "task_title": task.title if task else None,
            "taskTitle": task.title if task else "",
            "group_name": group_name,
            "groupName": group_name,
            "submitted_at": submitted_at,
            "submittedAt": submitted_at,
            "reason": reason,
            "status": teacher_status,
            "exception_types": item.exception_types_jsonb,
            "exceptionTypes": item.exception_types_jsonb,
            "messages": item.messages_jsonb,
        }
