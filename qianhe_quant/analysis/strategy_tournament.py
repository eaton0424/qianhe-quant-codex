from pathlib import Path
import pandas as pd
from qianhe_quant.backtest import run_vector_backtest
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.risk import check_backtest_risk
from qianhe_quant.strategies import STRATEGIES


def _risk_level(findings: list) -> str:
    if any(f.level == "HIGH" for f in findings):
        return "HIGH"
    if any(f.level == "MEDIUM" for f in findings):
        return "MEDIUM"
    return "LOW"


def _signal_stability(trade_count: int) -> float:
    return round(1.0 / (1.0 + trade_count / 12.0), 4)


def _notes(metrics: dict, findings: list) -> str:
    messages = [f"{f.level}:{f.item}" for f in findings]
    if metrics.get("trade_count", 0) <= 2:
        messages.append("LOW_SAMPLE_WARNING")
    if metrics.get("sharpe_like", 0.0) > 2.0 and metrics.get("trade_count", 0) < 5:
        messages.append("OVERFIT_RISK_TO_VERIFY")
    return " | ".join(messages)


def run_strategy_tournament(data_path: str | Path) -> pd.DataFrame:
    base_df = load_ohlcv_csv(data_path)
    rows: list[dict] = []
    for strategy_name in ("ma_cross", "breakout", "single_stock_research", "weekly_factor_rotation"):
        strategy = STRATEGIES[strategy_name]()
        signals = strategy.generate_signals(base_df).data
        result = run_vector_backtest(signals)
        findings = check_backtest_risk(result.metrics)
        max_drawdown = abs(result.metrics.get("max_drawdown", 0.0))
        return_drawdown_ratio = (
            result.metrics.get("total_return", 0.0) / max_drawdown if max_drawdown else 0.0
        )
        rows.append(
            {
                "strategy": strategy_name,
                "total_return": result.metrics.get("total_return", 0.0),
                "annualized_return": result.metrics.get("annual_return", 0.0),
                "max_drawdown": result.metrics.get("max_drawdown", 0.0),
                "volatility": result.metrics.get("volatility", 0.0),
                "win_rate": result.metrics.get("win_rate_by_active_days", 0.0),
                "trade_count": result.metrics.get("trade_count", 0),
                "return_drawdown_ratio": return_drawdown_ratio,
                "signal_stability": _signal_stability(result.metrics.get("trade_count", 0)),
                "risk_level": _risk_level(findings),
                "notes": _notes(result.metrics, findings),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["total_return", "return_drawdown_ratio", "signal_stability"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
