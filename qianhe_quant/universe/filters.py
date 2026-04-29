from dataclasses import dataclass, field
import pandas as pd


@dataclass(frozen=True)
class UniverseFilterResult:
    data: pd.DataFrame
    warnings: list[str] = field(default_factory=list)


def _copy_result(df: pd.DataFrame, warnings: list[str]) -> UniverseFilterResult:
    out = df.copy()
    out.attrs["universe_warnings"] = warnings
    return UniverseFilterResult(out, warnings)


def _last_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    if "symbol" in df.columns:
        return df.sort_values("date").groupby("symbol", as_index=False).tail(1)
    return df.tail(1)


def _exclude_st(df: pd.DataFrame, warnings: list[str]) -> pd.DataFrame:
    if "name" in df.columns:
        latest = _last_snapshot(df)
        bad_symbols = latest.loc[
            latest["name"].fillna("").astype(str).str.contains(r"(^ST)|(\*ST)|退", regex=True),
            "symbol" if "symbol" in latest.columns else latest.columns[0],
        ].tolist()
        if "symbol" in df.columns and bad_symbols:
            return df.loc[~df["symbol"].isin(bad_symbols)].copy()
        if bad_symbols:
            return df.iloc[0:0].copy()
    warnings.append("exclude_st pending real data: no name/ST marker field was available.")
    return df


def _exclude_delisting_risk(df: pd.DataFrame, warnings: list[str]) -> pd.DataFrame:
    if "delisting_risk" in df.columns:
        latest = _last_snapshot(df)
        bad_symbols = latest.loc[
            latest["delisting_risk"].fillna(False).astype(bool),
            "symbol" if "symbol" in latest.columns else latest.columns[0],
        ].tolist()
        if "symbol" in df.columns and bad_symbols:
            return df.loc[~df["symbol"].isin(bad_symbols)].copy()
        if bad_symbols:
            return df.iloc[0:0].copy()
    warnings.append("exclude_delisting_risk pending real data: no delisting-risk field was available.")
    return df


def _exclude_recent_ipo(df: pd.DataFrame, warnings: list[str], min_listed_days: int) -> pd.DataFrame:
    if "listed_days" in df.columns:
        latest = _last_snapshot(df)
        bad_symbols = latest.loc[
            latest["listed_days"].fillna(0).astype(float) < float(min_listed_days),
            "symbol" if "symbol" in latest.columns else latest.columns[0],
        ].tolist()
        if "symbol" in df.columns and bad_symbols:
            return df.loc[~df["symbol"].isin(bad_symbols)].copy()
        if bad_symbols:
            return df.iloc[0:0].copy()
    warnings.append("exclude_recent_ipo pending real data: no listed-days field was available.")
    return df


def _exclude_recent_suspension(df: pd.DataFrame, warnings: list[str], lookback_days: int) -> pd.DataFrame:
    if "suspended" in df.columns:
        recent = df.sort_values("date").groupby("symbol", as_index=False).tail(lookback_days) if "symbol" in df.columns else df.tail(lookback_days)
        bad_symbols = recent.loc[
            recent["suspended"].fillna(False).astype(bool),
            "symbol" if "symbol" in recent.columns else recent.columns[0],
        ].tolist()
        if "symbol" in df.columns and bad_symbols:
            return df.loc[~df["symbol"].isin(bad_symbols)].copy()
        if bad_symbols:
            return df.iloc[0:0].copy()
    elif "volume" in df.columns:
        recent = df.sort_values("date").groupby("symbol", as_index=False).tail(lookback_days) if "symbol" in df.columns else df.tail(lookback_days)
        bad_symbols = recent.loc[
            recent["volume"].fillna(0).astype(float) <= 0,
            "symbol" if "symbol" in recent.columns else recent.columns[0],
        ].tolist()
        if "symbol" in df.columns and bad_symbols:
            warnings.append("exclude_recent_suspension inferred from zero volume because no suspension field was available.")
            return df.loc[~df["symbol"].isin(bad_symbols)].copy()
        if bad_symbols:
            warnings.append("exclude_recent_suspension inferred from zero volume because no suspension field was available.")
            return df.iloc[0:0].copy()
    warnings.append("exclude_recent_suspension pending real data: no suspension field was available.")
    return df


def _liquidity_filter(df: pd.DataFrame, warnings: list[str], min_avg_amount_20d: float) -> pd.DataFrame:
    out = df.copy()
    estimated = False
    if "amount" not in out.columns:
        if {"close", "volume"}.issubset(out.columns):
            out["amount"] = out["close"].astype(float) * out["volume"].astype(float)
            estimated = True
        else:
            warnings.append("liquidity_filter pending real data: no amount field was available.")
            return out
    if estimated:
        warnings.append("liquidity_filter used estimated amount from close * volume.")
    out = out.sort_values("date").copy()
    if "symbol" in out.columns:
        out["avg_amount_20d"] = out.groupby("symbol")["amount"].transform(
            lambda s: s.rolling(20, min_periods=1).mean()
        )
        latest = out.groupby("symbol", as_index=False).tail(1)
        keep_symbols = latest.loc[
            latest["avg_amount_20d"].fillna(0.0).astype(float) >= float(min_avg_amount_20d),
            "symbol",
        ].tolist()
        return out.loc[out["symbol"].isin(keep_symbols)].copy()
    out["avg_amount_20d"] = out["amount"].rolling(20, min_periods=1).mean()
    latest = out["avg_amount_20d"].iloc[-1] if not out.empty else 0.0
    if float(latest) < float(min_avg_amount_20d):
        return out.iloc[0:0].copy()
    return out


def apply_universe_filters(
    df: pd.DataFrame,
    *,
    exclude_st: bool = True,
    exclude_delisting_risk: bool = True,
    exclude_recent_ipo: bool = True,
    exclude_recent_suspension: bool = True,
    liquidity_filter: bool = True,
    min_listed_days: int = 120,
    suspension_lookback_days: int = 5,
    min_avg_amount_20d: float = 50_000_000.0,
) -> UniverseFilterResult:
    warnings: list[str] = []
    out = df.copy()
    if exclude_st:
        out = _exclude_st(out, warnings)
    if exclude_delisting_risk and not out.empty:
        out = _exclude_delisting_risk(out, warnings)
    if exclude_recent_ipo and not out.empty:
        out = _exclude_recent_ipo(out, warnings, min_listed_days)
    if exclude_recent_suspension and not out.empty:
        out = _exclude_recent_suspension(out, warnings, suspension_lookback_days)
    if liquidity_filter and not out.empty:
        out = _liquidity_filter(out, warnings, min_avg_amount_20d)
    return _copy_result(out, warnings)
