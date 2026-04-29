from pathlib import Path
import pandas as pd
from qianhe_quant.metrics import format_metrics
from qianhe_quant.risk import RiskFinding


def build_markdown_report(strategy_name: str, metrics: dict, findings: list[RiskFinding]) -> str:
    risk_lines = "\n".join([f"- **{f.level} | {f.item}**: {f.message}" for f in findings])
    return f"""# Quant Backtest Report - {strategy_name}

## Scope
This report is for research, backtest review, paper-trade preparation, and risk logging only.
It is not investment advice and must not be used for live order execution.

## Core Metrics
```text
{format_metrics(metrics)}
```

## Risk Checks
{risk_lines}

## Next Review Questions

- Is the data source complete and adjusted correctly?
- Does the sample cover multiple market regimes?
- Are slippage and commission assumptions realistic?
- Is there any sign of look-ahead bias, survivorship bias, or overfitting?
- Do we need sector, market-cap, or liquidity filters?
"""


def build_strategy_review_report(strategy_name: str, metrics: dict, findings: list[RiskFinding], trade_count: int) -> str:
    finding_lines = "\n".join([f"- {f.level} | {f.item}: {f.message}" for f in findings])
    return f"""# strategy_review.md

## Strategy
- name: {strategy_name}
- trade_count: {trade_count}
- sample_window: {metrics.get("start_date")} to {metrics.get("end_date")}

## Performance Snapshot
- total_return: {metrics.get("total_return", 0.0):.4f}
- annual_return: {metrics.get("annual_return", 0.0):.4f}
- max_drawdown: {metrics.get("max_drawdown", 0.0):.4f}
- sharpe_like: {metrics.get("sharpe_like", 0.0):.4f}

## Review Notes
- This strategy remains research-only.
- Live trading is blocked by repository rules.
- Any promotion to paper trade requires manual confirmation.

## Risk Findings
{finding_lines}
"""


def build_risk_check_report(metrics: dict, findings: list[RiskFinding]) -> str:
    finding_lines = "\n".join([f"- {f.level} | {f.item}: {f.message}" for f in findings])
    return f"""# risk_check_report.md

## Risk Summary
- max_drawdown: {metrics.get("max_drawdown", 0.0):.4f}
- volatility: {metrics.get("volatility", 0.0):.4f}
- trade_count: {metrics.get("trade_count", 0)}
- win_rate_by_active_days: {metrics.get("win_rate_by_active_days", 0.0):.4f}

## Findings
{finding_lines}

## Compliance Notes
- no live trading
- no broker API connectivity
- no password or private-key storage
- manual confirmation required before any real-world action
"""


def save_dataframe(path: str | Path, df: pd.DataFrame) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    return out


def save_report(path: str | Path, content: str) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def build_strategy_tournament_report(results: pd.DataFrame) -> str:
    ranked = results.reset_index(drop=True).copy()
    ranked["return_rank"] = ranked["total_return"].rank(ascending=False, method="min").astype(int)
    ranked["drawdown_rank"] = ranked["max_drawdown"].rank(ascending=False, method="min").astype(int)
    ranked["stability_rank"] = ranked["signal_stability"].rank(ascending=False, method="min").astype(int)
    rows = "\n".join(
        [
            f"| {row.strategy} | {row.total_return:.2%} | {row.annualized_return:.2%} | {row.max_drawdown:.2%} | {row.volatility:.2%} | {row.win_rate:.2%} | {int(row.trade_count)} | {row.return_drawdown_ratio:.2f} | {row.signal_stability:.2f} | {row.risk_level} | {row.notes} |"
            for row in ranked.itertuples()
        ]
    )
    return f"""# Strategy Tournament Report

## Strategy Leaderboard
| strategy | total_return | annualized_return | max_drawdown | volatility | win_rate | trade_count | return_drawdown_ratio | signal_stability | risk_level | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{rows}

## Return Ranking
{chr(10).join([f"- {row.strategy}: rank {int(row.return_rank)}" for row in ranked.itertuples()])}

## Drawdown Ranking
{chr(10).join([f"- {row.strategy}: rank {int(row.drawdown_rank)}" for row in ranked.itertuples()])}

## Stability Ranking
{chr(10).join([f"- {row.strategy}: rank {int(row.stability_rank)}" for row in ranked.itertuples()])}

## Risk Notes
- High-return high-risk strategies require stricter manual review before entering any observation pool.
- Strategy rankings are for research, simulation, and comparison only.
- This report does not constitute investment advice.
"""


def build_weekly_strategy_lab_report(results: pd.DataFrame) -> str:
    ranked = results.sort_values("total_return", ascending=False).reset_index(drop=True)
    best = ranked.iloc[0]
    worst = ranked.iloc[-1]
    lower_drawdown = ranked.sort_values("max_drawdown", ascending=False).iloc[0]
    risky = ranked.loc[(ranked["total_return"] > ranked["total_return"].median()) & (ranked["risk_level"] != "LOW")]
    risky_lines = "\n".join([f"- {row.strategy}: {row.notes}" for row in risky.itertuples()]) or "- none"
    continue_watch = "\n".join([f"- {row.strategy}" for row in ranked.head(2).itertuples()])
    return f"""# Weekly Strategy Lab Report

## Weekly Strategy Ranking
{chr(10).join([f"- {idx + 1}. {row.strategy}: total_return {row.total_return:.2%}, max_drawdown {row.max_drawdown:.2%}, risk {row.risk_level}" for idx, row in enumerate(ranked.itertuples())])}

## Best Strategy
- {best.strategy}: total_return {best.total_return:.2%}, annualized_return {best.annualized_return:.2%}

## Weakest Strategy
- {worst.strategy}: total_return {worst.total_return:.2%}, max_drawdown {worst.max_drawdown:.2%}

## Lower Drawdown Preference
- {lower_drawdown.strategy}: max_drawdown {lower_drawdown.max_drawdown:.2%}, volatility {lower_drawdown.volatility:.2%}

## High Return High Risk Warning
{risky_lines}

## Strategy Failure Risk
- Any strategy with LOW_SAMPLE_WARNING or OVERFIT_RISK_TO_VERIFY in notes should remain under manual review.
- Missing valuation or liquidity data must be marked as pending before strategy promotion.

## Continue Observing Next Week
{continue_watch}

## Boundary
- This report is for research and simulation only.
- It does not constitute investment advice.
- No result here should be converted into a live trading instruction.
"""
