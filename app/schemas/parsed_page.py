"""Схемы сохраненного результата парсинга веб-страницы."""

from datetime import datetime

from app.schemas.common import ORMModel


class ParsedPageRead(ORMModel):
    id: int
    url: str
    title: str
    approach: str
    duration_ms: int
    fetched_at: datetime
