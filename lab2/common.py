"""Общие функции для вычислений и парсеров лабораторной работы 2."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from html import unescape
from time import perf_counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import ParsedPage, User

DEFAULT_LIMIT = 10_000_000_000_000
DEFAULT_URLS = (
    "https://example.com",
    "https://www.python.org",
    "https://fastapi.tiangolo.com",
    "https://docs.aiohttp.org",
)


@dataclass(frozen=True, slots=True)
class ParseResult:
    id: int
    url: str
    title: str
    approach: str
    duration_ms: int


def split_range(limit: int, parts: int) -> list[tuple[int, int]]:
    """Разбивает диапазон 1..limit на непересекающиеся включительные части."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if parts < 1:
        raise ValueError("parts must be positive")

    parts = min(parts, limit)
    chunk_size, remainder = divmod(limit, parts)
    ranges: list[tuple[int, int]] = []
    start = 1
    for index in range(parts):
        size = chunk_size + (1 if index < remainder else 0)
        end = start + size - 1
        ranges.append((start, end))
        start = end + 1
    return ranges


def sum_range(start: int, end: int, algorithm: str = "formula") -> int:
    """Считает сумму включительного диапазона формулой или последовательным циклом."""
    if start > end:
        return 0
    if algorithm == "formula":
        return (start + end) * (end - start + 1) // 2
    if algorithm == "loop":
        return sum(range(start, end + 1))
    raise ValueError("algorithm must be 'formula' or 'loop'")


def split_items(items: Sequence[str], parts: int) -> list[list[str]]:
    if parts < 1:
        raise ValueError("parts must be positive")
    if not items:
        return []
    ranges = split_range(len(items), min(parts, len(items)))
    return [list(items[start - 1 : end]) for start, end in ranges]


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Only absolute HTTP(S) URLs are supported: {url}")
    return url


def extract_title(html: str) -> str:
    title = BeautifulSoup(html, "html.parser").title
    if title is None:
        return "Untitled page"
    normalized = " ".join(title.get_text(" ", strip=True).split())
    return unescape(normalized) or "Untitled page"


def fetch_title(url: str, timeout: float = 15.0) -> str:
    validate_url(url)
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "ITMO-Web-Lab/2 (+educational parser)"},
    )
    response.raise_for_status()
    return extract_title(response.text)


def save_parsed_page(
    url: str,
    title: str,
    approach: str,
    duration_ms: int,
    *,
    owner_email: str | None = None,
    session_factory: sessionmaker[Session] = SessionLocal,
) -> ParseResult:
    """Сохраняет заголовок в ту же БД, которую использует Time Manager API."""
    email = owner_email or settings.parser_owner_email
    with session_factory() as db:
        owner = db.scalar(select(User).where(User.email == email))
        if owner is None:
            raise RuntimeError(f"Parser owner '{email}' does not exist")
        page = ParsedPage(
            owner_id=owner.id,
            url=url,
            title=title[:512],
            approach=approach,
            duration_ms=duration_ms,
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return ParseResult(
            id=page.id,
            url=page.url,
            title=page.title,
            approach=page.approach,
            duration_ms=page.duration_ms,
        )


def parse_sync(
    url: str,
    approach: str,
    *,
    fetcher: Callable[[str], str] = fetch_title,
    saver: Callable[[str, str, str, int], ParseResult] = save_parsed_page,
) -> ParseResult:
    started = perf_counter()
    title = fetcher(url)
    duration_ms = round((perf_counter() - started) * 1000)
    return saver(url, title, approach, duration_ms)


def print_parse_result(result: ParseResult) -> None:
    print(f"[{result.approach}] #{result.id} {result.title!r} <- {result.url} ({result.duration_ms} ms)")
