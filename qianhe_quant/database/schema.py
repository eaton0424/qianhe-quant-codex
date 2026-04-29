from __future__ import annotations

from pathlib import Path

from qianhe_quant.database.connection import connect_db, get_db_path, safe_close


MIGRATION_FILE = Path(__file__).with_name("migrations") / "001_init.sql"


def init_db(db_path: str | Path | None = None) -> Path:
    conn = connect_db(db_path)
    try:
        sql = MIGRATION_FILE.read_text(encoding="utf-8")
        conn.execute(sql)
    finally:
        safe_close(conn)
    return Path(db_path) if db_path is not None else get_db_path()


def get_table_names(db_path: str | Path | None = None) -> list[str]:
    conn = connect_db(db_path)
    try:
        rows = conn.execute("SHOW TABLES").fetchall()
        return sorted(row[0] for row in rows)
    finally:
        safe_close(conn)


def is_db_initialized(db_path: str | Path | None = None) -> bool:
    expected = {
        "symbols",
        "market_daily",
        "news_events",
        "announcements",
        "fundamentals",
        "factor_daily",
        "backtest_runs",
        "strategy_scores",
        "data_quality_logs",
    }
    try:
        tables = set(get_table_names(db_path))
    except Exception:
        return False
    return expected.issubset(tables)
