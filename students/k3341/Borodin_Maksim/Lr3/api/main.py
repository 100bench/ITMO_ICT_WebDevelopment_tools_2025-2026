import os

import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl

from worker.celery_app import celery_app, parse_url


PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")


class ParseRequest(BaseModel):
    url: HttpUrl


app = FastAPI(title="Lab 3 API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
async def parse_direct(data: ParseRequest) -> dict:
    try:
        # parser — dns-имя сервиса внутри сети compose
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{PARSER_URL}/parse",
                json={"url": str(data.url)},
            )
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return response.json()


@app.post("/parse/async", status_code=status.HTTP_202_ACCEPTED)
def parse_in_background(data: ParseRequest) -> dict[str, str]:
    # delay публикует задачу в redis и сразу возвращает управление
    task = parse_url.delay(str(data.url))
    return {"task_id": task.id, "status": task.status}


@app.get("/tasks/{task_id}")
def task_status(task_id: str) -> dict:
    task = celery_app.AsyncResult(task_id)
    answer = {"task_id": task_id, "status": task.status}
    if task.successful():
        answer["result"] = task.result
    elif task.failed():
        answer["error"] = str(task.result)
    return answer

