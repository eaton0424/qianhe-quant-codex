import pandas as pd


def avg_turnover_20d(df: pd.DataFrame) -> tuple[pd.Series, list[str]]:
    if "turnover" in df.columns:
        turnover = pd.to_numeric(df["turnover"], errors="coerce")
        return turnover.rolling(20, min_periods=1).mean().fillna(0.0), []
    if "volume" in df.columns:
        proxy = pd.to_numeric(df["volume"], errors="coerce")
        warnings = ["avg_turnover_20d pending real turnover data: using volume as a proxy."]
        return proxy.rolling(20, min_periods=1).mean().fillna(0.0), warnings
    return pd.Series(0.0, index=df.index, dtype=float), [
        "avg_turnover_20d pending real data: no turnover or volume field is available."
    ]


def avg_amount_20d_above_threshold(
    df: pd.DataFrame,
    threshold: float,
    allow_estimated_amount: bool = True,
) -> tuple[pd.Series, list[str]]:
    warnings: list[str] = []
    if "amount" in df.columns:
        amount = pd.to_numeric(df["amount"], errors="coerce")
    elif allow_estimated_amount and {"close", "volume"}.issubset(df.columns):
        amount = pd.to_numeric(df["close"], errors="coerce") * pd.to_numeric(df["volume"], errors="coerce")
        warnings.append("avg_amount_20d_above_threshold used estimated amount from close * volume.")
    else:
        return pd.Series(0, index=df.index, dtype=int), [
            "avg_amount_20d_above_threshold pending real data: amount field is not available."
        ]
    avg_amount = amount.rolling(20, min_periods=1).mean()
    return (avg_amount >= float(threshold)).fillna(False).astype(int), warnings
