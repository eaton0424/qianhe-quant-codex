import argparse
from pathlib import Path

from qianhe_quant.analysis.strategy_tournament import run_strategy_tournament
from qianhe_quant.database.connection import get_db_path, connect_db, safe_close
from qianhe_quant.database.repository import (
    load_symbol_ohlcv,
    save_backtest_run,
    save_strategy_scores,
)
from qianhe_quant.database.schema import get_table_names, init_db, is_db_initialized
from qianhe_quant.ingestion.ohlcv_importer import import_ohlcv_csv
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.daily_report import build_daily_quant_report, save_daily_quant_report
from qianhe_quant.metrics import format_metrics
from qianhe_quant.reporter import (
    build_markdown_report,
    build_risk_check_report,
    build_strategy_review_report,
    build_strategy_tournament_report,
    build_weekly_strategy_lab_report,
    save_dataframe,
    save_report,
)
from qianhe_quant.risk import check_backtest_risk
from qianhe_quant.strategies import STRATEGIES
from qianhe_quant.backtest import run_vector_backtest


DEFAULT_DB_PATH = get_db_path()


def _run_backtest(data_path: str, strategy_key: str):
    df = load_ohlcv_csv(data_path)
    strategy_cls = STRATEGIES[strategy_key]
    signals = strategy_cls().generate_signals(df).data
    result = run_vector_backtest(signals)
    findings = check_backtest_risk(result.metrics)
    return result, findings


def _run_backtest_from_db(symbol: str, strategy_key: str, db_path: str):
    df = load_symbol_ohlcv(symbol, db_path=db_path)
    strategy_cls = STRATEGIES[strategy_key]
    signals = strategy_cls().generate_signals(df).data
    result = run_vector_backtest(signals)
    findings = check_backtest_risk(result.metrics)
    return result, findings


def _build_local_database_status_report(db_path: Path) -> str:
    initialized = is_db_initialized(db_path)
    if not initialized:
        return f"""# Local Database Status Report

## Database Path
- {db_path}

## Initialization
- initialized: false

## Risk Notes
- Database is not initialized yet.
- Run `python -m qianhe_quant.cli db-init` before importing local data.
- This platform remains research-only and does not support live trading.
"""
    conn = connect_db(db_path)
    try:
        tables = get_table_names(db_path)
        market_daily_count = conn.execute("SELECT COUNT(*) FROM market_daily").fetchone()[0]
        symbols_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        quality_count = conn.execute("SELECT COUNT(*) FROM data_quality_logs").fetchone()[0]
        latest_import = conn.execute(
            """
            SELECT message, created_at
            FROM data_quality_logs
            WHERE check_name = 'import_result'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        safe_close(conn)

    latest_line = "- none"
    if latest_import:
        latest_line = f"- {latest_import[0]} at {latest_import[1]}"

    return f"""# Local Database Status Report

## Database Path
- {db_path}

## Initialization
- initialized: true

## Current Tables
{chr(10).join([f"- {table}" for table in tables])}

## Row Counts
- market_daily: {market_daily_count}
- symbols: {symbols_count}
- data_quality_logs: {quality_count}

## Latest Import Result
{latest_line}

## Risk Notes
- This database is for local research, simulation, and backtest workflows only.
- It does not connect to broker APIs.
- It must not be used for live order execution or investment advice.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Qianhe Quant research and paper-trade tool V1")
    sub = parser.add_subparsers(dest="cmd", required=True)

    bt = sub.add_parser("backtest", help="Run a research backtest")
    bt.add_argument("--data", required=True)
    bt.add_argument("--strategy", choices=sorted(STRATEGIES), default="ma_cross")

    rp = sub.add_parser("report", help="Generate markdown review reports")
    rp.add_argument("--data", required=True)
    rp.add_argument("--strategy", choices=sorted(STRATEGIES), default="ma_cross")
    rp.add_argument("--out", required=True)

    dr = sub.add_parser("daily-report", help="Generate daily quant research report")
    dr.add_argument("--data", required=True)
    dr.add_argument("--strategy", choices=sorted(STRATEGIES), default="single_stock_research")
    dr.add_argument("--out", required=True)

    sl = sub.add_parser("strategy-lab", help="Generate strategy tournament and weekly lab reports")
    sl.add_argument("--data", default="qianhe_quant/data/sample_ohlcv.csv")
    sl.add_argument("--out", required=True)

    dbi = sub.add_parser("db-init", help="Initialize local DuckDB schema")
    dbi.add_argument("--db", default=str(DEFAULT_DB_PATH))

    dbs = sub.add_parser("db-status", help="Show local database status and write a status report")
    dbs.add_argument("--db", default=str(DEFAULT_DB_PATH))

    dio = sub.add_parser("db-import-ohlcv", help="Import local OHLCV CSV into DuckDB")
    dio.add_argument("--csv", required=True)
    dio.add_argument("--symbol", required=True)
    dio.add_argument("--db", default=str(DEFAULT_DB_PATH))

    deo = sub.add_parser("db-export-ohlcv", help="Export standard OHLCV from DuckDB")
    deo.add_argument("--symbol", required=True)
    deo.add_argument("--out", required=True)
    deo.add_argument("--db", default=str(DEFAULT_DB_PATH))

    dbb = sub.add_parser("db-backtest", help="Run a research backtest from local DuckDB")
    dbb.add_argument("--symbol", required=True)
    dbb.add_argument("--strategy", choices=sorted(STRATEGIES), default="ma_cross")
    dbb.add_argument("--db", default=str(DEFAULT_DB_PATH))

    args = parser.parse_args()
    if args.cmd == "db-init":
        path = init_db(args.db)
        print(f"Database initialized: {path}")
        return

    if args.cmd == "db-status":
        db_path = Path(args.db)
        report = _build_local_database_status_report(db_path)
        report_path = save_report("reports/local_database_status_report.md", report)
        print(report)
        print(f"\nStatus report generated: {report_path}")
        return

    if args.cmd == "db-import-ohlcv":
        init_db(args.db)
        result = import_ohlcv_csv(args.csv, symbol=args.symbol, db_path=args.db)
        print(f"Imported {result.row_count} rows for {result.symbol}")
        print(f"Source: {result.source}")
        for warning in result.warnings:
            print(f"- WARNING: {warning}")
        return

    if args.cmd == "db-export-ohlcv":
        df = load_symbol_ohlcv(args.symbol, db_path=args.db).copy()
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        out = save_dataframe(args.out, df)
        print(f"Exported standard OHLCV: {out}")
        return

    if args.cmd == "db-backtest":
        result, findings = _run_backtest_from_db(args.symbol, args.strategy, args.db)
        run_id = save_backtest_run(args.strategy, result.metrics, notes=f"db-symbol={args.symbol}", db_path=args.db)
        save_strategy_scores(
            run_id,
            args.strategy,
            {
                "total_return": result.metrics.get("total_return", 0.0),
                "annual_return": result.metrics.get("annual_return", 0.0),
                "max_drawdown": result.metrics.get("max_drawdown", 0.0),
                "win_rate": result.metrics.get("win_rate_by_active_days", 0.0),
            },
            db_path=args.db,
        )
        print(format_metrics(result.metrics))
        print(f"\nBacktest run saved: {run_id}")
        print("\nRisk checks:")
        for f in findings:
            print(f"- {f.level} | {f.item}: {f.message}")
        return

    if args.cmd == "strategy-lab":
        tournament = run_strategy_tournament(args.data)
        tournament_out = save_report(args.out, build_strategy_tournament_report(tournament))
        weekly_out = save_report(
            Path(args.out).parent / "weekly_strategy_lab_report.md",
            build_weekly_strategy_lab_report(tournament),
        )
        print(f"Strategy tournament report generated: {tournament_out}")
        print(f"Weekly strategy lab report generated: {weekly_out}")
        return

    result, findings = _run_backtest(args.data, args.strategy)
    if args.cmd == "backtest":
        print(format_metrics(result.metrics))
        print("\nRisk checks:")
        for f in findings:
            print(f"- {f.level} | {f.item}: {f.message}")
    elif args.cmd == "report":
        report = build_markdown_report(args.strategy, result.metrics, findings)
        out = save_report(args.out, report)
        base_dir = Path(out).parent
        strategy_review_path = save_report(
            base_dir / "strategy_review.md",
            build_strategy_review_report(args.strategy, result.metrics, findings, len(result.trades)),
        )
        risk_report_path = save_report(
            base_dir / "risk_check_report.md",
            build_risk_check_report(result.metrics, findings),
        )
        paper_trade_log_path = save_dataframe(base_dir / "paper_trade_log.csv", result.trades)
        print(f"Report generated: {out}")
        print(f"Strategy review generated: {strategy_review_path}")
        print(f"Risk check report generated: {risk_report_path}")
        print(f"Paper trade log generated: {paper_trade_log_path}")
    elif args.cmd == "daily-report":
        latest_row = result.equity_curve.iloc[-1]
        report = build_daily_quant_report(args.strategy, result.metrics, findings, latest_row)
        out = save_daily_quant_report(args.out, report)
        print(f"Daily quant report generated: {out}")



if __name__ == "__main__":
    main()
