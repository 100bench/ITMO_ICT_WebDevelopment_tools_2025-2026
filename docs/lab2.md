# Лабораторная работа 2. Потоки, процессы и асинхронность

**Студент:** Бородни М. А.  
**Группа:** К3341  
**Код лабораторной:** [`lab-2`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-2)  
**Коммит:** [`c9fff91`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/c9fff91)

## Цель

Сравнить `threading`, `multiprocessing` и `asyncio` на CPU-bound и I/O-bound задачах. Для каждого подхода реализованы:

1. подсчет суммы чисел от 1 до `10_000_000_000_000` с разделением диапазона;
2. параллельная загрузка веб-страниц, извлечение `<title>` и сохранение результата в базе лабораторной 1.

## Структура решения

```text
lab2/
  common.py                 # диапазоны, HTML, запись в БД
  sum_threading.py          # сумма: threading
  sum_multiprocessing.py    # сумма: multiprocessing
  sum_async.py              # сумма: asyncio
  parse_threading.py        # парсинг: requests + threading
  parse_multiprocessing.py  # парсинг: requests + multiprocessing
  parse_async.py            # парсинг: aiohttp + asyncio
  benchmark_sums.py         # таблица времени подсчета
  benchmark_parsers.py      # таблица времени парсинга
```

Все программы можно запускать как Python-модули. Общие операции вынесены в [`lab2/common.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/common.py), чтобы варианты отличались именно способом организации конкурентной работы.

## Задача 1. Подсчет суммы

Диапазон `1..N` делится на непересекающиеся включительные отрезки примерно одинаковой длины. Функция `calculate_sum()` присутствует в каждой программе.

### Threading

В [`sum_threading.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/sum_threading.py) для каждого диапазона создается `threading.Thread`. Частичные суммы записываются в отдельные позиции списка, основной поток ожидает исполнителей через `join()`.

```python
def calculate_sum(start: int, end: int, algorithm: str = "formula") -> int:
    return sum_range(start, end, algorithm)

threads = [
    threading.Thread(target=worker, args=(index, start, end))
    for index, (start, end) in enumerate(ranges)
]
```

Потоки имеют общую память и удобны для операций ожидания. CPU-bound Python-код не получает линейного ускорения из-за GIL.

### Multiprocessing

В [`sum_multiprocessing.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/sum_multiprocessing.py) диапазоны передаются в `multiprocessing.Pool`. Процессы имеют отдельные интерпретаторы и могут выполнять вычисления на разных ядрах.

```python
with multiprocessing.Pool(processes=len(ranges)) as pool:
    partial = pool.map(_calculate, arguments)
```

Плата за настоящий параллелизм — запуск процессов, сериализация аргументов и отдельная память.

### Asyncio

В [`sum_async.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/sum_async.py) части запускаются через `asyncio.gather()`. Переключение кооперативное и происходит в точке `await`.

```python
async def calculate_sum(start: int, end: int, algorithm: str = "formula") -> int:
    await asyncio.sleep(0)
    return sum_range(start, end, algorithm)
```

`asyncio` не превращает вычисления в параллельные: все корутины исполняются в одном потоке event loop.

### Корректность и режимы вычисления

Полный проход по `10^13` числам практически невыполним для учебного запуска. Поэтому по умолчанию каждая подзадача использует формулу арифметической прогрессии:

```text
sum(start..end) = (start + end) * (end - start + 1) / 2
```

Итог всех трех программ одинаков:

```text
50000000000005000000000000
```

Дополнительный параметр `--algorithm loop` включает последовательное суммирование диапазона и позволяет сравнить CPU-bound поведение на меньшем `--limit`.

### Результаты замера суммы

Контрольный запуск: macOS, Python 3.14.5, четыре исполнителя, диапазон `1..10^13`, алгоритм `formula`.

| Подход | Результат | Время, с |
| --- | ---: | ---: |
| `threading` | 50000000000005000000000000 | 0.000275 |
| `multiprocessing` | 50000000000005000000000000 | 0.288773 |
| `asyncio` | 50000000000005000000000000 | 0.000099 |

Формула выполняет очень мало полезной работы. Поэтому результат показывает главным образом накладные расходы: особенно заметен запуск новых процессов. Числа не следует интерпретировать как общую производительность подходов.

Дополнительный итеративный запуск для `1..10_000_000`:

| Подход | Результат | Время, с |
| --- | ---: | ---: |
| `threading` | 50000005000000 | 0.038990 |
| `multiprocessing` | 50000005000000 | 0.271531 |
| `asyncio` | 50000005000000 | 0.041814 |

На таком коротком диапазоне затраты macOS на запуск процессов еще больше времени вычисления. На длительной CPU-bound задаче процессы способны использовать несколько ядер, в отличие от потоков и event loop.

Запуск новой таблицы замеров:

```bash
python -m lab2.benchmark_sums
python -m lab2.benchmark_sums --limit 10000000 --algorithm loop
```

## Задача 2. Параллельный парсинг

Для каждого URL выполняются четыре шага:

1. проверка абсолютного HTTP(S)-адреса;
2. загрузка HTML с таймаутом 15 секунд;
3. извлечение и нормализация содержимого `<title>`;
4. сохранение URL, заголовка, подхода и времени загрузки в PostgreSQL.

Функция `parse_and_save(url)` есть во всех трех программах.

### Хранение в БД лабораторной 1

Миграция [`20260915_0002_parsed_pages.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/alembic/versions/20260915_0002_parsed_pages.py) добавляет таблицу:

| Поле | Назначение |
| --- | --- |
| `id` | идентификатор результата |
| `owner_id` | связь с `users` из лабораторной 1 |
| `url` | адрес страницы |
| `title` | извлеченный заголовок |
| `approach` | `threading`, `multiprocessing` или `asyncio` |
| `duration_ms` | время HTTP-загрузки |
| `fetched_at` | время сохранения |

Связь `users -> parsed_pages` имеет тип one-to-many. Результаты текущего пользователя доступны через защищенные маршруты:

| Метод | URL | Назначение |
| --- | --- | --- |
| `GET` | `/parsed-pages` | список результатов |
| `GET` | `/parsed-pages/{page_id}` | один результат |

CLI-программы используют пользователя из `PARSER_OWNER_EMAIL`; по умолчанию это демонстрационный `demo@example.com` из миграции лабораторной 1.

### Реализации парсера

- [`parse_threading.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/parse_threading.py) делит список URL на равные части и обрабатывает каждую часть в `threading.Thread` с `requests`.
- [`parse_multiprocessing.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/parse_multiprocessing.py) передает части списка в отдельные процессы `multiprocessing.Pool`.
- [`parse_async.py`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/lab-2/lab2/parse_async.py) использует одну `aiohttp.ClientSession`, конкурентные корутины и `asyncio.gather()`; синхронная запись SQLAlchemy вынесена через `asyncio.to_thread()`.

### Результаты замера парсеров

Контрольный запуск для `example.com`, `python.org`, `fastapi.tiangolo.com` и `docs.aiohttp.org`:

| Подход | Сохранено страниц | Время, с |
| --- | ---: | ---: |
| `threading` | 4 | 0.775 |
| `multiprocessing` | 4 | 0.726 |
| `asyncio` | 4 | 0.505 |

При контрольном замере локальный Docker daemon еще не был доступен, поэтому только хранилище результатов временно заменялось SQLite. HTTP-загрузка и все три конкурентных подхода выполнялись реально. Целевой запуск использует PostgreSQL из `docker-compose.yml`.

Для I/O-bound задачи потоки и корутины эффективно перекрывают ожидание сети. `asyncio` показал минимальное время и требует меньше ресурсов, чем отдельный процесс на часть списка. Результаты меняются вместе с задержкой внешних сайтов.

Запуск всех трех вариантов и новой таблицы:

```bash
docker compose up -d --build
docker compose exec api python -m lab2.benchmark_parsers
```

Отдельный запуск:

```bash
docker compose exec api python -m lab2.parse_threading
docker compose exec api python -m lab2.parse_multiprocessing
docker compose exec api python -m lab2.parse_async
```

## Проверка

```bash
python -m pytest -q
alembic upgrade head --sql
```

В ветке `lab-2` проходят 9 тестов: API лабораторной 1, разбиение диапазонов и URL, нормализация HTML-заголовка, равенство трех сумм и сохранение результата парсинга в связанную с пользователем БД.

## Вывод

- `threading` прост для конкурентных блокирующих HTTP-запросов, но не обходит GIL для Python-вычислений.
- `multiprocessing` дает настоящий CPU-параллелизм, однако требует больше времени запуска и памяти.
- `asyncio` особенно удобно для большого числа сетевых операций, но не ускоряет CPU-bound функцию без процессов или вынесения работы из event loop.
