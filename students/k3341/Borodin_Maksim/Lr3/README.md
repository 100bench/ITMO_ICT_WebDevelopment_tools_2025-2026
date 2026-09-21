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
├── docker-compose.yml
└── Makefile    # команды запуска
```

Отчёт находится в отдельной ветке `docs`, общей для всех лабораторных работ.

## Запуск

```bash
cd students/k3341/Borodin_Maksim/Lr3
make run
```

Команда соберёт образы, запустит пять сервисов в фоновом режиме и покажет их статус. Логи можно открыть командой `make logs`.

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
make down
```
