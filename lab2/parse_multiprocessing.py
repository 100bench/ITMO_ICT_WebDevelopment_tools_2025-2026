"""Параллельный парсинг страниц с помощью multiprocessing."""

import argparse
import multiprocessing
from time import perf_counter

from lab2.common import DEFAULT_URLS, ParseResult, parse_sync, print_parse_result, split_items


def parse_and_save(url: str) -> ParseResult:
    result = parse_sync(url, "multiprocessing")
    print_parse_result(result)
    return result


def _parse_chunk(urls: list[str]) -> list[ParseResult]:
    return [parse_and_save(url) for url in urls]


def run(urls: list[str], workers: int = 4) -> tuple[list[ParseResult], float]:
    chunks = split_items(urls, workers)
    started = perf_counter()
    with multiprocessing.Pool(processes=len(chunks)) as pool:
        chunk_results = pool.map(_parse_chunk, chunks)
    return [result for chunk in chunk_results for result in chunk], perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", default=list(DEFAULT_URLS))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    results, elapsed = run(args.urls, args.workers)
    print(f"multiprocessing: saved {len(results)} page(s) in {elapsed:.3f} s")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
