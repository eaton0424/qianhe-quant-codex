from qianhe_quant.news_factor import build_daily_news_factor, load_news_events, score_news_headline


def test_score_news_headline_direction():
    assert score_news_headline("Company wins contract and upgrade") > 0
    assert score_news_headline("Company faces lawsuit and warning") < 0


def test_build_daily_news_factor_runs():
    news_df = load_news_events("qianhe_quant/data/sample_news.csv")
    factor_df = build_daily_news_factor(news_df)
    assert "news_factor_score" in factor_df.columns
    assert len(factor_df) == 4
