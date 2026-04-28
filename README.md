# 千合之本 AI 量化研究与模拟交易工具 V1

定位：把“主观投研判断”转为“可验证、可回测、可风控、可留痕”的量化研究工具。

> 默认禁止实盘下单。本工具只用于研究、回测、模拟交易和风控留痕。任何真实交易必须经过人工确认、合规审查与券商/交易所规则核验。

## 核心功能

1. 数据层：读取 CSV 行情数据，预留行情/财务/新闻接口。
2. 策略层：把主观逻辑转成可执行策略信号。
3. 回测层：计算资金曲线、收益、回撤、胜率、交易次数。
4. 风控层：检查单票权重、最大回撤、换手、异常信号。
5. 模拟交易层：paper account，不连接真实券商。
6. 研究信号层：支持本地新闻事件因子与单票研究信号。
7. 报告层：输出 Markdown 策略复盘报告、风控报告、日报和模拟交易日志。
8. Codex 层：通过 AGENTS.md、.codex 和 skills 固化工作流。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross
python -m qianhe_quant.cli report --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross --out reports/demo_report.md
python -m qianhe_quant.cli daily-report --data qianhe_quant/data/sample_ohlcv.csv --strategy single_stock_research --out reports/daily_quant_report.md
pytest
```

## 单票研究信号

当前仓库已包含“新亚电缆研究信号模块 V1”：

- `qianhe_quant/research/single_stock_research.py`
- `qianhe_quant/research/xinya_cable_signal.py`
- `qianhe_quant/templates/single_stock_signal_template.md`

示例使用方式：

```bash
python -c "from pathlib import Path; from qianhe_quant.research import build_xinya_cable_signal, generate_xinya_cable_signal_report; signal = build_xinya_cable_signal('qianhe_quant/data/sample_ohlcv.csv'); report = generate_xinya_cable_signal_report(signal); Path('reports/xinya_cable_signal_report.md').write_text(report, encoding='utf-8')"
pytest
```

输出边界：

- 只生成“研究信号”
- 不生成买入、卖出、持仓、仓位建议
- 所有结论都区分事实、观点、推断、待核验

## 推荐工作流

```text
主观观点 -> 量化假设 -> 指标定义 -> 策略规则 -> 历史回测 -> 风控检查 -> 模拟交易 -> 复盘报告 -> 待核验清单
```

## 当前边界

- 默认禁止实盘交易
- 不接真实券商 API
- 不保存交易密码、API 私钥或 Token
- 所有真实交易都必须经过人工确认和合规复核
