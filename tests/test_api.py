"""Тесты проверяют авторизацию и основной сценарий работы с задачей."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "full_name": "Test User", "password": "secret123"},
    )
    response = client.post("/auth/login", json={"email": "user@example.com", "password": "secret123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_login_and_me(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_task_with_tag_and_time_entry(client: TestClient) -> None:
    headers = auth_headers(client)
    project_id = client.post("/projects", headers=headers, json={"title": "Study"}).json()["id"]
    tag_id = client.post("/tags", headers=headers, json={"name": "Important", "color": "#ef4444"}).json()["id"]

    task_response = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Prepare lab", "project_id": project_id, "priority": "high"},
    )
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    link_response = client.post(
        f"/tasks/{task_id}/tags",
        headers=headers,
        json={"tag_id": tag_id, "relation_type": "topic"},
    )
    assert link_response.status_code == 201

    time_response = client.post(
        "/time-entries",
        headers=headers,
        json={
            "task_id": task_id,
            "started_at": "2026-05-28T10:00:00+03:00",
            "finished_at": "2026-05-28T11:30:00+03:00",
        },
    )
    assert time_response.status_code == 201
    assert time_response.json()["minutes"] == 90

    detail_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["total_minutes"] == 90
    assert detail_response.json()["tag_links"][0]["relation_type"] == "topic"
