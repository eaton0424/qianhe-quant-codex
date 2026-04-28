from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.strategies import STRATEGIES


def test_single_stock_research_strategy_runs():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    strategy = STRATEGIES["single_stock_research"]()
    signals = strategy.generate_signals(df).data
    assert "news_factor_score" in signals.columns
    assert "research_signal_score" in signals.columns
    assert "signal" in signals.columns

