"""Файл описывает схемы проектов."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class ProjectRead(ORMModel):
    id: int
    title: str
    description: str | None
    created_at: datetime
