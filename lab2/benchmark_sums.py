"""Единый запуск трех реализаций суммы и печать Markdown-таблицы."""

import argparse
import asyncio

from lab2.common import DEFAULT_LIMIT
from lab2.sum_async import run as run_async
from lab2.sum_multiprocessing import run as run_multiprocessing
from lab2.sum_threading import run as run_threading


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--algorithm", choices=("formula", "loop"), default="formula")
    args = parser.parse_args()

    expected = args.limit * (args.limit + 1) // 2
    measurements = [
        ("threading", *run_threading(args.limit, args.workers, args.algorithm)),
        ("multiprocessing", *run_multiprocessing(args.limit, args.workers, args.algorithm)),
        ("asyncio", *asyncio.run(run_async(args.limit, args.workers, args.algorithm))),
    ]
    if any(result != expected for _, result, _ in measurements):
        raise RuntimeError("At least one implementation returned an incorrect sum")

    print("| Подход | Результат | Время, с |")
    print("| --- | ---: | ---: |")
    for name, result, elapsed in measurements:
        print(f"| {name} | {result} | {elapsed:.6f} |")


if __name__ == "__main__":
    main()
