from pathlib import Path
from qianhe_quant.research import StockProfile, build_stock_research_signal, generate_stock_signal_report


def _build_sample_profile() -> StockProfile:
    return StockProfile(
        stock_code="000001",
        stock_name="样例股份",
        theme_tags=["电网设备", "订单修复"],
        facts=["公司披露了订单增长和产能建设信息。"],
        opinions=["市场把该标的视为电网建设链条中的研究对象。"],
        assumptions=["若订单兑现且量能确认，研究关注级别可以提升。"],
        risks=["估值波动较大，短期需要等待更多确认。"],
        verification_tasks=["核验订单披露是否来自正式公告。"],
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
    assert data["stock_name"] == "样例股份"
    assert data["signal_level"] in {"observe", "watch", "strong_watch", "avoid"}
    assert "电网设备" in data["theme_tags"]


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


def test_stock_research_templates_exist():
    input_template = Path("qianhe_quant/templates/stock_research_input_template.md")
    report_template = Path("qianhe_quant/templates/stock_signal_report_template.md")
    assert input_template.exists()
    assert report_template.exists()
