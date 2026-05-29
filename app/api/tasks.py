"""Файл содержит CRUD API для задач и управление тегами задачи."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Task, TaskTag, User
from app.repositories.domain import get_task, get_task_tag, list_tasks
from app.schemas.common import MessageResponse
from app.schemas.tag import TaskTagCreate, TaskTagRead, TaskTagUpdate
from app.schemas.task import TaskCreate, TaskDetail, TaskRead, TaskUpdate
from app.services.domain import ensure_project_access, ensure_tag_access

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _set_total_minutes(task: Task) -> Task:
    task.total_minutes = sum(entry.minutes for entry in task.time_entries)
    return task


@router.post("", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskRead:
    ensure_project_access(db, data.project_id, user.id)
    task = Task(owner_id=user.id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def read_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TaskRead]:
    return list_tasks(db, user.id)


@router.get("/{task_id}", response_model=TaskDetail)
def read_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskDetail:
    task = get_task(db, task_id, user.id, detailed=True)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return _set_total_minutes(task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TaskRead:
    task = get_task(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    values = data.model_dump(exclude_unset=True)
    ensure_project_access(db, values.get("project_id"), user.id)
    for key, value in values.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MessageResponse:
    task = get_task(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
    return MessageResponse(detail="Task deleted")


@router.post("/{task_id}/tags", response_model=TaskTagRead, status_code=201)
def add_task_tag(
    task_id: int,
    data: TaskTagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TaskTagRead:
    if not get_task(db, task_id, user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    ensure_tag_access(db, data.tag_id, user.id)
    link = get_task_tag(db, task_id, data.tag_id)
    if link:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already linked")
    link = TaskTag(task_id=task_id, tag_id=data.tag_id, relation_type=data.relation_type)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.patch("/{task_id}/tags/{tag_id}", response_model=TaskTagRead)
def update_task_tag(
    task_id: int,
    tag_id: int,
    data: TaskTagUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TaskTagRead:
    if not get_task(db, task_id, user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    ensure_tag_access(db, tag_id, user.id)
    link = get_task_tag(db, task_id, tag_id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task tag not found")
    link.relation_type = data.relation_type
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{task_id}/tags/{tag_id}", response_model=MessageResponse)
def delete_task_tag(
    task_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    if not get_task(db, task_id, user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    link = get_task_tag(db, task_id, tag_id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task tag not found")
    db.delete(link)
    db.commit()
    return MessageResponse(detail="Task tag deleted")
