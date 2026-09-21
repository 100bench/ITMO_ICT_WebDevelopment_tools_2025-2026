# Лабораторная работа 2. Потоки, процессы и асинхронность

**Студент:** Бородин М. А.<br>
**Группа:** К3341<br>
**Код:** [`students/k3341/Borodin_Maksim/Lr2`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-2/students/k3341/Borodin_Maksim/Lr2)<br>
**Коммит:** [`8ed6c3c`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/8ed6c3c)

## Цель

Сравнить `threading`, `multiprocessing` и `asyncio` на вычислительной и сетевой задачах.

## Структура

```text
students/k3341/Borodin_Maksim/Lr2/
├── sum_threading.py
├── sum_multiprocessing.py
├── sum_async.py
├── parser_threading.py
├── parser_multiprocessing.py
├── parser_async.py
├── common.py
├── parser_common.py
├── database.py
└── docs/index.md
```

## Задача 1. Подсчёт суммы

Все три программы считают сумму от 1 до `10_000_000_000_000`. Функция `split_range()` делит диапазон на четыре непересекающиеся части, а `calculate_sum()` вычисляет каждую частичную сумму.

Использована формула арифметической прогрессии:

```text
(start + end) * (end - start + 1) // 2
```

Она даёт точный ответ и не требует перебирать `10^13` чисел. Итог всех вариантов:

```text
50000000000005000000000000
```

Реализации отличаются способом запуска четырёх подзадач:

| Файл | Механизм |
|---|---|
| `sum_threading.py` | четыре `threading.Thread`, ожидание через `join()` |
| `sum_multiprocessing.py` | четыре процесса, результаты через `multiprocessing.Queue` |
| `sum_async.py` | четыре корутины, `create_task()` и `gather()` |

Контрольный замер:

| Подход | Время |
|---|---:|
| threading | 0.000185 с |
| multiprocessing | 0.078173 с |
| asyncio | 0.000089 с |

Здесь полезная работа очень короткая, поэтому измеряются в основном накладные расходы. Процессы запускаются дороже. `asyncio` не ускоряет CPU-bound работу и не выполняет Python-код на нескольких ядрах.

## Задача 2. Парсинг страниц

В каждом из трёх файлов есть функция `parse_and_save(url)`. Она:

1. загружает HTML;
2. извлекает тег `<title>` через BeautifulSoup;
3. сохраняет URL, заголовок и название подхода в таблицу `parsed_pages`;
4. печатает результат.

Для простого автономного запуска используется SQLite-файл `pages.db`. Его создаёт `database.py`. В парсере потоков применяется `ThreadPoolExecutor`, в процессах — `multiprocessing.Pool`, в асинхронном варианте — `aiohttp` и `asyncio.gather()`.

Контрольный замер трёх URL:

| Подход | Время |
|---|---:|
| threading | 0.315 с |
| multiprocessing | 0.434 с |
| asyncio | 1.037 с |

Сетевые значения меняются от запуска к запуску. Потоки и корутины подходят для I/O-bound задачи, потому что позволяют выполнять другую работу во время ожидания сети. Процессы тоже работают, но требуют больше памяти и времени запуска.

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
```

## Вывод

- потоки удобны для обычных блокирующих HTTP-запросов;
- процессы дают настоящий параллелизм и подходят для тяжёлых вычислений;
- `asyncio` организует конкурентное ожидание I/O в одном потоке;
- выбор механизма зависит от того, занята программа вычислениями или ожиданием.
