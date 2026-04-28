from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.strategies import MovingAverageCrossStrategy
from qianhe_quant.backtest import run_vector_backtest
from qianhe_quant.risk import assert_no_live_trading, LiveTradingBlocked

def test_backtest_runs_on_sample_data():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    signals = MovingAverageCrossStrategy().generate_signals(df).data
    result = run_vector_backtest(signals)
    assert "total_return" in result.metrics
    assert result.metrics["trade_count"] >= 0

def test_live_trading_blocked():
    try:
        assert_no_live_trading(True)
    except LiveTradingBlocked:
        assert True
    else:
        assert False, "live trading must be blocked"
