from dataclasses import dataclass, field
from enum import StrEnum


class SignalLevel(StrEnum):
    OBSERVE = "observe"
    WATCH = "watch"
    STRONG_WATCH = "strong_watch"
    AVOID = "avoid"


@dataclass(frozen=True)
class SignalEvidence:
    facts: list[str] = field(default_factory=list)
    views: list[str] = field(default_factory=list)
    inferences: list[str] = field(default_factory=list)
    verification_needed: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResearchSignal:
    stock_code: str
    stock_name: str
    theme_tags: list[str]
    trend_score: float
    breakout_score: float
    volume_score: float
    event_score: float
    risk_score: float
    final_research_signal: float
    signal_level: SignalLevel
    evidence_summary: SignalEvidence
    risk_notes: list[str]
    verification_tasks: list[str]

    @property
    def final_score(self) -> float:
        return self.final_research_signal

    def as_dict(self) -> dict:
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "theme_tags": self.theme_tags,
            "trend_score": self.trend_score,
            "breakout_score": self.breakout_score,
            "volume_score": self.volume_score,
            "event_score": self.event_score,
            "risk_score": self.risk_score,
            "final_score": self.final_score,
            "final_research_signal": self.final_research_signal,
            "signal_level": self.signal_level.value,
            "evidence_summary": {
                "facts": self.evidence_summary.facts,
                "views": self.evidence_summary.views,
                "inferences": self.evidence_summary.inferences,
                "verification_needed": self.evidence_summary.verification_needed,
            },
            "risk_notes": self.risk_notes,
            "verification_tasks": self.verification_tasks,
        }


def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def signal_level_from_score(final_research_signal: float, risk_score: float) -> SignalLevel:
    if risk_score >= 70:
        return SignalLevel.AVOID
    if final_research_signal >= 75:
        return SignalLevel.STRONG_WATCH
    if final_research_signal >= 50:
        return SignalLevel.WATCH
    return SignalLevel.OBSERVE
