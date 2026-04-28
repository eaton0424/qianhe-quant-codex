def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_metrics(metrics: dict) -> str:
    lines = [
        f"Sample window: {metrics.get('start_date')} to {metrics.get('end_date')}",
        f"Total return: {pct(metrics.get('total_return', 0.0))}",
        f"Annualized return: {pct(metrics.get('annual_return', 0.0))}",
        f"Max drawdown: {pct(metrics.get('max_drawdown', 0.0))}",
        f"Volatility: {pct(metrics.get('volatility', 0.0))}",
        f"Sharpe-like: {metrics.get('sharpe_like', 0.0):.2f}",
        f"Trade count: {metrics.get('trade_count', 0)}",
        f"Win rate on active days: {pct(metrics.get('win_rate_by_active_days', 0.0))}",
    ]
    return "\n".join(lines)
