from dataclasses import dataclass
import pandas as pd
from qianhe_quant.news_factor import build_daily_news_factor
from qianhe_quant.research.stock_profile import StockProfile


EVENT_MARKERS = {
    "announcement_event": {"announcement", "filing", "disclosure", "公告", "披露", "备案"},
    "news_event": {"news", "headline", "coverage", "新闻", "报道", "舆情"},
    "order_event": {"order", "contract", "bid", "订单", "合同", "中标"},
    "policy_event": {"policy", "regulation", "subsidy", "政策", "监管", "补贴"},
    "product_event": {"product", "launch", "capacity", "产品", "新品", "产能"},
    "management_event": {"chairman", "ceo", "management", "董事长", "高管", "管理层"},
    "risk_event": {"lawsuit", "delay", "warning", "probe", "诉讼", "延期", "风险", "核验"},
}


@dataclass(frozen=True)
class EventFactorAssessment:
    announcement_event: float
    news_event: float
    order_event: float
    policy_event: float
    product_event: float
    management_event: float
    risk_event: float
    event_score: float
    news_event_count: int = 0
    net_news_score: float = 0.0

    def as_dict(self) -> dict:
        return {
            "announcement_event": self.announcement_event,
            "news_event": self.news_event,
            "order_event": self.order_event,
            "policy_event": self.policy_event,
            "product_event": self.product_event,
            "management_event": self.management_event,
            "risk_event": self.risk_event,
            "event_score": self.event_score,
            "news_event_count": self.news_event_count,
            "net_news_score": self.net_news_score,
        }


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def _joined_text(profile: StockProfile) -> str:
    return " ".join(
        [
            profile.industry,
            *profile.theme_tags,
            *profile.facts,
            *profile.opinions,
            *profile.assumptions,
            *profile.risks,
            *profile.verification_tasks,
        ]
    ).lower()


def _keyword_score(text: str, keywords: set[str], weight: float = 16.0) -> float:
    matches = sum(1 for keyword in keywords if keyword in text)
    return _clamp_score(matches * weight)


def assess_event_factor(
    profile: StockProfile,
    news_df: pd.DataFrame | None = None,
    latest_date: pd.Timestamp | None = None,
) -> EventFactorAssessment:
    text = _joined_text(profile)
    announcement_event = _keyword_score(text, EVENT_MARKERS["announcement_event"], 18.0)
    news_event = _keyword_score(text, EVENT_MARKERS["news_event"], 12.0)
    order_event = _keyword_score(text, EVENT_MARKERS["order_event"], 18.0)
    policy_event = _keyword_score(text, EVENT_MARKERS["policy_event"], 14.0)
    product_event = _keyword_score(text, EVENT_MARKERS["product_event"], 14.0)
    management_event = _keyword_score(text, EVENT_MARKERS["management_event"], 14.0)
    risk_event = _keyword_score(text, EVENT_MARKERS["risk_event"], 14.0)

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
            news_event = _clamp_score(news_event + max(0.0, net_news_score * 10.0))
            risk_event = _clamp_score(risk_event + abs(min(0.0, net_news_score)) * 12.0)

    event_score = _clamp_score(
        announcement_event * 0.18
        + news_event * 0.17
        + order_event * 0.18
        + policy_event * 0.14
        + product_event * 0.14
        + management_event * 0.09
        + (100.0 - risk_event) * 0.10
    )

    return EventFactorAssessment(
        announcement_event=announcement_event,
        news_event=news_event,
        order_event=order_event,
        policy_event=policy_event,
        product_event=product_event,
        management_event=management_event,
        risk_event=risk_event,
        event_score=event_score,
        news_event_count=news_event_count,
        net_news_score=round(net_news_score, 2),
    )
