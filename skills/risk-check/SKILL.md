---
name: risk-check
description: Check quantitative strategies for compliance, drawdown, turnover, and operational risk before paper trading.
---

# Risk Check Skill

Always check:

1. Is the feature using future data?
2. Is the strategy overfit to one sample?
3. Is turnover too high?
4. Is max drawdown above threshold?
5. Is liquidity ignored?
6. Is there any live-trading code or secret storage?
7. Does the report distinguish research signal from investment advice?

If live trading is requested, refuse to implement direct execution and generate only an artificial confirmation checklist.
