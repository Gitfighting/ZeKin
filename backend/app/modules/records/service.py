from copy import deepcopy
from datetime import datetime

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
from app.modules.records.checkin_errors import CheckinBlockedError, get_blocking_checkin_failure
from app.modules.records.evaluators import (
    EvaluationResult,
    LocationRuleEvaluator,
    TimeRuleEvaluator,
)
from app.modules.records.models import Appeal, CheckinRecord
from app.modules.records.repository import RecordRepository
from app.modules.records.schemas import AppealRequest, CheckinRequest
from app.modules.records.verifiers import CheckinContext, CheckinPipeline
from app.shared.attendance import resolve_attendance_status
from app.shared.datetime_utils import get_beijing_now, to_beijing_iso
from app.shared.enums import AttendanceStatus, RecordStatus
from app.shared.enums import ExceptionType


def get_current_time() -> datetime:
    return get_beijing_now()


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
        occurrence_date = payload.occurrence_date or now.date().isoformat()

        pipeline = CheckinPipeline(rules)
        ctx = CheckinContext(
            db=self.db,
            task=task,
            student_profile_id=profile.id,
            now=now,
            payload=payload,
            occurrence_date=occurrence_date,
        )
        result = pipeline.run(ctx)

        blocking_error = get_blocking_checkin_failure(result)
        if blocking_error:
            record = CheckinRecord(
                task_id=task.id,
                student_profile_id=profile.id,
                submitted_at=now,
                occurrence_date=occurrence_date,
                status=RecordStatus.EXCEPTION.value,
                longitude=payload.longitude,
                latitude=payload.latitude,
                verification_results_jsonb=result.verification_results,
                enabled_methods_jsonb=result.enabled_methods,
                location_result_jsonb=result.verification_results.get("location", {}),
                dynamic_code_result_jsonb=(
                    result.verification_results.get("checkin_code")
                    or result.verification_results.get("qr_code", {})
                ),
                face_result_jsonb=result.verification_results.get("face", {}),
                submit_payload_jsonb=payload.submit_payload,
                evaluation_messages_jsonb=[blocking_error, *result.messages],
                need_review=True,
            )
            self.repository.add(record)
            self.repository.flush()
            exception = CheckinException(
                record_id=record.id,
                task_id=task.id,
                student_profile_id=profile.id,
                exception_types_jsonb=result.exception_types or ["location_error"],
                messages_jsonb=[blocking_error],
                status=RecordStatus.PENDING_REVIEW.value,
            )
            self.repository.add(exception)
            self.repository.commit()
            raise CheckinBlockedError(blocking_error, record.id)

        record = CheckinRecord(
            task_id=task.id,
            student_profile_id=profile.id,
            submitted_at=now,
            occurrence_date=occurrence_date,
            status=result.status,
            longitude=payload.longitude,
            latitude=payload.latitude,
            verification_results_jsonb=result.verification_results,
            enabled_methods_jsonb=result.enabled_methods,
            location_result_jsonb=result.verification_results.get("location", {}),
            dynamic_code_result_jsonb=(
                result.verification_results.get("checkin_code")
                or result.verification_results.get("qr_code", {})
            ),
            face_result_jsonb=result.verification_results.get("face", {}),
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
            "enabled_methods": result.enabled_methods,
            "verification_results": result.verification_results,
            "need_review": result.need_review,
        }

    def list_student_records(self, current_user: User) -> dict:
        profile = self._require_student_profile(current_user.id)
        items = []
        for record in self.repository.list_records_for_student(profile.id):
            task = self.repository.get_task(record.task_id)
            exception = self.repository.get_exception_by_record_id(record.id)
            attendance_status = resolve_attendance_status(
                record=record,
                exception=exception,
            )
            items.append(
                {
                    "id": record.id,
                    "task_id": record.task_id,
                    "task_title": task.title if task else f"任务 #{record.task_id}",
                    "status": record.status,
                    "attendance_status": attendance_status,
                    "attendanceStatus": attendance_status,
                    "submitted_at": record.submitted_at.isoformat(),
                    "occurrence_date": record.occurrence_date,
                    "manual_status": record.manual_status,
                    "need_review": record.need_review,
                }
            )
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
                created_at=get_beijing_now(),
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
                "created_at": to_beijing_iso(message.created_at),
            }
            for message in messages
        ]
        unread_count = sum(1 for message in messages if message.read_status != "read")
        return {"items": items, "total": len(items), "unread_count": unread_count}

    def _serialize_message(self, message: Message) -> dict:
        return {
            "id": message.id,
            "title": message.title,
            "content": message.content,
            "read_status": message.read_status,
            "created_at": to_beijing_iso(message.created_at),
        }

    def get_message_detail(self, current_user: User, message_id: int) -> dict:
        message = self.repository.get_message_for_user(current_user.id, message_id)
        if message is None:
            raise ValueError("消息不存在")
        if message.read_status != "read":
            message.read_status = "read"
            self.repository.commit()
        return self._serialize_message(message)

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
            record.manual_status = AttendanceStatus.PRESENT.value
            exception.status = "approved"
        elif decision == "reject":
            record.status = RecordStatus.REJECTED.value
            record.manual_status = AttendanceStatus.ABSENT.value
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
            result_label = "签到" if decision == "approve" else "未签到" if decision == "reject" else "待补充材料"
            self.repository.add(
                Message(
                    user_id=student_profile.user_id,
                    title="申诉审核结果",
                    content=f"您的异常申诉已处理，结果为{result_label}。{payload['comment'] or ''}".strip(),
                    created_at=get_beijing_now(),
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
        groups = self.repository.list_groups_for_task(task.id)
        group_name = " / ".join(group.name for group in groups)
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "group_name": group_name,
            "groupName": group_name,
            "rules_snapshot": self._sanitize_rules_for_student(
                deepcopy(task.rules_snapshot_jsonb)
            ),
        }

    @staticmethod
    def _sanitize_rules_for_student(rules: dict) -> dict:
        """学生端不下发签到码明文，仅保留校验方式声明。"""
        vr = rules.get("verificationRule")
        if not isinstance(vr, dict):
            return rules
        checkin_cfg = vr.get("checkin_code")
        if isinstance(checkin_cfg, dict) and "code" in checkin_cfg:
            sanitized = deepcopy(rules)
            sanitized_vr = sanitized["verificationRule"]
            sanitized_vr["checkin_code"] = {
                **checkin_cfg,
                "code": "",
            }
            return sanitized
        return rules

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
