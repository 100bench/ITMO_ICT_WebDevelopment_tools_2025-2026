"""Файл описывает схемы учета времени по задачам."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class TimeEntryBase(BaseModel):
    started_at: datetime
    finished_at: datetime | None = None
    minutes: int = Field(default=0, ge=0)
    note: str | None = None

    # Валидатор не дает сохранить отрицательный интервал времени.
    @model_validator(mode="after")
    def validate_interval(self) -> "TimeEntryBase":
        if self.finished_at and self.finished_at < self.started_at:
            raise ValueError("finished_at must be greater than started_at")
        return self


class TimeEntryCreate(TimeEntryBase):
    task_id: int


class TimeEntryUpdate(BaseModel):
    started_at: datetime | None = None
    finished_at: datetime | None = None
    minutes: int | None = Field(default=None, ge=0)
    note: str | None = None


class TimeEntryRead(ORMModel):
    id: int
    task_id: int
    started_at: datetime
    finished_at: datetime | None
    minutes: int
    note: str | None
