import asyncio
from time import perf_counter

from common.ranges import split_range


async def calculate_sum(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return (start + end) * (end - start + 1) // 2


async def main() -> None:
    started = perf_counter()
    tasks = [
        asyncio.create_task(calculate_sum(start, end))
        for start, end in split_range()
    ]
    # gather ожидает все созданные корутины
    results = await asyncio.gather(*tasks)
    print(f"Сумма: {sum(results)}")
    print(f"Asyncio: {perf_counter() - started:.6f} сек.")


if __name__ == "__main__":
    asyncio.run(main())

