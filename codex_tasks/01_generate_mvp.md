# Codex Task 01｜生成量化研究 MVP

请根据 AGENTS.md 完成一个研究型量化工具 MVP。要求：

1. 支持读取 OHLCV CSV。
2. 支持双均线和突破策略。
3. 支持 vector backtest。
4. 输出收益、最大回撤、胜率、交易次数。
5. 生成 Markdown 报告。
6. 默认禁止实盘交易。
7. 添加 pytest 测试。

验收命令：

```bash
python -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross
python -m qianhe_quant.cli report --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross --out reports/demo_report.md
pytest
```
