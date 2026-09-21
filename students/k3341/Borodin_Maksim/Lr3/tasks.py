import os

import requests
from celery import Celery


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")

celery_app = Celery("lab3", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.broker_connection_retry_on_startup = True


@celery_app.task(name="parse_url")
def parse_url(url: str) -> dict:
    response = requests.post(
        f"{PARSER_URL}/parse",
        json={"url": url},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()
