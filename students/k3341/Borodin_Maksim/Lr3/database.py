import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/lab3",
)


def init_db() -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS parsed_pages (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )


def save_page(url: str, title: str) -> int:
    with psycopg.connect(DATABASE_URL) as connection:
        row = connection.execute(
            "INSERT INTO parsed_pages (url, title) VALUES (%s, %s) RETURNING id",
            (url, title),
        ).fetchone()
    return row[0]

