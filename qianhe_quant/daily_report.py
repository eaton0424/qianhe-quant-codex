from pathlib import Path
import pandas as pd
from qianhe_quant.metrics import format_metrics
from qianhe_quant.risk import RiskFinding


def build_daily_quant_report(
    strategy_name: str,
    metrics: dict,
    findings: list[RiskFinding],
    latest_row: pd.Series,
) -> str:
    finding_lines = "\n".join([f"- {f.level} | {f.item}: {f.message}" for f in findings])
    latest_date = str(latest_row.get("date", ""))
    close = float(latest_row.get("close", 0.0))
    signal = int(latest_row.get("signal", 0))
    news_score = float(latest_row.get("news_factor_score", 0.0))
    event_count = int(latest_row.get("news_event_count", 0))

    return f"""# Daily Quant Research Report

## Summary
- date: {latest_date}
- strategy: {strategy_name}
- latest_close: {close:.2f}
- research_signal: {signal}
- news_factor_score: {news_score:.2f}
- news_event_count: {event_count}

## Backtest Snapshot
```text
{format_metrics(metrics)}
```

## Risk Checks
{finding_lines}

## Notes
- This is a research signal, not a buy or sell instruction.
- Live trading remains blocked.
- Any real-world action requires manual confirmation and compliance review.
"""


def save_daily_quant_report(path: str | Path, content: str) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out
