from pathlib import Path

from qianhe_quant.database.repository import load_market_daily
from qianhe_quant.database.schema import init_db
from qianhe_quant.ingestion.ohlcv_importer import import_ohlcv_csv


def test_ohlcv_importer_loads_sample_csv_into_market_daily(tmp_path: Path):
    db_path = tmp_path / "importer.duckdb"
    init_db(db_path)
    result = import_ohlcv_csv("qianhe_quant/data/sample_ohlcv.csv", symbol="SAMPLE", db_path=db_path)
    assert result.row_count > 0
    assert "estimated_amount" in result.source
    df = load_market_daily("SAMPLE", db_path=db_path)
    assert len(df) == result.row_count
