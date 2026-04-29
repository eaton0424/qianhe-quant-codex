from qianhe_quant.analysis.strategy_tournament import run_strategy_tournament
from qianhe_quant.reporter import build_strategy_tournament_report, build_weekly_strategy_lab_report


def test_strategy_tournament_includes_expected_strategies():
    results = run_strategy_tournament("qianhe_quant/data/sample_ohlcv.csv")
    expected = {"ma_cross", "breakout", "single_stock_research", "weekly_factor_rotation"}
    assert expected.issubset(set(results["strategy"]))


def test_strategy_lab_reports_contain_boundary_language():
    results = run_strategy_tournament("qianhe_quant/data/sample_ohlcv.csv")
    tournament_report = build_strategy_tournament_report(results)
    weekly_report = build_weekly_strategy_lab_report(results)
    assert "Strategy Leaderboard" in tournament_report
    assert "does not constitute investment advice" in tournament_report
    assert "research and simulation only" in weekly_report
