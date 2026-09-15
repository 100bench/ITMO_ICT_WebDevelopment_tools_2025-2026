"""Просмотр заголовков, сохраненных парсерами лабораторной работы 2."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.domain import get_parsed_page, list_parsed_pages
from app.schemas.parsed_page import ParsedPageRead

router = APIRouter(prefix="/parsed-pages", tags=["Parsed pages"])


@router.get("", response_model=list[ParsedPageRead])
def read_parsed_pages(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ParsedPageRead]:
    return list_parsed_pages(db, user.id)


@router.get("/{page_id}", response_model=ParsedPageRead)
def read_parsed_page(
    page_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ParsedPageRead:
    page = get_parsed_page(db, page_id, user.id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parsed page not found")
    return page
