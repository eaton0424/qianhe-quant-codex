from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pandas as pd

from qianhe_quant.database.connection import connect_db, safe_close


def check_missing_required_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    return [col for col in required_columns if col not in df.columns]


def check_duplicate_symbol_date(df: pd.DataFrame) -> int:
    if not {"symbol", "date"}.issubset(df.columns):
        return 0
    return int(df.duplicated(subset=["symbol", "date"]).sum())


def check_price_logic(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if not {"high", "low", "close"}.issubset(df.columns):
        return issues
    invalid = df.loc[(df["high"] < df["low"]) | (df["high"] < df["close"]) | (df["low"] > df["close"])]
    if not invalid.empty:
        issues.append(f"Found {len(invalid)} rows failing price logic checks.")
    return issues


def check_missing_values(df: pd.DataFrame, columns: list[str]) -> dict[str, int]:
    return {col: int(df[col].isna().sum()) for col in columns if col in df.columns}


def check_date_continuity(df: pd.DataFrame) -> list[str]:
    if "date" not in df.columns or len(df) <= 1:
        return []
    ordered = pd.to_datetime(df["date"]).sort_values().reset_index(drop=True)
    gaps = ordered.diff().dropna()
    large_gaps = gaps[gaps.dt.days > 7]
    if large_gaps.empty:
        return []
    return [f"Detected {len(large_gaps)} date gaps larger than 7 days."]


def write_quality_log(
    table_name: str,
    check_name: str,
    status: str,
    message: str,
    db_path: str | Path | None = None,
) -> None:
    conn = connect_db(db_path)
    try:
        conn.execute(
            """
            INSERT INTO data_quality_logs (log_id, table_name, check_name, status, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            [str(uuid4()), table_name, check_name, status, message],
        )
    finally:
        safe_close(conn)
