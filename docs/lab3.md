# Лабораторная работа 3. Docker, источники данных и очередь

**Студент:** Бородни М. А.  
**Группа:** К3341  
**Код лабораторной:** [`lab-3`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-3)  
**Коммит:** [`0fbbc91`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/0fbbc91)

## Цель

Упаковать Time Manager API, PostgreSQL и парсер в Docker; добавить вызов парсера через отдельный HTTP-сервис и фоновую очередь Celery/Redis.

Реализованы все три подзадачи:

1. отдельные контейнеры приложения, БД и парсера;
2. вызов парсера из основного FastAPI по HTTP;
3. асинхронный вызов через Redis и Celery worker с получением статуса.

## Архитектура

```text
                        прямой запрос
Client ──JWT──> API ───────────────────> Parser API ──┐
                  │                                   │
                  │ фоновая задача                    v
                  └────────> Redis ──> Celery ──> PostgreSQL
                                             сохранение parsed_pages
```

| Сервис Compose | Назначение | Порт хоста |
| --- | --- | ---: |
| `api` | основное FastAPI-приложение | 8000 |
| `parser` | отдельное FastAPI-приложение парсера | 8001 |
| `postgres` | общая БД Time Manager и парсера | 5432 |
| `redis` | брокер и backend результата Celery | 6379 |
| `celery-worker` | фоновая загрузка и сохранение страниц | — |

Оркестрация описана в [`docker-compose.yml`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/docker-compose.yml).

## Подзадача 1. Контейнеризация

Основной API и worker собираются по корневому [`Dockerfile`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/Dockerfile). Отдельный парсер собирается по [`parser_service/Dockerfile`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/parser_service/Dockerfile).

Оба Dockerfile:

1. используют `python:3.12-slim`;
2. устанавливают зафиксированные версии из `requirements.txt`;
3. копируют исходный код;
4. переключаются на непривилегированного пользователя `appuser`;
5. запускают нужное ASGI-приложение либо команду из Compose.

```dockerfile
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser . .
USER appuser
```

PostgreSQL и Redis имеют healthcheck. `parser` и `api` проверяются HTTP-запросом к `/health`. Основной API запускается после готовности зависимостей и автоматически применяет миграции:

```yaml
command: >
  sh -c "alembic upgrade head &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

Файл `.dockerignore` исключает Git, виртуальное окружение, кеши и тестовые материалы из контекста образа.

## Подзадача 2. Прямой HTTP-вызов

Отдельное приложение находится в [`parser_service/main.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/parser_service/main.py). Его маршрут `POST /parse`:

1. проверяет служебный `X-Parser-Token`;
2. принимает URL и `owner_id` от основного API;
3. загружает страницу функцией лабораторной 2;
4. записывает `ParsedPage` в общую БД;
5. возвращает сохраненный объект.

Клиент работает только с основным защищенным маршрутом `POST /parser/parse`. Реализация в [`app/api/parser.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/app/api/parser.py) берет пользователя из JWT и сама вызывает контейнер `parser` через `httpx.AsyncClient`.

Тело клиентского запроса:

```json
{
  "url": "https://example.com"
}
```

Пример успешного ответа:

```json
{
  "id": 1,
  "url": "https://example.com/",
  "title": "Example Domain",
  "approach": "http",
  "duration_ms": 287,
  "fetched_at": "2026-09-15T10:39:00Z"
}
```

Ошибки валидации URL, загрузки страницы и недоступности сервиса преобразуются в понятные HTTP-ответы `400`, `404`, `502`.

## Подзадача 3. Celery и Redis

Celery настроен в [`app/celery_app.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/app/celery_app.py):

```python
celery_app = Celery(
    "time_manager",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.parser"],
)
```

Данные задач и результатов сериализуются в JSON, состояние `STARTED` отслеживается, результат хранится один час. Worker повторяет временно неудачный HTTP-запрос до трех раз с backoff.

Фоновая функция [`parser.parse_url`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/app/tasks/parser.py) получает URL и идентификатор пользователя, вызывает общий парсер и сохраняет результат с подходом `celery`.

### API очереди

| Метод | URL | Ответ |
| --- | --- | --- |
| `POST` | `/parser/tasks` | HTTP 202, `task_id`, `PENDING` |
| `GET` | `/parser/tasks/{task_id}` | текущее состояние и результат/ошибка |
| `GET` | `/parsed-pages` | сохраненные страницы текущего пользователя |

Состояния задачи: `PENDING`, `STARTED`, `RETRY`, `SUCCESS`, `FAILURE`.

Пример постановки:

```json
{
  "task_id": "99845b80-8e31-4d5d-9fae-cf7d76f33b57",
  "status": "PENDING"
}
```

## Настройки

| Переменная | Назначение |
| --- | --- |
| `DATABASE_URL` | соединение с PostgreSQL |
| `PARSER_SERVICE_URL` | внутренний адрес контейнера парсера |
| `PARSER_SERVICE_TOKEN` | служебный токен API → parser |
| `CELERY_BROKER_URL` | Redis DB для очереди |
| `CELERY_RESULT_BACKEND` | Redis DB для результатов |

Значения для учебного запуска находятся в `.env.example`. Для реального развертывания пароли и токены необходимо заменить и хранить как secrets.

## Запуск и демонстрация

```bash
docker compose up -d --build
docker compose ps
```

После запуска:

- основной Swagger UI — `http://localhost:8000/docs`;
- Swagger парсера — `http://localhost:8001/docs`;
- healthcheck — `http://localhost:8000/health` и `http://localhost:8001/health`.

Для защищенных маршрутов нужно зарегистрироваться через `/auth/register`, получить JWT через `/auth/login` и вставить токен в Swagger `Authorize`.

Сценарий защиты:

1. вызвать `POST /parser/parse` и показать сразу сохраненный `Example Domain`;
2. вызвать `POST /parser/tasks`, скопировать `task_id`;
3. проверить `GET /parser/tasks/{task_id}` до состояния `SUCCESS`;
4. открыть `GET /parsed-pages` и показать обе строки;
5. показать журналы worker с зарегистрированной задачей `parser.parse_url`.

```bash
docker compose logs -f api parser celery-worker
docker compose down
```

## Проверка результата

Выполнены следующие проверки:

| Проверка | Результат |
| --- | --- |
| `pytest -q` | 14 тестов пройдено |
| `docker compose config --quiet` | конфигурация валидна |
| `docker compose build` | три Python-образа собраны |
| состояния контейнеров | API, parser, PostgreSQL и Redis — healthy; worker — ready |
| прямой запрос | HTTP 200, `Example Domain`, подход `http` |
| постановка в очередь | HTTP 202, состояние `PENDING` |
| обработка worker | состояние `SUCCESS`, `Example Domain` |
| чтение БД | сохранены результаты обоих способов |

После перевода образов на `appuser` очередь повторно прошла end-to-end сценарий `202 → SUCCESS`. Контейнеры проверки остановлены командой `docker compose down`, volume PostgreSQL сохранен.

## Вывод

Основное приложение не содержит логику загрузки HTML: прямой запрос делегируется отдельному сервису, а длительная работа может быть поставлена в Redis и выполнена Celery worker без блокировки HTTP-запроса. Docker Compose обеспечивает воспроизводимый запуск всех компонентов и общую сеть сервисов.
