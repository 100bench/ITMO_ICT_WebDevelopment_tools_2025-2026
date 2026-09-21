import multiprocessing
from time import perf_counter

import requests

from common.database import save_page
from common.parser import URLS, get_title


def parse_and_save(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    title = get_title(response.text)
    save_page(url, title, "multiprocessing")
    print(f"{url} -> {title}")
    return title


def main() -> None:
    started = perf_counter()
    with multiprocessing.Pool(processes=3) as pool:
        pool.map(parse_and_save, URLS)
    print(f"Multiprocessing parser: {perf_counter() - started:.3f} сек.")


if __name__ == "__main__":
    main()

