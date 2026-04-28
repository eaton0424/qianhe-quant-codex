from dataclasses import dataclass
from pathlib import Path
import pandas as pd


POSITIVE_KEYWORDS = {"beat", "approval", "contract", "growth", "upgrade", "launch"}
NEGATIVE_KEYWORDS = {"fraud", "probe", "lawsuit", "downgrade", "warning", "delay"}


@dataclass(frozen=True)
class NewsFactorConfig:
    positive_weight: float = 1.0
    negative_weight: float = -1.0


def load_news_events(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"date", "headline"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"News factor file is missing required columns: {sorted(missing)}")
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    out["headline"] = out["headline"].fillna("").astype(str)
    if "symbol" not in out.columns:
        out["symbol"] = "SAMPLE"
    return out.sort_values("date").reset_index(drop=True)


def score_news_headline(headline: str, config: NewsFactorConfig = NewsFactorConfig()) -> float:
    words = set(headline.lower().replace(",", " ").replace(".", " ").split())
    score = 0.0
    score += sum(config.positive_weight for keyword in POSITIVE_KEYWORDS if keyword in words)
    score += sum(config.negative_weight for keyword in NEGATIVE_KEYWORDS if keyword in words)
    return score


def build_daily_news_factor(news_df: pd.DataFrame, config: NewsFactorConfig = NewsFactorConfig()) -> pd.DataFrame:
    out = news_df.copy()
    out["news_factor_score"] = out["headline"].map(lambda text: score_news_headline(text, config))
    grouped = (
        out.groupby("date", as_index=False)
        .agg(
            news_factor_score=("news_factor_score", "sum"),
            news_event_count=("headline", "count"),
            positive_news_count=("news_factor_score", lambda s: int((s > 0).sum())),
            negative_news_count=("news_factor_score", lambda s: int((s < 0).sum())),
        )
    )
    return grouped
