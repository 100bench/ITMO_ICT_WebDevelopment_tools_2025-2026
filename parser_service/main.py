"""FastAPI-сервис для синхронного запуска парсера в отдельном контейнере."""

from functools import partial
from secrets import compare_digest

import requests
from fastapi import FastAPI, Header, HTTPException, status

from app.core.config import settings
from app.schemas.parsed_page import ParsedPageRead
from app.schemas.parser import InternalParsePageRequest
from lab2.common import parse_sync, save_parsed_page

app = FastAPI(title="Time Manager Parser Service")


@app.get("/health", tags=["System"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse", response_model=ParsedPageRead, tags=["Parser"])
def parse_page(
    data: InternalParsePageRequest,
    parser_token: str = Header(alias="X-Parser-Token"),
) -> ParsedPageRead:
    if not compare_digest(parser_token, settings.parser_service_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid parser service token")
    try:
        saver = partial(save_parsed_page, owner_id=data.owner_id)
        return ParsedPageRead.model_validate(parse_sync(str(data.url), "http", saver=saver))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not fetch page: {exc}") from exc
