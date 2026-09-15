"""Единый запуск трех парсеров и печать Markdown-таблицы времени."""

import argparse
import asyncio

from lab2.common import DEFAULT_URLS
from lab2.parse_async import run as run_async
from lab2.parse_multiprocessing import run as run_multiprocessing
from lab2.parse_threading import run as run_threading


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", default=list(DEFAULT_URLS))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    measurements = [
        ("threading", *run_threading(args.urls, args.workers)),
        ("multiprocessing", *run_multiprocessing(args.urls, args.workers)),
        ("asyncio", *asyncio.run(run_async(args.urls))),
    ]

    print("| Подход | Сохранено страниц | Время, с |")
    print("| --- | ---: | ---: |")
    for name, results, elapsed in measurements:
        print(f"| {name} | {len(results)} | {elapsed:.3f} |")


if __name__ == "__main__":
    main()
