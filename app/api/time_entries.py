"""Файл содержит CRUD API для учета времени по задачам."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import TimeEntry, User
from app.repositories.domain import get_time_entry, list_time_entries
from app.schemas.common import MessageResponse
from app.schemas.time_entry import TimeEntryCreate, TimeEntryRead, TimeEntryUpdate
from app.services.domain import calculate_minutes, ensure_task_access

router = APIRouter(prefix="/time-entries", tags=["Time entries"])


@router.post("", response_model=TimeEntryRead, status_code=201)
def create_time_entry(
    data: TimeEntryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> TimeEntryRead:
    ensure_task_access(db, data.task_id, user.id)
    values = data.model_dump()
    values["minutes"] = calculate_minutes(data.started_at, data.finished_at, data.minutes)
    entry = TimeEntry(**values)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[TimeEntryRead])
def read_time_entries(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TimeEntryRead]:
    return list_time_entries(db, user.id)


@router.get("/{entry_id}", response_model=TimeEntryRead)
def read_time_entry(entry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TimeEntryRead:
    entry = get_time_entry(db, entry_id, user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    return entry


@router.patch("/{entry_id}", response_model=TimeEntryRead)
def update_time_entry(
    entry_id: int,
    data: TimeEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TimeEntryRead:
    entry = get_time_entry(db, entry_id, user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    entry.minutes = calculate_minutes(entry.started_at, entry.finished_at, entry.minutes)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", response_model=MessageResponse)
def delete_time_entry(
    entry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MessageResponse:
    entry = get_time_entry(db, entry_id, user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    db.delete(entry)
    db.commit()
    return MessageResponse(detail="Time entry deleted")
