"""Файл описывает схемы задач и вложенный ответ с проектом, тегами и временем."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import TaskPriority, TaskStatus
from app.schemas.common import ORMModel
from app.schemas.project import ProjectRead
from app.schemas.tag import TaskTagRead
from app.schemas.time_entry import TimeEntryRead


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    deadline: datetime | None = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo
    project_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    deadline: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    project_id: int | None = None


class TaskRead(ORMModel):
    id: int
    title: str
    description: str | None
    deadline: datetime | None
    priority: TaskPriority
    status: TaskStatus
    project_id: int | None
    created_at: datetime


class TaskDetail(TaskRead):
    project: ProjectRead | None
    tag_links: list[TaskTagRead]
    time_entries: list[TimeEntryRead]
    total_minutes: int
