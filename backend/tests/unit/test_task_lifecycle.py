from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.tasks.lifecycle import TaskLifecycleService, auto_end_enabled
from app.modules.tasks.models import CheckinTask
from app.shared.enums import ScheduleMode, TaskStatus

BEIJING = ZoneInfo("Asia/Shanghai")


def _task(
    *,
    status: str = TaskStatus.IN_PROGRESS.value,
    starts_at: datetime,
    ends_at: datetime,
    schedule_mode: str = ScheduleMode.ONE_TIME.value,
    auto_end: bool = True,
) -> CheckinTask:
    return CheckinTask(
        title="测试任务",
        type_id=1,
        teacher_user_id=1,
        status=status,
        starts_at=starts_at,
        ends_at=ends_at,
        is_published=True,
        rules_snapshot_jsonb={"reviewRule": {"autoEnd": auto_end}},
        schedule_mode=schedule_mode,
        is_recurring=schedule_mode == ScheduleMode.RECURRING.value,
    )


def test_auto_end_enabled_defaults_true():
    task = _task(
        starts_at=datetime(2026, 6, 28, 8, 0, tzinfo=BEIJING),
        ends_at=datetime(2026, 6, 28, 18, 0, tzinfo=BEIJING),
    )
    task.rules_snapshot_jsonb = {}
    assert auto_end_enabled(task) is True


def test_refresh_task_marks_ended_after_end_time(db_session):
    task = _task(
        starts_at=datetime(2026, 6, 28, 8, 0, tzinfo=BEIJING),
        ends_at=datetime(2026, 6, 28, 10, 0, tzinfo=BEIJING),
    )
    db_session.add(task)
    db_session.commit()

    service = TaskLifecycleService(db_session)
    changed = service.refresh_task(
        task,
        now=datetime(2026, 6, 28, 10, 30, tzinfo=BEIJING),
    )
    db_session.commit()

    assert changed is True
    assert task.status == TaskStatus.ENDED.value


def test_refresh_task_keeps_active_before_end_time(db_session):
    task = _task(
        starts_at=datetime(2026, 6, 28, 8, 0, tzinfo=BEIJING),
        ends_at=datetime(2026, 6, 28, 18, 0, tzinfo=BEIJING),
    )
    db_session.add(task)
    db_session.commit()

    service = TaskLifecycleService(db_session)
    changed = service.refresh_task(
        task,
        now=datetime(2026, 6, 28, 12, 0, tzinfo=BEIJING),
    )
    db_session.commit()

    assert changed is False
    assert task.status == TaskStatus.IN_PROGRESS.value


def test_refresh_task_not_started_becomes_in_progress(db_session):
    task = _task(
        status=TaskStatus.NOT_STARTED.value,
        starts_at=datetime(2026, 6, 28, 8, 0, tzinfo=BEIJING),
        ends_at=datetime(2026, 6, 28, 18, 0, tzinfo=BEIJING),
    )
    db_session.add(task)
    db_session.commit()

    service = TaskLifecycleService(db_session)
    changed = service.refresh_task(
        task,
        now=datetime(2026, 6, 28, 9, 0, tzinfo=BEIJING),
    )
    db_session.commit()

    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS.value


def test_refresh_task_respects_auto_end_disabled(db_session):
    task = _task(
        starts_at=datetime(2026, 6, 28, 8, 0, tzinfo=BEIJING),
        ends_at=datetime(2026, 6, 28, 10, 0, tzinfo=BEIJING),
        auto_end=False,
    )
    db_session.add(task)
    db_session.commit()

    service = TaskLifecycleService(db_session)
    changed = service.refresh_task(
        task,
        now=datetime(2026, 6, 28, 12, 0, tzinfo=BEIJING),
    )
    db_session.commit()

    assert changed is False
    assert task.status == TaskStatus.IN_PROGRESS.value
