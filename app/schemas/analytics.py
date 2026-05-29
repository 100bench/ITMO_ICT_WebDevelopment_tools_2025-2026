"""Файл описывает ответы аналитики по затраченному времени."""

from pydantic import BaseModel


class TimeByTask(BaseModel):
    task_id: int
    task_title: str
    total_minutes: int


class TimeByProject(BaseModel):
    project_id: int | None
    project_title: str | None
    total_minutes: int
