"""Файл описывает схемы тегов и связи задачи с тегом."""

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(default="#64748b", max_length=20)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    color: str | None = Field(default=None, max_length=20)


class TagRead(ORMModel):
    id: int
    name: str
    color: str


class TaskTagCreate(BaseModel):
    tag_id: int
    relation_type: str = Field(default="default", max_length=50)


class TaskTagUpdate(BaseModel):
    relation_type: str = Field(min_length=1, max_length=50)


class TaskTagRead(ORMModel):
    tag: TagRead
    relation_type: str
