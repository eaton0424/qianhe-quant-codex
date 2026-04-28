import numpy as np
import pandas as pd
from qianhe_quant.indicators import moving_average
from qianhe_quant.strategy_base import Strategy, SignalFrame


class MovingAverageCrossStrategy(Strategy):
    """Research-only long/cash signal based on short and long moving averages."""

    name = "ma_cross"

    def __init__(self, short_window: int = 5, long_window: int = 20):
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> SignalFrame:
        out = df.copy()
        out["ma_short"] = moving_average(out["close"], self.short_window)
        out["ma_long"] = moving_average(out["close"], self.long_window)
        out["raw_signal"] = np.where(out["ma_short"] > out["ma_long"], 1, 0)
        out["signal"] = out["raw_signal"].fillna(0).astype(int)
        frame = SignalFrame(out)
        frame.validate()
        return frame
