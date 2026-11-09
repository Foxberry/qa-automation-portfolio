"""Minimal PostgreSQL helpers for data-quality checks."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import psycopg

from framework import config


@contextmanager
def connection():
    with psycopg.connect(config.PG_DSN, autocommit=True) as conn:
        yield conn


def query(sql: str, params: tuple | dict | None = None) -> list[tuple]:
    with connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def scalar(sql: str, params: tuple | dict | None = None):
    rows = query(sql, params)
    return rows[0][0] if rows else None


def run_script(path: str | Path) -> None:
    with connection() as conn:
        conn.execute(Path(path).read_text(encoding="utf-8"))
