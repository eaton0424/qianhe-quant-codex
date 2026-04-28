# V1 Acceptance Report

## Scope

This acceptance round covers research, backtest, paper-trade logging, reporting, and risk-check behavior only.

It does **not** add any live trading capability.

## Boundary Confirmation

Reviewed files:

- `AGENTS.md`
- `README.md`
- `docs/compliance-boundary.md`
- `docs/tool-spec.md`

Confirmed boundary requirements remain in effect:

- no real broker account integration
- no broker API connectivity for live execution
- no password, API private key, or token storage
- no automatic live order submission
- outputs must be described as research signals, not buy/sell advice

## Directory Structure Check

Core project directories are present and complete:

- `qianhe_quant/`
- `skills/`
- `docs/`
- `tests/`
- `codex_tasks/`
- `reports/`

Key root files are present:

- `AGENTS.md`
- `README.md`
- `requirements.txt`
- `.env.example`
- `.codex/config.toml`
- `.gitignore`

## Acceptance Commands

Because PowerShell script execution is restricted on this machine, direct activation through `Activate.ps1` is blocked.
The equivalent project interpreter was used via:

- `.\.venv\Scripts\python.exe`

This is functionally the same project environment for acceptance.

### 1. pytest

Command run:

```bash
.\.venv\Scripts\python.exe -m pytest -q
```

Result:

- `5 passed in 1.41s`

### 2. ma_cross Example Backtest

Command run:

```bash
.\.venv\Scripts\python.exe -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross
```

Result summary:

- sample window: `2024-01-02` to `2024-06-28`
- total return: `0.78%`
- annualized return: `1.54%`
- max drawdown: `-3.63%`
- volatility: `7.27%`
- sharpe-like: `0.21`
- trade count: `6`
- risk checks: `LOW | basic`

### 3. ma_cross Report

Command run:

```bash
.\.venv\Scripts\python.exe -m qianhe_quant.cli report --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross --out reports/demo_report.md
```

Generated artifacts:

- `reports/demo_report.md`
- `reports/strategy_review.md`
- `reports/risk_check_report.md`
- `reports/paper_trade_log.csv`

### 4. daily-report Example

Command run:

```bash
.\.venv\Scripts\python.exe -m qianhe_quant.cli daily-report --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross --out reports/daily_quant_report.md
```

Generated artifact:

- `reports/daily_quant_report.md`

## Compliance Scan

A repository scan was performed across:

- `qianhe_quant/`
- `skills/`
- `docs/`
- `tests/`
- `codex_tasks/`

Search targets included:

- broker / brokerage
- API key / token / private key / password
- live trading / real order / execution
- submit order / place order / 下单 / 实盘

Conclusion:

- no real broker integration code was found
- no live execution adapter was found
- no secret storage implementation was found
- references to live trading appear only as **prohibitions**, warnings, or compliance rules

Notes:

- `paper_trade.py` is limited to simulated account behavior
- `risk.py` explicitly blocks live trading in V1
- reporting files describe outputs as research artifacts

## Bug Check

No new research/backtest/paper-trade/risk/report bugs were discovered during this acceptance round that required code changes.

## Final Acceptance Result

Status: `PASS`

This V1 repository currently satisfies the stated boundary for:

- research signals
- historical backtest
- local news factor research
- simulated trade logging
- risk logging
- markdown reporting

It does **not** implement:

- real broker account access
- password or private-key storage
- automatic live trading
