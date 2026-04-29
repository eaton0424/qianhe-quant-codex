from __future__ import annotations

from pathlib import Path

import streamlit as st

from qianhe_quant.ui.components import render_hero, render_panel, render_report_block
from qianhe_quant.ui.report_viewer import read_report


def render_single_stock_page() -> None:
    render_hero(
        "个股研究信号",
        "把投研纪要整理成事实、观点、推断和待核验项，再映射到结构化研究信号报告。当前保留样例展示和后续上传入口。",
        badges=["Stock Profile", "Signal Engine", "Research Template"],
    )
    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        template_path = Path("qianhe_quant/templates/stock_research_input_template.md")
        if template_path.exists():
            render_report_block("StockProfile 输入模板说明", template_path.read_text(encoding="utf-8"))
        render_panel(
            "后续入口预留",
            """
            <ul>
                <li>纪要上传与文本结构化入口</li>
                <li>研究标签与事件因子填写区</li>
                <li>生成个股研究信号报告按钮</li>
            </ul>
            """,
        )
    with right:
        render_report_block(
            "样例个股研究信号报告",
            read_report(Path("reports/sample_stock_signal_report.md")),
        )
