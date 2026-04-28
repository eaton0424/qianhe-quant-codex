from dataclasses import dataclass, field
import pandas as pd
from qianhe_quant.news_factor import build_daily_news_factor
from qianhe_quant.research.stock_profile import StockProfile


POSITIVE_EVENT_KEYWORDS = {
    "order",
    "contract",
    "approval",
    "expansion",
    "growth",
    "capacity",
    "grid",
    "launch",
    "订单",
    "合同",
    "中标",
    "批复",
    "扩产",
    "增长",
    "电网",
    "投产",
    "新品",
    "交付",
}

CAUTION_EVENT_KEYWORDS = {
    "delay",
    "warning",
    "competition",
    "uncertain",
    "verify",
    "probe",
    "lawsuit",
    "downgrade",
    "核验",
    "延迟",
    "风险",
    "诉讼",
    "竞争",
    "不确定",
    "减值",
    "下滑",
}


@dataclass(frozen=True)
class EventFactorAssessment:
    event_score: float
    positive_markers: list[str] = field(default_factory=list)
    caution_markers: list[str] = field(default_factory=list)
    news_event_count: int = 0
    net_news_score: float = 0.0

    def as_dict(self) -> dict:
        return {
            "event_score": self.event_score,
            "positive_markers": self.positive_markers,
            "caution_markers": self.caution_markers,
            "news_event_count": self.news_event_count,
            "net_news_score": self.net_news_score,
        }


def _collect_keyword_markers(items: list[str], keywords: set[str]) -> list[str]:
    joined = " ".join(items).lower()
    return sorted(keyword for keyword in keywords if keyword in joined)


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def assess_event_factor(
    profile: StockProfile,
    news_df: pd.DataFrame | None = None,
    latest_date: pd.Timestamp | None = None,
) -> EventFactorAssessment:
    narrative_items = profile.theme_tags + profile.facts + profile.opinions + profile.assumptions
    positive_markers = _collect_keyword_markers(narrative_items, POSITIVE_EVENT_KEYWORDS)
    caution_markers = _collect_keyword_markers(
        narrative_items + profile.risks + profile.verification_tasks,
        CAUTION_EVENT_KEYWORDS,
    )

    base_score = 45.0 + len(positive_markers) * 8.0 - len(caution_markers) * 6.0
    news_event_count = 0
    net_news_score = 0.0
    if news_df is not None and not news_df.empty:
        scoped_news = news_df.copy()
        if latest_date is not None:
            window_start = latest_date - pd.Timedelta(days=30)
            scoped_news = scoped_news.loc[
                (scoped_news["date"] >= window_start) & (scoped_news["date"] <= latest_date)
            ].copy()
        if not scoped_news.empty:
            daily = build_daily_news_factor(scoped_news)
            news_event_count = int(daily["news_event_count"].sum())
            net_news_score = float(daily["news_factor_score"].sum())
            base_score += net_news_score * 10.0

    return EventFactorAssessment(
        event_score=_clamp_score(base_score),
        positive_markers=positive_markers,
        caution_markers=caution_markers,
        news_event_count=news_event_count,
        net_news_score=round(net_news_score, 2),
    )
