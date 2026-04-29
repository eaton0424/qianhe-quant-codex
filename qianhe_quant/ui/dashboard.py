from __future__ import annotations

from pathlib import Path

import streamlit as st

from qianhe_quant.ui.components import (
    inject_theme,
    render_hero,
    render_metric_cards,
    render_panel,
    render_report_block,
)
from qianhe_quant.ui.report_viewer import get_report_catalog, read_report
from qianhe_quant.ui.risk_page import render_risk_page
from qianhe_quant.ui.single_stock_page import render_single_stock_page
from qianhe_quant.ui.strategy_lab_page import render_strategy_lab_page


def _render_home() -> None:
    render_hero(
        "千合之本 AI 量化研究与模拟交易实验室",
        "面向研究、回测、模拟组合和风险留痕的本地量化工作台。界面风格参考交易面板，但所有结果仍然只用于研究和模拟。",
        badges=["Research Only", "No Broker API", "Strategy Lab Ready"],
    )
    render_metric_cards(
        [
            ("V1.0 基础回测", "已完成", "回测、模拟交易、基础报告链路稳定。"),
            ("V1.1 个股研究信号引擎", "已完成", "支持单票研究信号与模板化报告。"),
            ("V1.2 策略实验室", "已完成", "具备过滤器、因子实验和策略排行榜。"),
            ("V1.2.2 可视化面板", "当前版本", "本地浏览器可直接打开和使用。"),
        ]
    )

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        render_panel(
            "当前能力版图",
            """
            <ul>
                <li>个股研究信号与样例报告</li>
                <li>策略实验室与多策略排行榜</li>
                <li>周频模拟组合与回测结果</li>
                <li>风险报告与合规边界展示</li>
                <li>Markdown 报告中心</li>
            </ul>
            """,
        )
        latest_report = read_report(Path("reports/strategy_tournament_report.md"))
        render_report_block("最近一次策略排行榜报告", latest_report)
    with right:
        render_panel(
            "操作方式",
            """
            <ul>
                <li>左侧进入“策略实验室”运行和刷新排行榜</li>
                <li>在“个股研究信号”页查看模板与样例报告</li>
                <li>在“报告中心”集中查看所有 Markdown 结果</li>
                <li>所有页面均固定声明：仅供研究和模拟，不构成投资建议</li>
            </ul>
            """,
        )
        render_panel(
            "研究边界",
            """
            <ul>
                <li>不做实盘交易</li>
                <li>不接券商 API</li>
                <li>不保存交易密码、API 私钥、Token</li>
                <li>不输出买入、卖出、仓位、收益承诺</li>
            </ul>
            """,
            tone="risk",
        )


def _render_report_center() -> None:
    render_hero(
        "报告中心",
        "集中查看策略排行榜、周报、日度研究报告和个股研究样例报告。",
        badges=["Markdown Reports", "Research Archive"],
    )
    catalog = get_report_catalog()
    tabs = st.tabs(list(catalog.keys()))
    for tab, (name, path) in zip(tabs, catalog.items()):
        with tab:
            render_report_block(name, read_report(path))


def render_dashboard() -> None:
    st.set_page_config(
        page_title="千合之本 AI 量化研究与模拟交易实验室",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()

    st.sidebar.markdown("## 千合之本")
    st.sidebar.caption("仅供研究和模拟，不构成投资建议。")
    menu = st.sidebar.radio(
        "导航",
        ["首页", "策略实验室", "个股研究信号", "风险与合规", "报告中心"],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
**当前版本**

- V1.0 已封版
- V1.1 已封版
- V1.2 已封版
- V1.2.2 可视化面板
"""
    )

    if menu == "首页":
        _render_home()
    elif menu == "策略实验室":
        render_strategy_lab_page()
    elif menu == "个股研究信号":
        render_single_stock_page()
    elif menu == "风险与合规":
        render_risk_page()
    else:
        _render_report_center()
