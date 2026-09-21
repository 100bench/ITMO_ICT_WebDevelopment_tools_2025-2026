# Лабораторная работа 3. Docker, парсер и очередь

**Студент:** Бородин М. А.<br>
**Группа:** К3341<br>
**Код:** [`students/k3341/Borodin_Maksim/Lr3`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-3/students/k3341/Borodin_Maksim/Lr3)<br>
**Коммит:** [`46192b1`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/46192b1)

## Цель

Упаковать FastAPI-приложение, парсер и PostgreSQL в Docker; реализовать прямой вызов парсера и фоновую обработку через Celery и Redis.

## Структура

```text
students/k3341/Borodin_Maksim/Lr3/
├── api.py
├── parser.py
├── tasks.py
├── database.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Сервисы Docker Compose

| Сервис | Назначение | Порт хоста |
|---|---|---:|
| `api` | принимает запросы клиента | 8000 |
| `parser` | загружает страницу и сохраняет заголовок | 8001 |
| `db` | PostgreSQL, таблица `parsed_pages` | — |
| `redis` | брокер Celery и backend результата | — |
| `worker` | выполняет фоновые задачи | — |

Все Python-сервисы собираются одним небольшим [`Dockerfile`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-3/students/k3341/Borodin_Maksim/Lr3/Dockerfile). Команду запуска каждого контейнера задаёт Compose. Приложения работают от пользователя `appuser`, а не от root.

Compose создаёт общую сеть. Поэтому `api` обращается к `http://parser:8001`, parser — к хосту `db`, а Celery — к `redis:6379`. `localhost` внутри контейнера означал бы сам этот контейнер.

## Прямой вызов

Маршрут `POST /parse` в `api.py` принимает URL от клиента и передаёт его parser-service через `httpx.AsyncClient`.

```text
клиент -> API -> parser-service -> сайт -> PostgreSQL
```

Parser извлекает `<title>`, записывает строку в PostgreSQL и возвращает готовый результат. Клиент ждёт окончания операции.

```json
{
  "id": 1,
  "url": "https://example.com/",
  "title": "Example Domain"
}
```

## Вызов через Celery

Маршрут `POST /parse/async` вызывает `parse_url.delay(url)`. Celery помещает сообщение в Redis и сразу возвращает `task_id` с HTTP 202.

```text
клиент -> API -> Redis -> Celery worker -> parser-service -> PostgreSQL
```

Состояние проверяется через `GET /tasks/{task_id}`. Основные состояния: `PENDING`, `SUCCESS`, `FAILURE`.

Пример постановки задачи:

```json
{
  "task_id": "96fb4609-4ad0-46c9-8c60-211eeeeddfe7",
  "status": "PENDING"
}
```

После выполнения тот же маршрут возвращает `SUCCESS` и результат парсинга.

## Запуск

```bash
cd students/k3341/Borodin_Maksim/Lr3
docker compose up --build -d
```

Swagger: `http://localhost:8000/docs`.

Прямой запрос:

```bash
curl -X POST http://localhost:8000/parse \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

Фоновый запрос:

```bash
curl -X POST http://localhost:8000/parse/async \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'

curl http://localhost:8000/tasks/<task_id>
```

## Проверка

| Проверка | Результат |
|---|---|
| `docker compose config --quiet` | конфигурация валидна |
| сборка образов | успешно |
| healthcheck PostgreSQL, Redis и parser | healthy |
| прямой запрос | HTTP 200, `Example Domain` |
| Celery-задача | `PENDING` → `SUCCESS` |
| PostgreSQL | сохранены результаты обоих запросов |
| пользователь worker | `appuser`, uid 1000 |

После проверки контейнеры остановлены через `docker compose down`; volume PostgreSQL сохранён.

## Вывод

Docker обеспечивает одинаковую среду запуска, Compose объединяет сервисы в один оркестр, отдельный parser-service изолирует загрузку данных, а Celery с Redis позволяет выполнять долгую операцию в фоне, не удерживая HTTP-запрос клиента.
