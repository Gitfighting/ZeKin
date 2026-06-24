from copy import deepcopy
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.tasks.models import CheckinTask, CheckinTaskGroup
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import CreateTaskRequest
from app.shared.enums import TaskStatus


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TaskRepository(db)

    def create_task(self, *, teacher_user: User, payload: CreateTaskRequest) -> dict:
        task = CheckinTask(
            title=payload.title,
            type_id=payload.type_id,
            teacher_user_id=teacher_user.id,
            status=TaskStatus.DRAFT.value,
            starts_at=datetime.fromisoformat(payload.starts_at),
            ends_at=datetime.fromisoformat(payload.ends_at),
            rules_snapshot_jsonb=deepcopy(payload.rules_snapshot),
        )
        self.repository.add(task)
        self.repository.flush()
        for group_id in payload.group_ids:
            self.repository.add(CheckinTaskGroup(task_id=task.id, group_id=group_id))
        self.repository.commit()
        return self.serialize_task(task)

    def list_teacher_tasks(self, teacher_user_id: int) -> dict:
        items = [self.serialize_task(task) for task in self.repository.list_tasks_by_teacher(teacher_user_id)]
        return {"items": items, "total": len(items)}

    def get_task_detail(self, task_id: int) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        return self.serialize_task(task)

    def publish_task(self, task_id: int) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        task.is_published = True
        task.status = TaskStatus.NOT_STARTED.value
        self.repository.commit()
        return {"published": True, "status": task.status}

    def end_task(self, task_id: int) -> dict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        task.status = TaskStatus.ENDED.value
        self.repository.commit()
        return {"ended": True, "status": task.status}

    def teacher_dashboard(self, teacher_user_id: int) -> dict:
        tasks = self.repository.list_tasks_by_teacher(teacher_user_id)
        task_ids = [task.id for task in tasks]
        exceptions = self.repository.list_exceptions_for_teacher_task_ids(task_ids)
        return {"task_count": len(tasks), "exception_count": len(exceptions)}

    def list_teacher_groups(self, teacher_profile_id: int) -> dict:
        group_ids = self.repository.list_group_ids_for_teacher_profile(teacher_profile_id)
        return {"items": [{"id": group_id} for group_id in group_ids], "total": len(group_ids)}

    def serialize_task(self, task: CheckinTask) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "type_id": task.type_id,
            "status": task.status,
            "starts_at": task.starts_at.isoformat(),
            "ends_at": task.ends_at.isoformat(),
            "group_ids": self.repository.list_group_ids_for_task(task.id),
            "rules_snapshot": deepcopy(task.rules_snapshot_jsonb),
        }
