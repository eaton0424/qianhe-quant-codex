from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pandas as pd

from qianhe_quant.database.connection import connect_db, safe_close


def insert_market_daily(
    df: pd.DataFrame,
    symbol: str,
    source: str,
    overwrite_existing: bool = True,
    db_path: str | Path | None = None,
) -> int:
    conn = connect_db(db_path)
    try:
        payload = df.copy()
        payload["symbol"] = symbol
        payload["source"] = source
        payload["created_at"] = pd.Timestamp.now("UTC")
        payload = payload[["symbol", "date", "open", "high", "low", "close", "volume", "amount", "turnover", "source", "created_at"]]
        if overwrite_existing:
            dates = [pd.Timestamp(d).date() for d in payload["date"].tolist()]
            if dates:
                conn.executemany("DELETE FROM market_daily WHERE symbol = ? AND date = ?", [(symbol, d) for d in dates])
        conn.register("market_daily_payload", payload)
        conn.execute(
            """
            INSERT INTO market_daily (symbol, date, open, high, low, close, volume, amount, turnover, source, created_at)
            SELECT symbol, date, open, high, low, close, volume, amount, turnover, source, created_at
            FROM market_daily_payload
            """
        )
        conn.execute("DELETE FROM symbols WHERE symbol = ?", [symbol])
        conn.execute(
            """
            INSERT INTO symbols (symbol, name, created_at, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            [symbol, symbol],
        )
        return len(payload)
    finally:
        safe_close(conn)


def load_market_daily(symbol: str, db_path: str | Path | None = None) -> pd.DataFrame:
    conn = connect_db(db_path)
    try:
        return conn.execute(
            """
            SELECT symbol, date, open, high, low, close, volume, amount, turnover, source, created_at
            FROM market_daily
            WHERE symbol = ?
            ORDER BY date
            """,
            [symbol],
        ).df()
    finally:
        safe_close(conn)


def load_symbol_ohlcv(symbol: str, db_path: str | Path | None = None) -> pd.DataFrame:
    df = load_market_daily(symbol, db_path=db_path)
    if df.empty:
        raise ValueError(f"No OHLCV rows found for symbol={symbol}")
    return df[["date", "open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True)


def list_symbols(db_path: str | Path | None = None) -> list[str]:
    conn = connect_db(db_path)
    try:
        rows = conn.execute("SELECT symbol FROM symbols ORDER BY symbol").fetchall()
        return [row[0] for row in rows]
    finally:
        safe_close(conn)


def save_backtest_run(
    strategy_name: str,
    metrics: dict,
    notes: str = "",
    db_path: str | Path | None = None,
) -> str:
    run_id = str(uuid4())
    conn = connect_db(db_path)
    try:
        conn.execute(
            """
            INSERT INTO backtest_runs (
                run_id, strategy_name, start_date, end_date, total_return, annualized_return,
                max_drawdown, win_rate, trade_count, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                run_id,
                strategy_name,
                metrics.get("start_date"),
                metrics.get("end_date"),
                metrics.get("total_return", 0.0),
                metrics.get("annual_return", 0.0),
                metrics.get("max_drawdown", 0.0),
                metrics.get("win_rate_by_active_days", 0.0),
                metrics.get("trade_count", 0),
                notes,
            ],
        )
    finally:
        safe_close(conn)
    return run_id


def save_strategy_scores(
    run_id: str,
    strategy_name: str,
    scores: dict[str, float],
    db_path: str | Path | None = None,
) -> int:
    conn = connect_db(db_path)
    try:
        rows = [(run_id, strategy_name, name, value) for name, value in scores.items()]
        conn.executemany(
            """
            INSERT INTO strategy_scores (run_id, strategy_name, score_name, score_value)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        return len(rows)
    finally:
        safe_close(conn)
