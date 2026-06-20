from datetime import datetime

from pydantic import BaseModel

from api.modules.tasks.enums import Priority


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: Priority = Priority.medium
    category: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: Priority | None = None
    category: str | None = None
    is_done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    due_date: datetime | None
    priority: Priority | None
    category: str | None
    is_done: bool | None
    created_at: datetime
    updated_at: datetime

    mode_config = {"from_attributes": True}
