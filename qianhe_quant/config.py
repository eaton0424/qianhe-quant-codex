from dataclasses import dataclass

@dataclass(frozen=True)
class ResearchConfig:
    initial_cash: float = 1_000_000.0
    commission_rate: float = 0.0003
    slippage_rate: float = 0.0002
    max_position_pct: float = 0.30
    max_drawdown_limit: float = 0.20
    allow_live_trading: bool = False

DEFAULT_CONFIG = ResearchConfig()
