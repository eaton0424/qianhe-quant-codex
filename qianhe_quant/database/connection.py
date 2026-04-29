from __future__ import annotations

import os
from pathlib import Path

import duckdb


DEFAULT_DB_PATH = Path("data/local_db/qianhe_quant.duckdb")


def get_db_path() -> Path:
    override = os.getenv("QIANHE_QUANT_DB_PATH", "").strip()
    return Path(override) if override else DEFAULT_DB_PATH


def ensure_db_dir(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path is not None else get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect_db(db_path: str | Path | None = None) -> duckdb.DuckDBPyConnection:
    path = ensure_db_dir(db_path)
    return duckdb.connect(str(path))


def safe_close(conn: duckdb.DuckDBPyConnection | None) -> None:
    if conn is None:
        return
    try:
        conn.close()
    except Exception:
        pass
