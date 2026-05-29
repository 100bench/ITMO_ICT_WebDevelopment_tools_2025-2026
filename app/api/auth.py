"""Файл содержит эндпоинты регистрации и авторизации."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import TokenResponse, UserLogin, UserRegister
from app.schemas.user import UserRead
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    return register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    token = login_user(db, data.email, data.password)
    return TokenResponse(access_token=token)
