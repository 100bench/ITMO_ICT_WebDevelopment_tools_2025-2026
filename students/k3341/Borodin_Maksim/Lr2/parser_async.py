import asyncio
from time import perf_counter

import aiohttp

from database import save_page
from parser_common import URLS, get_title


async def parse_and_save(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            title = get_title(await response.text())
    save_page(url, title, "asyncio")
    print(f"{url} -> {title}")
    return title


async def main() -> None:
    started = perf_counter()
    await asyncio.gather(*(parse_and_save(url) for url in URLS))
    print(f"Asyncio parser: {perf_counter() - started:.3f} сек.")


if __name__ == "__main__":
    asyncio.run(main())

