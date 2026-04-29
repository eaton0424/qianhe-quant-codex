from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from qianhe_quant.data_quality.checks import (
    check_date_continuity,
    check_duplicate_symbol_date,
    check_missing_required_columns,
    check_missing_values,
    check_price_logic,
    write_quality_log,
)
from qianhe_quant.database.repository import insert_market_daily
from qianhe_quant.ingestion.data_cleaner import CleaningReport, clean_ohlcv_dataframe


REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class OHLCVImportResult:
    symbol: str
    row_count: int
    warnings: list[str]
    source: str
    cleaning_report: CleaningReport


def import_ohlcv_csv(
    csv_path: str | Path,
    symbol: str,
    db_path: str | Path | None = None,
    overwrite_existing: bool = True,
) -> OHLCVImportResult:
    raw = pd.read_csv(csv_path)
    cleaned, cleaning_report = clean_ohlcv_dataframe(raw)
    missing_cols = check_missing_required_columns(cleaned, REQUIRED_COLUMNS)
    if missing_cols:
        raise ValueError(f"CSV is missing required columns after cleaning: {missing_cols}")

    warnings = list(cleaning_report.warnings)
    source = "local_csv"
    if "amount" not in cleaned.columns:
        cleaned["amount"] = cleaned["close"] * cleaned["volume"]
        source = "local_csv|estimated_amount"
        warnings.append("amount column missing; estimated with close * volume")
    else:
        cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
        cleaned["amount"] = cleaned["amount"].fillna(cleaned["close"] * cleaned["volume"])
        if cleaned["amount"].isna().any():
            raise ValueError("amount column could not be recovered after estimation")

    cleaned["turnover"] = cleaned["amount"]
    cleaned["symbol"] = symbol

    duplicate_count = check_duplicate_symbol_date(cleaned[["symbol", "date"]].copy())
    if duplicate_count:
        warnings.append(f"duplicate symbol+date rows found before insert: {duplicate_count}")
        write_quality_log("market_daily", "duplicate_symbol_date", "WARNING", warnings[-1], db_path=db_path)

    price_issues = check_price_logic(cleaned)
    for issue in price_issues:
        warnings.append(issue)
        write_quality_log("market_daily", "price_logic", "WARNING", issue, db_path=db_path)

    missing_values = check_missing_values(cleaned, REQUIRED_COLUMNS + ["amount"])
    if any(missing_values.values()):
        message = f"missing values summary: {missing_values}"
        warnings.append(message)
        write_quality_log("market_daily", "missing_values", "WARNING", message, db_path=db_path)

    for issue in check_date_continuity(cleaned):
        warnings.append(issue)
        write_quality_log("market_daily", "date_continuity", "WARNING", issue, db_path=db_path)

    inserted = insert_market_daily(
        cleaned,
        symbol=symbol,
        source=source,
        overwrite_existing=overwrite_existing,
        db_path=db_path,
    )
    write_quality_log("market_daily", "import_result", "INFO", f"Imported {inserted} rows for {symbol}", db_path=db_path)
    return OHLCVImportResult(
        symbol=symbol,
        row_count=inserted,
        warnings=warnings,
        source=source,
        cleaning_report=cleaning_report,
    )
