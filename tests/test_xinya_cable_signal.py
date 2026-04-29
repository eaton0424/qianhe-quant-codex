from pathlib import Path

from qianhe_quant.research.xinya_cable_signal import (
    build_xinya_cable_signal,
    generate_xinya_cable_signal_report,
)


def test_xinya_cable_signal_fields_are_present():
    signal = build_xinya_cable_signal("qianhe_quant/data/sample_ohlcv.csv")
    data = signal.as_dict()
    expected_keys = {
        "stock_code",
        "stock_name",
        "theme_tags",
        "trend_score",
        "breakout_score",
        "volume_score",
        "event_score",
        "risk_score",
        "final_research_signal",
        "signal_level",
        "evidence_summary",
        "risk_notes",
        "verification_tasks",
    }
    assert expected_keys.issubset(data.keys())
    assert signal.stock_name == "\u65b0\u4e9a\u7535\u7f06"
    assert "\u5357\u65b9\u7535\u7f51\u8ba2\u5355" in signal.theme_tags


def test_xinya_cable_report_contains_research_boundary():
    signal = build_xinya_cable_signal("qianhe_quant/data/sample_ohlcv.csv")
    report = generate_xinya_cable_signal_report(signal)
    assert "research signal only" in report
    assert "buy, sell, hold" in report
    assert "Input Facts" in report


def test_xinya_template_file_exists():
    template_path = Path("qianhe_quant/templates/stock_signal_report_template.md")
    assert template_path.exists()
