# Лабораторная работа 1. FastAPI Time Manager

**Студент:** Бородин М. А.<br>
**Группа:** К3341<br>
**Тема:** Тайм-менеджер для задач, проектов, учета времени, расписания и уведомлений.<br>
**Код лабораторной:** [`lab-1`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-1)

## Цель

Реализовать серверное приложение на FastAPI с PostgreSQL, ORM SQLAlchemy, миграциями Alembic и JWT-аутентификацией.

Приложение позволяет:

- регистрировать и авторизовывать пользователей;
- создавать проекты, задачи и теги;
- задавать задачам дедлайны, приоритеты и статусы;
- связывать задачи и теги через many-to-many связь;
- учитывать затраченное время;
- создавать ежедневное расписание;
- хранить уведомления;
- получать аналитику по времени.

## Технологии

- **FastAPI** — HTTP API и Swagger UI.
- **SQLAlchemy** — ORM для PostgreSQL.
- **PostgreSQL** — основная база данных.
- **Alembic** — миграции схемы БД.
- **Pydantic** — схемы входных и выходных данных.
- **bcrypt** — хэширование паролей.
- **JWT HMAC-SHA256** — ручная реализация токенов.
- **Docker Compose** — запуск API и БД.
- **pytest** — минимальные тесты.

## Структура проекта

```text
app/
  api/             # FastAPI endpoints
  core/            # Настройки, БД, JWT, пароли
  models/          # SQLAlchemy-модели
  repositories/    # Запросы к БД
  schemas/         # Pydantic-схемы
  services/        # Бизнес-логика
  main.py          # Точка входа приложения
alembic/
  versions/        # Миграции
tests/             # Тесты
postman/           # Postman collection
```

## Модели данных

В проекте реализовано больше пяти таблиц:

| Таблица | Назначение |
| --- | --- |
| `users` | Пользователи |
| `projects` | Проекты пользователя |
| `tasks` | Задачи |
| `tags` | Теги |
| `task_tags` | Ассоциативная таблица задач и тегов |
| `time_entries` | Записи учета времени |
| `daily_schedules` | Расписание на день |
| `schedule_items` | Элементы расписания |
| `notifications` | Уведомления |

Основные связи:

- `users -> projects` — one-to-many.
- `users -> tasks` — one-to-many.
- `projects -> tasks` — one-to-many.
- `tasks -> time_entries` — one-to-many.
- `daily_schedules -> schedule_items` — one-to-many.
- `tasks <-> tags` — many-to-many через `task_tags`.

Ассоциативная таблица `task_tags` содержит дополнительное поле `relation_type`, которое характеризует связь задачи и тега.

```python
class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    tag_id = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    relation_type = mapped_column(String(50), default="default", nullable=False)
```

## Подключение к БД

Подключение к PostgreSQL находится в `app/core/database.py`.

```python
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Настройки читаются из `.env` через `pydantic-settings`.

```python
class Settings(BaseSettings):
    app_name: str = "Time Manager API"
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int
```

## Миграции

Alembic настроен в:

- `alembic.ini`;
- `alembic/env.py`;
- `alembic/versions/20260528_0001_initial.py`.

Применение миграций:

```bash
alembic upgrade head
```

В начальной миграции создаются таблицы и демонстрационные данные.

Демо-пользователь для защиты:

```text
email: demo@example.com
password: demo123
```

## Авторизация

Реализовано:

- регистрация;
- вход;
- генерация JWT;
- ручная проверка JWT;
- bcrypt-хэширование паролей;
- получение текущего пользователя;
- список пользователей;
- смена пароля.

В Swagger нужно выполнить `POST /auth/login`, скопировать `access_token`, нажать `Authorize` и вставить токен без слова `Bearer`.

## Эндпоинты

### Auth

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/auth/register` | Регистрация |
| `POST` | `/auth/login` | Вход и получение JWT |

### Users

| Метод | URL | Назначение |
| --- | --- | --- |
| `GET` | `/users/me` | Текущий пользователь |
| `GET` | `/users` | Список пользователей |
| `PATCH` | `/users/me/password` | Смена пароля |

### Projects

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/projects` | Создание проекта |
| `GET` | `/projects` | Список проектов |
| `GET` | `/projects/{project_id}` | Получение проекта |
| `PATCH` | `/projects/{project_id}` | Обновление проекта |
| `DELETE` | `/projects/{project_id}` | Удаление проекта |

### Tasks

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/tasks` | Создание задачи |
| `GET` | `/tasks` | Список задач |
| `GET` | `/tasks/{task_id}` | Задача с вложенными объектами |
| `PATCH` | `/tasks/{task_id}` | Обновление задачи |
| `DELETE` | `/tasks/{task_id}` | Удаление задачи |
| `POST` | `/tasks/{task_id}/tags` | Добавление тега к задаче |
| `PATCH` | `/tasks/{task_id}/tags/{tag_id}` | Обновление поля `relation_type` |
| `DELETE` | `/tasks/{task_id}/tags/{tag_id}` | Удаление тега у задачи |

### Tags

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/tags` | Создание тега |
| `GET` | `/tags` | Список тегов |
| `GET` | `/tags/{tag_id}` | Получение тега |
| `PATCH` | `/tags/{tag_id}` | Обновление тега |
| `DELETE` | `/tags/{tag_id}` | Удаление тега |

### Time Entries

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/time-entries` | Создание записи времени |
| `GET` | `/time-entries` | Список записей |
| `GET` | `/time-entries/{entry_id}` | Получение записи |
| `PATCH` | `/time-entries/{entry_id}` | Обновление записи |
| `DELETE` | `/time-entries/{entry_id}` | Удаление записи |

### Schedules

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/schedules` | Создание расписания |
| `GET` | `/schedules` | Список расписаний |
| `GET` | `/schedules/{schedule_id}` | Получение расписания |
| `PATCH` | `/schedules/{schedule_id}` | Обновление расписания |
| `POST` | `/schedules/{schedule_id}/items` | Добавление пункта |
| `DELETE` | `/schedules/{schedule_id}` | Удаление расписания |

### Notifications

| Метод | URL | Назначение |
| --- | --- | --- |
| `POST` | `/notifications` | Создание уведомления |
| `GET` | `/notifications` | Список уведомлений |
| `GET` | `/notifications/{notification_id}` | Получение уведомления |
| `PATCH` | `/notifications/{notification_id}` | Обновление уведомления |
| `DELETE` | `/notifications/{notification_id}` | Удаление уведомления |

### Analytics

| Метод | URL | Назначение |
| --- | --- | --- |
| `GET` | `/analytics/time-by-task` | Время по задачам |
| `GET` | `/analytics/time-by-project` | Время по проектам |

## Что показать на защите

1. `POST /auth/login` — войти под `demo@example.com / demo123`.
2. Swagger `Authorize` — вставить JWT.
3. `GET /users/me` — показать текущего пользователя.
4. `GET /tasks/1` — показать вложенные объекты и `total_minutes`.
5. `PATCH /tasks/1/tags/1` — показать many-to-many связь и поле `relation_type`.
6. `GET /analytics/time-by-task` — показать аналитику времени.
7. `GET /schedules` и `GET /notifications` — показать дополнительные функции.

## Запуск

```bash
docker compose up -d --build
```

Swagger UI:

```text
http://localhost:8000/docs
```

Локальный запуск:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Проверка

```bash
python -m pytest -q
alembic upgrade head --sql
```

Postman collection находится в ветке `lab-1`:

```text
postman/time_manager_lab1.postman_collection.json
```
