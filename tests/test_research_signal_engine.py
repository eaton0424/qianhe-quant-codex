from pathlib import Path
from qianhe_quant.research import StockProfile, build_stock_research_signal, generate_stock_signal_report
from qianhe_quant.research.event_factor import assess_event_factor


def _build_sample_profile() -> StockProfile:
    return StockProfile(
        stock_code="000001",
        stock_name="样例电网股份",
        industry="电力设备",
        theme_tags=["电网设备", "订单修复"],
        facts=["公司披露了订单增长和产能扩张更新。"],
        opinions=["市场当前把该标的归入电网投资研究观察池。"],
        assumptions=["如果订单兑现且量能确认，研究关注强度可以提升。"],
        risks=["估值对短期确认不足和波动比较敏感。"],
        verification_tasks=["核验订单表述是否来自正式公告。"],
    )


def test_research_signal_engine_outputs_required_fields():
    profile = _build_sample_profile()
    signal = build_stock_research_signal(
        profile,
        "qianhe_quant/data/sample_ohlcv.csv",
        "qianhe_quant/data/sample_news.csv",
    )
    data = signal.as_dict()
    assert data["stock_code"] == "000001"
    assert data["stock_name"] == "样例电网股份"
    assert data["final_score"] == data["final_research_signal"]
    assert data["signal_level"] in {"observe", "watch", "strong_watch", "avoid"}
    assert "电网设备" in data["theme_tags"]


def test_event_factor_exposes_standard_event_fields():
    profile = _build_sample_profile()
    assessment = assess_event_factor(profile)
    data = assessment.as_dict()
    expected = {
        "announcement_event",
        "news_event",
        "order_event",
        "policy_event",
        "product_event",
        "management_event",
        "risk_event",
        "event_score",
    }
    assert expected.issubset(data.keys())


def test_research_signal_report_respects_boundary_language():
    profile = _build_sample_profile()
    signal = build_stock_research_signal(
        profile,
        "qianhe_quant/data/sample_ohlcv.csv",
        "qianhe_quant/data/sample_news.csv",
    )
    report = generate_stock_signal_report(profile, signal)
    assert "research signal only" in report
    assert "buy, sell, hold" in report
    assert "Input Facts" in report
    assert "Evidence Summary: Inferences" in report
    assert "industry:" in report
    assert "样例电网股份" in report
    assert "订单增长" in report


def test_stock_research_templates_exist():
    input_template = Path("qianhe_quant/templates/stock_research_input_template.md")
    report_template = Path("qianhe_quant/templates/stock_signal_report_template.md")
    assert input_template.exists()
    assert report_template.exists()
