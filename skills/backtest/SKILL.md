---
name: backtest
description: Implement and validate research-only backtests for quantitative strategies.
---

# Backtest Skill

Use this skill when implementing a strategy or changing backtest logic.

Required steps:

1. Check there is no future function.
2. Use next-bar execution or explicitly documented execution timing.
3. Include commission and slippage.
4. Output total return, annual return, max drawdown, volatility, trade count, win rate.
5. Add or update tests.
6. Run the sample backtest and pytest.
