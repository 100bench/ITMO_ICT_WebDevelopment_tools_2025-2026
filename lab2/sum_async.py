"""Подсчет суммы с кооперативными задачами asyncio."""

import argparse
import asyncio
from time import perf_counter

from lab2.common import DEFAULT_LIMIT, split_range, sum_range


async def calculate_sum(start: int, end: int, algorithm: str = "formula") -> int:
    # Явная точка переключения демонстрирует кооперативную модель asyncio.
    await asyncio.sleep(0)
    return sum_range(start, end, algorithm)


async def run(limit: int = DEFAULT_LIMIT, workers: int = 4, algorithm: str = "formula") -> tuple[int, float]:
    ranges = split_range(limit, workers)
    started = perf_counter()
    partial = await asyncio.gather(*(calculate_sum(start, end, algorithm) for start, end in ranges))
    return sum(partial), perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--algorithm", choices=("formula", "loop"), default="formula")
    args = parser.parse_args()
    result, elapsed = asyncio.run(run(args.limit, args.workers, args.algorithm))
    print(f"asyncio: sum(1..{args.limit}) = {result}; {elapsed:.6f} s; algorithm={args.algorithm}")


if __name__ == "__main__":
    main()
