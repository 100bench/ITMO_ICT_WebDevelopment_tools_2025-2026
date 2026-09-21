from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

import requests

from database import save_page
from parser_common import URLS, get_title


def parse_and_save(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    title = get_title(response.text)
    save_page(url, title, "threading")
    print(f"{url} -> {title}")
    return title


def main() -> None:
    started = perf_counter()
    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(parse_and_save, URLS))
    print(f"Threading parser: {perf_counter() - started:.3f} сек.")


if __name__ == "__main__":
    main()

