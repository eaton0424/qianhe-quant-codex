CREATE TABLE IF NOT EXISTS symbols (
    symbol VARCHAR PRIMARY KEY,
    name VARCHAR,
    exchange VARCHAR,
    industry VARCHAR,
    list_date DATE,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS market_daily (
    symbol VARCHAR NOT NULL,
    date DATE NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    amount DOUBLE,
    turnover DOUBLE,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

CREATE TABLE IF NOT EXISTS news_events (
    event_id VARCHAR PRIMARY KEY,
    symbol VARCHAR,
    date DATE,
    title VARCHAR,
    content VARCHAR,
    source VARCHAR,
    sentiment DOUBLE,
    tags VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS announcements (
    announcement_id VARCHAR PRIMARY KEY,
    symbol VARCHAR,
    date DATE,
    title VARCHAR,
    content VARCHAR,
    source VARCHAR,
    tags VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fundamentals (
    symbol VARCHAR,
    date DATE,
    pe DOUBLE,
    pb DOUBLE,
    roe DOUBLE,
    revenue DOUBLE,
    net_profit DOUBLE,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS factor_daily (
    symbol VARCHAR,
    date DATE,
    factor_name VARCHAR,
    factor_value DOUBLE,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date, factor_name)
);

CREATE TABLE IF NOT EXISTS backtest_runs (
    run_id VARCHAR PRIMARY KEY,
    strategy_name VARCHAR,
    start_date DATE,
    end_date DATE,
    total_return DOUBLE,
    annualized_return DOUBLE,
    max_drawdown DOUBLE,
    win_rate DOUBLE,
    trade_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR
);

CREATE TABLE IF NOT EXISTS strategy_scores (
    run_id VARCHAR,
    strategy_name VARCHAR,
    score_name VARCHAR,
    score_value DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_quality_logs (
    log_id VARCHAR PRIMARY KEY,
    table_name VARCHAR,
    check_name VARCHAR,
    status VARCHAR,
    message VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
