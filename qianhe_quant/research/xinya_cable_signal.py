from pathlib import Path
from qianhe_quant.research.research_signal_engine import (
    build_stock_research_signal,
    generate_stock_signal_report,
)
from qianhe_quant.research.single_stock_research import ResearchSignal
from qianhe_quant.research.stock_profile import StockProfile


THEME_TAGS = [
    "次新股",
    "电网设备",
    "特种线缆",
    "南方电网订单",
    "机器人/新能源延伸待核验",
]


def _build_xinya_profile(stock_code: str, stock_name: str) -> StockProfile:
    return StockProfile(
        stock_code=stock_code,
        stock_name=stock_name,
        industry="Power Equipment",
        theme_tags=THEME_TAGS,
        facts=[
            "公司当前被纳入电网设备与特种线缆研究范围。",
            "样例行情和本地新闻数据可用于研究信号回放与复盘。",
        ],
        opinions=[
            "若市场持续围绕电网建设与订单逻辑交易，该标的可能获得更高研究优先级。",
            "南方电网订单主题更适合作为研究标签，而不是执行指令。",
        ],
        assumptions=[
            "若趋势、突破和事件信号同步改善，研究关注级别可进一步提升。",
            "若机器人/新能源延伸逻辑无法被公告或客户信息验证，信号需要降级处理。",
        ],
        risks=[
            "单票研究容易受到叙事集中度过高的影响。",
            "机器人/新能源延伸逻辑当前仍待核验。",
        ],
        verification_tasks=[
            "核验准确证券代码与交易所信息。",
            "核验南方电网订单表述是否来自正式公告或合同。",
            "核验机器人/新能源延伸是否有产品、客户或收入支撑。",
        ],
    )


def build_xinya_cable_signal(
    price_csv_path: str | Path,
    news_csv_path: str | Path = "qianhe_quant/data/sample_news.csv",
    stock_code: str = "TO_VERIFY",
    stock_name: str = "新亚电缆",
) -> ResearchSignal:
    profile = _build_xinya_profile(stock_code, stock_name)
    return build_stock_research_signal(profile, price_csv_path, news_csv_path)


def generate_xinya_cable_signal_report(
    signal: ResearchSignal,
    template_path: str | Path = "qianhe_quant/templates/stock_signal_report_template.md",
) -> str:
    profile = _build_xinya_profile(signal.stock_code, signal.stock_name)
    return generate_stock_signal_report(profile, signal, template_path)
