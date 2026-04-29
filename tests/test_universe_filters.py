import pandas as pd
from qianhe_quant.data_loader import load_ohlcv_csv
from qianhe_quant.universe.filters import apply_universe_filters


def test_universe_filters_warn_without_optional_fields():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv")
    result = apply_universe_filters(df)
    assert not result.data.empty
    assert any("pending real data" in warning for warning in result.warnings)


def test_universe_filters_remove_recent_ipo_when_field_exists():
    df = load_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv").copy()
    df["symbol"] = "AAA"
    df["listed_days"] = 30
    result = apply_universe_filters(df, min_listed_days=120, liquidity_filter=False)
    assert result.data.empty
