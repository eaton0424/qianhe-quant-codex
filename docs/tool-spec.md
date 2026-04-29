# 工具规格说明

## 输入

- 股票或指数 OHLCV 数据 CSV
- 研究对象基本信息：`stock_code`、`stock_name`、`industry`
- 研究标签：`theme_tags`
- 研究纪要拆分结果：`facts`、`opinions`、`assumptions`
- 风险与待核验事项：`risks`、`verification_tasks`
- 策略参数
- 风控阈值

## 事件因子

通用个股研究引擎支持以下事件因子字段：

- `announcement_event`
- `news_event`
- `order_event`
- `policy_event`
- `product_event`
- `management_event`
- `risk_event`

## 输出

- 策略信号表
- 研究信号结果
- 研究信号等级：`observe` / `watch` / `strong_watch` / `avoid`
- 回测指标
- 模拟交易记录
- Markdown 回测报告
- Markdown 个股研究信号报告
- 风控发现清单

## 非目标

- 不做实盘自动交易
- 不做收益承诺
- 不做监管规避
- 不做无来源的数据判断
- 不接真实券商 API
- 不保存交易密码、API 私钥或 Token
