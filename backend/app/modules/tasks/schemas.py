from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    title: str
    type_id: int
    group_ids: list[int]
    starts_at: str
    ends_at: str
    rules_snapshot: dict
