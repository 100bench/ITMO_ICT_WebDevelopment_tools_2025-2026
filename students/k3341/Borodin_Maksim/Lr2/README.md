# Лабораторная работа 2

Простая реализация задания по `threading`, `multiprocessing` и `asyncio`.

## Файлы

- `sum_*.py` — три варианта подсчёта суммы `1..10^13`;
- `parser_*.py` — три варианта параллельного парсинга;
- `database.py` — сохранение заголовков страниц в SQLite;
- `docs/index.md` — отчёт для MkDocs.

## Запуск

```bash
cd students/k3341/Borodin_Maksim/Lr2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python sum_threading.py
python sum_multiprocessing.py
python sum_async.py

python parser_threading.py
python parser_multiprocessing.py
python parser_async.py

mkdocs serve
```

Результаты парсинга сохраняются в автоматически создаваемый файл `pages.db`.

