"""Подсчет суммы с разделением работы между потоками."""

import argparse
import threading
from time import perf_counter

from lab2.common import DEFAULT_LIMIT, split_range, sum_range


def calculate_sum(start: int, end: int, algorithm: str = "formula") -> int:
    return sum_range(start, end, algorithm)


def run(limit: int = DEFAULT_LIMIT, workers: int = 4, algorithm: str = "formula") -> tuple[int, float]:
    ranges = split_range(limit, workers)
    partial: list[int] = [0] * len(ranges)

    def worker(index: int, start: int, end: int) -> None:
        partial[index] = calculate_sum(start, end, algorithm)

    started = perf_counter()
    threads = [
        threading.Thread(target=worker, args=(index, start, end), name=f"sum-{index}")
        for index, (start, end) in enumerate(ranges)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return sum(partial), perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--algorithm", choices=("formula", "loop"), default="formula")
    args = parser.parse_args()
    result, elapsed = run(args.limit, args.workers, args.algorithm)
    print(f"threading: sum(1..{args.limit}) = {result}; {elapsed:.6f} s; algorithm={args.algorithm}")


if __name__ == "__main__":
    main()
