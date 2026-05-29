"""Файл содержит бизнес-логику регистрации, входа и смены пароля."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.users import get_user_by_email
from app.schemas.auth import UserRegister


# Функция создает пользователя, если email еще не занят.
def register_user(db: Session, data: UserRegister) -> User:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=data.email, full_name=data.full_name, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Функция проверяет логин и пароль, затем выдает JWT.
def login_user(db: Session, email: str, password: str) -> str:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return create_access_token(str(user.id))


# Функция меняет пароль после проверки старого пароля.
def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    user.password_hash = hash_password(new_password)
    db.commit()
