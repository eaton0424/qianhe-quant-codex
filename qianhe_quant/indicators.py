import pandas as pd


def moving_average(series: pd.Series, window: int) -> pd.Series:
    if window <= 0:
        raise ValueError("window must be a positive integer")
    return series.rolling(window=window, min_periods=window).mean()


def daily_return(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)


def rolling_high(series: pd.Series, window: int) -> pd.Series:
    if window <= 0:
        raise ValueError("window must be a positive integer")
    return series.rolling(window=window, min_periods=window).max()
