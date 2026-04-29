import pandas as pd


def pb_low_rank(df: pd.DataFrame, quantile: float = 0.3) -> tuple[pd.Series, list[str]]:
    if "pb" not in df.columns:
        return pd.Series(0, index=df.index, dtype=int), [
            "pb_low_rank pending real data: pb field is not available."
        ]
    pb = pd.to_numeric(df["pb"], errors="coerce")
    cutoff = pb.quantile(quantile)
    return (pb <= cutoff).fillna(False).astype(int), []


def pe_between_0_and_20(df: pd.DataFrame) -> tuple[pd.Series, list[str]]:
    if "pe" not in df.columns:
        return pd.Series(0, index=df.index, dtype=int), [
            "pe_between_0_and_20 pending real data: pe field is not available."
        ]
    pe = pd.to_numeric(df["pe"], errors="coerce")
    return ((pe > 0) & (pe <= 20)).fillna(False).astype(int), []
