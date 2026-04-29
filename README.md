# 千合之本 AI 量化研究与模拟交易工具

定位：把主观投研判断转成可验证、可回测、可留痕的本地量化研究工具。  
默认禁止实盘交易。本仓库只用于研究、回测、模拟交易、风控留痕与报告生成。

## 当前版本

- `V1.0` 基础回测、模拟交易、报告
- `V1.1` 通用个股研究信号引擎
- `V1.2` 策略实验室、多策略排行榜、风险报告
- `V1.3` 本地量化数据库与数据接入层

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

基础回测：

```powershell
python -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross
```

策略实验室：

```powershell
python -m qianhe_quant.cli strategy-lab --out reports/strategy_tournament_report.md
```

本地数据库入口：

- [V1.3 Quickstart](D:/Users/hp/Documents/New%20project/qianhe_quant_codex_tool_v1/docs/v1.3-quickstart.md)
- [Local Database Guide](D:/Users/hp/Documents/New%20project/qianhe_quant_codex_tool_v1/docs/local-database-guide.md)

## V1.3 常用命令

初始化数据库：

```powershell
python -m qianhe_quant.cli db-init
```

导入本地 CSV：

```powershell
python -m qianhe_quant.cli db-import-ohlcv --csv qianhe_quant/data/sample_ohlcv.csv --symbol SAMPLE
```

查看数据库状态：

```powershell
python -m qianhe_quant.cli db-status
```

导出标准 OHLCV：

```powershell
python -m qianhe_quant.cli db-export-ohlcv --symbol SAMPLE --out qianhe_quant/data/sample_ohlcv_from_db.csv
```

直接从数据库跑研究回测：

```powershell
python -m qianhe_quant.cli db-backtest --symbol SAMPLE --strategy ma_cross
```

## 核心边界

- 不做实盘交易
- 不接券商 API
- 不保存交易密码、API 私钥、Token
- 不自动下单
- 不输出买入、卖出、仓位、收益承诺

所有输出只允许称为：

- 研究信号
- 模拟组合
- 回测结果
- 数据质量报告
- 风险提示

## 主要目录

```text
qianhe_quant/
├── analysis/
├── data/
├── data_quality/
├── database/
├── ingestion/
├── research/
├── strategies/
├── templates/
└── ui/
```

## 相关报告

- `reports/local_database_status_report.md`
- `reports/strategy_tournament_report.md`
- `reports/weekly_strategy_lab_report.md`
- `reports/daily_quant_report.md`
