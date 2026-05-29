# Лабораторная работа 1: Time Manager API

Серверное приложение на FastAPI для управления задачами, сроками, приоритетами, учетом времени, расписанием и уведомлениями.

## Запуск через Docker Compose

```bash
docker compose up -d --build
```

После запуска:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: `localhost:5432`

Миграции Alembic применяются автоматически при старте контейнера `api`.

## Локальный запуск без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Основные эндпоинты

- `POST /auth/register` — регистрация.
- `POST /auth/login` — вход и получение JWT.
- `GET /users/me` — текущий пользователь.
- `GET /users` — список пользователей.
- `PATCH /users/me/password` — смена пароля.
- `/projects` — CRUD проектов.
- `/tasks` — CRUD задач.
- `/tasks/{task_id}/tags` — many-to-many связь задач и тегов с полем `relation_type`.
- `/tags` — CRUD тегов.
- `/time-entries` — CRUD учета времени.
- `/schedules` — ежедневное расписание.
- `/notifications` — уведомления.
- `/analytics/time-by-task` — анализ времени по задачам.
- `/analytics/time-by-project` — анализ времени по проектам.

## Проверка

```bash
python -m pytest -q
alembic upgrade head --sql
```
