from pathlib import Path
import pandas as pd
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.news_factor import build_daily_news_factor, load_news_events
from qianhe_quant.research.single_stock_research import (
    ResearchSignal,
    SignalEvidence,
    clamp_score,
    signal_level_from_score,
)


THEME_TAGS = [
    "次新股",
    "电网设备",
    "特种线缆",
    "南方电网订单",
    "机器人/新能源延伸待核验",
]


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _score_trend(df: pd.DataFrame) -> float:
    latest = df.iloc[-1]
    ma5 = df["close"].rolling(5).mean().iloc[-1]
    ma20 = df["close"].rolling(20).mean().iloc[-1]
    score = 0.0
    if latest["close"] > ma5:
        score += 35
    if latest["close"] > ma20:
        score += 35
    if ma5 > ma20:
        score += 30
    return clamp_score(score)


def _score_breakout(df: pd.DataFrame) -> float:
    latest = df.iloc[-1]
    prior_20_high = df["high"].rolling(20).max().shift(1).iloc[-1]
    if pd.isna(prior_20_high):
        return 0.0
    breakout_ratio = _safe_ratio(float(latest["close"]) - float(prior_20_high), float(prior_20_high))
    if breakout_ratio > 0.03:
        return 90.0
    if breakout_ratio > 0.0:
        return 70.0
    if breakout_ratio > -0.02:
        return 40.0
    return 20.0


def _score_volume(df: pd.DataFrame) -> float:
    latest = df.iloc[-1]
    volume_ma5 = df["volume"].rolling(5).mean().iloc[-1]
    if pd.isna(volume_ma5) or volume_ma5 == 0:
        return 0.0
    volume_ratio = _safe_ratio(float(latest["volume"]), float(volume_ma5))
    if volume_ratio >= 1.8:
        return 90.0
    if volume_ratio >= 1.3:
        return 70.0
    if volume_ratio >= 1.0:
        return 50.0
    return 25.0


def _score_event(df: pd.DataFrame, news_df: pd.DataFrame) -> tuple[float, dict]:
    latest_date = df["date"].max()
    window_start = latest_date - pd.Timedelta(days=30)
    recent_news = news_df.loc[(news_df["date"] >= window_start) & (news_df["date"] <= latest_date)].copy()
    if recent_news.empty:
        return 30.0, {"news_event_count": 0, "net_news_score": 0.0}

    daily = build_daily_news_factor(recent_news)
    net_score = float(daily["news_factor_score"].sum())
    event_count = int(daily["news_event_count"].sum())
    positive_count = int(daily["positive_news_count"].sum())
    negative_count = int(daily["negative_news_count"].sum())

    base_score = 50.0 + net_score * 10.0
    if positive_count > negative_count:
        base_score += 10.0
    elif negative_count > positive_count:
        base_score -= 10.0

    return clamp_score(base_score), {
        "news_event_count": event_count,
        "net_news_score": net_score,
        "positive_news_count": positive_count,
        "negative_news_count": negative_count,
    }


def _score_risk(df: pd.DataFrame, event_meta: dict) -> tuple[float, list[str]]:
    latest_close = float(df["close"].iloc[-1])
    max_close_20 = float(df["close"].rolling(20).max().iloc[-1])
    drawdown_from_recent_high = _safe_ratio(max_close_20 - latest_close, max_close_20)

    risk_score = 25.0
    risk_notes: list[str] = [
        "This module is research-only and does not produce execution instructions.",
        "Single-stock signals can be fragile when evidence is concentrated in one narrative.",
    ]

    if drawdown_from_recent_high > 0.08:
        risk_score += 25.0
        risk_notes.append("Price remains meaningfully below the recent 20-day closing high.")

    if event_meta.get("negative_news_count", 0) > event_meta.get("positive_news_count", 0):
        risk_score += 20.0
        risk_notes.append("Recent event balance tilts negative and needs closer manual review.")

    if "机器人/新能源延伸待核验" in THEME_TAGS:
        risk_score += 10.0
        risk_notes.append("Theme extension into robotics/new energy is still pending verification.")

    return clamp_score(risk_score), risk_notes


def build_xinya_cable_signal(
    price_csv_path: str | Path,
    news_csv_path: str | Path = "qianhe_quant/data/sample_news.csv",
    stock_code: str = "TO_VERIFY",
    stock_name: str = "新亚电缆",
) -> ResearchSignal:
    df = load_ohlcv_csv(price_csv_path)
    news_df = load_news_events(news_csv_path)

    trend_score = _score_trend(df)
    breakout_score = _score_breakout(df)
    volume_score = _score_volume(df)
    event_score, event_meta = _score_event(df, news_df)
    risk_score, risk_notes = _score_risk(df, event_meta)

    final_research_signal = clamp_score(
        trend_score * 0.30
        + breakout_score * 0.20
        + volume_score * 0.15
        + event_score * 0.25
        + (100.0 - risk_score) * 0.10
    )
    signal_level = signal_level_from_score(final_research_signal, risk_score)

    latest = df.iloc[-1]
    evidence_summary = SignalEvidence(
        facts=[
            f"Latest sample close is {float(latest['close']):.2f}.",
            f"Trend score is {trend_score:.2f}, breakout score is {breakout_score:.2f}, volume score is {volume_score:.2f}.",
            f"Recent local-news event score is {event_score:.2f} based on {event_meta['news_event_count']} event rows.",
        ],
        views=[
            "The current narrative fit is strongest when the market treats the name as a grid-equipment and special-cable research case.",
            "The South China grid-order theme is worth tracking as a research theme rather than a trade instruction.",
        ],
        inferences=[
            "A higher trend score plus a constructive event score may justify stronger monitoring intensity.",
            "If breakout and volume fail to confirm, the signal should remain in observation rather than escalation.",
        ],
        verification_needed=[
            "Verify the exact stock code and exchange identifier before external publication.",
            "Verify whether South China grid order references are contract facts or only market interpretation.",
            "Verify whether robotics/new-energy theme linkage is supported by filings, products, or customer disclosures.",
        ],
    )

    verification_tasks = [
        "Cross-check the latest company filings for order, capacity, and customer disclosures.",
        "Review whether the next earnings or announcement window changes the event score meaningfully.",
        "Confirm whether special-cable exposure is revenue material or only theme-level commentary.",
    ]

    return ResearchSignal(
        stock_code=stock_code,
        stock_name=stock_name,
        theme_tags=THEME_TAGS,
        trend_score=trend_score,
        breakout_score=breakout_score,
        volume_score=volume_score,
        event_score=event_score,
        risk_score=risk_score,
        final_research_signal=final_research_signal,
        signal_level=signal_level,
        evidence_summary=evidence_summary,
        risk_notes=risk_notes,
        verification_tasks=verification_tasks,
    )


def generate_xinya_cable_signal_report(
    signal: ResearchSignal,
    template_path: str | Path = "qianhe_quant/templates/single_stock_signal_template.md",
) -> str:
    template = Path(template_path).read_text(encoding="utf-8")
    replacements = {
        "{{stock_code}}": signal.stock_code,
        "{{stock_name}}": signal.stock_name,
        "{{theme_tags}}": ", ".join(signal.theme_tags),
        "{{trend_score}}": f"{signal.trend_score:.2f}",
        "{{breakout_score}}": f"{signal.breakout_score:.2f}",
        "{{volume_score}}": f"{signal.volume_score:.2f}",
        "{{event_score}}": f"{signal.event_score:.2f}",
        "{{risk_score}}": f"{signal.risk_score:.2f}",
        "{{final_research_signal}}": f"{signal.final_research_signal:.2f}",
        "{{signal_level}}": signal.signal_level.value,
        "{{facts}}": "\n".join(f"- {item}" for item in signal.evidence_summary.facts),
        "{{views}}": "\n".join(f"- {item}" for item in signal.evidence_summary.views),
        "{{inferences}}": "\n".join(f"- {item}" for item in signal.evidence_summary.inferences),
        "{{verification_needed}}": "\n".join(
            f"- {item}" for item in signal.evidence_summary.verification_needed
        ),
        "{{risk_notes}}": "\n".join(f"- {item}" for item in signal.risk_notes),
        "{{verification_tasks}}": "\n".join(f"- {item}" for item in signal.verification_tasks),
    }

    report = template
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
