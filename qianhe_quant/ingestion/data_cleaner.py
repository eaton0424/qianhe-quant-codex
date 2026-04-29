from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleaningReport:
    input_rows: int
    output_rows: int
    dropped_empty_date: int
    dropped_empty_close: int
    dropped_duplicates: int
    warnings: list[str]


def clean_ohlcv_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    cleaned = df.copy()
    cleaned.columns = [str(col).strip().lower() for col in cleaned.columns]
    if "trade_date" in cleaned.columns and "date" not in cleaned.columns:
        cleaned = cleaned.rename(columns={"trade_date": "date"})
    if "vol" in cleaned.columns and "volume" not in cleaned.columns:
        cleaned = cleaned.rename(columns={"vol": "volume"})
    if "amt" in cleaned.columns and "amount" not in cleaned.columns:
        cleaned = cleaned.rename(columns={"amt": "amount"})

    input_rows = len(cleaned)
    warnings: list[str] = []

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    dropped_empty_date = int(cleaned["date"].isna().sum())
    cleaned = cleaned.loc[cleaned["date"].notna()].copy()

    numeric_cols = [col for col in ["open", "high", "low", "close", "volume", "amount", "turnover"] if col in cleaned.columns]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    dropped_empty_close = int(cleaned["close"].isna().sum()) if "close" in cleaned.columns else 0
    if "close" in cleaned.columns:
        cleaned = cleaned.loc[cleaned["close"].notna()].copy()

    before_dedup = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)
    dropped_duplicates = before_dedup - len(cleaned)

    if dropped_empty_date:
        warnings.append(f"Dropped {dropped_empty_date} rows with invalid or empty date.")
    if dropped_empty_close:
        warnings.append(f"Dropped {dropped_empty_close} rows with empty close.")
    if dropped_duplicates:
        warnings.append(f"Removed {dropped_duplicates} duplicate date rows.")

    report = CleaningReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        dropped_empty_date=dropped_empty_date,
        dropped_empty_close=dropped_empty_close,
        dropped_duplicates=dropped_duplicates,
        warnings=warnings,
    )
    return cleaned, report
