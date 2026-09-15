"""Подсчет суммы с разделением работы между процессами."""

import argparse
import multiprocessing
from time import perf_counter

from lab2.common import DEFAULT_LIMIT, split_range, sum_range


def calculate_sum(start: int, end: int, algorithm: str = "formula") -> int:
    return sum_range(start, end, algorithm)


def _calculate(args: tuple[int, int, str]) -> int:
    return calculate_sum(*args)


def run(limit: int = DEFAULT_LIMIT, workers: int = 4, algorithm: str = "formula") -> tuple[int, float]:
    ranges = split_range(limit, workers)
    started = perf_counter()
    with multiprocessing.Pool(processes=len(ranges)) as pool:
        partial = pool.map(_calculate, [(start, end, algorithm) for start, end in ranges])
    return sum(partial), perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--algorithm", choices=("formula", "loop"), default="formula")
    args = parser.parse_args()
    result, elapsed = run(args.limit, args.workers, args.algorithm)
    print(f"multiprocessing: sum(1..{args.limit}) = {result}; {elapsed:.6f} s; algorithm={args.algorithm}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
