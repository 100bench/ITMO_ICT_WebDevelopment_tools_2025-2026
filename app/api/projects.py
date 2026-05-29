"""Файл содержит CRUD API для проектов."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Project, User
from app.repositories.domain import get_project, list_projects
from app.schemas.common import MessageResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProjectRead:
    project = Project(owner_id=user.id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def read_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ProjectRead]:
    return list_projects(db, user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def read_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProjectRead:
    project = get_project(db, project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ProjectRead:
    project = get_project(db, project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MessageResponse:
    project = get_project(db, project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()
    return MessageResponse(detail="Project deleted")
