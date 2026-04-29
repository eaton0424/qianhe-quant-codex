from __future__ import annotations

from pathlib import Path

import streamlit as st

from qianhe_quant.ui.components import render_hero, render_panel, render_report_block, render_risk_notice
from qianhe_quant.ui.report_viewer import read_report


def render_risk_page() -> None:
    render_hero(
        "风险与合规",
        "这一页固定展示系统边界和策略实验室风险信息，确保面板再像产品，也不会越过研究与模拟的边界。",
        badges=["No Live Trading", "No Broker API", "Manual Review Required"],
    )
    left, right = st.columns([0.8, 1.2], gap="large")
    with left:
        render_risk_notice(
            "系统边界",
            [
                "禁止实盘交易。",
                "禁止接入券商 API。",
                "禁止保存交易密码、API 私钥、Token。",
                "禁止自动下单。",
                "所有结果仅允许称为研究信号、模拟组合、回测结果、风险提示。",
            ],
        )
        render_panel(
            "执行纪律",
            """
            <ul>
                <li>仅供研究和模拟，不构成投资建议</li>
                <li>任何真实动作都必须人工确认</li>
                <li>排行榜靠收益、回撤、波动和稳定性综合判断</li>
            </ul>
            """,
            tone="risk",
        )
    with right:
        render_report_block(
            "每周策略实验室风险报告",
            read_report(Path("reports/weekly_strategy_lab_report.md")),
        )
