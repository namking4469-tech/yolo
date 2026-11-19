"""SQLite 데이터베이스 도우미. 모든 페이지가 이 파일을 통해 DB에 접근한다."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(os.environ.get("APP_DB", Path(__file__).parent / "app.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    category TEXT NOT NULL,
    price    INTEGER NOT NULL CHECK (price >= 0),
    stock    INTEGER NOT NULL CHECK (stock >= 0)
);
CREATE TABLE IF NOT EXISTS posts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

CATEGORIES = ["과일", "음료", "과자", "문구", "전자"]

SEED_PRODUCTS = [
    ("사과", "과일", 1500, 120),
    ("바나나", "과일", 3000, 80),
    ("포도", "과일", 7000, 25),
    ("생수 2L", "음료", 1200, 300),
    ("오렌지 주스", "음료", 3500, 60),
    ("초코 쿠키", "과자", 2500, 90),
    ("감자칩", "과자", 1800, 150),
    ("볼펜", "문구", 1000, 500),
    ("노트", "문구", 2000, 240),
    ("무선 마우스", "전자", 25000, 15),
    ("USB 메모리 64GB", "전자", 12000, 40),
]


def now() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
                SEED_PRODUCTS,
            )


def query(sql: str, params: tuple = ()) -> list[dict]:
    """SELECT 를 실행하고 결과를 dict 목록으로 돌려준다."""
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def execute(sql: str, params: tuple = ()) -> int:
    """INSERT / UPDATE / DELETE 를 실행한다. INSERT 면 새 행의 id 를 돌려준다."""
    with connect() as conn:
        return conn.execute(sql, params).lastrowid


def read_only_query(sql: str, limit: int = 500) -> tuple[list[str], list[tuple]]:
    """사용자가 입력한 SQL 을 읽기 전용으로 실행한다.

    DB 를 읽기 전용으로 열기 때문에 데이터를 바꾸는 문장은 실패하고,
    비밀번호 해시와 솔트 컬럼은 읽지 못하게 막는다.
    """
    conn = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro", uri=True)

    def guard(action, arg1, arg2, _dbname, _source):
        if action == sqlite3.SQLITE_READ and arg1 == "users" and arg2 in ("password_hash", "salt"):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    conn.set_authorizer(guard)
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        return columns, cur.fetchmany(limit)
    finally:
        conn.close()


init_db()
