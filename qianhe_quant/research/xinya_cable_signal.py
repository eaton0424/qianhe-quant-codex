from pathlib import Path

from qianhe_quant.research.research_signal_engine import (
    build_stock_research_signal,
    generate_stock_signal_report,
)
from qianhe_quant.research.single_stock_research import ResearchSignal
from qianhe_quant.research.stock_profile import StockProfile


THEME_TAGS = [
    "\u6b21\u65b0\u80a1",
    "\u7535\u7f51\u8bbe\u5907",
    "\u7279\u79cd\u7ebf\u7f06",
    "\u5357\u65b9\u7535\u7f51\u8ba2\u5355",
    "\u673a\u5668\u4eba/\u65b0\u80fd\u6e90\u5ef6\u4f38\u5f85\u6838\u9a8c",
]


def _build_xinya_profile(stock_code: str, stock_name: str) -> StockProfile:
    return StockProfile(
        stock_code=stock_code,
        stock_name=stock_name,
        industry="Power Equipment",
        theme_tags=THEME_TAGS,
        facts=[
            "\u516c\u53f8\u5f53\u524d\u88ab\u7eb3\u5165\u7535\u7f51\u8bbe\u5907\u4e0e\u7279\u79cd\u7ebf\u7f06\u7814\u7a76\u8303\u56f4\u3002",
            "\u6837\u4f8b\u884c\u60c5\u548c\u672c\u5730\u65b0\u95fb\u6570\u636e\u53ef\u7528\u4e8e\u7814\u7a76\u4fe1\u53f7\u56de\u653e\u4e0e\u590d\u76d8\u3002",
        ],
        opinions=[
            "\u82e5\u5e02\u573a\u6301\u7eed\u56f4\u7ed5\u7535\u7f51\u5efa\u8bbe\u4e0e\u8ba2\u5355\u903b\u8f91\u4ea4\u6613\uff0c\u8be5\u6807\u7684\u53ef\u80fd\u83b7\u5f97\u66f4\u9ad8\u7814\u7a76\u4f18\u5148\u7ea7\u3002",
            "\u5357\u65b9\u7535\u7f51\u8ba2\u5355\u4e3b\u9898\u66f4\u9002\u5408\u4f5c\u4e3a\u7814\u7a76\u6807\u7b7e\uff0c\u800c\u4e0d\u662f\u6267\u884c\u6307\u4ee4\u3002",
        ],
        assumptions=[
            "\u82e5\u8d8b\u52bf\u3001\u7a81\u7834\u548c\u4e8b\u4ef6\u4fe1\u53f7\u540c\u6b65\u6539\u5584\uff0c\u7814\u7a76\u5173\u6ce8\u7ea7\u522b\u53ef\u8fdb\u4e00\u6b65\u63d0\u5347\u3002",
            "\u82e5\u673a\u5668\u4eba/\u65b0\u80fd\u6e90\u5ef6\u4f38\u903b\u8f91\u65e0\u6cd5\u88ab\u516c\u544a\u6216\u5ba2\u6237\u4fe1\u606f\u9a8c\u8bc1\uff0c\u4fe1\u53f7\u9700\u8981\u964d\u7ea7\u5904\u7406\u3002",
        ],
        risks=[
            "\u5355\u7968\u7814\u7a76\u5bb9\u6613\u53d7\u5230\u53d9\u4e8b\u96c6\u4e2d\u5ea6\u8fc7\u9ad8\u7684\u5f71\u54cd\u3002",
            "\u673a\u5668\u4eba/\u65b0\u80fd\u6e90\u5ef6\u4f38\u903b\u8f91\u5f53\u524d\u4ecd\u5f85\u6838\u9a8c\u3002",
        ],
        verification_tasks=[
            "\u6838\u9a8c\u51c6\u786e\u8bc1\u5238\u4ee3\u7801\u4e0e\u4ea4\u6613\u6240\u4fe1\u606f\u3002",
            "\u6838\u9a8c\u5357\u65b9\u7535\u7f51\u8ba2\u5355\u8868\u8ff0\u662f\u5426\u6765\u81ea\u6b63\u5f0f\u516c\u544a\u6216\u5408\u540c\u3002",
            "\u6838\u9a8c\u673a\u5668\u4eba/\u65b0\u80fd\u6e90\u5ef6\u4f38\u662f\u5426\u6709\u4ea7\u54c1\u3001\u5ba2\u6237\u6216\u6536\u5165\u652f\u6491\u3002",
        ],
    )


def build_xinya_cable_signal(
    price_csv_path: str | Path,
    news_csv_path: str | Path = "qianhe_quant/data/sample_news.csv",
    stock_code: str = "TO_VERIFY",
    stock_name: str = "\u65b0\u4e9a\u7535\u7f06",
) -> ResearchSignal:
    profile = _build_xinya_profile(stock_code, stock_name)
    return build_stock_research_signal(profile, price_csv_path, news_csv_path)


def generate_xinya_cable_signal_report(
    signal: ResearchSignal,
    template_path: str | Path = "qianhe_quant/templates/stock_signal_report_template.md",
) -> str:
    profile = _build_xinya_profile(signal.stock_code, signal.stock_name)
    return generate_stock_signal_report(profile, signal, template_path)
