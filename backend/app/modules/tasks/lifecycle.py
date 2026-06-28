from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.tasks.models import CheckinTask, CheckinTaskOccurrence
from app.modules.tasks.repository import TaskRepository
from app.shared.datetime_utils import as_beijing_datetime, get_beijing_now
from app.shared.enums import ScheduleMode, TaskStatus


def auto_end_enabled(task: CheckinTask) -> bool:
    rules = task.rules_snapshot_jsonb or {}
    review_rule = rules.get("reviewRule") or {}
    return review_rule.get("autoEnd", True) is not False


class TaskLifecycleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TaskRepository(db)

    def refresh_tasks(self, tasks: list[CheckinTask], now: datetime | None = None) -> bool:
        changed = False
        for task in tasks:
            if self.refresh_task(task, now=now):
                changed = True
        if changed:
            self.repository.commit()
        return changed

    def refresh_task(self, task: CheckinTask, now: datetime | None = None) -> bool:
        if not task.is_published:
            return False
        if task.status == TaskStatus.DRAFT.value:
            return False

        current = as_beijing_datetime(now or get_beijing_now())
        changed = False

        if auto_end_enabled(task):
            changed |= self._refresh_occurrences(task, current)
            changed |= self._refresh_task_status(task, current)
        else:
            changed |= self._refresh_task_progress(task, current)

        if changed:
            self.repository.flush()
        return changed

    def _refresh_task_progress(self, task: CheckinTask, now: datetime) -> bool:
        start = as_beijing_datetime(task.starts_at)
        if (
            task.status == TaskStatus.NOT_STARTED.value
            and now >= start
            and now < as_beijing_datetime(task.ends_at)
        ):
            task.status = TaskStatus.IN_PROGRESS.value
            return True
        return False

    def _refresh_task_status(self, task: CheckinTask, now: datetime) -> bool:
        end = as_beijing_datetime(task.ends_at)
        changed = False

        if now >= end:
            if task.status != TaskStatus.ENDED.value:
                task.status = TaskStatus.ENDED.value
                changed = True
            for occurrence in self.repository.list_occurrences_for_task(task.id):
                if occurrence.status != TaskStatus.ENDED.value:
                    occurrence.status = TaskStatus.ENDED.value
                    changed = True
            return changed

        start = as_beijing_datetime(task.starts_at)
        if task.status == TaskStatus.NOT_STARTED.value and now >= start:
            task.status = TaskStatus.IN_PROGRESS.value
            changed = True

        return changed

    def _refresh_occurrences(self, task: CheckinTask, now: datetime) -> bool:
        if task.schedule_mode != ScheduleMode.RECURRING.value:
            return False

        changed = False
        task_end = as_beijing_datetime(task.ends_at)
        for occurrence in self.repository.list_occurrences_for_task(task.id):
            if self._occurrence_should_end(occurrence, now, task_end):
                if occurrence.status != TaskStatus.ENDED.value:
                    occurrence.status = TaskStatus.ENDED.value
                    changed = True
        return changed

    @staticmethod
    def _occurrence_should_end(
        occurrence: CheckinTaskOccurrence,
        now: datetime,
        task_end: datetime,
    ) -> bool:
        occurrence_end = as_beijing_datetime(occurrence.ends_at)
        effective_end = occurrence_end if occurrence_end <= task_end else task_end
        return now >= effective_end
