from __future__ import annotations

from pathlib import Path


REPORTS = {
    "策略排行榜报告": Path("reports/strategy_tournament_report.md"),
    "每周策略实验室报告": Path("reports/weekly_strategy_lab_report.md"),
    "日度量化研究报告": Path("reports/daily_quant_report.md"),
    "样例个股研究信号报告": Path("reports/sample_stock_signal_report.md"),
}


def read_report(path: Path) -> str:
    if not path.exists():
        return f"报告不存在：`{path}`"
    return path.read_text(encoding="utf-8", errors="replace")


def get_report_catalog() -> dict[str, Path]:
    return REPORTS.copy()
