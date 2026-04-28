# 千合之本 AI 量化研究与模拟交易系统 V1 冻结报告

## 一、冻结范围

本次 V1 冻结范围仅包括：

- 研究信号
- 历史回测
- 模拟交易留痕
- 风控检查
- Markdown / CSV 报告输出

不包括：

- 真实券商账户接入
- 实盘自动下单
- 交易密码、API 私钥、Token 保存

## 二、仓库结构检查

当前仓库已包含：

- `AGENTS.md`
- `README.md`
- `qianhe_quant/`
- `docs/`
- `skills/`
- `tests/`
- `reports/`
- `codex_tasks/`

## 三、V1 验收结果

### 1. pytest

已通过：

- `8 passed`

### 2. sample 回测

命令：

```bash
python -m qianhe_quant.cli backtest --data qianhe_quant/data/sample_ohlcv.csv --strategy ma_cross
```

结果摘要：

- sample window: `2024-01-02` to `2024-06-28`
- total return: `0.78%`
- annualized return: `1.54%`
- max drawdown: `-3.63%`
- volatility: `7.27%`
- sharpe-like: `0.21`
- trade count: `6`
- risk checks: `LOW | basic`

### 3. daily-report

命令：

```bash
python -m qianhe_quant.cli daily-report --data qianhe_quant/data/sample_ohlcv.csv --strategy single_stock_research --out reports/daily_quant_report.md
```

结果：

- 已成功生成 `reports/daily_quant_report.md`

### 4. 新亚电缆研究信号报告

已存在：

- `reports/xinya_cable_signal_report.md`

## 四、合规边界核查

已核查：

- `AGENTS.md`
- `README.md`
- `docs/compliance-boundary.md`
- `docs/tool-spec.md`

并对 `qianhe_quant/`、`skills/`、`docs/`、`tests/`、`codex_tasks/` 进行了关键词扫描。

结论：

- 未发现真实券商 API 接入实现
- 未发现交易密码保存实现
- 未发现 API 私钥或 Token 保存实现
- 未发现自动实盘下单代码

扫描到的相关关键词均出现在：

- 合规文档
- skills 规则
- 测试断言
- 报告免责声明
- 风控阻断逻辑

## 五、V1 已具备能力

- 基于本地 CSV 的 OHLCV 数据读取
- 双均线与突破类研究策略
- 向量化历史回测
- 收益、年化、回撤、波动率、Sharpe-like、交易次数等指标计算
- 基础风控检查与阻断提示
- 模拟交易日志导出
- 每日量化研究报告输出
- 单票研究信号模块 V1
- 本地新闻事件因子
- 新亚电缆研究信号 Markdown 报告
- 验收报告与二次验收报告留痕

## 六、V1 尚未具备能力

- 真实市场数据自动拉取
- 标准化纪要输入到研究信号的通用接口
- 多标的统一研究模板引擎
- 真正可配置的研究因子权重系统
- 研究信号到模拟交易流程的批量调度
- 更细粒度的组合级风险约束
- 任何形式的实盘执行

## 七、V1.1 开发路线

V1.1 的优先方向应是“个股研究模板标准化”，而不是实盘接入。

建议路线：

1. 任意股票纪要标准化输入
   - 将纪要拆成事实、观点、推断、待核验四层
2. 标的标签标准化
   - 行业、主题、订单、客户、产品、监管、事件
3. 事件因子标准化
   - 公告、订单、业绩、产能、政策、舆情
4. 趋势 / 量能 / 风险因子统一打分
   - 形成可复盘的评分框架
5. 通用研究信号报告模板
   - 从“新亚电缆模块”推广到任意单票
6. 待核验事项清单化
   - 输出后续人工跟踪任务，而不是执行建议

## 八、冻结结论

状态：`V1 Frozen`

当前版本适合：

- 研究
- 回测
- 模拟交易留痕
- 风控检查
- 研究报告沉淀

当前版本不适合：

- 实盘交易
- 券商 API 接入
- 自动执行买卖指令
