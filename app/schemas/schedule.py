"""Файл описывает схемы ежедневного расписания."""

from datetime import date, time

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.task import TaskRead


class ScheduleItemBase(BaseModel):
    task_id: int | None = None
    start_time: time
    end_time: time
    comment: str | None = None


class ScheduleItemCreate(ScheduleItemBase):
    pass


class ScheduleItemRead(ORMModel):
    id: int
    task_id: int | None
    start_time: time
    end_time: time
    comment: str | None
    task: TaskRead | None


class DailyScheduleCreate(BaseModel):
    schedule_date: date
    title: str = Field(min_length=1, max_length=120)
    items: list[ScheduleItemCreate] = []


class DailyScheduleUpdate(BaseModel):
    schedule_date: date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=120)


class DailyScheduleRead(ORMModel):
    id: int
    schedule_date: date
    title: str
    items: list[ScheduleItemRead]
