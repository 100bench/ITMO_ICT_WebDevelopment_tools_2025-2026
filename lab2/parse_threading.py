"""Параллельный парсинг страниц с помощью threading."""

import argparse
import threading
from time import perf_counter

from lab2.common import DEFAULT_URLS, ParseResult, parse_sync, print_parse_result, split_items


def parse_and_save(url: str) -> ParseResult:
    result = parse_sync(url, "threading")
    print_parse_result(result)
    return result


def run(urls: list[str], workers: int = 4) -> tuple[list[ParseResult], float]:
    results: list[ParseResult] = []
    failures: list[Exception] = []
    lock = threading.Lock()

    def worker(chunk: list[str]) -> None:
        for url in chunk:
            try:
                result = parse_and_save(url)
                with lock:
                    results.append(result)
            except Exception as exc:
                with lock:
                    failures.append(exc)

    started = perf_counter()
    threads = [
        threading.Thread(target=worker, args=(chunk,), name=f"parser-{index}")
        for index, chunk in enumerate(split_items(urls, workers))
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if failures:
        raise RuntimeError(f"{len(failures)} page(s) could not be parsed") from failures[0]
    return results, perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", default=list(DEFAULT_URLS))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    results, elapsed = run(args.urls, args.workers)
    print(f"threading: saved {len(results)} page(s) in {elapsed:.3f} s")


if __name__ == "__main__":
    main()
