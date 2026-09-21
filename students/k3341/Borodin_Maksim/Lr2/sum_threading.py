import threading
from time import perf_counter

from common import split_range


def calculate_sum(start: int, end: int) -> int:
    return (start + end) * (end - start + 1) // 2


def main() -> None:
    started = perf_counter()
    ranges = split_range()
    results = [0] * len(ranges)

    def worker(index: int, start: int, end: int) -> None:
        results[index] = calculate_sum(start, end)

    threads = [
        threading.Thread(target=worker, args=(index, start, end))
        for index, (start, end) in enumerate(ranges)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print(f"Сумма: {sum(results)}")
    print(f"Threading: {perf_counter() - started:.6f} сек.")


if __name__ == "__main__":
    main()

