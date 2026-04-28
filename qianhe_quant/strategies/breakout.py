import numpy as np
import pandas as pd
from qianhe_quant.indicators import rolling_high
from qianhe_quant.strategy_base import Strategy, SignalFrame


class BreakoutStrategy(Strategy):
    """Research-only breakout signal when close exceeds the prior rolling high."""

    name = "breakout"

    def __init__(self, window: int = 20):
        self.window = window

    def generate_signals(self, df: pd.DataFrame) -> SignalFrame:
        out = df.copy()
        prior_high = rolling_high(out["high"], self.window).shift(1)
        out["prior_high"] = prior_high
        out["signal"] = np.where(out["close"] > out["prior_high"], 1, 0)
        out["signal"] = out["signal"].fillna(0).astype(int)
        frame = SignalFrame(out)
        frame.validate()
        return frame
