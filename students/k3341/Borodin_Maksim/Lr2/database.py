import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("pages.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS parsed_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                method TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_page(url: str, title: str, method: str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH, timeout=30) as connection:
        connection.execute(
            "INSERT INTO parsed_pages (url, title, method) VALUES (?, ?, ?)",
            (url, title, method),
        )

