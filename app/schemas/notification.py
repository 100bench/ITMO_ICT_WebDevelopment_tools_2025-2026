"""Файл описывает схемы уведомлений о дедлайнах и событиях."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.task import TaskRead


class NotificationCreate(BaseModel):
    task_id: int | None = None
    message: str = Field(min_length=1, max_length=255)
    notify_at: datetime


class NotificationUpdate(BaseModel):
    message: str | None = Field(default=None, min_length=1, max_length=255)
    notify_at: datetime | None = None
    is_read: bool | None = None


class NotificationRead(ORMModel):
    id: int
    task_id: int | None
    message: str
    notify_at: datetime
    is_read: bool
    task: TaskRead | None
