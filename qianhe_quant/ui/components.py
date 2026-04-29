from __future__ import annotations

import pandas as pd
import streamlit as st


THEME_CSS = """
<style>
    :root {
        --bg-main: #07111f;
        --bg-panel: rgba(10, 24, 43, 0.88);
        --bg-panel-soft: rgba(16, 36, 63, 0.66);
        --border: rgba(86, 149, 224, 0.24);
        --text-main: #edf5ff;
        --text-soft: #9db4d5;
        --accent: #4fd1c5;
        --accent-2: #7aa2ff;
        --warning: #f8c668;
        --danger: #ff7c7c;
        --shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(79, 209, 197, 0.18), transparent 28%),
            radial-gradient(circle at top left, rgba(122, 162, 255, 0.22), transparent 26%),
            linear-gradient(180deg, #06101b 0%, #081728 52%, #07111f 100%);
        color: var(--text-main);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(7, 18, 31, 0.98), rgba(9, 23, 41, 0.96));
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }

    .qh-hero {
        background: linear-gradient(135deg, rgba(14, 28, 48, 0.96), rgba(13, 39, 66, 0.88));
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        border-radius: 28px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.25rem;
        position: relative;
        overflow: hidden;
    }

    .qh-hero::after {
        content: "";
        position: absolute;
        inset: auto -10% -38% auto;
        width: 280px;
        height: 280px;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(79, 209, 197, 0.18), transparent 66%);
        filter: blur(4px);
    }

    .qh-eyebrow {
        display: inline-block;
        color: #06131f;
        background: linear-gradient(90deg, var(--accent), #9be7dd);
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        margin-bottom: 0.9rem;
    }

    .qh-hero h1, .qh-hero h2, .qh-hero h3 {
        color: var(--text-main);
        margin: 0;
    }

    .qh-hero p {
        color: var(--text-soft);
        margin-top: 0.7rem;
        margin-bottom: 0;
        max-width: 760px;
        line-height: 1.7;
    }

    .qh-badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1rem;
    }

    .qh-badge {
        border: 1px solid rgba(122, 162, 255, 0.22);
        background: rgba(122, 162, 255, 0.1);
        color: #d4e4ff;
        padding: 0.45rem 0.72rem;
        border-radius: 999px;
        font-size: 0.84rem;
    }

    .qh-card {
        background: linear-gradient(180deg, rgba(13, 31, 53, 0.94), rgba(9, 25, 44, 0.92));
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        border-radius: 24px;
        padding: 1.15rem 1.2rem;
        min-height: 132px;
    }

    .qh-card-label {
        color: var(--text-soft);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.55rem;
    }

    .qh-card-value {
        color: var(--text-main);
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.15;
    }

    .qh-card-note {
        color: #89a5ca;
        margin-top: 0.6rem;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .qh-panel {
        background: var(--bg-panel);
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        border-radius: 24px;
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
    }

    .qh-panel h3 {
        color: var(--text-main);
        margin-top: 0;
    }

    .qh-panel p, .qh-panel li {
        color: var(--text-soft);
        line-height: 1.7;
    }

    .qh-risk {
        background: linear-gradient(180deg, rgba(52, 26, 25, 0.96), rgba(35, 18, 18, 0.92));
        border: 1px solid rgba(255, 124, 124, 0.2);
    }

    .qh-info {
        background: linear-gradient(180deg, rgba(12, 36, 62, 0.96), rgba(10, 27, 49, 0.92));
    }

    .qh-report {
        background: rgba(6, 17, 31, 0.75);
        border: 1px solid rgba(122, 162, 255, 0.18);
        border-radius: 22px;
        padding: 1rem 1.15rem;
    }

    .qh-label {
        color: var(--warning);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 18px;
        overflow: hidden;
        background: rgba(9, 24, 43, 0.92);
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid rgba(79, 209, 197, 0.34);
        background: linear-gradient(135deg, rgba(79, 209, 197, 0.2), rgba(122, 162, 255, 0.16));
        color: var(--text-main);
        font-weight: 600;
        padding: 0.7rem 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        background: rgba(16, 35, 58, 0.84);
        color: var(--text-soft);
        padding: 0.45rem 0.9rem;
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(79, 209, 197, 0.14);
        border-color: rgba(79, 209, 197, 0.25);
        color: var(--text-main);
    }
</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, badges: list[str] | None = None) -> None:
    badge_html = ""
    if badges:
        badge_html = "".join(f"<span class='qh-badge'>{badge}</span>" for badge in badges)
        badge_html = f"<div class='qh-badge-row'>{badge_html}</div>"
    st.markdown(
        f"""
        <section class="qh-hero">
            <div class="qh-eyebrow">Panda-style Quant Workspace</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {badge_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(items: list[tuple[str, str, str | None]]) -> None:
    columns = st.columns(len(items)) if items else []
    for column, item in zip(columns, items):
        label, value, note = item
        column.markdown(
            f"""
            <section class="qh-card">
                <div class="qh-card-label">{label}</div>
                <div class="qh-card-value">{value}</div>
                <div class="qh-card-note">{note or ""}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render_panel(title: str, body: str, *, tone: str = "info") -> None:
    tone_class = "qh-risk" if tone == "risk" else "qh-info"
    st.markdown(
        f"""
        <section class="qh-panel {tone_class}">
            <div class="qh-label">{title}</div>
            <div>{body}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_strategy_rank_table(results: pd.DataFrame) -> None:
    if results.empty:
        st.info("当前没有可展示的策略排行榜结果。")
        return
    display = results.copy()
    if "strategy" in display.columns:
        display = display.rename(columns={"strategy": "strategy_name"})
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_risk_notice(title: str, messages: list[str]) -> None:
    items = "".join(f"<li>{message}</li>" for message in messages)
    render_panel(title, f"<ul>{items}</ul>", tone="risk")


def render_report_block(title: str, content: str) -> None:
    st.markdown(
        f"""
        <section class="qh-report">
            <div class="qh-label">{title}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(content)
