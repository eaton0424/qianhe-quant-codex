from pathlib import Path

from qianhe_quant.database.repository import (
    list_symbols,
    load_symbol_ohlcv,
    save_backtest_run,
    save_strategy_scores,
)
from qianhe_quant.database.schema import init_db
from qianhe_quant.ingestion.ohlcv_importer import import_ohlcv_csv


def test_database_repository_roundtrip(tmp_path: Path):
    db_path = tmp_path / "repo_test.duckdb"
    init_db(db_path)
    import_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv", symbol="SAMPLE", db_path=db_path)

    symbols = list_symbols(db_path)
    assert "SAMPLE" in symbols

    ohlcv = load_symbol_ohlcv("SAMPLE", db_path=db_path)
    assert list(ohlcv.columns) == ["date", "open", "high", "low", "close", "volume", "amount"]

    run_id = save_backtest_run(
        "ma_cross",
        {
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "total_return": 0.1,
            "annual_return": 0.2,
            "max_drawdown": -0.05,
            "win_rate_by_active_days": 0.55,
            "trade_count": 4,
        },
        notes="research-only",
        db_path=db_path,
    )
    saved = save_strategy_scores(run_id, "ma_cross", {"return_drawdown_ratio": 2.0}, db_path=db_path)
    assert saved == 1
