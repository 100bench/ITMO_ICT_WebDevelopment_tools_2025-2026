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

## Авторизация в Swagger

1. Выполнить `POST /auth/register`.
2. Выполнить `POST /auth/login` и скопировать `access_token`.
3. Нажать кнопку `Authorize` в Swagger UI.
4. Вставить токен в поле Bearer-авторизации без слова `Bearer`.

Все рабочие методы, кроме `/health`, `/auth/register` и `/auth/login`, защищены JWT.

## Данные для демонстрации

После применения миграций в базе уже есть пользователь для защиты:

```text
email: demo@example.com
password: demo123
```

Для него заранее созданы проекты, задачи, теги, связи many-to-many, записи учета времени, расписание и уведомления.

## Postman

Коллекция для проверки основных сценариев находится в файле:

```text
postman/time_manager_lab1.postman_collection.json
```

В Postman нужно импортировать коллекцию и запустить запросы по порядку. Коллекция сама сохраняет JWT и идентификаторы созданных проекта, тега, задачи, записи времени, расписания и уведомления.

## Проверка

```bash
python -m pytest -q
alembic upgrade head --sql
```
