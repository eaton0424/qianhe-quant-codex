import numpy as np
import pandas as pd


def close_above_ma20(df: pd.DataFrame) -> pd.Series:
    ma20 = df["close"].rolling(20, min_periods=20).mean()
    return (df["close"] > ma20).fillna(False).astype(int)


def ma20_above_ma60(df: pd.DataFrame) -> pd.Series:
    ma20 = df["close"].rolling(20, min_periods=20).mean()
    ma60 = df["close"].rolling(60, min_periods=60).mean()
    return (ma20 > ma60).fillna(False).astype(int)


def ma5_gt_ma10_gt_ma20(df: pd.DataFrame) -> pd.Series:
    ma5 = df["close"].rolling(5, min_periods=5).mean()
    ma10 = df["close"].rolling(10, min_periods=10).mean()
    ma20 = df["close"].rolling(20, min_periods=20).mean()
    return ((ma5 > ma10) & (ma10 > ma20)).fillna(False).astype(int)


def twenty_day_high_breakout(df: pd.DataFrame) -> pd.Series:
    prior_20_high = df["high"].rolling(20, min_periods=20).max().shift(1)
    return np.where(df["close"] > prior_20_high, 1, 0)
