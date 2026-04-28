from dataclasses import dataclass
import pandas as pd
from qianhe_quant.config import ResearchConfig, DEFAULT_CONFIG
from qianhe_quant.indicators import daily_return


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict


def run_vector_backtest(signal_df: pd.DataFrame, config: ResearchConfig = DEFAULT_CONFIG) -> BacktestResult:
    """Simple long/cash vector backtest. signal=1 means next-bar long; signal=0 means cash."""
    df = signal_df.copy()
    if "signal" not in df.columns:
        raise ValueError("Backtest requires a signal column")
    df["asset_return"] = daily_return(df["close"])
    df["position"] = df["signal"].shift(1).fillna(0).clip(lower=0, upper=1)
    df["position_change"] = df["position"].diff().abs().fillna(df["position"].abs())
    trading_cost = df["position_change"] * (config.commission_rate + config.slippage_rate)
    df["strategy_return"] = df["position"] * df["asset_return"] - trading_cost
    df["equity"] = config.initial_cash * (1 + df["strategy_return"]).cumprod()
    trades = df.loc[df["position_change"] > 0, ["date", "close", "position", "position_change"]].copy()
    trades["action"] = trades["position"].map(lambda x: "BUY" if x > 0 else "SELL")
    trades["symbol"] = signal_df["symbol"] if "symbol" in signal_df.columns else "SAMPLE"
    trades["suggested_qty"] = (config.initial_cash * config.max_position_pct / trades["close"]).astype(int)
    metrics = compute_core_metrics(df)
    return BacktestResult(equity_curve=df, trades=trades, metrics=metrics)


def compute_core_metrics(df: pd.DataFrame) -> dict:
    equity = df["equity"]
    total_return = equity.iloc[-1] / equity.iloc[0] - 1 if len(equity) > 1 else 0.0
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown = float(drawdown.min())
    daily = df["strategy_return"]
    annual_return = float((1 + total_return) ** (252 / max(len(df), 1)) - 1)
    volatility = float(daily.std(ddof=0) * (252 ** 0.5))
    sharpe = float(annual_return / volatility) if volatility else 0.0
    trade_count = int((df["position_change"] > 0).sum())
    win_rate = float((daily[daily != 0] > 0).mean()) if (daily != 0).any() else 0.0
    return {
        "total_return": float(total_return),
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe_like": sharpe,
        "trade_count": trade_count,
        "win_rate_by_active_days": win_rate,
        "start_date": str(df["date"].iloc[0].date()),
        "end_date": str(df["date"].iloc[-1].date()),
    }
