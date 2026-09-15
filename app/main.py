"""Файл создает FastAPI-приложение и подключает все роутеры лабораторной работы."""

from fastapi import FastAPI

from app.api import analytics, auth, notifications, parsed_pages, projects, schedules, tags, tasks, time_entries, users
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.router)
app.include_router(time_entries.router)
app.include_router(schedules.router)
app.include_router(notifications.router)
app.include_router(analytics.router)
app.include_router(parsed_pages.router)


@app.get("/health", tags=["System"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
