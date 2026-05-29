"""Файл содержит эндпоинты пользователя и смены пароля."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.users import list_users
from app.schemas.common import MessageResponse
from app.schemas.user import PasswordChange, UserRead
from app.services.auth import change_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@router.get("", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[UserRead]:
    return list_users(db)


@router.patch("/me/password", response_model=MessageResponse)
def update_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    change_password(db, current_user, data.old_password, data.new_password)
    return MessageResponse(detail="Password changed")
