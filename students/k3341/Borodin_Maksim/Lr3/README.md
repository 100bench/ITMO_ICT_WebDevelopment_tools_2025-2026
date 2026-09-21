# Лабораторная работа 3

Минимальная реализация FastAPI + parser-service + PostgreSQL + Redis + Celery в Docker Compose.

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

Файл `docs/index.md` содержит краткий отчёт для MkDocs.

