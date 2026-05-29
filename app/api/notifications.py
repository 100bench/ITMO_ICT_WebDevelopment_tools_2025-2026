"""Файл содержит CRUD API для уведомлений о приближении дедлайнов."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Notification, User
from app.repositories.domain import get_notification, list_notifications
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from app.services.domain import ensure_task_access

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", response_model=NotificationRead, status_code=201)
def create_notification(
    data: NotificationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> NotificationRead:
    ensure_task_access(db, data.task_id, user.id)
    notification = Notification(owner_id=user.id, **data.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return get_notification(db, notification.id, user.id)


@router.get("", response_model=list[NotificationRead])
def read_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[NotificationRead]:
    return list_notifications(db, user.id)


@router.get("/{notification_id}", response_model=NotificationRead)
def read_notification(
    notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> NotificationRead:
    notification = get_notification(db, notification_id, user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.patch("/{notification_id}", response_model=NotificationRead)
def update_notification(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NotificationRead:
    notification = get_notification(db, notification_id, user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(notification, key, value)
    db.commit()
    db.refresh(notification)
    return get_notification(db, notification.id, user.id)


@router.delete("/{notification_id}", response_model=MessageResponse)
def delete_notification(
    notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MessageResponse:
    notification = get_notification(db, notification_id, user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return MessageResponse(detail="Notification deleted")
