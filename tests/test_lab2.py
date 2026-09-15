"""Проверки общих функций и трех вариантов вычисления суммы."""

import asyncio

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import ParsedPage, User
from lab2.common import extract_title, save_parsed_page, split_items, split_range
from lab2.sum_async import run as run_async
from lab2.sum_multiprocessing import run as run_multiprocessing
from lab2.sum_threading import run as run_threading


def test_split_range_has_no_gaps_or_overlaps() -> None:
    ranges = split_range(10, 3)
    assert ranges == [(1, 4), (5, 7), (8, 10)]


def test_split_items_preserves_order() -> None:
    assert split_items(["a", "b", "c", "d", "e"], 2) == [["a", "b", "c"], ["d", "e"]]


def test_extract_title_normalizes_whitespace() -> None:
    assert extract_title("<html><title>  FastAPI\n docs </title></html>") == "FastAPI docs"
    assert extract_title("<html><body>no title</body></html>") == "Untitled page"


def test_all_sum_approaches_return_same_result() -> None:
    limit = 100_000
    expected = limit * (limit + 1) // 2
    threaded, _ = run_threading(limit, workers=3)
    multiprocessed, _ = run_multiprocessing(limit, workers=3)
    asynchronous, _ = asyncio.run(run_async(limit, workers=3))
    assert threaded == multiprocessed == asynchronous == expected


def test_parser_result_is_saved_in_lab1_database() -> None:
    engine = create_engine("sqlite://")
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)
    with testing_session() as db:
        db.add(User(email="parser@example.com", full_name="Parser", password_hash="not-used"))
        db.commit()

    result = save_parsed_page(
        "https://example.com",
        "Example Domain",
        "threading",
        12,
        owner_email="parser@example.com",
        session_factory=testing_session,
    )

    with testing_session() as db:
        page = db.scalar(select(ParsedPage))
        assert page is not None
        assert page.id == result.id
        assert page.title == "Example Domain"
        assert page.owner.email == "parser@example.com"
