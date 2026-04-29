# Local Database Guide

## Why use a local database

V1.3 moves the project from scattered CSV-based experiments toward a local-first quant research platform. DuckDB is used because it is lightweight, local, analytics-friendly, and easy to back up.

## Default path

- `data/local_db/qianhe_quant.duckdb`

You can override this with:

- `QIANHE_QUANT_DB_PATH`

## Initialize the database

```powershell
python -m qianhe_quant.cli db-init
```

## Import local OHLCV CSV

```powershell
python -m qianhe_quant.cli db-import-ohlcv --csv qianhe_quant/data/sample_ohlcv.csv --symbol SAMPLE
```

## Run data quality checks

```powershell
python -m qianhe_quant.cli db-status
```

This command also writes:

- `reports/local_database_status_report.md`

## Export standard OHLCV for backtests

```powershell
python -m qianhe_quant.cli db-export-ohlcv --symbol SAMPLE --out qianhe_quant/data/sample_ohlcv_from_db.csv
```

## Continue running research backtests

```powershell
python -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv_from_db.csv --strategy ma_cross
python -m qianhe_quant.cli strategy-lab --data qianhe_quant/data/sample_ohlcv_from_db.csv --out reports/strategy_tournament_report.md
```

## Files that should not be uploaded to GitHub

- `data/local_db/*.duckdb`
- `data/local_db/*.wal`

Only submit schema, scripts, sample data, docs, tests, and reports.

## Backup suggestions

- Create a timestamped copy of `qianhe_quant.duckdb`
- Use `git bundle` for code
- Keep exported CSV snapshots for critical sample windows

## Current boundary

- No live trading
- No broker API connectivity
- No password, private-key, or token storage
- No automatic order execution
- Outputs remain limited to research signals, simulated portfolios, backtest results, data quality reports, and risk prompts
