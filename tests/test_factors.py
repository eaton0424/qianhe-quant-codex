from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.factors.liquidity import avg_amount_20d_above_threshold, avg_turnover_20d
from qianhe_quant.factors.trend import (
    close_above_ma20,
    ma20_above_ma60,
    ma5_gt_ma10_gt_ma20,
    twenty_day_high_breakout,
)
from qianhe_quant.factors.valuation import pb_low_rank, pe_between_0_and_20


def test_trend_factors_return_series():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    assert len(close_above_ma20(df)) == len(df)
    assert len(ma20_above_ma60(df)) == len(df)
    assert len(ma5_gt_ma10_gt_ma20(df)) == len(df)
    assert len(twenty_day_high_breakout(df)) == len(df)


def test_valuation_factors_warn_when_fields_missing():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    pb_signal, pb_warnings = pb_low_rank(df)
    pe_signal, pe_warnings = pe_between_0_and_20(df)
    assert pb_signal.sum() == 0
    assert pe_signal.sum() == 0
    assert pb_warnings
    assert pe_warnings


def test_liquidity_factor_estimates_amount_when_missing():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    signal, warnings = avg_amount_20d_above_threshold(df, threshold=1.0)
    turnover, turnover_warnings = avg_turnover_20d(df)
    assert signal.iloc[-1] == 1
    assert len(turnover) == len(df)
    assert warnings
    assert turnover_warnings
