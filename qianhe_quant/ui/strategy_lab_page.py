from __future__ import annotations

from pathlib import Path

import streamlit as st

from qianhe_quant.analysis.strategy_tournament import run_strategy_tournament
from qianhe_quant.reporter import save_report
from qianhe_quant.reports.strategy_lab_report import (
    build_strategy_tournament_report,
    build_weekly_strategy_lab_report,
)
from qianhe_quant.ui.components import (
    render_hero,
    render_metric_cards,
    render_panel,
    render_report_block,
    render_risk_notice,
    render_strategy_rank_table,
)
from qianhe_quant.ui.report_viewer import read_report


STRATEGY_LIST = [
    "ma_cross",
    "breakout",
    "single_stock_research",
    "weekly_factor_rotation",
]


def _run_strategy_lab() -> tuple[Path, Path]:
    results = run_strategy_tournament("qianhe_quant/data/sample_ohlcv.csv")
    tournament_path = save_report(
        "reports/strategy_tournament_report.md",
        build_strategy_tournament_report(results),
    )
    weekly_path = save_report(
        "reports/weekly_strategy_lab_report.md",
        build_weekly_strategy_lab_report(results),
    )
    st.session_state["strategy_lab_results"] = results
    return tournament_path, weekly_path


def render_strategy_lab_page() -> None:
    render_hero(
        "策略实验室",
        "把回测、因子实验、排行榜和风险观察整合到一个本地研究面板里。这里运行的是研究用模拟组合，不是实盘指令。",
        badges=["Strategy Lab", "Weekly Rotation", "Ranking + Risk"],
    )
    render_metric_cards(
        [
            ("策略数量", str(len(STRATEGY_LIST)), "当前纳入比较的核心策略数。"),
            ("运行模式", "研究 / 模拟", "只输出研究信号、模拟组合与回测结果。"),
            ("实盘状态", "已禁用", "不接券商 API，不自动下单。"),
        ]
    )

    summary_col, action_col = st.columns([0.85, 1.15], gap="large")
    with summary_col:
        render_panel(
            "策略池",
            "<ul>" + "".join(f"<li><code>{name}</code></li>" for name in STRATEGY_LIST) + "</ul>",
        )
    with action_col:
        c1, c2, c3 = st.columns(3)
        if c1.button("运行策略实验室", use_container_width=True):
            tournament_path, weekly_path = _run_strategy_lab()
            st.success(f"已生成：{tournament_path} 和 {weekly_path}")
        if c2.button("刷新策略排行榜", use_container_width=True):
            _run_strategy_lab()
            st.info("已刷新策略排行榜。")
        if c3.button("打开策略报告", use_container_width=True):
            st.session_state["show_strategy_lab_reports"] = True

    results = st.session_state.get("strategy_lab_results")
    if results is None:
        try:
            results = run_strategy_tournament("qianhe_quant/data/sample_ohlcv.csv")
            st.session_state["strategy_lab_results"] = results
        except Exception as exc:  # pragma: no cover
            st.error(f"策略实验室暂时无法运行：{exc}")
            results = None

    if results is not None:
        rank_col, note_col = st.columns([1.35, 0.65], gap="large")
        with rank_col:
            st.subheader("策略排行榜")
            render_strategy_rank_table(results)
        with note_col:
            risky = results.loc[results["risk_level"] != "LOW", "strategy"].tolist()
            render_risk_notice(
                "风险提示",
                [
                    "仅供研究和模拟，不构成投资建议。",
                    "高收益并不代表可直接使用，必须结合回撤、波动和样本稳定性判断。",
                    f"当前需要重点人工复核的策略：{', '.join(risky) if risky else '暂无'}。",
                ],
            )

    if st.session_state.get("show_strategy_lab_reports"):
        report_tab, weekly_tab = st.tabs(["策略排行榜报告", "每周策略实验室报告"])
        with report_tab:
            render_report_block("策略排行榜报告", read_report(Path("reports/strategy_tournament_report.md")))
        with weekly_tab:
            render_report_block("每周策略实验室报告", read_report(Path("reports/weekly_strategy_lab_report.md")))
