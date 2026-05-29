"""Файл содержит CRUD API для ежедневного расписания."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import DailySchedule, ScheduleItem, User
from app.repositories.domain import get_schedule, list_schedules
from app.schemas.common import MessageResponse
from app.schemas.schedule import DailyScheduleCreate, DailyScheduleRead, DailyScheduleUpdate, ScheduleItemCreate, ScheduleItemRead
from app.services.domain import ensure_task_access

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("", response_model=DailyScheduleRead, status_code=201)
def create_schedule(
    data: DailyScheduleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> DailyScheduleRead:
    for item in data.items:
        ensure_task_access(db, item.task_id, user.id)
    schedule = DailySchedule(owner_id=user.id, schedule_date=data.schedule_date, title=data.title)
    schedule.items = [ScheduleItem(**item.model_dump()) for item in data.items]
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return get_schedule(db, schedule.id, user.id)


@router.get("", response_model=list[DailyScheduleRead])
def read_schedules(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[DailyScheduleRead]:
    return list_schedules(db, user.id)


@router.get("/{schedule_id}", response_model=DailyScheduleRead)
def read_schedule(
    schedule_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> DailyScheduleRead:
    schedule = get_schedule(db, schedule_id, user.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule


@router.patch("/{schedule_id}", response_model=DailyScheduleRead)
def update_schedule(
    schedule_id: int,
    data: DailyScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DailyScheduleRead:
    schedule = get_schedule(db, schedule_id, user.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return get_schedule(db, schedule.id, user.id)


@router.post("/{schedule_id}/items", response_model=ScheduleItemRead, status_code=201)
def add_schedule_item(
    schedule_id: int,
    data: ScheduleItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScheduleItemRead:
    schedule = get_schedule(db, schedule_id, user.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    ensure_task_access(db, data.task_id, user.id)
    item = ScheduleItem(schedule_id=schedule_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{schedule_id}", response_model=MessageResponse)
def delete_schedule(
    schedule_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MessageResponse:
    schedule = get_schedule(db, schedule_id, user.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
    return MessageResponse(detail="Schedule deleted")
