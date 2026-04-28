from pathlib import Path
import numpy as np
import pandas as pd
from qianhe_quant.indicators import moving_average, rolling_high
from qianhe_quant.news_factor import build_daily_news_factor, load_news_events
from qianhe_quant.strategy_base import SignalFrame, Strategy


class SingleStockResearchSignalStrategy(Strategy):
    """Research-only signal for event-driven single-stock review such as Xinya Cable-style cases."""

    name = "single_stock_research"

    def __init__(
        self,
        breakout_window: int = 20,
        fast_ma: int = 5,
        slow_ma: int = 20,
        news_csv_path: str | Path = "qianhe_quant/data/sample_news.csv",
    ):
        if fast_ma >= slow_ma:
            raise ValueError("fast_ma must be smaller than slow_ma")
        self.breakout_window = breakout_window
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.news_csv_path = Path(news_csv_path)

    def generate_signals(self, df: pd.DataFrame) -> SignalFrame:
        out = df.copy()
        out["ma_fast"] = moving_average(out["close"], self.fast_ma)
        out["ma_slow"] = moving_average(out["close"], self.slow_ma)
        out["prior_high"] = rolling_high(out["high"], self.breakout_window).shift(1)
        out["volume_ma_5"] = out["volume"].rolling(window=5, min_periods=5).mean()
        out["volume_spike"] = np.where(out["volume"] > out["volume_ma_5"] * 1.1, 1, 0)
        out["trend_ok"] = np.where(out["ma_fast"] > out["ma_slow"], 1, 0)
        out["breakout_ok"] = np.where(out["close"] > out["prior_high"], 1, 0)

        news_df = load_news_events(self.news_csv_path)
        daily_news = build_daily_news_factor(news_df)
        out = out.merge(daily_news, on="date", how="left")
        out["news_factor_score"] = out["news_factor_score"].fillna(0.0)
        out["news_event_count"] = out["news_event_count"].fillna(0).astype(int)
        out["positive_news_count"] = out["positive_news_count"].fillna(0).astype(int)
        out["negative_news_count"] = out["negative_news_count"].fillna(0).astype(int)
        out["news_ok"] = np.where(out["news_factor_score"] > 0, 1, 0)

        out["research_signal_score"] = (
            out["trend_ok"] + out["breakout_ok"] + out["volume_spike"] + out["news_ok"]
        )
        out["signal"] = np.where(out["research_signal_score"] >= 3, 1, 0).astype(int)
        frame = SignalFrame(out)
        frame.validate()
        return frame

