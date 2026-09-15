"""Настройка Celery для очереди парсинга."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "time_manager",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.parser"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
    timezone="Europe/Moscow",
    enable_utc=True,
)
