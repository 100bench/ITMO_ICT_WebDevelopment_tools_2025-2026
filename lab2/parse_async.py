"""Параллельный парсинг страниц с помощью asyncio и aiohttp."""

import argparse
import asyncio
from time import perf_counter

import aiohttp

from lab2.common import DEFAULT_URLS, ParseResult, extract_title, print_parse_result, save_parsed_page, validate_url


async def parse_and_save(url: str, session: aiohttp.ClientSession | None = None) -> ParseResult:
    validate_url(url)
    owns_session = session is None
    if session is None:
        session = aiohttp.ClientSession(headers={"User-Agent": "ITMO-Web-Lab/2 (+educational parser)"})
    started = perf_counter()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            response.raise_for_status()
            title = extract_title(await response.text())
        duration_ms = round((perf_counter() - started) * 1000)
        result = await asyncio.to_thread(save_parsed_page, url, title, "asyncio", duration_ms)
        print_parse_result(result)
        return result
    finally:
        if owns_session:
            await session.close()


async def run(urls: list[str]) -> tuple[list[ParseResult], float]:
    started = perf_counter()
    async with aiohttp.ClientSession(headers={"User-Agent": "ITMO-Web-Lab/2 (+educational parser)"}) as session:
        results = await asyncio.gather(*(parse_and_save(url, session) for url in urls))
    return list(results), perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", default=list(DEFAULT_URLS))
    args = parser.parse_args()
    results, elapsed = asyncio.run(run(args.urls))
    print(f"asyncio: saved {len(results)} page(s) in {elapsed:.3f} s")


if __name__ == "__main__":
    main()
