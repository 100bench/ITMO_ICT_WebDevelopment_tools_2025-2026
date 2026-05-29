"""Файл содержит CRUD API для тегов."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Tag, User
from app.repositories.domain import get_tag, list_tags
from app.schemas.common import MessageResponse
from app.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("", response_model=TagRead, status_code=201)
def create_tag(data: TagCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TagRead:
    tag = Tag(owner_id=user.id, **data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("", response_model=list[TagRead])
def read_tags(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TagRead]:
    return list_tags(db, user.id)


@router.get("/{tag_id}", response_model=TagRead)
def read_tag(tag_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TagRead:
    tag = get_tag(db, tag_id, user.id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, data: TagUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TagRead:
    tag = get_tag(db, tag_id, user.id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tag, key, value)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=MessageResponse)
def delete_tag(tag_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MessageResponse:
    tag = get_tag(db, tag_id, user.id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return MessageResponse(detail="Tag deleted")
