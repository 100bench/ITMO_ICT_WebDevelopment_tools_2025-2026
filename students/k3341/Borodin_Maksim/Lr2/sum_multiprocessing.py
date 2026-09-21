import multiprocessing
from time import perf_counter

from common import split_range


def calculate_sum(start: int, end: int) -> int:
    return (start + end) * (end - start + 1) // 2


def worker(start: int, end: int, queue: multiprocessing.Queue) -> None:
    queue.put(calculate_sum(start, end))


def main() -> None:
    started = perf_counter()
    ranges = split_range()
    queue = multiprocessing.Queue()
    processes = [
        multiprocessing.Process(target=worker, args=(start, end, queue))
        for start, end in ranges
    ]
    for process in processes:
        process.start()

    result = sum(queue.get() for _ in processes)
    for process in processes:
        process.join()

    print(f"Сумма: {result}")
    print(f"Multiprocessing: {perf_counter() - started:.6f} сек.")


if __name__ == "__main__":
    main()

