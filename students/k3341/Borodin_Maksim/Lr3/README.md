# Лабораторная работа 3

Минимальная реализация FastAPI + parser-service + PostgreSQL + Redis + Celery в Docker Compose.

## Структура

```text
Lr3/
├── api/        # публичные HTTP-маршруты
├── parser/     # загрузка и разбор страниц
├── worker/     # Celery и фоновая задача
├── database/   # работа с PostgreSQL
├── Dockerfile
└── docker-compose.yml
```

Отчёт находится в отдельной ветке `docs`, общей для всех лабораторных работ.

## Запуск

```bash
cd students/k3341/Borodin_Maksim/Lr3
docker compose up --build -d
```

Swagger основного API: <http://localhost:8000/docs>.

Прямой вызов парсера:

```bash
curl -X POST http://localhost:8000/parse \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

Фоновый вызов:

```bash
curl -X POST http://localhost:8000/parse/async \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'

curl http://localhost:8000/tasks/<task_id>
```

Остановка:

```bash
docker compose down
```
