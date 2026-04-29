import pandas as pd

from qianhe_quant.data_quality.checks import (
    check_date_continuity,
    check_duplicate_symbol_date,
    check_missing_required_columns,
    check_missing_values,
    check_price_logic,
)


def test_data_quality_helpers_flag_expected_conditions():
    df = pd.DataFrame(
        {
            "symbol": ["A", "A"],
            "date": ["2024-01-01", "2024-01-01"],
            "high": [10, 8],
            "low": [9, 9.5],
            "close": [9.5, 9.2],
            "open": [9.2, 9.1],
            "volume": [100, 120],
        }
    )
    assert check_missing_required_columns(df, ["date", "open", "close"]) == []
    assert check_duplicate_symbol_date(df) == 1
    assert check_price_logic(df)
    assert check_missing_values(df, ["date", "close"]) == {"date": 0, "close": 0}
    gap_df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-20"])})
    assert check_date_continuity(gap_df)
