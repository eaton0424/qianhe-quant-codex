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
