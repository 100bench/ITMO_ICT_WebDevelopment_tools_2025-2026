# Лабораторная работа 3: Docker, источники данных и очередь

FastAPI-приложение, PostgreSQL и парсер из лабораторной 2 упакованы в отдельные контейнеры. Прямой запрос к парсеру проходит через его HTTP API, а фоновый — через очередь Celery и Redis.

## Сервисы

| Сервис | Назначение | Порт хоста |
| --- | --- | ---: |
| `api` | Основной Time Manager API | 8000 |
| `parser` | Отдельное FastAPI-приложение парсера | 8001 |
| `postgres` | Общая БД приложения и парсера | 5432 |
| `redis` | Брокер Celery и хранилище результатов | 6379 |
| `celery-worker` | Фоновая обработка URL | — |

## Запуск

```bash
docker compose up -d --build
docker compose ps
```

Миграции применяет контейнер `api` до запуска Uvicorn. Проверка журналов:

```bash
docker compose logs -f api parser celery-worker
```

После запуска доступны:

- основной Swagger UI: http://localhost:8000/docs;
- Swagger парсера: http://localhost:8001/docs;
- healthcheck API: http://localhost:8000/health;
- healthcheck парсера: http://localhost:8001/health.

## Прямой вызов парсера

Защищенный маршрут `POST /parser/parse` принимает URL от клиента. Основной API добавляет идентификатор текущего пользователя и служебный токен, отправляет запрос контейнеру `parser`, получает результат и возвращает его клиенту. Заголовок сохраняется в `parsed_pages`.

```json
{
  "url": "https://example.com"
}
```

## Вызов через Celery

1. `POST /parser/tasks` принимает тот же JSON и возвращает HTTP 202 с `task_id`.
2. Основной API помещает задачу `parser.parse_url` в Redis.
3. `celery-worker` загружает страницу и сохраняет результат в PostgreSQL.
4. `GET /parser/tasks/{task_id}` возвращает `PENDING`, `STARTED`, `SUCCESS` или `FAILURE`.
5. `GET /parsed-pages` показывает все сохраненные текущим пользователем страницы.

Пример ответа при постановке задачи:

```json
{
  "task_id": "99845b80-8e31-4d5d-9fae-cf7d76f33b57",
  "status": "PENDING"
}
```

## Изоляция сервисов

- Основное приложение собирается по корневому `Dockerfile`.
- Парсер собирается по `parser_service/Dockerfile`.
- Оба контейнера используют один образный контекст и одинаковые версии зависимостей.
- API, парсер и Celery worker работают от непривилегированного пользователя `appuser`.
- Парсер проверяет внутренний заголовок `X-Parser-Token`; значение задается через `PARSER_SERVICE_TOKEN`.
- Для реального развертывания пароли PostgreSQL, JWT-секрет и служебный токен нужно заменить и вынести из `.env.example`.

## Остановка

```bash
docker compose down
```

Чтобы также удалить демонстрационные данные PostgreSQL:

```bash
docker compose down -v
```

## Проверка

```bash
python -m pytest -q
docker compose config --quiet
alembic upgrade head --sql
```
