from pathlib import Path
import pandas as pd
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.news_factor import load_news_events
from qianhe_quant.research.event_factor import EventFactorAssessment, assess_event_factor
from qianhe_quant.research.single_stock_research import (
    ResearchSignal,
    SignalEvidence,
    clamp_score,
    signal_level_from_score,
)
from qianhe_quant.research.stock_profile import StockProfile


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


def _score_risk(
    profile: StockProfile,
    df: pd.DataFrame,
    event_assessment: EventFactorAssessment,
) -> tuple[float, list[str]]:
    latest_close = float(df["close"].iloc[-1])
    recent_high = float(df["close"].rolling(20).max().iloc[-1])
    drawdown_from_recent_high = _safe_ratio(recent_high - latest_close, recent_high)

    risk_score = 20.0 + len(profile.risks) * 8.0 + len(profile.verification_tasks) * 3.0
    risk_notes = list(profile.risks)
    risk_notes.append("This module is research-only and does not produce execution instructions.")

    if drawdown_from_recent_high > 0.08:
        risk_score += 20.0
        risk_notes.append("Price remains meaningfully below the recent 20-day closing high.")

    if event_assessment.net_news_score < 0:
        risk_score += 15.0
        risk_notes.append("Recent event balance tilts negative and needs closer manual review.")

    if len(event_assessment.caution_markers) > len(event_assessment.positive_markers):
        risk_score += 10.0
        risk_notes.append("Cautionary narrative markers currently outweigh positive event markers.")

    return clamp_score(risk_score), risk_notes


def build_stock_research_signal(
    profile: StockProfile,
    price_csv_path: str | Path,
    news_csv_path: str | Path = "qianhe_quant/data/sample_news.csv",
) -> ResearchSignal:
    df = load_ohlcv_csv(price_csv_path)
    news_df = load_news_events(news_csv_path)

    trend_score = _score_trend(df)
    breakout_score = _score_breakout(df)
    volume_score = _score_volume(df)
    latest_date = df["date"].max()
    event_assessment = assess_event_factor(profile, news_df, latest_date)
    risk_score, risk_notes = _score_risk(profile, df, event_assessment)

    final_research_signal = clamp_score(
        trend_score * 0.25
        + breakout_score * 0.20
        + volume_score * 0.15
        + event_assessment.event_score * 0.25
        + (100.0 - risk_score) * 0.15
    )
    signal_level = signal_level_from_score(final_research_signal, risk_score)

    latest = df.iloc[-1]
    evidence_summary = SignalEvidence(
        facts=profile.facts
        + [
            f"Latest sample close is {float(latest['close']):.2f}.",
            f"Trend score is {trend_score:.2f}, breakout score is {breakout_score:.2f}, volume score is {volume_score:.2f}.",
            f"Event score is {event_assessment.event_score:.2f} with {event_assessment.news_event_count} local news rows in the recent window.",
        ],
        views=profile.opinions
        + [
            f"Theme tags under review: {', '.join(profile.theme_tags) or 'none'}.",
            "The signal level is for research prioritization only, not execution.",
        ],
        inferences=profile.assumptions
        + [
            "If event strength and price confirmation improve together, monitoring intensity can move higher.",
            "If verification items accumulate or risk score stays elevated, the name should remain under observation.",
        ],
        verification_needed=profile.verification_tasks
        + [
            "Re-check the latest disclosures before publishing any external summary.",
            "Confirm that narrative tags are supported by filings, products, customers, or announcements.",
        ],
    )

    return ResearchSignal(
        stock_code=profile.stock_code,
        stock_name=profile.stock_name,
        theme_tags=profile.theme_tags,
        trend_score=trend_score,
        breakout_score=breakout_score,
        volume_score=volume_score,
        event_score=event_assessment.event_score,
        risk_score=risk_score,
        final_research_signal=final_research_signal,
        signal_level=signal_level,
        evidence_summary=evidence_summary,
        risk_notes=risk_notes,
        verification_tasks=profile.verification_tasks,
    )


def generate_stock_signal_report(
    profile: StockProfile,
    signal: ResearchSignal,
    template_path: str | Path = "qianhe_quant/templates/stock_signal_report_template.md",
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
        "{{facts}}": "\n".join(f"- {item}" for item in profile.facts),
        "{{opinions}}": "\n".join(f"- {item}" for item in profile.opinions),
        "{{assumptions}}": "\n".join(f"- {item}" for item in profile.assumptions),
        "{{risk_inputs}}": "\n".join(f"- {item}" for item in profile.risks),
        "{{verification_tasks}}": "\n".join(f"- {item}" for item in profile.verification_tasks),
        "{{evidence_facts}}": "\n".join(f"- {item}" for item in signal.evidence_summary.facts),
        "{{evidence_views}}": "\n".join(f"- {item}" for item in signal.evidence_summary.views),
        "{{evidence_inferences}}": "\n".join(f"- {item}" for item in signal.evidence_summary.inferences),
        "{{evidence_verification}}": "\n".join(
            f"- {item}" for item in signal.evidence_summary.verification_needed
        ),
        "{{risk_notes}}": "\n".join(f"- {item}" for item in signal.risk_notes),
    }

    report = template
    for key, value in replacements.items():
        report = report.replace(key, value or "- none")
    return report
