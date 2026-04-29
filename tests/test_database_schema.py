from pathlib import Path

from qianhe_quant.database.connection import safe_close
from qianhe_quant.database.schema import get_table_names, init_db, is_db_initialized


def test_database_schema_init_creates_expected_tables(tmp_path: Path):
    db_path = tmp_path / "schema_test.duckdb"
    init_db(db_path)
    tables = set(get_table_names(db_path))
    assert {"symbols", "market_daily", "news_events", "announcements", "fundamentals", "factor_daily", "backtest_runs", "strategy_scores", "data_quality_logs"}.issubset(tables)
    assert is_db_initialized(db_path) is True
