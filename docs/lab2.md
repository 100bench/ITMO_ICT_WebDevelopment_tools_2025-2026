# Лабораторная работа 2. Потоки, процессы и асинхронность

**Студент:** Бородин М. А.<br>
**Группа:** К3341<br>
**Код:** [`students/k3341/Borodin_Maksim/Lr2`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab-2/students/k3341/Borodin_Maksim/Lr2)<br>
**Коммит:** [`0ea8cfc`](https://github.com/100bench/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/0ea8cfc)

## Цель

Сравнить `threading`, `multiprocessing` и `asyncio` на вычислительной и сетевой задачах.

## Структура

```text
students/k3341/Borodin_Maksim/Lr2/
├── common/
│   ├── ranges.py
│   ├── parser.py
│   └── database.py
├── sums/
│   ├── threading_sum.py
│   ├── multiprocessing_sum.py
│   └── async_sum.py
└── parsers/
    ├── threading_parser.py
    ├── multiprocessing_parser.py
    └── async_parser.py
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
| `sums/threading_sum.py` | четыре `threading.Thread`, ожидание через `join()` |
| `sums/multiprocessing_sum.py` | четыре процесса, результаты через `multiprocessing.Queue` |
| `sums/async_sum.py` | четыре корутины, `create_task()` и `gather()` |

Контрольный замер:

| Подход | Время |
|---|---:|
| threading | 0.000221 с |
| multiprocessing | 0.080329 с |
| asyncio | 0.000095 с |

Здесь полезная работа очень короткая, поэтому измеряются в основном накладные расходы. Процессы запускаются дороже. `asyncio` не ускоряет CPU-bound работу и не выполняет Python-код на нескольких ядрах.

## Задача 2. Парсинг страниц

В каждом из трёх файлов есть функция `parse_and_save(url)`. Она:

1. загружает HTML;
2. извлекает тег `<title>` через BeautifulSoup;
3. сохраняет URL, заголовок и название подхода в таблицу `parsed_pages`;
4. печатает результат.

Для простого автономного запуска используется SQLite-файл `pages.db`. Его создаёт `common/database.py`. В парсере потоков применяется `ThreadPoolExecutor`, в процессах — `multiprocessing.Pool`, в асинхронном варианте — `aiohttp` и `asyncio.gather()`.

Контрольный замер трёх URL:

| Подход | Время |
|---|---:|
| threading | 0.276 с |
| multiprocessing | 0.463 с |
| asyncio | 0.274 с |

Сетевые значения меняются от запуска к запуску. Потоки и корутины подходят для I/O-bound задачи, потому что позволяют выполнять другую работу во время ожидания сети. Процессы тоже работают, но требуют больше памяти и времени запуска.

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

## Вывод

- потоки удобны для обычных блокирующих HTTP-запросов;
- процессы дают настоящий параллелизм и подходят для тяжёлых вычислений;
- `asyncio` организует конкурентное ожидание I/O в одном потоке;
- выбор механизма зависит от того, занята программа вычислениями или ожиданием.
