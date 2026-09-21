from contextlib import asynccontextmanager

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from database.db import init_db, save_page


class ParseRequest(BaseModel):
    url: HttpUrl


@asynccontextmanager
async def lifespan(_: FastAPI):
    # инициализация выполняется до приёма первого запроса
    init_db()
    yield


app = FastAPI(title="Parser service", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
def parse_page(data: ParseRequest) -> dict[str, str | int]:
    url = str(data.url)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    tag = BeautifulSoup(response.text, "html.parser").title
    title = tag.get_text(strip=True) if tag else "Без заголовка"
    page_id = save_page(url, title)
    return {"id": page_id, "url": url, "title": title}

