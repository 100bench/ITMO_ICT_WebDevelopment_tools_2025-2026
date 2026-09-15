"""Схемы HTTP-вызова парсера и фоновой Celery-задачи."""

from typing import Any

from pydantic import AnyHttpUrl, BaseModel, Field

from app.schemas.parsed_page import ParsedPageRead


class ParsePageRequest(BaseModel):
    url: AnyHttpUrl


class InternalParsePageRequest(ParsePageRequest):
    owner_id: int = Field(gt=0)


class QueuedParseResponse(BaseModel):
    task_id: str
    status: str = "PENDING"


class ParseTaskStatus(BaseModel):
    task_id: str
    status: str
    result: ParsedPageRead | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None
