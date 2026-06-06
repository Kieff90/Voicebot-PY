import sqlite3
from pathlib import Path

_SCHEMA = Path(__file__).parent / "schema.sql"


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA.read_text(encoding="utf-8"))
    conn.commit()
