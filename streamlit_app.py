"""
streamlit_app.py
================
GLOBAL 50 — Corporate Intelligence
Executive Analytics & Institutional BI Platform.

Executive analysis platform tracking the world's 50 largest companies by revenue,
profitability, and workforce scale. Features dual corporate themes (Light & Dark modes),
a rich executive hero header, balanced micro-visualizations, dynamic KPI scorecards,
global multidimensional filtering, sidebar business questions navigation,
in-depth corporate 360 intelligence, and professional multi-sheet Excel data export.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd
import streamlit as st

import analysis
from scraper import load_data

# Page Configuration
st.set_page_config(
    page_title="Global 50 | Corporate Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State Variables
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "sidebar_theme_pick" not in st.session_state:
    st.session_state["sidebar_theme_pick"] = "🌙 Dark Mode" if st.session_state["dark_mode"] else "☀️ Light Mode"
if "header_theme_toggle_btn" not in st.session_state:
    st.session_state["header_theme_toggle_btn"] = "🌙 Dark" if st.session_state["dark_mode"] else "☀️ Light"

if "main_nav_radio" not in st.session_state:
    st.session_state["main_nav_radio"] = "Overview"
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Overview"
if "active_question_target" not in st.session_state:
    st.session_state["active_question_target"] = None

# Two-way Theme Synchronization Callbacks
def on_theme_change_sidebar() -> None:
    is_dark = (st.session_state.get("sidebar_theme_pick") == "🌙 Dark Mode")
    st.session_state["dark_mode"] = is_dark
    st.session_state["header_theme_toggle_btn"] = "🌙 Dark" if is_dark else "☀️ Light"

def on_theme_change_header() -> None:
    is_dark = (st.session_state.get("header_theme_toggle_btn") == "🌙 Dark")
    st.session_state["dark_mode"] = is_dark
    st.session_state["sidebar_theme_pick"] = "🌙 Dark Mode" if is_dark else "☀️ Light Mode"

# Global Navigation Helper
def navigate_to(page: str, question: str | None = None) -> None:
    st.session_state["nav_pending"] = page
    st.session_state["nav_selection"] = page
    if question is not None:
        st.session_state["active_question_target"] = question

# Business Questions Taxonomy
BUSINESS_QUESTIONS_MAP = analysis.BUSINESS_QUESTIONS_MAP



# =============================================================================
# DUAL-THEME EXECUTIVE DESIGN SYSTEM (CSS)
# =============================================================================
def get_app_css(dark_mode: bool) -> str:
    """Generate dynamic CSS tokens and styles for Light and Dark corporate modes."""
    if dark_mode:
        # Dark Corporate Palette
        bg_page = "#0B1120"
        bg_card = "#151E2E"
        bg_subtle = "#111827"
        border_color = "#263244"
        border_subtle = "#1E293B"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        accent_blue = "#3B82F6"
        accent_emerald = "#10B981"
        accent_amber = "#F59E0B"
        accent_rose = "#EF4444"
        input_bg = "#111827"
        input_border = "#263244"
        sidebar_bg = "#0E1626"
        shadow_card = "0 2px 4px rgba(0, 0, 0, 0.25)"
        pill_bg = "#1E293B"
        pill_border = "#263244"
    else:
        # Light Corporate Palette
        bg_page = "#F6F8FB"
        bg_card = "#FFFFFF"
        bg_subtle = "#F8FAFC"
        border_color = "#E2E8F0"
        border_subtle = "#F1F5F9"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#94A3B8"
        accent_blue = "#2563EB"
        accent_emerald = "#10B981"
        accent_amber = "#F59E0B"
        accent_rose = "#EF4444"
        input_bg = "#F8FAFC"
        input_border = "#CBD5E1"
        sidebar_bg = "#FFFFFF"
        shadow_card = "0 1px 3px rgba(15, 23, 42, 0.04)"
        pill_bg = "#FFFFFF"
        pill_border = "#E2E8F0"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --bg-page: {bg_page};
        --bg-card: {bg_card};
        --bg-subtle: {bg_subtle};
        --border-color: {border_color};
        --border-subtle: {border_subtle};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --text-muted: {text_muted};
        --accent-blue: {accent_blue};
        --accent-emerald: {accent_emerald};
        --accent-amber: {accent_amber};
        --accent-rose: {accent_rose};
        --input-bg: {input_bg};
        --input-border: {input_border};
        --sidebar-bg: {sidebar_bg};
        --shadow-card: {shadow_card};
        --pill-bg: {pill_bg};
        --pill-border: {pill_border};
    }}

    /* Global Reset & Base Typography */
    html, body, .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-primary);
    }}

    /* Explicitly preserve native Streamlit Material Symbols & Icons ligatures */
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"],
    [class*="stIcon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        font-feature-settings: 'liga' 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }}

    /* Background Canvas */
    .stApp {{
        background-color: var(--bg-page) !important;
    }}

    /* Eliminate unnecessary blank header gap */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        height: 1.5rem !important;
    }}

    /* Comfortable Top & Lateral Container Spacing */
    .main .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1440px !important;
    }}

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.25rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }}

    /* Executive Hero Header Container */
    .hero-container {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-card);
    }}

    .hero-kicker {{
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent-blue);
        margin-bottom: 2px;
    }}

    .hero-title {{
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }}

    .hero-subtitle {{
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 4px;
        line-height: 1.45;
    }}

    .hero-pills-row {{
        display: flex;
        gap: 8px;
        margin-top: 12px;
        flex-wrap: wrap;
    }}

    .hero-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: var(--pill-bg);
        border: 1px solid var(--pill-border);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-primary);
    }}

    .hero-pill-highlight {{
        color: var(--accent-blue);
        font-weight: 800;
    }}

    .header-meta-label {{
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
    }}

    /* Unified Global Filter Container */
    .filter-panel {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-card);
    }}

    .filter-panel-title {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-bottom: 12px;
    }}

    /* KPI Card Component */
    .kpi-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: var(--shadow-card);
        min-height: 128px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }}

    .kpi-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin: 0;
    }}

    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 3px 0;
        letter-spacing: -0.02em;
    }}

    .kpi-entity {{
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .kpi-meta {{
        font-size: 0.76rem;
        color: var(--text-secondary);
        margin-top: 1px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .kpi-tag {{
        font-size: 0.68rem;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 4px;
        background-color: var(--bg-subtle);
        border: 1px solid var(--border-color);
        color: var(--accent-blue);
    }}

    /* Section Header Container */
    .section-header-block {{
        margin-top: 16px;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border-color);
    }}

    .section-kicker {{
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--accent-blue);
        margin-bottom: 2px;
    }}

    .section-title {{
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.01em;
    }}

    .section-subtitle {{
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }}

    /* Content Container Card */
    .content-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-card);
    }}

    .card-title {{
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 10px 0;
    }}

    /* Zero Result Message Card */
    .empty-state-card {{
        background-color: var(--bg-card);
        border: 1px dashed var(--border-color);
        border-radius: 8px;
        padding: 32px 24px;
        text-align: center;
        margin: 20px 0;
    }}

    .empty-state-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }}

    .empty-state-desc {{
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 16px;
    }}

    /* Strategic Business Question Card */
    .question-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-card);
        min-height: 152px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .question-kicker {{
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--accent-blue);
        margin-bottom: 2px;
    }}

    .question-title {{
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.25;
        margin-bottom: 8px;
    }}

    .question-metric-row {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 6px;
        padding-bottom: 4px;
        border-bottom: 1px solid var(--border-subtle);
    }}

    .question-entity {{
        font-size: 0.95rem;
        font-weight: 800;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 65%;
    }}

    .question-metric {{
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--accent-emerald);
    }}

    .question-answer {{
        font-size: 0.78rem;
        color: var(--text-secondary);
        line-height: 1.38;
    }}

    /* Active Filter Badges */
    .filter-badge {{
        display: inline-flex;
        align-items: center;
        background-color: var(--bg-subtle);
        border: 1px solid var(--border-color);
        color: var(--accent-blue);
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 2px;
    }}

    /* Comparison Metric Card */
    .cmp-metric-box {{
        background-color: var(--bg-subtle);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 10px 12px;
        text-align: center;
        margin-bottom: 8px;
    }}

    .cmp-metric-label {{
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 4px;
    }}

    .cmp-metric-leader {{
        font-size: 0.88rem;
        font-weight: 800;
        color: var(--text-primary);
    }}

    .cmp-metric-diff {{
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent-emerald);
        margin-top: 2px;
    }}

    /* Footer */
    .footer-container {{
        text-align: center;
        padding: 24px 0 12px 0;
        color: var(--text-muted);
        font-size: 0.78rem;
        border-top: 1px solid var(--border-color);
        margin-top: 24px;
    }}

    /* Refined Form Controls */
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        border-color: var(--input-border) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }}

    .stTextInput input {{
        background-color: var(--input-bg) !important;
        border-color: var(--input-border) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }}

    .stButton button {{
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        background-color: var(--bg-card) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }}

    /* Navigation Radio Styling */
    div[data-testid="stRadio"] > div {{
        gap: 4px;
    }}

    div[data-testid="stRadio"] label {{
        background-color: var(--input-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.15s ease;
        margin-bottom: 4px;
    }}

    div[data-testid="stRadio"] label:hover {{
        border-color: var(--accent-blue);
        color: var(--text-primary);
        background-color: var(--bg-subtle);
    }}

    div[data-testid="stRadio"] [data-checked="true"] + div {{
        color: var(--accent-blue) !important;
        font-weight: 700 !important;
    }}

    /* Executive Expander Styling */
    div[data-testid="stExpander"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        margin-bottom: 6px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-card);
    }}

    div[data-testid="stExpander"] details {{
        border: none !important;
        background-color: transparent !important;
    }}

    div[data-testid="stExpander"] summary {{
        border-radius: 8px !important;
        padding: 8px 12px !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
    }}

    div[data-testid="stExpander"] summary:hover {{
        background-color: var(--bg-subtle) !important;
        color: var(--accent-blue) !important;
    }}

    div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{
        color: var(--text-muted) !important;
        margin-right: 6px !important;
    }}

    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        padding: 6px 8px 8px 8px !important;
        border-top: 1px solid var(--border-color) !important;
    }}

    /* Sidebar button styling within expanders */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] .stButton button {{
        padding: 5px 10px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        margin-bottom: 3px !important;
        border-color: var(--border-subtle) !important;
        border-radius: 5px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] .stButton button:hover {{
        border-color: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
        background-color: var(--bg-subtle) !important;
    }}
    </style>
    """


# Inject active theme CSS
st.markdown(get_app_css(st.session_state["dark_mode"]), unsafe_allow_html=True)


# =============================================================================
# DATA LAYER (CACHED)
# =============================================================================
@st.cache_data(show_spinner=False)
def load_app_data() -> pd.DataFrame:
    """Load cached dataset from CSV with enriched metrics."""
    return load_data(force_scrape=False)


df_raw = load_app_data()


# =============================================================================
# MODULAR COMPONENT 1: SIDEBAR WITH BUSINESS QUESTIONS
# =============================================================================
def render_sidebar(total_records: int, dark_mode: bool) -> str:
    """Render the compact, premium executive sidebar with navigation, business questions, and theme switch."""
    with st.sidebar:
        # Brand Block
        st.markdown(
            """
            <div style="padding: 4px 0 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
                <div style="font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent-blue);">GLOBAL 50</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-primary); line-height: 1.2;">Corporate Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Primary Navigation
        st.markdown(
            "<div style='font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 6px;'>Navigation</div>",
            unsafe_allow_html=True,
        )

        nav_options = ["Overview", "Analytics", "Business Questions", "Company Explorer", "Compare", "Data"]

        # Consume pending programmatic navigation BEFORE creating the radio widget
        pending_nav = st.session_state.pop("nav_pending", None)
        if pending_nav and pending_nav in nav_options:
            st.session_state["main_nav_radio"] = pending_nav
            st.session_state["nav_selection"] = pending_nav

        if "main_nav_radio" not in st.session_state or st.session_state["main_nav_radio"] not in nav_options:
            st.session_state["main_nav_radio"] = "Overview"
            st.session_state["nav_selection"] = "Overview"

        def _on_nav_change():
            st.session_state["nav_selection"] = st.session_state["main_nav_radio"]

        st.radio(
            label="Navigation",
            options=nav_options,
            key="main_nav_radio",
            label_visibility="collapsed",
            on_change=_on_nav_change,
        )
        st.session_state["nav_selection"] = st.session_state.get("main_nav_radio", "Overview")

        # ---------------------------------------------------------------------
        # BUSINESS QUESTIONS ANALYTICAL NAVIGATOR
        # ---------------------------------------------------------------------
        st.markdown(
            """
            <div style="margin-top: 22px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">Business Questions</span>
                <span style="font-size: 0.68rem; font-weight: 800; color: var(--accent-blue); background: var(--bg-subtle); padding: 1px 6px; border-radius: 4px; border: 1px solid var(--border-color);">10 Analyses</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick Jump Dropdown
        bq_labels = ["-- Select Analytical Question --"] + list(BUSINESS_QUESTIONS_MAP.keys())

        def _handle_bq_jump():
            picked = st.session_state.get("sb_bq_quick_jump")
            if picked and picked != "-- Select Analytical Question --" and picked in BUSINESS_QUESTIONS_MAP:
                navigate_to("Business Questions", question=picked)
                st.session_state["sb_bq_quick_jump"] = "-- Select Analytical Question --"

        st.selectbox(
            "Quick Analytical Jump",
            options=bq_labels,
            index=0,
            label_visibility="collapsed",
            key="sb_bq_quick_jump",
            on_change=_handle_bq_jump,
        )

        # Categorized Clickable Question Groups
        groups = {
            "FINANCIAL": ("💼", ["Revenue Leaders", "Profit Leaders", "Profitability"]),
            "GEOGRAPHIC": ("🌐", ["Country Revenue", "Country Benchmarking"]),
            "INDUSTRY": ("🏭", ["Industry Revenue", "Industry Profitability"]),
            "EFFICIENCY": ("⚡", ["Revenue per Employee", "Workforce vs Revenue"]),
            "CONCENTRATION": ("🎯", ["Revenue Concentration"]),
        }

        active_target = st.session_state.get("active_question_target")
        for grp_name, (icon, q_list) in groups.items():
            is_group_active = bool(active_target and active_target in q_list)
            with st.expander(f"{icon}  {grp_name}", expanded=is_group_active):
                for q_key in q_list:
                    is_active = (active_target == q_key)
                    label = f"● {q_key}" if is_active else f"▸ {q_key}"
                    if st.button(label, key=f"btn_nav_{q_key.replace(' ', '_')}", width="stretch"):
                        navigate_to("Business Questions", question=q_key)
                        st.rerun()

        # Theme Selector in Sidebar
        st.markdown(
            "<div style='font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-top: 24px; margin-bottom: 6px;'>Appearance Theme</div>",
            unsafe_allow_html=True,
        )
        st.radio(
            label="Theme",
            options=["☀️ Light Mode", "🌙 Dark Mode"],
            index=1 if st.session_state["dark_mode"] else 0,
            horizontal=True,
            label_visibility="collapsed",
            key="sidebar_theme_pick",
            on_change=on_theme_change_sidebar,
        )

        # Dataset Information Card
        st.markdown(
            f"""
            <div style="margin-top: 28px; padding: 14px 16px; background-color: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 8px;">
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 8px;">Dataset Intelligence</div>
                <div style="margin-bottom: 6px;">
                    <div style="font-size: 0.72rem; color: var(--text-muted);">Universe</div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">Global 50 Corporations</div>
                </div>
                <div style="margin-bottom: 6px;">
                    <div style="font-size: 0.72rem; color: var(--text-muted);">Verified Records</div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">{total_records} Entities</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: var(--text-muted);">Data Source</div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">Fortune Global 500 / Wikipedia</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state["nav_selection"]


# =============================================================================
# MODULAR COMPONENT 2: EXECUTIVE HERO HEADER
# =============================================================================
def render_hero_header(df_filtered: pd.DataFrame, df_full: pd.DataFrame, dark_mode: bool) -> None:
    """
    Render compact, visually rich 2-column executive hero header:
    LEFT: Brand title, subtitle, and dynamic contextual summary badges.
    RIGHT: Dark mode toggle & compact sovereign revenue distribution micro-visualization.
    """
    total_rev_filtered = float(df_filtered["Revenue (USD)"].sum()) if not df_filtered.empty else 0.0
    total_rev_pool_t = total_rev_filtered / 1000.0

    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    c_left, c_right = st.columns([1.35, 1.0])

    with c_left:
        st.markdown(
            f"""
            <div class="hero-kicker">GLOBAL 50</div>
            <h1 class="hero-title">Corporate Intelligence</h1>
            <div class="hero-subtitle">
                Executive analysis of the world's largest companies by revenue, profitability and workforce.
            </div>
            <div class="hero-pills-row">
                <div class="hero-pill">
                    <span>🏛️</span> <span><b>{len(df_filtered)}</b> Companies</span>
                </div>
                <div class="hero-pill">
                    <span>💰</span> <span class="hero-pill-highlight">${total_rev_pool_t:.1f}T</span> <span>Revenue Pool</span>
                </div>
                <div class="hero-pill">
                    <span>🌐</span> <span>Global Corporate Benchmark</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_right:
        # Top row: Micro-label and Dark Mode switch
        r_top_c1, r_top_c2 = st.columns([1.2, 1.0])
        with r_top_c1:
            st.markdown(
                '<div class="header-meta-label">SECTOR REVENUE ALLOCATION</div>',
                unsafe_allow_html=True,
            )
        with r_top_c2:
            st.radio(
                "Theme Toggle",
                options=["☀️ Light", "🌙 Dark"],
                index=1 if st.session_state["dark_mode"] else 0,
                horizontal=True,
                label_visibility="collapsed",
                key="header_theme_toggle_btn",
                on_change=on_theme_change_header,
            )

        # Mini Revenue Pool Micro-Visualization
        fig_mini = analysis.chart_header_mini_distribution(df_filtered, dark_mode=dark_mode)
        st.plotly_chart(fig_mini, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# MODULAR COMPONENT 3: KPI CARDS
# =============================================================================
def render_kpi_cards(kpis: Dict[str, Any], dark_mode: bool = False) -> None:
    """Render four standardized, equal-height corporate KPI cards with clear hierarchy."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Active Enterprises</div>
                <div class="kpi-value">{kpis['total_companies']}</div>
                <div>
                    <div class="kpi-entity">Global 50 Universe</div>
                    <div class="kpi-meta">
                        <span>Showing {kpis['total_companies']} of 50 ({kpis['total_share_pct']:.0f}%)</span>
                        <span class="kpi-tag">Cohort</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Highest Revenue</div>
                <div class="kpi-value">{kpis['highest_revenue_formatted']}</div>
                <div>
                    <div class="kpi-entity">{kpis['highest_revenue_company']} · Rank #{kpis['highest_revenue_rank']}</div>
                    <div class="kpi-meta">
                        <span>Global Turnover Leader</span>
                        <span class="kpi-tag">Rank #1</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Highest Net Profit</div>
                <div class="kpi-value">{kpis['highest_profit_formatted']}</div>
                <div>
                    <div class="kpi-entity">{kpis['highest_profit_company']} · Rank #{kpis['highest_profit_rank']}</div>
                    <div class="kpi-meta">
                        <span>Capital Conversion Engine</span>
                        <span class="kpi-tag">Profit</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Largest Workforce</div>
                <div class="kpi-value">{kpis['largest_employer_formatted']}</div>
                <div>
                    <div class="kpi-entity">{kpis['largest_employer_company']} · Rank #{kpis['largest_employer_rank']}</div>
                    <div class="kpi-meta">
                        <span>Global Labor Scale Anchor</span>
                        <span class="kpi-tag">Labor</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# =============================================================================
# MODULAR COMPONENT 4: GLOBAL FILTER BAR
# =============================================================================
def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render unified single-panel global filter container."""
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<div class="filter-panel-title">Global Filter Controls</div>', unsafe_allow_html=True)

    all_countries = sorted(df["Country"].unique().tolist())
    all_industries = sorted(df["Industry"].unique().tolist())
    min_rev = float(df["Revenue (USD)"].min())
    max_rev = float(df["Revenue (USD)"].max())

    # Session State Initialization for Filters
    if "filter_search" not in st.session_state:
        st.session_state["filter_search"] = ""
    if "filter_countries" not in st.session_state:
        st.session_state["filter_countries"] = []
    if "filter_industries" not in st.session_state:
        st.session_state["filter_industries"] = []
    if "filter_revenue" not in st.session_state:
        st.session_state["filter_revenue"] = (min_rev, max_rev)

    # 4-Column Control Layout
    f_c1, f_c2, f_c3, f_c4 = st.columns([1.2, 1.2, 1.2, 1.4])

    with f_c1:
        search_val = st.text_input(
            "Search Company",
            value=st.session_state["filter_search"],
            placeholder="Search company name...",
            key="input_search",
        )

    with f_c2:
        countries_val = st.multiselect(
            "Country",
            options=all_countries,
            default=st.session_state["filter_countries"],
            placeholder="All Countries",
            key="input_countries",
        )

    with f_c3:
        industries_val = st.multiselect(
            "Industry",
            options=all_industries,
            default=st.session_state["filter_industries"],
            placeholder="All Industries",
            key="input_industries",
        )

    with f_c4:
        rev_val = st.slider(
            "Revenue Range ($B)",
            min_value=min_rev,
            max_value=max_rev,
            value=st.session_state["filter_revenue"],
            step=5.0,
            format="$%.0fB",
            key="input_revenue",
        )

    # Apply Filtering
    filtered = analysis.filter_dataframe(
        df,
        countries=countries_val if countries_val else None,
        industries=industries_val if industries_val else None,
        search_query=search_val if search_val else None,
        min_revenue=rev_val[0],
        max_revenue=rev_val[1],
    )

    # Track active filters
    active_filters = []
    if search_val.strip():
        active_filters.append(f"Search: '{search_val.strip()}'")
    if countries_val:
        active_filters.append(f"Countries ({len(countries_val)})")
    if industries_val:
        active_filters.append(f"Industries ({len(industries_val)})")
    if rev_val != (min_rev, max_rev):
        active_filters.append(f"${rev_val[0]:.0f}B - ${rev_val[1]:.0f}B")

    # Filter Feedback & Reset Row
    fb_col1, fb_col2 = st.columns([3, 1])
    with fb_col1:
        badge_html = "".join([f'<span class="filter-badge">{f}</span>' for f in active_filters])
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-secondary); margin-top: 6px;">
                <span><b>Showing {len(filtered)} of {len(df)} companies</b></span>
                {badge_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with fb_col2:
        def _do_reset():
            st.session_state["input_search"] = ""
            st.session_state["input_countries"] = []
            st.session_state["input_industries"] = []
            st.session_state["input_revenue"] = (min_rev, max_rev)

        if active_filters and st.button("Reset Filters", key="btn_reset_filters", width="stretch", on_click=_do_reset):
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    return filtered


# =============================================================================
# HELPER: SECTION HEADER & QUESTION FOCUS BANNER
# =============================================================================
def render_section_header(title: str, subtitle: str = "", label: str = "") -> None:
    """Render a structured executive section title with small label and subtitle."""
    kicker_html = f'<div class="section-kicker">{label}</div>' if label else ""
    subtitle_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header-block">
            {kicker_html}
            <h2 class="section-title">{title}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analytical_focus_banner(active_page: str) -> None:
    """Render a prominent, clean banner if the user navigated via a sidebar Business Question."""
    target_q = st.session_state.get("active_question_target")
    if not target_q or target_q not in BUSINESS_QUESTIONS_MAP:
        return

    q_data = BUSINESS_QUESTIONS_MAP[target_q]
    if q_data["page"] != active_page:
        return

    f_col1, f_col2 = st.columns([5.5, 1.0])
    with f_col1:
        st.markdown(
            f"""
            <div style="background: var(--bg-card); border: 1px solid var(--accent-blue); border-left: 4px solid var(--accent-blue); border-radius: 6px; padding: 10px 16px; margin-bottom: 14px; box-shadow: var(--shadow-card);">
                <div style="font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-blue);">
                    ANALYTICAL QUESTION FOCUS &bull; {q_data['group']}
                </div>
                <div style="font-size: 0.95rem; font-weight: 800; color: var(--text-primary); margin-top: 2px;">
                    "{q_data['question']}"
                </div>
                <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 3px;">
                    Targeting analysis: <b>{q_data['target_desc']}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col2:
        if st.button("✕ Dismiss Focus", key="btn_dismiss_focus", width="stretch"):
            st.session_state["active_question_target"] = None
            st.rerun()


# =============================================================================
# HELPER: ZERO RESULTS STATE
# =============================================================================
def render_empty_state() -> None:
    """Render clean empty-state fallback when filters eliminate all rows."""
    st.markdown(
        """
        <div class="empty-state-card">
            <div class="empty-state-title">No companies match the selected filters</div>
            <div class="empty-state-desc">Try clearing your search query or broadening your country, industry, or revenue range selections.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    e_col1, e_col2, e_col3 = st.columns([1.5, 1, 1.5])
    with e_col2:
        def _do_empty_reset():
            st.session_state["input_search"] = ""
            st.session_state["input_countries"] = []
            st.session_state["input_industries"] = []
            min_r = float(df_raw["Revenue (USD)"].min())
            max_r = float(df_raw["Revenue (USD)"].max())
            st.session_state["input_revenue"] = (min_r, max_r)

        if st.button("Reset Filters to Baseline", key="btn_empty_reset", width="stretch", on_click=_do_empty_reset):
            st.rerun()


# =============================================================================
# MODULAR COMPONENT 5: FOOTER
# =============================================================================
def render_footer() -> None:
    """Render subdued corporate footer."""
    st.markdown(
        """
        <div class="footer-container">
            GLOBAL 50 Corporate Intelligence &bull; Fortune Global 500 Monitoring &bull; Data Source: Wikipedia
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 1: OVERVIEW
# =============================================================================
def render_overview_section(df: pd.DataFrame, dark_mode: bool = False) -> None:
    """
    Render Overview page with 3 structured balanced 2-column sections:
    1. Executive Overview (Top 10 Revenue & Top 10 Profit)
    2. Global Corporate Distribution (Companies by Country & Companies by Industry)
    3. Revenue Distribution (Revenue by Country & Revenue by Industry)
    """
    render_analytical_focus_banner(active_page="Overview")

    if df.empty:
        render_empty_state()
        return

    # Section 1: Executive Overview (Top 10 Revenue & Top 10 Profit)
    render_section_header("Top Corporate Leaders by Financial Performance", "Ranked comparison of the world's 10 largest revenue and profit engines", label="EXECUTIVE OVERVIEW")
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_top10_revenue(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)

    with r1_c2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_top10_profit(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)

    # Section 2: Global Corporate Distribution (Companies by Country & Industry)
    render_section_header("Enterprise Distribution Across Nations & Sectors", "Distribution of corporate headquarters across sovereign jurisdictions and business sectors", label="CORPORATE FOOTPRINT")
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_companies_by_country(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)

    with r2_c2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_companies_by_industry(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)

    # Section 3: Revenue Distribution (Revenue by Country & Industry)
    render_section_header("Aggregate Capital and Turnover Pools", "Gross turnover concentration captured across sovereign markets and industry sectors", label="REVENUE DISTRIBUTION")
    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_revenue_by_country(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)

    with r3_c2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.plotly_chart(analysis.chart_revenue_by_industry(df, dark_mode=dark_mode))
        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 2: ANALYTICS (ADVANCED ANALYTICS WITH MULTIPLE CHOICES)
# =============================================================================
def render_analytics_section(df: pd.DataFrame, dark_mode: bool = False) -> None:
    """
    Render Advanced Analytics view with multiple interactive dimension choices and controls:
    1. Complete Suite (All 5 Pillars)
    2. Financial Dynamics & Pareto Scale
    3. Profitability & Capital Conversion
    4. Workforce Productivity & Labor Leverage
    5. Cross-Sector Industry Benchmarks
    6. Sovereign Market Scale & Geographic Footprint
    """
    render_analytical_focus_banner(active_page="Analytics")

    if df.empty:
        render_empty_state()
        return

    render_section_header(
        "Institutional Corporate Analytics",
        "Select analytical pillars to explore empirical relationships, capital efficiency, and market distributions",
        label="ADVANCED ANALYTICS",
    )

    # Interactive Dimension Selector
    dim_choices = [
        "📊 Complete Suite (All Analyses)",
        "💰 Financial Dynamics & Pareto",
        "📈 Profitability & Capital Conversion",
        "⚡ Workforce Productivity & Scaling",
        "🏭 Industry Sector Benchmarks",
        "🌐 Sovereign Geographic Scale",
    ]
    selected_dim = st.radio(
        "Select Analytical Dimension",
        options=dim_choices,
        index=0,
        horizontal=True,
        key="analytics_dim_radio_pick",
    )

    show_all = (selected_dim == "📊 Complete Suite (All Analyses)")

    # -------------------------------------------------------------------------
    # 1. Financial Performance & Revenue Concentration (Pareto)
    # -------------------------------------------------------------------------
    if show_all or selected_dim == "💰 Financial Dynamics & Pareto":
        render_section_header("Volume vs. Profit Dynamics & Revenue Concentration", "Empirical scale relationships, OLS trendlines, and Pareto concentration curves", label="1. FINANCIAL PERFORMANCE")

        fp_ctl1, fp_ctl2 = st.columns([1.5, 1.5])
        with fp_ctl1:
            st.radio("Trendline Model", ["With OLS Regression Trendline", "Scatter Distribution Only"], horizontal=True, key="an_opt_trend")
        with fp_ctl2:
            st.radio("Concentration Scope", ["Top 5 & Top 10 Share", "50% Revenue Concentration Cutoff"], horizontal=True, key="an_opt_pareto")

        fp_c1, fp_c2 = st.columns(2)
        with fp_c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_revenue_vs_profit(df, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

        with fp_c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_pareto_revenue_concentration(df, dark_mode=dark_mode))
            pareto_stats = analysis.get_revenue_concentration_stats(df)
            st.markdown(
                f"""
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px 14px; margin-top: 4px; font-size: 0.78rem; color: var(--text-secondary);">
                    <b>Concentration Analysis:</b> The Top 5 companies capture <b>{pareto_stats['top5_share']:.1f}%</b> of total revenue, 
                    and the Top 10 control <b>{pareto_stats['top10_share']:.1f}%</b>. 
                    50% of aggregate revenue is concentrated across just <b>{pareto_stats['half_count']} companies</b>.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Profitability Analysis
    # -------------------------------------------------------------------------
    if show_all or selected_dim == "📈 Profitability & Capital Conversion":
        render_section_header("Capital Conversion & Net Profit Margin Rankings", "Net conversion efficiency, top operating margins, and industry dispersion", label="2. PROFITABILITY ANALYSIS")

        pr_ctl1, pr_ctl2 = st.columns([1.5, 1.5])
        with pr_ctl1:
            scope_pick = st.radio("Cohort Scope", ["Top 5", "Top 10", "Top 15", "All Companies"], index=1, horizontal=True, key="an_opt_scope")
            top_n_map = {"Top 5": 5, "Top 10": 10, "Top 15": 15, "All Companies": len(df)}
            top_n_val = top_n_map[scope_pick]
        with pr_ctl2:
            sort_metric = st.radio("Ranking Focus", ["Net Profit Margin (%)", "Absolute Net Profit ($B)"], horizontal=True, key="an_opt_pr_metric")

        pr_c1, pr_c2 = st.columns(2)
        with pr_c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            if sort_metric == "Absolute Net Profit ($B)":
                st.plotly_chart(analysis.chart_top10_profit(df, dark_mode=dark_mode))
            else:
                st.plotly_chart(analysis.chart_top_profit_margins(df, top_n=top_n_val, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

        with pr_c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_margin_by_industry(df, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Workforce Productivity & Capital Efficiency
    # -------------------------------------------------------------------------
    if show_all or selected_dim == "⚡ Workforce Productivity & Scaling":
        render_section_header("Labor Productivity & Capital Efficiency Quadrant", "Revenue generated per worker and multidimensional capital efficiency quadrant", label="3. WORKFORCE PRODUCTIVITY")

        wp_ctl1, wp_ctl2 = st.columns([1.5, 1.5])
        with wp_ctl1:
            wp_focus = st.radio("Productivity View", ["Capital Efficiency Quadrant", "Revenue per Employee Rankings (Bar Chart)", "Both Visualizations"], index=2 if show_all else 0, horizontal=True, key="an_opt_wp_focus")

        if wp_focus in ["Capital Efficiency Quadrant", "Both Visualizations"]:
            wp_c1, wp_c2 = st.columns(2) if wp_focus == "Both Visualizations" else (st.container(), None)
            with wp_c1:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.plotly_chart(analysis.chart_capital_efficiency_quadrant(df, dark_mode=dark_mode))
                st.markdown('</div>', unsafe_allow_html=True)
            if wp_c2:
                with wp_c2:
                    st.markdown('<div class="content-card">', unsafe_allow_html=True)
                    st.plotly_chart(analysis.chart_workforce_productivity(df, dark_mode=dark_mode))
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_workforce_productivity(df, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. Industry Benchmarking
    # -------------------------------------------------------------------------
    if show_all or selected_dim == "🏭 Industry Sector Benchmarks":
        render_section_header("Cross-Sector Cohort Comparisons & Benchmark Matrix", "Aggregated industry turnover, profitability, and workforce leverage benchmarks", label="4. INDUSTRY BENCHMARKING")
        ind_bench = analysis.get_industry_benchmarks(df)

        ib_ctl1, ib_ctl2 = st.columns([1.5, 1.5])
        with ib_ctl1:
            sort_ind_col = st.selectbox("Rank Sectors By", ["Total Revenue", "Avg Revenue", "Avg Margin", "Avg Rev per Worker"], key="an_opt_ind_sort")
            col_map = {
                "Total Revenue": "Total_Revenue",
                "Avg Revenue": "Avg_Revenue",
                "Avg Margin": "Avg_Margin",
                "Avg Rev per Worker": "Avg_Rev_Per_Emp",
            }
            ind_bench = ind_bench.sort_values(by=col_map[sort_ind_col], ascending=False)

        ib_c1, ib_c2 = st.columns([1.1, 1.3])
        with ib_c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_industry_benchmarks(ind_bench, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

        with ib_c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">Industry Aggregation Matrix (Sorted by {sort_ind_col})</div>', unsafe_allow_html=True)
            st.dataframe(
                ind_bench[
                    [
                        "Industry",
                        "Company_Count",
                        "Total_Revenue",
                        "Avg_Revenue",
                        "Avg_Margin",
                        "Avg_Rev_Per_Emp",
                    ]
                ]
                .rename(
                    columns={
                        "Company_Count": "Firms",
                        "Total_Revenue": "Total Rev ($B)",
                        "Avg_Revenue": "Mean Rev ($B)",
                        "Avg_Margin": "Mean Margin (%)",
                        "Avg_Rev_Per_Emp": "Rev/Worker ($)",
                    }
                )
                .style.format(
                    {
                        "Total Rev ($B)": "${:,.1f}B",
                        "Mean Rev ($B)": "${:,.1f}B",
                        "Mean Margin (%)": "{:.2f}%",
                        "Rev/Worker ($)": "${:,.0f}",
                    }
                ),
                hide_index=True,
                height=345,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. Country Benchmarking & Global Map
    # -------------------------------------------------------------------------
    if show_all or selected_dim == "🌐 Sovereign Geographic Scale":
        render_section_header("Sovereign Market Scale & Global Geographic Footprint", "National corporate benchmarks and interactive global choropleth map", label="5. COUNTRY BENCHMARKING")
        cntry_bench = analysis.get_country_benchmarks(df)

        geo_mode = st.radio("Geographic Visualization Mode", ["Dual View (Rankings & Map)", "Global Choropleth Map Focus", "Sovereign Benchmarking Matrix Focus"], horizontal=True, key="an_opt_geo_mode")

        if geo_mode == "Global Choropleth Map Focus":
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_revenue_by_country_map(df, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)
        elif geo_mode == "Sovereign Benchmarking Matrix Focus":
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Sovereign Aggregation Matrix</div>', unsafe_allow_html=True)
            st.dataframe(
                cntry_bench[
                    ["Country", "Company_Count", "Total_Revenue", "Avg_Revenue", "Total_Profit", "Avg_Margin"]
                ]
                .rename(
                    columns={
                        "Company_Count": "Firms",
                        "Total_Revenue": "Total Rev ($B)",
                        "Avg_Revenue": "Mean Rev ($B)",
                        "Total_Profit": "Total Profit ($B)",
                        "Avg_Margin": "Mean Margin (%)",
                    }
                )
                .style.format(
                    {
                        "Total Rev ($B)": "${:,.1f}B",
                        "Mean Rev ($B)": "${:,.1f}B",
                        "Total Profit ($B)": "${:,.1f}B",
                        "Mean Margin (%)": "{:.2f}%",
                    }
                ),
                hide_index=True,
                height=380,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            cb_c1, cb_c2 = st.columns([1.1, 1.3])
            with cb_c1:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.plotly_chart(analysis.chart_country_benchmarks(cntry_bench, dark_mode=dark_mode))
                st.markdown('</div>', unsafe_allow_html=True)
            with cb_c2:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Sovereign Aggregation Matrix</div>', unsafe_allow_html=True)
                st.dataframe(
                    cntry_bench[
                        ["Country", "Company_Count", "Total_Revenue", "Avg_Revenue", "Total_Profit", "Avg_Margin"]
                    ]
                    .rename(
                        columns={
                            "Company_Count": "Firms",
                            "Total_Revenue": "Total Rev ($B)",
                            "Avg_Revenue": "Mean Rev ($B)",
                            "Total_Profit": "Total Profit ($B)",
                            "Avg_Margin": "Mean Margin (%)",
                        }
                    )
                    .style.format(
                        {
                            "Total Rev ($B)": "${:,.1f}B",
                            "Mean Rev ($B)": "${:,.1f}B",
                            "Total Profit ($B)": "${:,.1f}B",
                            "Mean Margin (%)": "{:.2f}%",
                        }
                    ),
                    hide_index=True,
                    height=345,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_revenue_by_country_map(df, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

    # Callout Banner to Business Questions Hub
    st.markdown(
        """
        <div class="content-card" style="margin-top: 20px; border-left: 4px solid var(--accent-blue); padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-blue);">STRATEGIC INQUIRY HUB</div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: var(--text-primary); margin-top: 2px;">Explore Dedicated Strategic Business Questions</div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;">Access all 10 core executive inquiries with dedicated filters, interactive deep-dive visualizers, and data-driven insights.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚀 Open Dedicated Business Questions Section", key="btn_open_bq_from_analytics", width="stretch"):
        navigate_to("Business Questions")
        st.rerun()


# =============================================================================
# HELPER: QUESTION DETAILS GENERATOR FOR BUSINESS QUESTIONS HUB
# =============================================================================
def get_question_details(df: pd.DataFrame, q_key: str, dark_mode: bool = False) -> Dict[str, Any]:
    """Dynamically compute analytical scorecards, narrative answer, chart, and takeaways for a question."""
    total_rev = df["Revenue (USD)"].sum()
    total_profit = df["Profit (USD)"].dropna().sum()
    clean_profit_df = df.dropna(subset=["Profit (USD)", "Profit Margin (%)"])
    cntry_bench = analysis.get_country_benchmarks(df)
    ind_bench = analysis.get_industry_benchmarks(df)

    if q_key == "Revenue Leaders":
        sorted_df = df.sort_values(by="Revenue (USD)", ascending=False)
        top1 = sorted_df.iloc[0]
        top2 = sorted_df.iloc[1] if len(sorted_df) > 1 else top1
        share = (top1["Revenue (USD)"] / total_rev * 100) if total_rev > 0 else 0
        return {
            "title": "Which companies generate the highest revenue?",
            "group": "FINANCIAL PERFORMANCE",
            "kpi1_label": "Global Revenue Leader", "kpi1_val": top1["Company"],
            "kpi2_label": "Top-Line Turnover", "kpi2_val": f"${top1['Revenue (USD)']:,.1f}B",
            "kpi3_label": "Universe Share", "kpi3_val": f"{share:.1f}% of Cohort",
            "kpi4_label": "Runner-Up Entity", "kpi4_val": f"{top2['Company']} (${top2['Revenue (USD)']:,.1f}B)",
            "answer": f"**{top1['Company']}** stands as the global revenue leader with **${top1['Revenue (USD)']:,.1f}B** in annual gross turnover, capturing **{share:.1f}%** of the total evaluated revenue pool. It is followed by **{top2['Company']}** at **${top2['Revenue (USD)']:,.1f}B**.",
            "fig": analysis.chart_top10_revenue(df, dark_mode=dark_mode),
            "table": sorted_df[["Rank", "Company", "Country", "Industry", "Revenue (USD)", "Profit (USD)"]].head(10),
            "takeaways": [
                "Top-line turnover is heavily concentrated in logistics, e-commerce, and global supply chain conglomerates.",
                f"The top two entities alone account for over ${(top1['Revenue (USD)'] + top2['Revenue (USD)']):,.1f}B in gross commercial activity.",
                "High revenue volume does not always guarantee peak profit margins, underscoring high operational overhead."
            ]
        }
    elif q_key == "Profit Leaders":
        sorted_df = df.sort_values(by="Profit (USD)", ascending=False)
        top1 = sorted_df.iloc[0]
        top2 = sorted_df.iloc[1] if len(sorted_df) > 1 else top1
        share = (top1["Profit (USD)"] / total_profit * 100) if total_profit > 0 else 0
        return {
            "title": "Which companies generate the highest profit?",
            "group": "FINANCIAL PERFORMANCE",
            "kpi1_label": "Net Income Leader", "kpi1_val": top1["Company"],
            "kpi2_label": "Annual Net Income", "kpi2_val": f"${top1['Profit (USD)']:,.1f}B",
            "kpi3_label": "Net Profit Share", "kpi3_val": f"{share:.1f}% of Total Profit",
            "kpi4_label": "Runner-Up Engine", "kpi4_val": f"{top2['Company']} (${top2['Profit (USD)']:,.1f}B)",
            "answer": f"**{top1['Company']}** dominates absolute capital conversion, generating an unprecedented **${top1['Profit (USD)']:,.1f}B** in net earnings (**{share:.1f}%** of all corporate profits generated across the cohort). **{top2['Company']}** ranks second with **${top2['Profit (USD)']:,.1f}B**.",
            "fig": analysis.chart_top10_profit(df, dark_mode=dark_mode),
            "table": sorted_df[["Rank", "Company", "Country", "Industry", "Profit (USD)", "Revenue (USD)", "Profit Margin (%)"]].head(10),
            "takeaways": [
                "Technology platforms and high-margin integrated energy titans command the lion's share of absolute global profits.",
                "The profit champion generates more net income than the bottom 30 profitable companies in the universe combined.",
                "Sustained profit leadership is underpinned by intellectual property monopolies and high barriers to market entry."
            ]
        }
    elif q_key == "Profitability":
        sorted_df = clean_profit_df.sort_values(by="Profit Margin (%)", ascending=False)
        top1 = sorted_df.iloc[0] if not sorted_df.empty else df.iloc[0]
        top2 = sorted_df.iloc[1] if len(sorted_df) > 1 else top1
        avg_m = clean_profit_df["Profit Margin (%)"].mean() if not clean_profit_df.empty else 0
        return {
            "title": "Which companies have the strongest profit margins?",
            "group": "FINANCIAL PERFORMANCE",
            "kpi1_label": "Margin Efficiency Leader", "kpi1_val": top1["Company"],
            "kpi2_label": "Net Profit Margin", "kpi2_val": f"{top1['Profit Margin (%)']:.2f}%",
            "kpi3_label": "Cohort Average Margin", "kpi3_val": f"{avg_m:.2f}%",
            "kpi4_label": "Runner-Up Efficiency", "kpi4_val": f"{top2['Company']} ({top2['Profit Margin (%)']:.1f}%)",
            "answer": f"**{top1['Company']}** achieves peerless operational profitability with a net margin of **{top1['Profit Margin (%)']:.2f}%**, converting nearly a third of top-line receipts directly into bottom-line shareholder earnings, far outstripping the universe benchmark of **{avg_m:.1f}%**.",
            "fig": analysis.chart_top_profit_margins(df, top_n=10, dark_mode=dark_mode),
            "table": sorted_df[["Rank", "Company", "Industry", "Profit Margin (%)", "Revenue (USD)", "Profit (USD)"]].head(10),
            "takeaways": [
                "Extreme profit margins (>25%) are clustered in semiconductor foundry monopolies and hyper-scale digital ecosystems.",
                "Volume leaders (e.g. mass retail) operate on thin 1.5% - 3.5% margins, proving capital conversion asymmetry.",
                "Pricing power and proprietary fab infrastructure insulate margin leaders from global inflationary shocks."
            ]
        }
    elif q_key == "Country Revenue":
        cnt_rev = df.groupby("Country")["Revenue (USD)"].sum().sort_values(ascending=False)
        top1_c = cnt_rev.index[0]
        top1_v = cnt_rev.iloc[0]
        top2_c = cnt_rev.index[1] if len(cnt_rev) > 1 else top1_c
        top2_v = cnt_rev.iloc[1] if len(cnt_rev) > 1 else 0
        share = (top1_v / total_rev * 100) if total_rev > 0 else 0
        return {
            "title": "Which countries generate the most revenue?",
            "group": "GEOGRAPHIC SCALE",
            "kpi1_label": "Leading Sovereign Hub", "kpi1_val": top1_c,
            "kpi2_label": "Sovereign Revenue Pool", "kpi2_val": f"${top1_v:,.1f}B",
            "kpi3_label": "Global Cohort Share", "kpi3_val": f"{share:.1f}%",
            "kpi4_label": "Secondary Sovereign Hub", "kpi4_val": f"{top2_c} (${top2_v:,.1f}B)",
            "answer": f"The **{top1_c}** represents the world's primary sovereign commercial engine, anchoring **${top1_v:,.1f}B** (**{share:.1f}%** of all Global 50 turnover). **{top2_c}** follows as the secondary corporate hub with **${top2_v:,.1f}B**.",
            "fig": analysis.chart_revenue_by_country(df, dark_mode=dark_mode),
            "table": cntry_bench[["Country", "Company_Count", "Total_Revenue", "Avg_Revenue", "Total_Profit"]].rename(columns={"Company_Count": "Firms", "Total_Revenue": "Total Rev ($B)", "Avg_Revenue": "Mean Rev ($B)", "Total_Profit": "Profit ($B)"}),
            "takeaways": [
                "Corporate scale is heavily polarized around the US-China economic corridor, which jointly commands over two-thirds of aggregate revenue.",
                "European corporate presence is concentrated in specialized industrial equipment, automotive, and retail grocery.",
                "Jurisdictional legal systems and deep capital markets directly correlate with headquarters retention."
            ]
        }
    elif q_key == "Country Benchmarking":
        cnt_cnt = df.groupby("Country")["Company"].count().sort_values(ascending=False)
        top_c = cnt_cnt.index[0]
        num_firms = cnt_cnt.iloc[0]
        return {
            "title": "How do sovereign jurisdictions compare in corporate scale?",
            "group": "GEOGRAPHIC SCALE",
            "kpi1_label": "Most Populated Hub", "kpi1_val": f"{top_c} ({num_firms} Firms)",
            "kpi2_label": "Total Active Jurisdictions", "kpi2_val": f"{len(cnt_cnt)} Countries",
            "kpi3_label": "Average Firms / Nation", "kpi3_val": f"{len(df) / len(cnt_cnt):.1f} Firms",
            "kpi4_label": "Cross-Border Spread", "kpi4_val": "Americas, APAC & EMEA",
            "answer": f"Sovereign market analysis indicates that **{top_c}** hosts **{num_firms}** of the 50 largest corporations. The remaining entities are dispersed across **{len(cnt_cnt) - 1}** advanced economies spanning North America, East Asia, and Western Europe.",
            "fig": analysis.chart_country_benchmarks(cntry_bench, dark_mode=dark_mode),
            "table": cntry_bench[["Country", "Company_Count", "Total_Revenue", "Avg_Margin"]].rename(columns={"Company_Count": "Firms", "Total_Revenue": "Total Rev ($B)", "Avg_Margin": "Mean Margin (%)"}),
            "takeaways": [
                "Sovereign corporate clusters reflect strategic national competitive advantages (Tech in US, Manufacturing in China/Taiwan/Japan).",
                "Advanced sovereign hubs exhibit significantly higher average net margins due to tech and high-value energy weighting.",
                "Global footprint highlights the necessity of geographic diversification in corporate supply chains."
            ]
        }
    elif q_key == "Industry Revenue":
        ind_rev = df.groupby("Industry")["Revenue (USD)"].sum().sort_values(ascending=False)
        top_i = ind_rev.index[0]
        top_v = ind_rev.iloc[0]
        top2_i = ind_rev.index[1] if len(ind_rev) > 1 else top_i
        share = (top_v / total_rev * 100) if total_rev > 0 else 0
        return {
            "title": "Which industries generate the most revenue?",
            "group": "INDUSTRY DYNAMICS",
            "kpi1_label": "Largest Volume Sector", "kpi1_val": top_i,
            "kpi2_label": "Sector Turnover", "kpi2_val": f"${top_v:,.1f}B",
            "kpi3_label": "Gross Pool Share", "kpi3_val": f"{share:.1f}%",
            "kpi4_label": "Runner-Up Sector", "kpi4_val": f"{top2_i} (${ind_rev.iloc[1]:,.1f}B)",
            "answer": f"The **{top_i}** sector captures the largest single turnover pool with **${top_v:,.1f}B** (**{share:.1f}%** of total revenue), driven by massive global consumer consumption and essential energy infrastructure.",
            "fig": analysis.chart_revenue_by_industry(df, dark_mode=dark_mode),
            "table": ind_bench[["Industry", "Company_Count", "Total_Revenue", "Avg_Revenue"]].rename(columns={"Company_Count": "Firms", "Total_Revenue": "Total Rev ($B)", "Avg_Revenue": "Mean Rev ($B)"}),
            "takeaways": [
                "Essential economic sectors (Retail/Consumer and Energy) drive the baseline volume of global corporate transactions.",
                "High sector revenue does not guarantee high aggregate net income—margin structures vary drastically.",
                "Sector diversification within the Global 50 ensures broad macroeconomic resilience."
            ]
        }
    elif q_key == "Industry Profitability":
        ind_prof = clean_profit_df.groupby("Industry")["Profit Margin (%)"].mean().sort_values(ascending=False)
        top_i = ind_prof.index[0] if not ind_prof.empty else "N/A"
        top_m = ind_prof.iloc[0] if not ind_prof.empty else 0
        return {
            "title": "Which industries are the strongest in profitability?",
            "group": "INDUSTRY DYNAMICS",
            "kpi1_label": "Highest Margin Sector", "kpi1_val": top_i,
            "kpi2_label": "Average Sector Margin", "kpi2_val": f"{top_m:.2f}%",
            "kpi3_label": "Spread vs Baseline", "kpi3_val": f"+{(top_m - clean_profit_df['Profit Margin (%)'].mean()):.1f}% above mean",
            "kpi4_label": "Lowest Margin Sector", "kpi4_val": f"{ind_prof.index[-1]} ({ind_prof.iloc[-1]:.1f}%)" if not ind_prof.empty else "N/A",
            "answer": f"The **{top_i}** sector displays paramount profitability, averaging **{top_m:.2f}%** in net profit margins. In contrast, commodity and volume-driven sectors face high input costs that compress average margins below 4%.",
            "fig": analysis.chart_margin_by_industry(df, dark_mode=dark_mode),
            "table": ind_bench[["Industry", "Company_Count", "Avg_Margin", "Total_Profit"]].rename(columns={"Company_Count": "Firms", "Avg_Margin": "Mean Margin (%)", "Total_Profit": "Profit ($B)"}),
            "takeaways": [
                "Technology platforms and asset-light digital ecosystems outpace asset-heavy manufacturing in profit retention.",
                "Regulatory moats, patents, and software distribution economics explain cross-sector margin divergence.",
                "Investors demanding high ROIC gravitate toward semiconductor and technology leaders."
            ]
        }
    elif q_key == "Revenue per Employee":
        sorted_df = df.sort_values(by="Revenue per Employee ($)", ascending=False)
        top1 = sorted_df.iloc[0]
        avg_w = df["Revenue per Employee ($)"].mean()
        return {
            "title": "Which companies have the highest revenue per employee?",
            "group": "WORKFORCE EFFICIENCY",
            "kpi1_label": "Labor Efficiency Leader", "kpi1_val": top1["Company"],
            "kpi2_label": "Revenue / Worker", "kpi2_val": f"${top1['Revenue per Employee ($)']:,.0f}",
            "kpi3_label": "Benchmark Mean", "kpi3_val": f"${avg_w:,.0f} / Worker",
            "kpi4_label": "Efficiency Multiplier", "kpi4_val": f"{(top1['Revenue per Employee ($)'] / avg_w):.1f}x Universe Avg",
            "answer": f"**{top1['Company']}** demonstrates peak labor efficiency, generating **${top1['Revenue per Employee ($)']:,.0f}** for every individual employed. This productivity is **{(top1['Revenue per Employee ($)'] / avg_w):.1f}x** higher than the global cohort average.",
            "fig": analysis.chart_workforce_productivity(df, dark_mode=dark_mode),
            "table": sorted_df[["Rank", "Company", "Industry", "Employees", "Revenue per Employee ($)", "Revenue (USD)"]].head(10),
            "takeaways": [
                "Energy refineries, automated trading houses, and asset-backed logistics generate millions in revenue per employee.",
                "Traditional retail giants maintain massive headcount (>1M employees), limiting revenue per worker below $300k.",
                "Automation and digital infrastructure are the primary catalysts of 21st-century workforce productivity."
            ]
        }
    elif q_key == "Workforce vs Revenue":
        corr = df[["Revenue (USD)", "Employees"]].dropna().corr().iloc[0, 1]
        top_emp = df.sort_values(by="Employees", ascending=False).iloc[0]
        return {
            "title": "Does workforce size relate to revenue and profitability?",
            "group": "WORKFORCE EFFICIENCY",
            "kpi1_label": "Largest Employer", "kpi1_val": f"{top_emp['Company']} ({top_emp['Employees']:,})",
            "kpi2_label": "Workforce-Revenue Corr", "kpi2_val": f"r = {corr:.2f}",
            "kpi3_label": "Correlation Strength", "kpi3_val": "Moderate Positive" if corr > 0.4 else "Weak / Non-linear",
            "kpi4_label": "Leverage Model", "kpi4_val": "Capital-driven > Labor-driven",
            "answer": f"Workforce scaling reveals a correlation of **r = {corr:.2f}** with revenue. While massive labor forces drive raw top-line volume (**{top_emp['Company']}** employs **{top_emp['Employees']:,}** workers), net profit generation is decoupled from headcount, driven by capital and IP leverage.",
            "fig": analysis.chart_capital_efficiency_quadrant(df, dark_mode=dark_mode),
            "table": df.sort_values(by="Employees", ascending=False)[["Rank", "Company", "Employees", "Revenue (USD)", "Profit (USD)", "Revenue per Employee ($)"]].head(10),
            "takeaways": [
                "Expanding workforce headcount yields diminishing marginal net income beyond certain scale thresholds.",
                "The Quadrant visualizer isolates firms into 4 archetypes: Scaled Giants, Efficiency Champions, Lean Disruptors, and Volume Aggregators.",
                "Elite corporate valuations prioritize capital leverage over headcount expansion."
            ]
        }
    else:  # Revenue Concentration
        pareto = analysis.get_revenue_concentration_stats(df)
        return {
            "title": "How concentrated is global corporate revenue?",
            "group": "MARKET CONCENTRATION",
            "kpi1_label": "Top 5 Revenue Share", "kpi1_val": f"{pareto['top5_share']:.1f}%",
            "kpi2_label": "Top 10 Revenue Share", "kpi2_val": f"{pareto['top10_share']:.1f}%",
            "kpi3_label": "50% Revenue Concentration", "kpi3_val": f"Just {pareto['half_count']} Companies",
            "kpi4_label": "Total Revenue Pool", "kpi4_val": f"${total_rev:,.1f}B",
            "answer": f"Global enterprise revenue exhibits pronounced oligopoly concentration: The Top 5 firms control **{pareto['top5_share']:.1f}%**, and the Top 10 command **{pareto['top10_share']:.1f}%**. Exactly half of all revenue generated by the 50 largest corporations is captured by just **{pareto['half_count']} entities**.",
            "fig": analysis.chart_pareto_revenue_concentration(df, dark_mode=dark_mode),
            "table": df.sort_values(by="Revenue (USD)", ascending=False)[["Rank", "Company", "Country", "Revenue (USD)"]].head(pareto['half_count']),
            "takeaways": [
                "Pareto 80/20 dynamics apply strongly at the macro enterprise level.",
                "Mega-cap enterprises enjoy significant network effects and cost-of-capital advantages over smaller competitors.",
                "Supply chain concentration heightens systemic vulnerability to single-firm operational disruptions."
            ]
        }


# =============================================================================
# SECTION 3: BUSINESS QUESTIONS HUB (DEDICATED FULL SECTION)
# =============================================================================
def render_business_questions_section(df: pd.DataFrame, dark_mode: bool = False) -> None:
    """
    Dedicated Business Questions Section:
    An exhaustive, dedicated strategic inquiry hub featuring question-specific domain filters,
    keyword searching, deep-dive visualizers, supporting data tables, and an Executive Matrix.
    """
    render_analytical_focus_banner(active_page="Business Questions")

    if df.empty:
        render_empty_state()
        return

    render_section_header(
        "Strategic Business Questions & Empirical Answers",
        "Dedicated executive analytical hub answering the 10 fundamental business inquiries of the Global 50 cohort",
        label="BUSINESS QUESTIONS HUB",
    )

    # Dedicated Filter Controls for Questions Only
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<div class="filter-panel-title">Business Questions Filter & Explorer Controls</div>', unsafe_allow_html=True)

    q_c1, q_c2, q_c3 = st.columns([1.5, 1.3, 1.2])

    with q_c1:
        domain_options = [
            "All Domains (10 Questions)",
            "💼 Financial Performance (3)",
            "🌐 Geographic Scale (2)",
            "🏭 Industry Dynamics (2)",
            "⚡ Workforce Efficiency (2)",
            "🎯 Revenue Concentration (1)",
        ]
        chosen_domain = st.selectbox(
            "Filter by Domain",
            options=domain_options,
            index=0,
            key="bq_section_domain_filter",
        )

    with q_c2:
        search_kw = st.text_input(
            "Search Questions",
            placeholder="Search questions by keyword (e.g. margin, profit, worker)...",
            key="bq_section_search_kw",
        )

    with q_c3:
        bq_view_mode = st.radio(
            "Analysis Format",
            options=["🎯 Deep Dive Analysis", "📋 Executive Matrix (All)"],
            horizontal=True,
            key="bq_section_view_mode",
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Filter matching questions
    domain_map = {
        "💼 Financial Performance (3)": "FINANCIAL",
        "🌐 Geographic Scale (2)": "GEOGRAPHIC",
        "🏭 Industry Dynamics (2)": "INDUSTRY",
        "⚡ Workforce Efficiency (2)": "EFFICIENCY",
        "🎯 Revenue Concentration (1)": "CONCENTRATION",
    }

    matching_keys = []
    for q_key, q_info in BUSINESS_QUESTIONS_MAP.items():
        if chosen_domain != "All Domains (10 Questions)":
            expected_grp = domain_map.get(chosen_domain)
            if q_info["group"] != expected_grp:
                continue
        if search_kw.strip():
            kw = search_kw.strip().lower()
            if kw not in q_key.lower() and kw not in q_info["question"].lower() and kw not in q_info["group"].lower():
                continue
        matching_keys.append(q_key)

    if not matching_keys:
        st.markdown(
            """
            <div class="empty-state-card">
                <div class="empty-state-title">No questions match your filter criteria</div>
                <div class="empty-state-desc">Try resetting the domain filter or clearing your search keywords.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # View Mode 1: Deep Dive Analysis
    if bq_view_mode == "🎯 Deep Dive Analysis":
        active_target = st.session_state.get("active_question_target")
        if active_target and active_target in matching_keys:
            st.session_state["bq_deep_dive_picker"] = active_target
        elif "bq_deep_dive_picker" not in st.session_state or st.session_state["bq_deep_dive_picker"] not in matching_keys:
            st.session_state["bq_deep_dive_picker"] = matching_keys[0]

        dd_c1, dd_c2 = st.columns([3, 1])
        with dd_c1:
            selected_q = st.selectbox(
                "Select Analytical Question to Explore",
                options=matching_keys,
                key="bq_deep_dive_picker",
            )
        with dd_c2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<span class='filter-badge'>Question {matching_keys.index(selected_q) + 1} of {len(matching_keys)} Matching</span>", unsafe_allow_html=True)

        st.session_state["active_question_target"] = selected_q
        q_details = get_question_details(df, selected_q, dark_mode=dark_mode)

        # Question Title Banner Card
        st.markdown(
            f"""
            <div class="content-card" style="border-left: 4px solid var(--accent-blue); padding: 18px 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-blue);">{q_details['group']}</span>
                    <span class="kpi-tag">Empirical Analytical Inquiry</span>
                </div>
                <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-primary); margin: 0 0 8px 0; line-height: 1.3;">
                    {q_details['title']}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4 Standardized Analytical Scorecards
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(
                f"""
                <div class="kpi-card" style="min-height: 110px;">
                    <div class="kpi-label">{q_details['kpi1_label']}</div>
                    <div class="kpi-value" style="font-size: 1.45rem;">{q_details['kpi1_val']}</div>
                    <div class="kpi-meta"><span class="kpi-tag">Leader</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc2:
            st.markdown(
                f"""
                <div class="kpi-card" style="min-height: 110px;">
                    <div class="kpi-label">{q_details['kpi2_label']}</div>
                    <div class="kpi-value" style="font-size: 1.45rem; color: var(--accent-emerald);">{q_details['kpi2_val']}</div>
                    <div class="kpi-meta"><span class="kpi-tag">Metric</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc3:
            st.markdown(
                f"""
                <div class="kpi-card" style="min-height: 110px;">
                    <div class="kpi-label">{q_details['kpi3_label']}</div>
                    <div class="kpi-value" style="font-size: 1.45rem; color: var(--accent-blue);">{q_details['kpi3_val']}</div>
                    <div class="kpi-meta"><span class="kpi-tag">Scale</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc4:
            st.markdown(
                f"""
                <div class="kpi-card" style="min-height: 110px;">
                    <div class="kpi-label">{q_details['kpi4_label']}</div>
                    <div class="kpi-value" style="font-size: 1.1rem; margin-top: 8px;">{q_details['kpi4_val']}</div>
                    <div class="kpi-meta"><span class="kpi-tag">Benchmark</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Dynamic Calculated Narrative Answer Box
        st.markdown(
            f"""
            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px 20px; margin: 14px 0; box-shadow: var(--shadow-card);">
                <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: var(--accent-blue); margin-bottom: 6px;">DYNAMIC EXECUTIVE ANSWER</div>
                <div style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.55;">
                    {q_details['answer']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Interactive Plotly Chart & Supporting Data Table
        ch_c1, ch_c2 = st.columns([1.5, 1.1])
        with ch_c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(q_details['fig'], config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        with ch_c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Supporting Empirical Records</div>', unsafe_allow_html=True)
            tbl_df = q_details['table']
            format_dict = {}
            for col in tbl_df.columns:
                if "Revenue" in col or "Total Rev" in col or "Mean Rev" in col:
                    format_dict[col] = "${:,.1f}B"
                elif "Profit" in col and "Margin" not in col and "Employee" not in col:
                    format_dict[col] = lambda x: f"${x:,.1f}B" if pd.notna(x) else "N/A"
                elif "Margin" in col:
                    format_dict[col] = lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
                elif "Employee" in col or "Worker" in col:
                    format_dict[col] = lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
                elif "Employees" in col or "Firms" in col:
                    format_dict[col] = "{:,}"

            st.dataframe(tbl_df.style.format(format_dict), hide_index=True, height=360)
            st.markdown('</div>', unsafe_allow_html=True)

        # Strategic Business Implications
        st.markdown(
            f"""
            <div class="content-card" style="padding: 18px 22px;">
                <div class="card-title" style="color: var(--accent-blue);">Executive Takeaways & Strategic Implications</div>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: var(--text-primary); line-height: 1.6;">
                    <li><b>Market Structure:</b> {q_details['takeaways'][0]}</li>
                    <li><b>Performance Divergence:</b> {q_details['takeaways'][1]}</li>
                    <li><b>Managerial Action:</b> {q_details['takeaways'][2]}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # View Mode 2: Executive Question Matrix
    else:
        st.markdown(
            f"<div style='margin-bottom: 12px; font-size: 0.82rem; color: var(--text-secondary);'>Displaying <b>{len(matching_keys)}</b> strategic inquiries matching current criteria:</div>",
            unsafe_allow_html=True,
        )
        matrix_cols = st.columns(2)
        for i, q_key in enumerate(matching_keys):
            q_info = BUSINESS_QUESTIONS_MAP[q_key]
            q_det = get_question_details(df, q_key, dark_mode=dark_mode)
            with matrix_cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="question-card" style="margin-bottom: 10px;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span class="question-kicker">{q_info['group']}</span>
                                <span class="kpi-tag">{q_info['target_desc']}</span>
                            </div>
                            <div class="question-title">{q_info['question']}</div>
                        </div>
                        <div>
                            <div class="question-metric-row">
                                <span class="question-entity" title="{q_det['kpi1_val']}">{q_det['kpi1_val']}</span>
                                <span class="question-metric">{q_det['kpi2_val']}</span>
                            </div>
                            <div class="question-answer">{q_det['answer']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"🔍 Explore Deep Dive: {q_key}", key=f"btn_matrix_dd_{q_key.replace(' ', '_')}", width="stretch"):
                    st.session_state["active_question_target"] = q_key
                    st.session_state["bq_section_view_mode"] = "🎯 Deep Dive Analysis"
                    st.rerun()


# =============================================================================
# SECTION 3: COMPANY EXPLORER (COMPANY 360)
# =============================================================================
def render_explorer_section(df_filtered: pd.DataFrame, df_full: pd.DataFrame, dark_mode: bool = False) -> None:
    """Render Company Explorer profile shell with Company 360 visual benchmark."""
    render_section_header("Enterprise 360 Profile & Sector Benchmarking", "Comprehensive financial profile, labor leverage, and peer benchmark positioning", label="COMPANY EXPLORER")

    company_options = sorted(df_full["Company"].unique().tolist())
    selected_comp = st.selectbox("Select Company for Deep-Dive Profile", options=company_options, index=0)

    if selected_comp:
        prof = analysis.get_company_profile(df_full, selected_comp)

        # Profile Header Card
        st.markdown(
            f"""
            <div class="content-card" style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.45rem; font-weight: 800; color: var(--text-primary);">{prof['Company']}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 3px;">
                            Headquarters: <b>{prof['Country']}</b> ({prof['ISO_Alpha3']}) | Sector: <b>{prof['Industry']}</b>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: var(--bg-subtle); border: 1px solid var(--border-color); color: var(--accent-blue); font-weight: 800; border-radius: 6px; padding: 6px 14px; font-size: 0.88rem;">
                            Global Revenue Rank #{prof['Rank']}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Scorecard Metrics
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Gross Revenue</div>
                    <div class="kpi-value">${prof['Revenue']:,.0f}B</div>
                    <div class="kpi-meta">Rank #{prof['Ranks']['Revenue']} of 50</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_c2:
            p_val = f"${prof['Profit']:,.0f}B" if prof['Profit'] is not None else "N/A"
            p_meta = f"Rank #{prof['Ranks']['Profit']}" if prof['Ranks']['Profit'] is not None else "Private Corporation"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Net Profit</div>
                    <div class="kpi-value">{p_val}</div>
                    <div class="kpi-meta">{p_meta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_c3:
            mar_val = f"{prof['Margin']:.1f}%" if prof['Margin'] is not None else "N/A"
            mar_meta = f"Rank #{prof['Ranks']['Margin']}" if prof['Ranks']['Margin'] is not None else "N/A"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Profit Margin</div>
                    <div class="kpi-value">{mar_val}</div>
                    <div class="kpi-meta">{mar_meta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_c4:
            emp_val = analysis.format_kpi_number(prof['Employees'])
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Workforce</div>
                    <div class="kpi-value">{emp_val}</div>
                    <div class="kpi-meta">Rank #{prof['Ranks']['Employees']} of 50</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

        # 2-Column: Company Profile Benchmark Visualization + Benchmark Comparison Table
        exp_c1, exp_c2 = st.columns([1.1, 1.2])
        with exp_c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.plotly_chart(analysis.chart_company_profile_benchmark(df_full, selected_comp, dark_mode=dark_mode))
            st.markdown('</div>', unsafe_allow_html=True)

        with exp_c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Comparative Positioning vs. Industry & Global Medians</div>', unsafe_allow_html=True)

            bench_df = pd.DataFrame(
                {
                    "Indicator": [
                        "Revenue (USD)",
                        "Net Profit (USD)",
                        "Profit Margin (%)",
                        "Total Workforce",
                        "Revenue per Employee",
                    ],
                    selected_comp: [
                        f"${prof['Revenue']:,.1f}B",
                        f"${prof['Profit']:,.1f}B" if prof["Profit"] is not None else "N/A",
                        f"{prof['Margin']:.2f}%" if prof["Margin"] is not None else "N/A",
                        f"{prof['Employees']:,}",
                        f"${prof['Rev_per_Emp']:,.0f}",
                    ],
                    f"Sector Avg ({prof['Industry']})": [
                        f"${prof['Industry_Avg']['Revenue']:,.1f}B",
                        f"${prof['Industry_Avg']['Profit']:,.1f}B" if pd.notna(prof["Industry_Avg"]["Profit"]) else "N/A",
                        f"{prof['Industry_Avg']['Margin']:.2f}%" if pd.notna(prof["Industry_Avg"]["Margin"]) else "N/A",
                        f"{int(prof['Industry_Avg']['Employees']):,}",
                        f"${(prof['Industry_Avg']['Revenue'] * 1e9 / prof['Industry_Avg']['Employees']):,.0f}"
                        if prof["Industry_Avg"]["Employees"] > 0
                        else "N/A",
                    ],
                    "Global 50 Median": [
                        f"${prof['Global_Median']['Revenue']:,.1f}B",
                        f"${prof['Global_Median']['Profit']:,.1f}B",
                        f"{prof['Global_Median']['Margin']:.2f}%",
                        f"{int(prof['Global_Median']['Employees']):,}",
                        f"${(prof['Global_Median']['Revenue'] * 1e9 / prof['Global_Median']['Employees']):,.0f}"
                        if prof["Global_Median"]["Employees"] > 0
                        else "N/A",
                    ],
                }
            )

            st.dataframe(bench_df, hide_index=True, height=240)

            # Strategic Benchmark Positioning Callout
            st.markdown(
                f"""
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 0.78rem; color: var(--text-secondary);">
                    <b>Executive Summary:</b> <b>{prof['Company']}</b> operates at <b>{prof['Revenue'] / prof['Global_Median']['Revenue']:.1f}x</b> the Global 50 median revenue scale 
                    and captures a <b>Rank #{prof['Ranks']['Revenue']}</b> standing worldwide.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 4: COMPARE COMPANIES
# =============================================================================
def render_compare_section(df: pd.DataFrame, dark_mode: bool = False) -> None:
    """Render Head-to-Head Company Comparator."""
    render_section_header("Head-to-Head Enterprise Comparison", "Direct comparative analysis of scale, margin conversion, and workforce leverage", label="DIRECT COMPARATOR")

    all_comps = sorted(df["Company"].unique().tolist())
    cmp_c1, cmp_c2 = st.columns(2)

    with cmp_c1:
        comp_a = st.selectbox("Select First Enterprise", options=all_comps, index=0, key="cmp_select_a")
    with cmp_c2:
        default_b_idx = 1 if len(all_comps) > 1 else 0
        comp_b = st.selectbox("Select Second Enterprise", options=all_comps, index=default_b_idx, key="cmp_select_b")

    if comp_a and comp_b:
        if comp_a == comp_b:
            st.info("Select two different enterprises for side-by-side comparative benchmarking.")
            return

        c1_row = df[df["Company"] == comp_a].iloc[0]
        c2_row = df[df["Company"] == comp_b].iloc[0]

        st.markdown('<div class="content-card" style="margin-top: 8px;">', unsafe_allow_html=True)

        # Delta Indicator Metric Cards
        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        with d_c1:
            rev_diff = abs(c1_row["Revenue (USD)"] - c2_row["Revenue (USD)"])
            rev_lead = comp_a if c1_row["Revenue (USD)"] >= c2_row["Revenue (USD)"] else comp_b
            st.markdown(
                f"""
                <div class="cmp-metric-box">
                    <div class="cmp-metric-label">Revenue Leader</div>
                    <div class="cmp-metric-leader">{rev_lead}</div>
                    <div class="cmp-metric-diff">+${rev_diff:,.1f}B advantage</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with d_c2:
            p1 = c1_row["Profit (USD)"] if pd.notna(c1_row["Profit (USD)"]) else 0
            p2 = c2_row["Profit (USD)"] if pd.notna(c2_row["Profit (USD)"]) else 0
            prof_diff = abs(p1 - p2)
            prof_lead = comp_a if p1 >= p2 else comp_b
            st.markdown(
                f"""
                <div class="cmp-metric-box">
                    <div class="cmp-metric-label">Profit Leader</div>
                    <div class="cmp-metric-leader">{prof_lead}</div>
                    <div class="cmp-metric-diff">+${prof_diff:,.1f}B advantage</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with d_c3:
            m1 = c1_row["Profit Margin (%)"] if pd.notna(c1_row["Profit Margin (%)"]) else 0
            m2 = c2_row["Profit Margin (%)"] if pd.notna(c2_row["Profit Margin (%)"]) else 0
            m_diff = abs(m1 - m2)
            m_lead = comp_a if m1 >= m2 else comp_b
            st.markdown(
                f"""
                <div class="cmp-metric-box">
                    <div class="cmp-metric-label">Margin Leader</div>
                    <div class="cmp-metric-leader">{m_lead}</div>
                    <div class="cmp-metric-diff">+{m_diff:.1f}% percentage pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with d_c4:
            e_diff = abs(c1_row["Employees"] - c2_row["Employees"])
            e_lead = comp_a if c1_row["Employees"] >= c2_row["Employees"] else comp_b
            st.markdown(
                f"""
                <div class="cmp-metric-box">
                    <div class="cmp-metric-label">Workforce Scale</div>
                    <div class="cmp-metric-leader">{e_lead}</div>
                    <div class="cmp-metric-diff">+{e_diff:,} workers</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Single Meaningful Comparison Chart & Side-by-Side Table
        fig_cmp, table_cmp = analysis.compare_companies(df, comp_a, comp_b, dark_mode=dark_mode)
        st.plotly_chart(fig_cmp)
        st.dataframe(table_cmp, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 5: DATA EXPLORER & PROFESSIONAL DATA EXPORT
# =============================================================================
def render_data_section(df: pd.DataFrame, dark_mode: bool = False) -> None:
    """Render Data view with formatted repository and professional Excel/CSV export controls."""
    render_section_header("Tabular Repository & Professional Data Export", "Interactive tabular records, descriptive distribution statistics, and full multi-sheet Excel export", label="DATASET REPOSITORY")

    if df.empty:
        render_empty_state()
        return

    # -------------------------------------------------------------------------
    # 1. DEDICATED DATA EXPORT CONTROL CARD
    # -------------------------------------------------------------------------
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">DATA EXPORT</div>', unsafe_allow_html=True)

    # Summarize active filters for document provenance
    active_filters_desc = []
    if st.session_state.get("input_search"):
        active_filters_desc.append(f"Search: '{st.session_state['input_search']}'")
    if st.session_state.get("input_countries"):
        active_filters_desc.append(f"Countries: {', '.join(st.session_state['input_countries'])}")
    if st.session_state.get("input_industries"):
        active_filters_desc.append(f"Industries: {', '.join(st.session_state['input_industries'])}")
    if st.session_state.get("input_revenue"):
        active_filters_desc.append(f"Revenue: ${st.session_state['input_revenue'][0]:.0f}B - ${st.session_state['input_revenue'][1]:.0f}B")

    filters_summary = " · ".join(active_filters_desc) if active_filters_desc else "All Companies (Full Global 50 Universe)"

    st.markdown(
        f"""
        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.45;">
            Export the current filtered dataset with formatted tables, auto-filters, conditional data bars, and executive benchmarks.
            <div style="margin-top: 6px; font-size: 0.82rem; color: var(--text-primary);">
                <b>Current Selection:</b> Showing <b>{len(df)}</b> of <b>{len(df_raw)}</b> enterprises ({len(df)/len(df_raw)*100:.0f}% of universe)
                &bull; <i>{filters_summary}</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dynamic File Names
    excel_filename = analysis.get_export_filename(
        countries=st.session_state.get("input_countries"),
        industries=st.session_state.get("input_industries"),
        search=st.session_state.get("input_search"),
        ext="xlsx",
    )
    csv_filename = analysis.get_export_filename(
        countries=st.session_state.get("input_countries"),
        industries=st.session_state.get("input_industries"),
        search=st.session_state.get("input_search"),
        ext="csv",
    )

    # Generate Professional Excel Workbook
    excel_buf = analysis.generate_excel_export(df, active_filters_desc=filters_summary)

    # Generate CSV Buffer
    req_cols = [
        "Rank", "Company", "Country", "Industry",
        "Revenue (USD)", "Profit (USD)", "Employees",
        "Profit Margin (%)", "Revenue per Employee ($)",
    ]
    csv_buf = io.StringIO()
    df[req_cols].to_csv(csv_buf, index=False)

    exp_c1, exp_c2, exp_c3 = st.columns([1.6, 1.4, 2.0])
    with exp_c1:
        st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_buf.getvalue(),
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            width="stretch",
            help="Primary professional export featuring 4 formatted sheets, auto-filters, freeze panes, data bars, and native Excel charts.",
        )

    with exp_c2:
        st.download_button(
            label="📄 Download CSV",
            data=csv_buf.getvalue(),
            file_name=csv_filename,
            mime="text/csv",
            width="stretch",
            help="Raw comma-separated tabular values for lightweight data ingestion.",
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. TABULAR RECORDS GRID
    # -------------------------------------------------------------------------
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Tabular Records</div>', unsafe_allow_html=True)

    display_df = df[req_cols].copy()

    # Clean formatted DataFrame without index
    st.dataframe(
        display_df.style.format(
            {
                "Revenue (USD)": "${:,.1f}B",
                "Profit (USD)": lambda x: f"${x:,.1f}B" if pd.notna(x) else "N/A (Private)",
                "Profit Margin (%)": lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A",
                "Employees": "{:,}",
                "Revenue per Employee ($)": "${:,.0f}",
            }
        ),
        hide_index=True,
        height=380,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. PARAMETRIC DISTRIBUTION STATISTICS
    # -------------------------------------------------------------------------
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Parametric Distribution Statistics</div>', unsafe_allow_html=True)
    num_cols = ["Revenue (USD)", "Profit (USD)", "Profit Margin (%)", "Employees", "Revenue per Employee ($)"]
    desc = df[num_cols].describe().T
    desc = desc.assign(
        median=df[num_cols].median(),
        skew=df[num_cols].skew(),
    )
    st.dataframe(
        desc[["count", "mean", "std", "min", "25%", "median", "75%", "max", "skew"]].style.format("{:,.2f}"),
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION CONTROLLER
# =============================================================================
def main():
    dark_mode = st.session_state["dark_mode"]

    # 1. Render Sidebar & Navigation (includes Business Questions)
    nav_selection = render_sidebar(total_records=len(df_raw), dark_mode=dark_mode)

    # 2. Extract active filter criteria for header & KPIs
    s_query = st.session_state.get("input_search", "")
    s_countries = st.session_state.get("input_countries", [])
    s_industries = st.session_state.get("input_industries", [])
    s_rev = st.session_state.get("input_revenue", None)
    min_rev = s_rev[0] if s_rev else None
    max_rev = s_rev[1] if s_rev else None

    df_filtered = analysis.filter_dataframe(
        df_raw,
        search_query=s_query,
        countries=s_countries,
        industries=s_industries,
        min_revenue=min_rev,
        max_revenue=max_rev,
    )

    # 3. Render Executive Hero Header at Top
    render_hero_header(df_filtered=df_filtered, df_full=df_raw, dark_mode=dark_mode)

    # 4. Render 4 Standardized KPI Cards
    kpis = analysis.get_kpis(df_filtered, df_raw)
    kpis["highest_revenue_formatted"] = analysis.format_kpi_number(kpis["highest_revenue_val"], is_currency=True, is_billions_input=True)
    kpis["highest_profit_formatted"] = analysis.format_kpi_number(kpis["highest_profit_val"], is_currency=True, is_billions_input=True)
    kpis["largest_employer_formatted"] = analysis.format_kpi_number(kpis["largest_employer_count"])
    render_kpi_cards(kpis, dark_mode=dark_mode)

    # 5. Render Unified Global Filters
    df_filtered = render_filters(df_raw)

    # 6. Route Navigation Views
    if nav_selection == "Overview":
        render_overview_section(df_filtered, dark_mode=dark_mode)
    elif nav_selection == "Analytics":
        render_analytics_section(df_filtered, dark_mode=dark_mode)
    elif nav_selection == "Business Questions":
        render_business_questions_section(df_filtered, dark_mode=dark_mode)
    elif nav_selection == "Company Explorer":
        render_explorer_section(df_filtered, df_raw, dark_mode=dark_mode)
    elif nav_selection == "Compare":
        render_compare_section(df_raw, dark_mode=dark_mode)
    elif nav_selection == "Data":
        render_data_section(df_filtered, dark_mode=dark_mode)

    # 7. Render Subdued Corporate Footer
    render_footer()


if __name__ == "__main__":
    main()
