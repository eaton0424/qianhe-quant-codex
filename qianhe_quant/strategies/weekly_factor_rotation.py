from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from qianhe_quant.factors.liquidity import avg_amount_20d_above_threshold, avg_turnover_20d
from qianhe_quant.factors.trend import (
    close_above_ma20,
    ma20_above_ma60,
    ma5_gt_ma10_gt_ma20,
    twenty_day_high_breakout,
)
from qianhe_quant.factors.valuation import pb_low_rank, pe_between_0_and_20
from qianhe_quant.strategy_base import SignalFrame, Strategy
from qianhe_quant.universe.filters import apply_universe_filters


@dataclass(frozen=True)
class StrategyLabConfig:
    min_listed_days: int = 120
    suspension_lookback_days: int = 5
    min_avg_amount_20d: float = 50_000_000.0
    top_n: int = 5
    rebalance_frequency: str = "weekly"
    commission_rate: float = 0.0003
    slippage_rate: float = 0.0002
    allow_estimated_amount: bool = True


def _parse_scalar(raw: str):
    value = raw.strip().strip("'\"")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_strategy_lab_config(path: str | Path = "configs/strategy_lab.yaml") -> StrategyLabConfig:
    file_path = Path(path)
    if not file_path.exists():
        return StrategyLabConfig()
    data: dict[str, object] = {}
    section = None
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if stripped.endswith(":") and ":" not in stripped[:-1]:
            section = stripped[:-1]
            data.setdefault(section, {})
            continue
        key, value = stripped.split(":", 1)
        parsed = _parse_scalar(value)
        if indent > 0 and section:
            section_map = data.setdefault(section, {})
            if isinstance(section_map, dict):
                section_map[key.strip()] = parsed
        else:
            data[key.strip()] = parsed
            section = None

    universe = data.get("universe", {}) if isinstance(data.get("universe"), dict) else {}
    lab = data.get("strategy_lab", {}) if isinstance(data.get("strategy_lab"), dict) else {}
    execution = data.get("execution", {}) if isinstance(data.get("execution"), dict) else {}
    return StrategyLabConfig(
        min_listed_days=int(universe.get("min_listed_days", 120)),
        suspension_lookback_days=int(universe.get("suspension_lookback_days", 5)),
        min_avg_amount_20d=float(universe.get("min_avg_amount_20d", 50_000_000.0)),
        top_n=int(lab.get("top_n", 5)),
        rebalance_frequency=str(lab.get("rebalance_frequency", "weekly")),
        commission_rate=float(execution.get("commission_rate", 0.0003)),
        slippage_rate=float(execution.get("slippage_rate", 0.0002)),
        allow_estimated_amount=bool(lab.get("allow_estimated_amount", True)),
    )


class WeeklyFactorRotationStrategy(Strategy):
    name = "weekly_factor_rotation"

    def __init__(self, config_path: str | Path = "configs/strategy_lab.yaml"):
        self.lab_config = load_strategy_lab_config(config_path)

    def generate_signals(self, df: pd.DataFrame) -> SignalFrame:
        out = df.copy()
        if "symbol" not in out.columns:
            out["symbol"] = "SAMPLE"

        filter_result = apply_universe_filters(
            out,
            min_listed_days=self.lab_config.min_listed_days,
            suspension_lookback_days=self.lab_config.suspension_lookback_days,
            min_avg_amount_20d=self.lab_config.min_avg_amount_20d,
        )
        filtered = filter_result.data.copy()
        warnings = list(filter_result.warnings)
        if filtered.empty:
            out["signal"] = 0
            out["strategy_lab_warnings"] = " | ".join(warnings or ["No eligible symbols after filters."])
            frame = SignalFrame(out)
            frame.validate()
            return frame

        filtered["trend_close_above_ma20"] = close_above_ma20(filtered)
        filtered["trend_ma20_above_ma60"] = ma20_above_ma60(filtered)
        filtered["trend_ma5_gt_ma10_gt_ma20"] = ma5_gt_ma10_gt_ma20(filtered)
        filtered["trend_twenty_day_high_breakout"] = twenty_day_high_breakout(filtered)
        filtered["trend_score"] = (
            filtered["trend_close_above_ma20"]
            + filtered["trend_ma20_above_ma60"]
            + filtered["trend_ma5_gt_ma10_gt_ma20"]
            + filtered["trend_twenty_day_high_breakout"]
        )

        pb_rank, pb_warnings = pb_low_rank(filtered)
        pe_band, pe_warnings = pe_between_0_and_20(filtered)
        turnover_20d, turnover_warnings = avg_turnover_20d(filtered)
        amount_gate, amount_warnings = avg_amount_20d_above_threshold(
            filtered,
            self.lab_config.min_avg_amount_20d,
            allow_estimated_amount=self.lab_config.allow_estimated_amount,
        )
        warnings.extend(pb_warnings + pe_warnings + turnover_warnings + amount_warnings)

        filtered["valuation_pb_low_rank"] = pb_rank
        filtered["valuation_pe_between_0_and_20"] = pe_band
        filtered["valuation_score"] = filtered["valuation_pb_low_rank"] + filtered["valuation_pe_between_0_and_20"]
        filtered["avg_turnover_20d"] = turnover_20d
        filtered["liquidity_amount_gate"] = amount_gate
        filtered["liquidity_score"] = filtered["liquidity_amount_gate"].astype(int)
        filtered["composite_score"] = (
            filtered["trend_score"] * 0.5
            + filtered["valuation_score"] * 0.2
            + filtered["liquidity_score"] * 0.3
        )

        filtered["week_period"] = filtered["date"].dt.to_period("W-FRI")
        filtered["is_rebalance_day"] = filtered.groupby("week_period")["date"].transform("max") == filtered["date"]
        rebalance_rows = filtered.loc[filtered["is_rebalance_day"]].copy()
        rebalance_rows["rank"] = rebalance_rows.groupby("date")["composite_score"].rank(
            ascending=False,
            method="first",
        )
        rebalance_rows["weekly_selection"] = (
            (rebalance_rows["rank"] <= float(self.lab_config.top_n))
            & (rebalance_rows["trend_score"] >= 2)
            & (rebalance_rows["liquidity_score"] >= 1)
        ).astype(int)
        filtered = filtered.merge(
            rebalance_rows[["date", "symbol", "weekly_selection"]],
            on=["date", "symbol"],
            how="left",
        )
        filtered["weekly_selection"] = filtered["weekly_selection"].fillna(0).astype(int)
        filtered["target_position"] = filtered["weekly_selection"].replace(0, pd.NA).ffill().fillna(0).astype(int)
        filtered["signal"] = filtered["target_position"].astype(int)
        filtered["strategy_lab_warnings"] = " | ".join(sorted(set(warnings))) if warnings else ""

        frame = SignalFrame(filtered)
        frame.validate()
        return frame
