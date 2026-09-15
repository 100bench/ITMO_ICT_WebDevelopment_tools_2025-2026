"""Проверки HTTP-сервиса парсера и маршрутов лабораторной работы 3."""

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import parser as parser_api
from app.api.deps import get_current_user
from app.main import app
from app.models import User
from lab2.common import ParseResult
from parser_service import main as parser_service


def parsed_result(approach: str = "http") -> ParseResult:
    return ParseResult(
        id=42,
        url="https://example.com/",
        title="Example Domain",
        approach=approach,
        duration_ms=125,
        fetched_at=datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc),
    )


def current_user() -> User:
    return User(id=7, email="user@example.com", full_name="Test User", password_hash="not-used")


def test_parser_service_requires_internal_token(monkeypatch) -> None:
    monkeypatch.setattr(parser_service, "parse_sync", lambda *args, **kwargs: parsed_result())
    with TestClient(parser_service.app) as client:
        response = client.post(
            "/parse",
            headers={"X-Parser-Token": "wrong"},
            json={"url": "https://example.com", "owner_id": 7},
        )
    assert response.status_code == 401


def test_parser_service_returns_saved_page(monkeypatch) -> None:
    monkeypatch.setattr(parser_service, "parse_sync", lambda *args, **kwargs: parsed_result())
    with TestClient(parser_service.app) as client:
        response = client.post(
            "/parse",
            headers={"X-Parser-Token": "change-me-parser-token"},
            json={"url": "https://example.com", "owner_id": 7},
        )
    assert response.status_code == 200
    assert response.json()["title"] == "Example Domain"


def test_main_api_forwards_direct_parse_for_current_user(monkeypatch) -> None:
    seen: dict[str, object] = {}

    async def fake_request(url: str, owner_id: int):
        seen.update(url=url, owner_id=owner_id)
        return parsed_result()

    monkeypatch.setattr(parser_api, "request_parser_service", fake_request)
    app.dependency_overrides[get_current_user] = current_user
    try:
        with TestClient(app) as client:
            response = client.post("/parser/parse", json={"url": "https://example.com"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert seen == {"url": "https://example.com/", "owner_id": 7}


def test_main_api_enqueues_parse(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def fake_delay(url: str, owner_id: int):
        seen.update(url=url, owner_id=owner_id)
        return SimpleNamespace(id="task-123")

    monkeypatch.setattr(parser_api.parse_url_task, "delay", fake_delay)
    app.dependency_overrides[get_current_user] = current_user
    try:
        with TestClient(app) as client:
            response = client.post("/parser/tasks", json={"url": "https://example.com"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json() == {"task_id": "task-123", "status": "PENDING"}
    assert seen == {"url": "https://example.com/", "owner_id": 7}


def test_task_status_returns_success_result(monkeypatch) -> None:
    result = {
        "id": 42,
        "url": "https://example.com/",
        "title": "Example Domain",
        "approach": "celery",
        "duration_ms": 125,
        "fetched_at": "2026-09-15T10:00:00Z",
        "owner_id": 7,
    }
    fake_task = SimpleNamespace(state="SUCCESS", result=result, info=None)
    monkeypatch.setattr(parser_api.celery_app, "AsyncResult", lambda task_id: fake_task)
    app.dependency_overrides[get_current_user] = current_user
    try:
        with TestClient(app) as client:
            response = client.get("/parser/tasks/task-123")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["result"]["approach"] == "celery"
