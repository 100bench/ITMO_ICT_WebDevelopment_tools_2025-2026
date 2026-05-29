"""Файл содержит API для анализа затраченного времени."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.domain import time_by_project, time_by_task
from app.schemas.analytics import TimeByProject, TimeByTask

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/time-by-task", response_model=list[TimeByTask])
def read_time_by_task(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TimeByTask]:
    return [TimeByTask(task_id=row[0], task_title=row[1], total_minutes=row[2]) for row in time_by_task(db, user.id)]


@router.get("/time-by-project", response_model=list[TimeByProject])
def read_time_by_project(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TimeByProject]:
    return [
        TimeByProject(project_id=row[0], project_title=row[1], total_minutes=row[2])
        for row in time_by_project(db, user.id)
    ]
