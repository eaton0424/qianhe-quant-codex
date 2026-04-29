import argparse
from pathlib import Path
from qianhe_quant.analysis.strategy_tournament import run_strategy_tournament
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.strategies import STRATEGIES
from qianhe_quant.backtest import run_vector_backtest
from qianhe_quant.metrics import format_metrics
from qianhe_quant.risk import check_backtest_risk
from qianhe_quant.reporter import (
    build_markdown_report,
    build_risk_check_report,
    build_strategy_tournament_report,
    build_strategy_review_report,
    build_weekly_strategy_lab_report,
    save_dataframe,
    save_report,
)
from qianhe_quant.daily_report import build_daily_quant_report, save_daily_quant_report


def _run_backtest(data_path: str, strategy_key: str):
    df = load_ohlcv_csv(data_path)
    strategy_cls = STRATEGIES[strategy_key]
    signals = strategy_cls().generate_signals(df).data
    result = run_vector_backtest(signals)
    findings = check_backtest_risk(result.metrics)
    return result, findings


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

    args = parser.parse_args()
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
