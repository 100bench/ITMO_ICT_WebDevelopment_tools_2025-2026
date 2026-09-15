"""Celery-задача загружает страницу и сохраняет результат в PostgreSQL."""

from functools import partial

import requests

from app.celery_app import celery_app
from app.schemas.parsed_page import ParsedPageRead
from lab2.common import parse_sync, save_parsed_page


@celery_app.task(
    bind=True,
    name="parser.parse_url",
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def parse_url_task(self: object, url: str, owner_id: int) -> dict[str, object]:
    saver = partial(save_parsed_page, owner_id=owner_id)
    result = parse_sync(url, "celery", saver=saver)
    payload = ParsedPageRead.model_validate(result).model_dump(mode="json")
    return {**payload, "owner_id": owner_id}
