"""API-прокси для прямого и поставленного в очередь запуска парсера."""

from typing import Any

import httpx
from celery.states import FAILURE, SUCCESS
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.celery_app import celery_app
from app.core.config import settings
from app.models import User
from app.schemas.parsed_page import ParsedPageRead
from app.schemas.parser import ParsePageRequest, ParseTaskStatus, QueuedParseResponse
from app.tasks.parser import parse_url_task

router = APIRouter(prefix="/parser", tags=["Parser"])


async def request_parser_service(url: str, owner_id: int) -> ParsedPageRead:
    endpoint = f"{settings.parser_service_url.rstrip('/')}/parse"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                endpoint,
                json={"url": url, "owner_id": owner_id},
                headers={"X-Parser-Token": settings.parser_service_token},
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Parser service unavailable: {exc}") from exc
    return ParsedPageRead.model_validate(response.json())


@router.post("/parse", response_model=ParsedPageRead)
async def parse_page(data: ParsePageRequest, user: User = Depends(get_current_user)) -> ParsedPageRead:
    return await request_parser_service(str(data.url), user.id)


@router.post("/tasks", response_model=QueuedParseResponse, status_code=status.HTTP_202_ACCEPTED)
def enqueue_parse(data: ParsePageRequest, user: User = Depends(get_current_user)) -> QueuedParseResponse:
    task = parse_url_task.delay(str(data.url), user.id)
    return QueuedParseResponse(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=ParseTaskStatus)
def read_parse_task(task_id: str, user: User = Depends(get_current_user)) -> ParseTaskStatus:
    task = celery_app.AsyncResult(task_id)
    if task.state == SUCCESS:
        payload = dict(task.result)
        if payload.pop("owner_id", None) != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parse task not found")
        return ParseTaskStatus(task_id=task_id, status=task.state, result=ParsedPageRead.model_validate(payload))
    if task.state == FAILURE:
        return ParseTaskStatus(task_id=task_id, status=task.state, error=str(task.result))
    meta: dict[str, Any] | None = task.info if isinstance(task.info, dict) else None
    return ParseTaskStatus(task_id=task_id, status=task.state, meta=meta)
