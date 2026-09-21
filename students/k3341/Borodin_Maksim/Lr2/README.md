# Лабораторная работа 2

Простая реализация задания по `threading`, `multiprocessing` и `asyncio`.

## Структура

```text
Lr2/
├── common/    # диапазоны, HTML и работа с БД
├── sums/      # три способа подсчёта суммы
└── parsers/   # три способа параллельного парсинга
```

Отчёт вынесен в отдельную ветку `docs`, где собрана документация всех лабораторных работ.

## Запуск

```bash
cd students/k3341/Borodin_Maksim/Lr2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m sums.threading_sum
python -m sums.multiprocessing_sum
python -m sums.async_sum

python -m parsers.threading_parser
python -m parsers.multiprocessing_parser
python -m parsers.async_parser
```

Результаты парсинга сохраняются в автоматически создаваемый файл `pages.db`.
