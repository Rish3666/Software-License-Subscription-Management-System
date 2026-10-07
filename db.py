"""Connection layer for the License Management UI.

Priority:
1. MySQL 8 — set env vars LM_DB_HOST, LM_DB_USER, LM_DB_PASSWORD (defaults:
   host=127.0.0.1, user=root, db=license_mgmt) or a full LM_DB_URL.
2. SQLite fallback — data/app.db (demo mirror with the same schema, views,
   triggers and seed data) so the prototype runs without a MySQL server.

All UI queries use the shared views and plain SQL so they run on both engines.
"""
import os
import sqlite3
from contextlib import contextmanager

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")

_engine_kind = None  # "mysql" | "sqlite", set on first use


def _mysql_conn():
    import pymysql
    url = os.environ.get("LM_DB_URL")
    if url:  # mysql+pymysql://user:pass@host:3306/license_mgmt
        from urllib.parse import urlparse
        p = urlparse(url.replace("mysql+pymysql://", "mysql://"))
        return pymysql.connect(
            host=p.hostname or "127.0.0.1", port=p.port or 3306,
            user=p.username or "root", password=p.password or "",
            database=(p.path or "/license_mgmt").lstrip("/"),
            cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    return pymysql.connect(
        host=os.environ.get("LM_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("LM_DB_PORT", "3306")),
        user=os.environ.get("LM_DB_USER", "root"),
        password=os.environ.get("LM_DB_PASSWORD", ""),
        database=os.environ.get("LM_DB_NAME", "license_mgmt"),
        cursorclass=pymysql.cursors.DictCursor, autocommit=True)


@contextmanager
def get_conn():
    """Yield a DBAPI connection. Tries MySQL first, falls back to SQLite."""
    global _engine_kind
    if _engine_kind is None:
        try:
            c = _mysql_conn(); c.close(); _engine_kind = "mysql"
        except Exception:
            _engine_kind = "sqlite"
    if _engine_kind == "mysql":
        conn = _mysql_conn()
        try:
            yield conn
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()


def engine_kind() -> str:
    global _engine_kind
    if _engine_kind is None:
        with get_conn():
            pass
    return _engine_kind or "sqlite"


def q(sql: str, params=()) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame."""
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def execute(sql: str, params=()) -> None:
    with get_conn() as conn:
        conn.execute(sql, params)
        conn.commit()


def scalar(sql: str, params=()):
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def today() -> str:
    import datetime
    return datetime.date.today().isoformat()
