from dataclasses import dataclass
from qianhe_quant.config import ResearchConfig, DEFAULT_CONFIG


@dataclass
class RiskFinding:
    level: str
    item: str
    message: str


def check_backtest_risk(metrics: dict, config: ResearchConfig = DEFAULT_CONFIG) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    if abs(metrics.get("max_drawdown", 0.0)) > config.max_drawdown_limit:
        findings.append(
            RiskFinding("HIGH", "max_drawdown", "Max drawdown breached the risk limit; do not promote this strategy to paper trade.")
        )
    if metrics.get("trade_count", 0) > 120:
        findings.append(
            RiskFinding("MEDIUM", "turnover", "Trade count is elevated; review turnover, slippage, and execution assumptions.")
        )
    if metrics.get("win_rate_by_active_days", 0.0) < 0.45:
        findings.append(
            RiskFinding("MEDIUM", "win_rate", "Win rate on active days is weak; re-check signal stability and sample quality.")
        )
    if not findings:
        findings.append(RiskFinding("LOW", "basic", "No hard risk rule was breached, but manual review is still required."))
    return findings


class LiveTradingBlocked(RuntimeError):
    pass


def assert_no_live_trading(allow_live_trading: bool = False) -> None:
    if allow_live_trading:
        raise LiveTradingBlocked(
            "Live trading is blocked in V1. This repository is limited to research, backtest, paper trade, and manual review artifacts."
        )
