from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.strategies.weekly_factor_rotation import WeeklyFactorRotationStrategy, load_strategy_lab_config


def test_weekly_factor_rotation_generates_valid_signal_frame():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    strategy = WeeklyFactorRotationStrategy()
    frame = strategy.generate_signals(df)
    assert "signal" in frame.data.columns
    assert "composite_score" in frame.data.columns
    assert "strategy_lab_warnings" in frame.data.columns
    frame.validate()


def test_strategy_lab_config_loads_yaml():
    config = load_strategy_lab_config("configs/strategy_lab.yaml")
    assert config.top_n == 5
    assert config.rebalance_frequency == "weekly"
