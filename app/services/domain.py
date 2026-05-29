"""Файл содержит бизнес-правила для задач, времени, расписаний и уведомлений."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Task
from app.repositories.domain import get_project, get_tag, get_task


def ensure_project_access(db: Session, project_id: int | None, owner_id: int) -> None:
    if project_id is not None and not get_project(db, project_id, owner_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def ensure_task_access(db: Session, task_id: int | None, owner_id: int) -> Task | None:
    if task_id is None:
        return None
    task = get_task(db, task_id, owner_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def ensure_tag_access(db: Session, tag_id: int, owner_id: int) -> None:
    if not get_tag(db, tag_id, owner_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


# Функция рассчитывает длительность записи, если пользователь не передал минуты вручную.
def calculate_minutes(started_at: datetime, finished_at: datetime | None, minutes: int) -> int:
    if minutes > 0 or finished_at is None:
        return minutes
    return max(int((finished_at - started_at).total_seconds() // 60), 0)
