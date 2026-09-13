"""
analysis.py
===========
Executive Analytics Engine & Data Visualization Suite for Fortune Global 50 Intelligence.
Provides data filtering, KPI synthesis, distribution statistics, industry/country benchmarking,
financial ratio analysis, and theme-adaptive Plotly visualizations (Light & Dark modes).
"""

from __future__ import annotations
import datetime
import io
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================================
# THEME CONFIGURATIONS (LIGHT & DARK CORPORATE DESIGN SYSTEMS)
# =========================================================================

THEME_LIGHT = {
    "name": "light",
    "bg_page": "#F6F8FB",
    "bg_card": "#FFFFFF",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "border": "#E2E8F0",
    "grid": "#E2E8F0",
    "blue_primary": "#1E3A8A",
    "blue_accent": "#2563EB",
    "emerald": "#10B981",
    "amber": "#F59E0B",
    "rose": "#EF4444",
    "indigo": "#4F46E5",
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "colorway": ["#1E3A8A", "#2563EB", "#0284C7", "#0D9488", "#10B981", "#F59E0B", "#6366F1", "#EC4899"],
    "hover_bg": "#FFFFFF",
    "hover_border": "#CBD5E1",
    "geo_land": "#F1F5F9",
    "geo_ocean": "#F8FAFC",
    "geo_coastline": "#CBD5E1",
}

THEME_DARK = {
    "name": "dark",
    "bg_page": "#0B1120",
    "bg_card": "#151E2E",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border": "#263244",
    "grid": "#1E293B",
    "blue_primary": "#3B82F6",
    "blue_accent": "#60A5FA",
    "emerald": "#10B981",
    "amber": "#F59E0B",
    "rose": "#EF4444",
    "indigo": "#818CF8",
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "colorway": ["#3B82F6", "#60A5FA", "#38BDF8", "#2DD4BF", "#34D399", "#FBBF24", "#A5B4FC", "#F472B6"],
    "hover_bg": "#151E2E",
    "hover_border": "#263244",
    "geo_land": "#1E293B",
    "geo_ocean": "#0B1120",
    "geo_coastline": "#334155",
}

# Legacy default alias for backward compatibility
THEME = THEME_LIGHT


def get_theme(dark_mode: bool = False) -> Dict[str, Any]:
    """Return the executive design palette corresponding to the active theme mode."""
    return THEME_DARK if dark_mode else THEME_LIGHT


def apply_executive_layout(
    fig: go.Figure,
    title_text: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
    height: int = 350,
    show_yaxis_grid: bool = True,
    show_xaxis_grid: bool = False,
    dark_mode: bool = False,
) -> go.Figure:
    """
    Applies consistent corporate styling, typography, responsive paddings,
    and light/dark theme attributes to a Plotly figure.
    """
    theme = get_theme(dark_mode)

    fig.update_layout(
        template="plotly_white" if not dark_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=theme["colorway"],
        font=dict(
            family=theme["font_family"],
            size=12,
            color=theme["text_primary"],
        ),
        title=dict(
            text=f"<b>{title_text}</b>" if title_text else "",
            font=dict(
                size=14,
                color=theme["text_primary"],
                family=theme["font_family"],
            ),
            x=0.01,
            y=0.96,
            xanchor="left",
            yanchor="top",
        ) if title_text else None,
        margin=dict(l=10, r=20, t=42 if title_text else 20, b=30),
        height=height,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=theme["hover_bg"],
            bordercolor=theme["hover_border"],
            font=dict(
                family=theme["font_family"],
                size=12,
                color=theme["text_primary"],
            ),
        ),
        xaxis=dict(
            title=dict(
                text=xaxis_title,
                font=dict(size=11, color=theme["text_secondary"]),
            ) if xaxis_title else None,
            tickfont=dict(size=10, color=theme["text_secondary"]),
            showgrid=show_xaxis_grid,
            gridcolor=theme["grid"],
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(
                text=yaxis_title,
                font=dict(size=11, color=theme["text_secondary"]),
            ) if yaxis_title else None,
            tickfont=dict(size=10, color=theme["text_secondary"]),
            showgrid=show_yaxis_grid,
            gridcolor=theme["grid"],
            zeroline=False,
        ),
    )
    return fig


# =========================================================================
# KPI & NUMBER FORMATTING
# =========================================================================

def format_kpi_number(
    val: float | int | None,
    is_currency: bool = False,
    is_billions_input: bool = False,
) -> str:
    """Format large numbers into executive notation ($T, $B, $M, or M, k)."""
    if val is None or pd.isna(val):
        return "N/A"

    v = float(val)
    prefix = "$" if is_currency else ""

    if is_billions_input:
        if abs(v) >= 1000.0:
            return f"{prefix}{v / 1000.0:,.2f}T"
        return f"{prefix}{v:,.1f}B" if v % 1 != 0 else f"{prefix}{v:,.0f}B"

    # Raw value scaling
    abs_v = abs(v)
    if abs_v >= 1e12:
        return f"{prefix}{v / 1e12:,.2f}T"
    if abs_v >= 1e9:
        return f"{prefix}{v / 1e9:,.1f}B"
    if abs_v >= 1e6:
        return f"{prefix}{v / 1e6:,.1f}M"
    if abs_v >= 1e3:
        return f"{prefix}{v / 1e3:,.1f}k"
    return f"{prefix}{v:,.0f}"


# =========================================================================
# DATA FILTERING & KPI SYNTHESIS
# =========================================================================

def filter_dataframe(
    df: pd.DataFrame,
    search_query: str = "",
    countries: List[str] | None = None,
    industries: List[str] | None = None,
    min_revenue: float | None = None,
    max_revenue: float | None = None,
) -> pd.DataFrame:
    """Filter master dataset by company search, countries, industries, and revenue bounds."""
    if df.empty:
        return df.copy()

    filtered = df.copy()

    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[filtered["Company"].astype(str).str.lower().str.contains(q, regex=False)]

    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]

    if industries:
        filtered = filtered[filtered["Industry"].isin(industries)]

    if min_revenue is not None and pd.notna(min_revenue):
        filtered = filtered[filtered["Revenue (USD)"] >= float(min_revenue)]

    if max_revenue is not None and pd.notna(max_revenue):
        filtered = filtered[filtered["Revenue (USD)"] <= float(max_revenue)]

    return filtered


def get_kpis(df: pd.DataFrame, full_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate core executive KPIs with rank context and delta references."""
    if df.empty:
        return {
            "total_companies": 0,
            "total_share_pct": 0.0,
            "total_revenue_b": 0.0,
            "avg_revenue_b": 0.0,
            "total_profit_b": 0.0,
            "avg_profit_b": 0.0,
            "total_employees": 0,
            "highest_revenue_company": "N/A",
            "highest_revenue_val": 0.0,
            "highest_revenue_rank": None,
            "highest_profit_company": "N/A",
            "highest_profit_val": 0.0,
            "highest_profit_rank": None,
            "largest_employer_company": "N/A",
            "largest_employer_count": 0,
            "largest_employer_rank": None,
        }

    total_companies = len(df)
    full_count = len(full_df) if not full_df.empty else total_companies
    share_pct = (total_companies / full_count) * 100.0 if full_count > 0 else 100.0

    total_rev = float(df["Revenue (USD)"].sum())
    avg_rev = float(df["Revenue (USD)"].mean())

    clean_profit = df["Profit (USD)"].dropna()
    total_prof = float(clean_profit.sum()) if not clean_profit.empty else 0.0
    avg_prof = float(clean_profit.mean()) if not clean_profit.empty else 0.0

    total_emp = int(df["Employees"].sum())

    # Top by Revenue
    top_rev_row = df.sort_values(by="Revenue (USD)", ascending=False).iloc[0]
    top_rev_comp = top_rev_row["Company"]
    top_rev_val = float(top_rev_row["Revenue (USD)"])
    top_rev_rank = int(top_rev_row["Rank"])

    # Top by Profit
    if not clean_profit.empty:
        top_prof_row = df.loc[clean_profit.idxmax()]
        top_prof_comp = top_prof_row["Company"]
        top_prof_val = float(top_prof_row["Profit (USD)"])
        top_prof_rank = int(top_prof_row["Rank"])
    else:
        top_prof_comp = "N/A"
        top_prof_val = 0.0
        top_prof_rank = None

    # Top by Employees
    top_emp_row = df.sort_values(by="Employees", ascending=False).iloc[0]
    top_emp_comp = top_emp_row["Company"]
    top_emp_val = int(top_emp_row["Employees"])
    top_emp_rank = int(top_emp_row["Rank"])

    return {
        "total_companies": total_companies,
        "total_share_pct": round(share_pct, 1),
        "total_revenue_b": total_rev,
        "avg_revenue_b": avg_rev,
        "total_profit_b": total_prof,
        "avg_profit_b": avg_prof,
        "total_employees": total_emp,
        "highest_revenue_company": top_rev_comp,
        "highest_revenue_val": top_rev_val,
        "highest_revenue_rank": top_rev_rank,
        "highest_profit_company": top_prof_comp,
        "highest_profit_val": top_prof_val,
        "highest_profit_rank": top_prof_rank,
        "largest_employer_company": top_emp_comp,
        "largest_employer_count": top_emp_val,
        "largest_employer_rank": top_emp_rank,
    }


# =========================================================================
# HERO MINI VISUALIZATION (EXECUTIVE BENCHMARK SPARK-STRIP)
# =========================================================================

def chart_header_mini_distribution(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Subtle, compact corporate revenue pool visualization for the executive hero header.
    Shows the Top 5 revenue sectors and their sovereign revenue pool contribution.
    """
    theme = get_theme(dark_mode)

    if df.empty or "Revenue (USD)" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No Benchmark Data Available",
            showarrow=False,
            font=dict(color=theme["text_muted"], size=10),
        )
        return apply_executive_layout(fig, height=110, show_yaxis_grid=False, dark_mode=dark_mode)

    # Aggregate by Top 4 Industries + Other
    ind_rev = df.groupby("Industry")["Revenue (USD)"].sum().sort_values(ascending=False)
    top_inds = ind_rev.head(4)
    other_rev = ind_rev.iloc[4:].sum() if len(ind_rev) > 4 else 0.0

    labels = list(top_inds.index) + (["Other Sectors"] if other_rev > 0 else [])
    values = list(top_inds.values) + ([other_rev] if other_rev > 0 else [])
    total_rev = sum(values)

    # Format shortened names for ultra-compact executive aesthetic
    short_labels = [
        l.replace("Information technology", "Tech")
        .replace("Oil and gas", "Energy")
        .replace("Consumer electronics", "Electronics")
        .replace("Automotive", "Auto")
        .replace("Financial services", "Finance")
        .replace("Other Sectors", "Other")
        for l in labels
    ]

    fig = go.Figure()

    # Create a horizontal stacked bar representing sovereign pool distribution
    colors = [theme["blue_primary"], theme["blue_accent"], theme["emerald"], theme["indigo"], theme["amber"]]
    for i, (full_name, short_name, val) in enumerate(zip(labels, short_labels, values)):
        pct = (val / total_rev * 100.0) if total_rev > 0 else 0
        fig.add_trace(
            go.Bar(
                y=["Revenue Pool"],
                x=[val],
                name=f"{full_name} (${val:,.0f}B · {pct:.0f}%)",
                orientation="h",
                marker=dict(color=colors[i % len(colors)], line=dict(color=theme["bg_card"], width=1.5)),
                hovertemplate=f"<b>{full_name}</b><br>Revenue: ${val:,.1f}B<br>Share of Pool: {pct:.1f}%<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="stack",
        height=95,
        margin=dict(l=5, r=5, t=10, b=22),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            visible=False,
            showgrid=False,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
        ),
        hoverlabel=dict(
            bgcolor=theme["hover_bg"],
            bordercolor=theme["hover_border"],
            font=dict(color=theme["text_primary"], size=11),
        ),
    )

    # Add micro annotations inside each segment for all visible sectors
    cum_x = 0.0
    for i, (full_name, short_name, val) in enumerate(zip(labels, short_labels, values)):
        mid_x = cum_x + (val / 2.0)
        pct = (val / total_rev * 100.0) if total_rev > 0 else 0

        # High-contrast font: dark text on bright amber/yellow, white on dark blue/purple/emerald
        bar_color = colors[i % len(colors)]
        if bar_color in [theme["amber"], "#F59E0B", "#FBBF24", "#FCD34D"]:
            font_color = "#0F172A"
        else:
            font_color = "#FFFFFF"

        # Adaptive text display based on segment width
        display_name = short_name
        if short_name == "Other" and pct >= 25:
            display_name = "Other Sectors"
        elif short_name == "Auto" and pct >= 15:
            display_name = "Automotive"

        if pct >= 8:
            display_text = f"<b>{display_name}</b> {pct:.0f}%"
        elif pct >= 5:
            display_text = f"<b>{pct:.0f}%</b>"
        else:
            display_text = ""

        if display_text:
            fig.add_annotation(
                x=mid_x,
                y=0,
                text=display_text,
                showarrow=False,
                font=dict(color=font_color, size=9.5, family=theme["font_family"]),
            )
        cum_x += val

    return fig


# =========================================================================
# OVERVIEW CHARTS
# =========================================================================

def chart_top10_revenue(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Horizontal Plotly bar chart: Top 10 companies by Revenue (USD)."""
    theme = get_theme(dark_mode)

    if df.empty or "Revenue (USD)" not in df.columns:
        fig = go.Figure()
        return apply_executive_layout(fig, "Top 10 Companies by Revenue (No Data)", height=360, dark_mode=dark_mode)

    top10 = df.nlargest(min(10, len(df)), "Revenue (USD)").sort_values(by="Revenue (USD)", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=top10["Revenue (USD)"],
            y=top10["Company"],
            orientation="h",
            marker=dict(
                color=top10["Revenue (USD)"],
                colorscale=[[0.0, theme["blue_accent"]], [1.0, theme["blue_primary"]]],
                showscale=False,
            ),
            text=[f"${x:,.0f}B" for x in top10["Revenue (USD)"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#FFFFFF", size=10, family=theme["font_family"]),
            customdata=np.stack((top10["Rank"], top10["Country"], top10["Industry"]), axis=-1),
            hovertemplate=(
                "<b>%{y}</b> (Rank #%{customdata[0]})<br>"
                "Revenue: $%{x:,.1f}B<br>"
                "Country: %{customdata[1]}<br>"
                "Industry: %{customdata[2]}<extra></extra>"
            ),
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Top 10 Companies by Revenue",
        xaxis_title="Revenue (USD Billions)",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


def chart_top10_profit(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Horizontal Plotly bar chart: Top 10 companies by Net Profit (USD)."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Profit (USD)"]).copy()
    if clean.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Top 10 Companies by Net Profit (No Data)", height=360, dark_mode=dark_mode)

    top10 = clean.nlargest(min(10, len(clean)), "Profit (USD)").sort_values(by="Profit (USD)", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=top10["Profit (USD)"],
            y=top10["Company"],
            orientation="h",
            marker=dict(
                color=top10["Profit (USD)"],
                colorscale=[[0.0, "#34D399"], [1.0, theme["emerald"]]],
                showscale=False,
            ),
            text=[f"${x:,.0f}B" for x in top10["Profit (USD)"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#FFFFFF", size=10, family=theme["font_family"]),
            customdata=np.stack((top10["Rank"], top10["Country"], top10["Profit Margin (%)"]), axis=-1),
            hovertemplate=(
                "<b>%{y}</b> (Rank #%{customdata[0]})<br>"
                "Net Profit: $%{x:,.1f}B<br>"
                "Margin: %{customdata[2]:.1f}%<br>"
                "Country: %{customdata[1]}<extra></extra>"
            ),
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Top 10 Companies by Net Profit",
        xaxis_title="Net Profit (USD Billions)",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


def chart_companies_by_country(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Distribution of Global 50 companies across Sovereign Nations."""
    theme = get_theme(dark_mode)

    if df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Companies by Country (No Data)", height=360, dark_mode=dark_mode)

    cnt = df["Country"].value_counts().sort_values(ascending=True)

    fig = go.Figure(
        go.Bar(
            x=cnt.values,
            y=cnt.index,
            orientation="h",
            marker=dict(color=theme["blue_accent"]),
            text=[f"{v} ({v / len(df) * 100:.0f}%)" for v in cnt.values],
            textposition="outside",
            textfont=dict(size=10, color=theme["text_secondary"]),
            hovertemplate="<b>%{y}</b><br>Companies: %{x}<extra></extra>",
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Company Representation by Country",
        xaxis_title="Number of Companies",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


def chart_companies_by_industry(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Distribution of Global 50 companies across Industry Sectors."""
    theme = get_theme(dark_mode)

    if df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Companies by Industry (No Data)", height=360, dark_mode=dark_mode)

    ind = df["Industry"].value_counts().sort_values(ascending=True)

    fig = go.Figure(
        go.Bar(
            x=ind.values,
            y=ind.index,
            orientation="h",
            marker=dict(color=theme["indigo"]),
            text=[f"{v} ({v / len(df) * 100:.0f}%)" for v in ind.values],
            textposition="outside",
            textfont=dict(size=10, color=theme["text_secondary"]),
            hovertemplate="<b>%{y}</b><br>Companies: %{x}<extra></extra>",
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Company Representation by Industry",
        xaxis_title="Number of Companies",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


def chart_revenue_by_country(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Aggregate Revenue concentration by Country."""
    theme = get_theme(dark_mode)

    if df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Aggregate Revenue by Country (No Data)", height=360, dark_mode=dark_mode)

    rev_cnt = df.groupby("Country")["Revenue (USD)"].sum().sort_values(ascending=True)
    total_rev = df["Revenue (USD)"].sum()

    fig = go.Figure(
        go.Bar(
            x=rev_cnt.values,
            y=rev_cnt.index,
            orientation="h",
            marker=dict(color=theme["blue_primary"]),
            text=[f"${v:,.0f}B ({v / total_rev * 100:.0f}%)" for v in rev_cnt.values],
            textposition="outside",
            textfont=dict(size=10, color=theme["text_secondary"]),
            hovertemplate="<b>%{y}</b><br>Aggregate Revenue: $%{x:,.1f}B<extra></extra>",
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Total Revenue by Country",
        xaxis_title="Aggregate Revenue (USD Billions)",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


chart_revenue_by_country_bar = chart_revenue_by_country


def chart_revenue_by_industry(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Aggregate Revenue concentration by Industry Sector."""
    theme = get_theme(dark_mode)

    if df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Aggregate Revenue by Industry (No Data)", height=360, dark_mode=dark_mode)

    rev_ind = df.groupby("Industry")["Revenue (USD)"].sum().sort_values(ascending=True)
    total_rev = df["Revenue (USD)"].sum()

    fig = go.Figure(
        go.Bar(
            x=rev_ind.values,
            y=rev_ind.index,
            orientation="h",
            marker=dict(color=theme["emerald"]),
            text=[f"${v:,.0f}B ({v / total_rev * 100:.0f}%)" for v in rev_ind.values],
            textposition="outside",
            textfont=dict(size=10, color=theme["text_secondary"]),
            hovertemplate="<b>%{y}</b><br>Aggregate Revenue: $%{x:,.1f}B<extra></extra>",
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Total Revenue by Industry",
        xaxis_title="Aggregate Revenue (USD Billions)",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


chart_revenue_by_industry_bar = chart_revenue_by_industry


# =========================================================================
# ANALYTICS PAGE CHARTS
# =========================================================================

def chart_revenue_vs_profit(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Scatter Plot: Revenue vs. Net Profit with workforce bubble scaling."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Profit (USD)", "Revenue (USD)"]).copy()
    if clean.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Revenue vs. Net Profit (No Data)", height=420, dark_mode=dark_mode)

    fig = px.scatter(
        clean,
        x="Revenue (USD)",
        y="Profit (USD)",
        size="Employees",
        color="Industry",
        hover_name="Company",
        custom_data=["Country", "Profit Margin (%)", "Employees"],
        size_max=36,
        color_discrete_sequence=theme["colorway"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Revenue: $%{x:,.1f}B<br>"
            "Profit: $%{y:,.1f}B<br>"
            "Margin: %{customdata[1]:.1f}%<br>"
            "Workforce: %{customdata[2]:,} employees<br>"
            "Country: %{customdata[0]}<extra></extra>"
        )
    )

    # Reference Zero Profit Line
    fig.add_hline(y=0, line_dash="dash", line_color=theme["border"], line_width=1)

    fig = apply_executive_layout(
        fig,
        title_text="Revenue vs. Net Profit (Bubble Size = Workforce)",
        xaxis_title="Revenue (USD Billions)",
        yaxis_title="Net Profit (USD Billions)",
        height=420,
        show_xaxis_grid=True,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=9, color=theme["text_secondary"]),
        )
    )
    return fig


def chart_workforce_productivity(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Bar Chart: Top 15 companies by Revenue generated per Employee."""
    theme = get_theme(dark_mode)

    if df.empty or "Revenue per Employee ($)" not in df.columns:
        fig = go.Figure()
        return apply_executive_layout(fig, "Workforce Productivity (No Data)", height=400, dark_mode=dark_mode)

    top15 = df.nlargest(min(15, len(df)), "Revenue per Employee ($)").sort_values(
        by="Revenue per Employee ($)", ascending=True
    )

    fig = go.Figure(
        go.Bar(
            x=top15["Revenue per Employee ($)"] / 1000.0,
            y=top15["Company"],
            orientation="h",
            marker=dict(
                color=top15["Revenue per Employee ($)"],
                colorscale=[[0.0, theme["blue_accent"]], [1.0, theme["emerald"]]],
                showscale=False,
            ),
            text=[f"${x:,.0f}k" for x in (top15["Revenue per Employee ($)"] / 1000.0)],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#FFFFFF", size=10, family=theme["font_family"]),
            customdata=np.stack((top15["Employees"], top15["Industry"], top15["Revenue (USD)"]), axis=-1),
            hovertemplate=(
                "<b>%{y}</b> (%{customdata[1]})<br>"
                "Revenue per Worker: $%{x:,.0f}k<br>"
                "Total Revenue: $%{customdata[2]:,.1f}B<br>"
                "Total Workforce: %{customdata[0]:,} employees<extra></extra>"
            ),
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Workforce Productivity: Revenue Generated per Employee",
        xaxis_title="Revenue per Employee ($ Thousands)",
        height=400,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


chart_revenue_per_employee = chart_workforce_productivity


def chart_revenue_by_country_map(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Choropleth World Map: Aggregate Corporate Revenue by Sovereign Jurisdiction."""
    theme = get_theme(dark_mode)

    if df.empty or "ISO_Alpha3" not in df.columns:
        fig = go.Figure()
        return apply_executive_layout(fig, "Global Geographic Footprint (No Data)", height=420, dark_mode=dark_mode)

    country_grp = df.groupby(["ISO_Alpha3", "Country"]).agg(
        Total_Revenue=("Revenue (USD)", "sum"),
        Company_Count=("Company", "count"),
        Avg_Profit=("Profit (USD)", "mean"),
    ).reset_index()

    colorscale = "Blues" if not dark_mode else "Tealgrn"

    fig = px.choropleth(
        country_grp,
        locations="ISO_Alpha3",
        color="Total_Revenue",
        hover_name="Country",
        color_continuous_scale=colorscale,
        custom_data=["Company_Count", "Total_Revenue"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Total Revenue Pool: $%{customdata[1]:,.1f}B<br>"
            "Global 50 Companies: %{customdata[0]}<extra></extra>"
        )
    )

    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor=theme["geo_coastline"],
        showland=True,
        landcolor=theme["geo_land"],
        showocean=True,
        oceancolor=theme["geo_ocean"],
        projection_type="natural earth",
    )

    fig = apply_executive_layout(
        fig,
        title_text="Global Sovereign Revenue Pool Distribution",
        height=420,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="Revenue ($B)", font=dict(size=10, color=theme["text_secondary"])),
            tickfont=dict(size=9, color=theme["text_secondary"]),
            len=0.7,
            thickness=14,
        )
    )
    return fig


def chart_margin_by_industry(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Box & Whisker Plot: Profit Margin (%) dispersion by Industry sector."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Profit Margin (%)"]).copy()
    if clean.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Profit Margin by Sector (No Data)", height=380, dark_mode=dark_mode)

    fig = px.box(
        clean,
        x="Industry",
        y="Profit Margin (%)",
        color="Industry",
        points="all",
        hover_name="Company",
        color_discrete_sequence=theme["colorway"],
    )

    fig.update_traces(
        jitter=0.3,
        pointpos=-1.8,
        marker=dict(size=6),
        hovertemplate="<b>%{hovertext}</b><br>Margin: %{y:.2f}%<extra></extra>",
    )

    fig = apply_executive_layout(
        fig,
        title_text="Profit Margin Spread by Industry Sector",
        xaxis_title="",
        yaxis_title="Net Profit Margin (%)",
        height=380,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=-25)
    return fig


def chart_headcount_correlation(df: pd.DataFrame, dark_mode: bool = False) -> Tuple[go.Figure, float, float]:
    """Correlation Scatter between Workforce Size, Revenue, and Net Profit."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Employees", "Revenue (USD)"]).copy()
    if len(clean) < 2:
        fig = go.Figure()
        return apply_executive_layout(fig, "Workforce Scaling Correlation (No Data)", height=380, dark_mode=dark_mode), 0.0, 0.0

    r_rev = float(clean["Employees"].corr(clean["Revenue (USD)"]))
    r_prof = (
        float(clean["Employees"].corr(clean["Profit (USD)"]))
        if clean["Profit (USD)"].notna().sum() > 1
        else 0.0
    )

    fig = px.scatter(
        clean,
        x="Employees",
        y="Revenue (USD)",
        color="Industry",
        hover_name="Company",
        color_discrete_sequence=theme["colorway"],
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Employees: %{x:,}<br>Revenue: $%{y:,.1f}B<extra></extra>"
    )

    # Trendline without requiring external statsmodels dependency
    try:
        x_vals = clean["Employees"].astype(float)
        y_vals = clean["Revenue (USD)"].astype(float)
        if len(x_vals) >= 2 and x_vals.nunique() > 1:
            m, b = np.polyfit(x_vals, y_vals, 1)
            x_range = np.linspace(x_vals.min(), x_vals.max(), 50)
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=m * x_range + b,
                    mode="lines",
                    name=f"OLS Trend (r = {r_rev:+.2f})",
                    line=dict(color=theme["rose"], width=1.5, dash="dash"),
                    hoverinfo="skip",
                )
            )
    except Exception:
        pass

    fig = apply_executive_layout(
        fig,
        title_text=f"Headcount vs. Revenue (Pearson r = {r_rev:.2f})",
        xaxis_title="Total Employees",
        yaxis_title="Revenue (USD Billions)",
        height=380,
        show_xaxis_grid=True,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(showlegend=False)
    return fig, r_rev, r_prof



def chart_distribution_diagnostics(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Distribution Diagnostics & Outlier Spread for Revenue, Profit, and Margin."""
    theme = get_theme(dark_mode)

    clean = df.copy()
    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=clean["Revenue (USD)"].dropna(),
            name="Revenue ($B)",
            marker_color=theme["blue_primary"],
            boxpoints="all",
            jitter=0.25,
            pointpos=-1.6,
        )
    )
    fig.add_trace(
        go.Box(
            y=clean["Profit (USD)"].dropna(),
            name="Profit ($B)",
            marker_color=theme["emerald"],
            boxpoints="all",
            jitter=0.25,
            pointpos=-1.6,
        )
    )
    fig.add_trace(
        go.Box(
            y=clean["Profit Margin (%)"].dropna(),
            name="Margin (%)",
            marker_color=theme["indigo"],
            boxpoints="all",
            jitter=0.25,
            pointpos=-1.6,
        )
    )

    return apply_executive_layout(
        fig,
        title_text="Distribution Diagnostics & Outlier Spread (Box Plot)",
        yaxis_title="Metric Value ($B / %)",
        height=360,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )


# =========================================================================
# PHASE 4 ADVANCED ANALYTICS ENGINES
# =========================================================================

def chart_top_profit_margins(df: pd.DataFrame, top_n: int = 10, dark_mode: bool = False) -> go.Figure:
    """Horizontal Bar: Top companies ranked by Net Profit Margin (%)."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Profit Margin (%)", "Revenue (USD)", "Profit (USD)"]).copy()
    clean = clean[clean["Revenue (USD)"] > 0]
    if clean.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Top Profit Margins (No Data)", height=360, dark_mode=dark_mode)

    top_m = clean.nlargest(min(top_n, len(clean)), "Profit Margin (%)").sort_values(
        by="Profit Margin (%)", ascending=True
    )

    fig = go.Figure(
        go.Bar(
            x=top_m["Profit Margin (%)"],
            y=top_m["Company"],
            orientation="h",
            marker=dict(
                color=top_m["Profit Margin (%)"],
                colorscale=[[0.0, theme["blue_accent"]], [1.0, theme["emerald"]]],
                showscale=False,
            ),
            text=[f"{x:.1f}%" for x in top_m["Profit Margin (%)"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#FFFFFF", size=10, family=theme["font_family"]),
            customdata=np.stack((top_m["Revenue (USD)"], top_m["Profit (USD)"], top_m["Industry"]), axis=-1),
            hovertemplate=(
                "<b>%{y}</b> (%{customdata[2]})<br>"
                "Margin: %{x:.2f}%<br>"
                "Profit: $%{customdata[1]:,.1f}B<br>"
                "Revenue: $%{customdata[0]:,.1f}B<extra></extra>"
            ),
        )
    )

    return apply_executive_layout(
        fig,
        title_text=f"Top {len(top_m)} Companies by Profit Margin",
        xaxis_title="Net Profit Margin (%)",
        height=360,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )


def chart_capital_efficiency_quadrant(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """4-Quadrant Scatter Plot: Capital Efficiency (Rev per Worker vs. Profit Margin)."""
    theme = get_theme(dark_mode)

    clean = df.dropna(subset=["Profit Margin (%)", "Revenue per Employee ($)"]).copy()
    clean = clean[clean["Revenue (USD)"] > 0]
    if clean.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Capital Efficiency Quadrant (No Data)", height=450, dark_mode=dark_mode)

    clean = clean.assign(Rev_per_Emp_M=clean["Revenue per Employee ($)"] / 1e6)
    med_x = float(clean["Rev_per_Emp_M"].median())
    med_y = float(clean["Profit Margin (%)"].median())

    fig = px.scatter(
        clean,
        x="Rev_per_Emp_M",
        y="Profit Margin (%)",
        color="Industry",
        hover_name="Company",
        size="Revenue (USD)",
        custom_data=["Country", "Revenue (USD)", "Employees", "Revenue per Employee ($)"],
        size_max=32,
        color_discrete_sequence=theme["colorway"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Revenue/Employee: $%{customdata[3]:,.0f}<br>"
            "Profit Margin: %{y:.2f}%<br>"
            "Revenue: $%{customdata[1]:,.1f}B<br>"
            "Employees: %{customdata[2]:,}<br>"
            "Country: %{customdata[0]}<extra></extra>"
        )
    )

    # Median Benchmark Crosshairs
    fig.add_vline(
        x=med_x,
        line_dash="dash",
        line_color=theme["border"],
        line_width=1.5,
        annotation_text=f"Median Rev/Emp (${med_x:.2f}M)",
        annotation_position="top left",
        annotation_font=dict(size=9, color=theme["text_secondary"]),
    )
    fig.add_hline(
        y=med_y,
        line_dash="dash",
        line_color=theme["border"],
        line_width=1.5,
        annotation_text=f"Median Margin ({med_y:.1f}%)",
        annotation_position="bottom right",
        annotation_font=dict(size=9, color=theme["text_secondary"]),
    )

    # Quadrant Callouts
    max_x = clean["Rev_per_Emp_M"].max()
    max_y = clean["Profit Margin (%)"].max()

    fig.add_annotation(
        x=max_x * 0.85,
        y=max_y * 0.95,
        text="<b>HIGH PRODUCTIVITY & HIGH MARGIN</b><br>(Elite Value Creators)",
        showarrow=False,
        font=dict(size=9, color=theme["emerald"]),
        bordercolor=theme["emerald"],
        borderwidth=1,
        borderpad=4,
        bgcolor=theme["bg_card"],
        opacity=0.9,
    )

    fig = apply_executive_layout(
        fig,
        title_text="Capital & Labor Efficiency Quadrant",
        xaxis_title="Revenue per Worker ($ Millions)",
        yaxis_title="Profit Margin (%)",
        height=450,
        show_xaxis_grid=True,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=9, color=theme["text_secondary"]),
        )
    )
    return fig


def get_industry_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate comprehensive industry benchmarks (totals, means, medians)."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Industry", "Company_Count", "Total_Revenue", "Avg_Revenue",
                "Total_Profit", "Avg_Profit", "Avg_Margin", "Total_Employees", "Avg_Rev_Per_Emp"
            ]
        )

    bench = df.groupby("Industry").agg(
        Company_Count=("Company", "count"),
        Total_Revenue=("Revenue (USD)", "sum"),
        Avg_Revenue=("Revenue (USD)", "mean"),
        Total_Profit=("Profit (USD)", "sum"),
        Avg_Profit=("Profit (USD)", "mean"),
        Avg_Margin=("Profit Margin (%)", "mean"),
        Total_Employees=("Employees", "sum"),
        Avg_Rev_Per_Emp=("Revenue per Employee ($)", "mean"),
    ).reset_index()

    return bench.sort_values(by="Total_Revenue", ascending=False)


def chart_industry_benchmarks(bench_df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Grouped Bar Chart: Average Revenue vs. Average Net Profit across Sectors."""
    theme = get_theme(dark_mode)

    if bench_df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Industry Benchmarks (No Data)", height=380, dark_mode=dark_mode)

    sorted_b = bench_df.sort_values(by="Avg_Revenue", ascending=True)

    fig = go.Figure(
        data=[
            go.Bar(
                name="Avg Revenue ($B)",
                y=sorted_b["Industry"],
                x=sorted_b["Avg_Revenue"],
                orientation="h",
                marker_color=theme["blue_primary"],
                text=[f"${x:,.1f}B" for x in sorted_b["Avg_Revenue"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", size=9),
            ),
            go.Bar(
                name="Avg Profit ($B)",
                y=sorted_b["Industry"],
                x=sorted_b["Avg_Profit"],
                orientation="h",
                marker_color=theme["emerald"],
                text=[f"${x:,.1f}B" if pd.notna(x) else "N/A" for x in sorted_b["Avg_Profit"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", size=9),
            ),
        ]
    )

    fig = apply_executive_layout(
        fig,
        title_text="Industry Benchmark: Average Revenue vs. Average Profit",
        xaxis_title="USD Billions",
        height=380,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=theme["text_secondary"])),
    )
    return fig


def get_country_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate comprehensive country benchmarks."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Country", "Company_Count", "Total_Revenue", "Avg_Revenue",
                "Total_Profit", "Avg_Profit", "Avg_Margin", "Total_Employees"
            ]
        )

    bench = df.groupby("Country").agg(
        Company_Count=("Company", "count"),
        Total_Revenue=("Revenue (USD)", "sum"),
        Avg_Revenue=("Revenue (USD)", "mean"),
        Total_Profit=("Profit (USD)", "sum"),
        Avg_Profit=("Profit (USD)", "mean"),
        Avg_Margin=("Profit Margin (%)", "mean"),
        Total_Employees=("Employees", "sum"),
    ).reset_index()

    return bench.sort_values(by="Total_Revenue", ascending=False)


def chart_country_benchmarks(bench_df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Grouped Bar Chart: Sovereign Benchmarks (Avg Revenue vs. Avg Profit)."""
    theme = get_theme(dark_mode)

    if bench_df.empty:
        fig = go.Figure()
        return apply_executive_layout(fig, "Country Benchmarks (No Data)", height=380, dark_mode=dark_mode)

    sorted_b = bench_df.sort_values(by="Total_Revenue", ascending=True)

    fig = go.Figure(
        data=[
            go.Bar(
                name="Total Revenue ($B)",
                y=sorted_b["Country"],
                x=sorted_b["Total_Revenue"],
                orientation="h",
                marker_color=theme["blue_primary"],
                text=[f"${x:,.0f}B" for x in sorted_b["Total_Revenue"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", size=9),
            ),
            go.Bar(
                name="Total Profit ($B)",
                y=sorted_b["Country"],
                x=sorted_b["Total_Profit"],
                orientation="h",
                marker_color=theme["emerald"],
                text=[f"${x:,.0f}B" if pd.notna(x) else "N/A" for x in sorted_b["Total_Profit"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", size=9),
            ),
        ]
    )

    fig = apply_executive_layout(
        fig,
        title_text="Sovereign Comparison: Total Revenue & Profit by Country",
        xaxis_title="USD Billions",
        height=380,
        show_xaxis_grid=True,
        show_yaxis_grid=False,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=theme["text_secondary"])),
    )
    return fig


def get_revenue_concentration_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Pareto revenue concentration metrics across Top 5, 10, 20."""
    if df.empty or "Revenue (USD)" not in df.columns:
        return {
            "total_revenue": 0.0,
            "top5_share": 0.0,
            "top10_share": 0.0,
            "top20_share": 0.0,
            "half_count": 0,
            "half_share": 0.0,
        }

    sorted_df = df.sort_values(by="Revenue (USD)", ascending=False).reset_index(drop=True).copy()
    total_rev = float(sorted_df["Revenue (USD)"].sum())

    top5_rev = float(sorted_df.iloc[:min(5, len(sorted_df))]["Revenue (USD)"].sum())
    top5_share = (top5_rev / total_rev) * 100.0 if total_rev > 0 else 0.0

    top10_rev = float(sorted_df.iloc[:min(10, len(sorted_df))]["Revenue (USD)"].sum())
    top10_share = (top10_rev / total_rev) * 100.0 if total_rev > 0 else 0.0

    top20_rev = float(sorted_df.iloc[:min(20, len(sorted_df))]["Revenue (USD)"].sum())
    top20_share = (top20_rev / total_rev) * 100.0 if total_rev > 0 else 0.0

    sorted_df = sorted_df.assign(cumsum=sorted_df["Revenue (USD)"].cumsum())
    half_rows = sorted_df[sorted_df["cumsum"] <= total_rev * 0.5]
    half_count = len(half_rows) + 1 if len(half_rows) < len(sorted_df) else len(sorted_df)

    return {
        "total_revenue": total_rev,
        "top5_share": top5_share,
        "top10_share": top10_share,
        "top20_share": top20_share,
        "half_count": half_count,
        "half_share": 50.0,
    }


def chart_pareto_revenue_concentration(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Cumulative Pareto Curve: Revenue concentration across the Global 50."""
    theme = get_theme(dark_mode)

    if df.empty or "Revenue (USD)" not in df.columns:
        fig = go.Figure()
        return apply_executive_layout(fig, "Revenue Concentration (No Data)", height=380, dark_mode=dark_mode)

    sorted_df = df.sort_values(by="Revenue (USD)", ascending=False).reset_index(drop=True).copy()
    total_rev = sorted_df["Revenue (USD)"].sum()
    cum_rev = sorted_df["Revenue (USD)"].cumsum()
    cum_pct = (cum_rev / total_rev) * 100.0 if total_rev > 0 else np.zeros(len(sorted_df))
    rank_idx = np.arange(1, len(sorted_df) + 1)
    sorted_df = sorted_df.assign(cum_rev=cum_rev, cum_pct=cum_pct, rank_idx=rank_idx)

    fig = go.Figure()

    # Individual bars
    fig.add_trace(
        go.Bar(
            x=sorted_df["rank_idx"],
            y=sorted_df["Revenue (USD)"],
            name="Individual Revenue ($B)",
            marker_color=theme["blue_primary"],
            opacity=0.6,
            hovertext=sorted_df["Company"],
            hovertemplate="<b>%{hovertext}</b> (Rank #%{x})<br>Revenue: $%{y:,.1f}B<extra></extra>",
            yaxis="y",
        )
    )

    # Cumulative line
    fig.add_trace(
        go.Scatter(
            x=sorted_df["rank_idx"],
            y=sorted_df["cum_pct"],
            name="Cumulative Share (%)",
            mode="lines+markers",
            line=dict(color=theme["emerald"], width=2.5),
            marker=dict(size=4),
            hovertext=sorted_df["Company"],
            hovertemplate="<b>%{hovertext}</b> (Rank #%{x})<br>Cumulative Share: %{y:.1f}%<extra></extra>",
            yaxis="y2",
        )
    )

    # 50% & 80% Threshold Lines
    fig.add_hline(y=50, line_dash="dot", line_color=theme["amber"], line_width=1.5, yref="y2")
    fig.add_hline(y=80, line_dash="dot", line_color=theme["rose"], line_width=1.5, yref="y2")

    fig = apply_executive_layout(
        fig,
        title_text="Pareto Revenue Concentration & Cumulative Contribution",
        xaxis_title="Company Rank (Sorted by Revenue)",
        yaxis_title="Individual Revenue ($B)",
        height=380,
        show_xaxis_grid=False,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )

    fig.update_layout(
        yaxis2=dict(
            title=dict(text="Cumulative Share (%)", font=dict(size=11, color=theme["text_secondary"])),
            tickfont=dict(size=10, color=theme["text_secondary"]),
            overlaying="y",
            side="right",
            range=[0, 105],
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9, color=theme["text_secondary"]),
        ),
    )
    return fig


def get_business_questions_answers(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Calculates answers to the 6 core executive strategic business questions."""
    if df.empty:
        return [
            {
                "id": i,
                "question": f"Question {i}",
                "entity": "N/A",
                "metric": "N/A",
                "answer": "Insufficient data available under current filter settings.",
                "context": "",
            }
            for i in range(1, 7)
        ]

    # Q1: Which company dominates global revenue?
    top_rev = df.sort_values(by="Revenue (USD)", ascending=False).iloc[0]
    total_rev = df["Revenue (USD)"].sum()
    rev_share = (top_rev["Revenue (USD)"] / total_rev * 100.0) if total_rev > 0 else 0
    q1 = {
        "id": 1,
        "question": "Which company dominates global revenue?",
        "entity": top_rev["Company"],
        "metric": f"${top_rev['Revenue (USD)']:,.1f}B ({rev_share:.1f}% of universe)",
        "answer": (
            f"**{top_rev['Company']}** stands as the global revenue leader with **${top_rev['Revenue (USD)']:,.1f}B** "
            f"in annual top-line revenue, capturing **{rev_share:.1f}%** of the total revenue pool among the evaluated companies."
        ),
        "context": f"Rank #{top_rev['Rank']} · {top_rev['Industry']} · {top_rev['Country']}",
    }

    # Q2: Which company converts revenue into actual profit most efficiently?
    clean_profit = df.dropna(subset=["Profit (USD)", "Profit Margin (%)"])
    clean_profit = clean_profit[clean_profit["Revenue (USD)"] > 0]
    if not clean_profit.empty:
        top_margin = clean_profit.sort_values(by="Profit Margin (%)", ascending=False).iloc[0]
        q2 = {
            "id": 2,
            "question": "Which company converts revenue into actual profit most efficiently?",
            "entity": top_margin["Company"],
            "metric": f"{top_margin['Profit Margin (%)']:.1f}% Margin",
            "answer": (
                f"**{top_margin['Company']}** demonstrates paramount capital conversion, turning **{top_margin['Profit Margin (%)']:.1f}%** "
                f"of its top-line revenue into net profit (**${top_margin['Profit (USD)']:,.1f}B** profit from **${top_margin['Revenue (USD)']:,.1f}B** revenue)."
            ),
            "context": f"Rank #{top_margin['Rank']} · {top_margin['Industry']} · {top_margin['Country']}",
        }
    else:
        q2 = {
            "id": 2,
            "question": "Which company converts revenue into actual profit most efficiently?",
            "entity": "N/A",
            "metric": "N/A",
            "answer": "No public profit data available for the active filter selection.",
            "context": "",
        }

    # Q3: Which sector commands the largest share of the global revenue pool?
    ind_rev = df.groupby("Industry")["Revenue (USD)"].sum().sort_values(ascending=False)
    top_ind_name = ind_rev.index[0]
    top_ind_val = ind_rev.iloc[0]
    top_ind_share = (top_ind_val / total_rev * 100.0) if total_rev > 0 else 0
    top_ind_count = len(df[df["Industry"] == top_ind_name])
    q3 = {
        "id": 3,
        "question": "Which sector commands the largest share of the global revenue pool?",
        "entity": top_ind_name,
        "metric": f"${top_ind_val:,.1f}B ({top_ind_share:.1f}% pool)",
        "answer": (
            f"The **{top_ind_name}** sector commands the largest market share with **${top_ind_val:,.1f}B** "
            f"(**{top_ind_share:.1f}%** of total pool) generated across **{top_ind_count}** enterprise organizations."
        ),
        "context": f"{top_ind_count} companies in cohort · Avg ${(top_ind_val / top_ind_count):,.1f}B / co",
    }

    # Q4: Which nation serves as the primary sovereign anchor for enterprise scale?
    cnt_rev = df.groupby("Country")["Revenue (USD)"].sum().sort_values(ascending=False)
    top_cnt_name = cnt_rev.index[0]
    top_cnt_val = cnt_rev.iloc[0]
    top_cnt_share = (top_cnt_val / total_rev * 100.0) if total_rev > 0 else 0
    top_cnt_count = len(df[df["Country"] == top_cnt_name])
    q4 = {
        "id": 4,
        "question": "Which nation serves as the primary sovereign anchor for enterprise scale?",
        "entity": top_cnt_name,
        "metric": f"${top_cnt_val:,.1f}B ({top_cnt_count} companies)",
        "answer": (
            f"The **{top_cnt_name}** is the world's preeminent sovereign corporate hub, headquarters to **{top_cnt_count}** "
            f"enterprises producing **${top_cnt_val:,.1f}B** (**{top_cnt_share:.1f}%** of aggregate revenue)."
        ),
        "context": f"{top_cnt_count} corporate headquarters · {top_cnt_share:.1f}% sovereign pool share",
    }

    # Q5: Which enterprise extracts the highest revenue per individual worker?
    top_worker = df.sort_values(by="Revenue per Employee ($)", ascending=False).iloc[0]
    q5 = {
        "id": 5,
        "question": "Which enterprise extracts the highest revenue per individual worker?",
        "entity": top_worker["Company"],
        "metric": f"${(top_worker['Revenue per Employee ($)'] / 1000.0):,.0f}k / employee",
        "answer": (
            f"**{top_worker['Company']}** demonstrates peak workforce productivity, generating **${top_worker['Revenue per Employee ($)']:,.0f}** "
            f"in annual revenue for each of its **{top_worker['Employees']:,}** employees."
        ),
        "context": f"Rank #{top_worker['Rank']} · {top_worker['Industry']} · ${top_worker['Revenue (USD)']:,.1f}B Revenue",
    }

    # Q6: How concentrated is global enterprise capital among the Top 10 firms?
    top10_df = df.sort_values(by="Revenue (USD)", ascending=False).iloc[:min(10, len(df))]
    top10_rev = top10_df["Revenue (USD)"].sum()
    top10_pct = (top10_rev / total_rev * 100.0) if total_rev > 0 else 0
    q6 = {
        "id": 6,
        "question": "How concentrated is global enterprise capital among the Top 10 firms?",
        "entity": f"Top 10 Mega-Caps",
        "metric": f"{top10_pct:.1f}% Total Revenue",
        "answer": (
            f"High oligopolistic concentration: The Top 10 enterprises generate **${top10_rev:,.1f}B**, representing **{top10_pct:.1f}%** "
            f"of all capital flowing through this global corporate cohort."
        ),
        "context": f"10 of {len(df)} companies · Average ${top10_rev / len(top10_df):,.1f}B per mega-cap",
    }

    return [q1, q2, q3, q4, q5, q6]


# =========================================================================
# COMPANY 360 & COMPARISON HELPERS
# =========================================================================

def get_company_profile(df: pd.DataFrame, company_name: str) -> Dict[str, Any]:
    """Retrieve full company metrics and compute ranking percentiles and sector medians."""
    match = df[df["Company"] == company_name]
    if match.empty:
        raise ValueError(f"Company {company_name} not found in dataset.")

    row = match.iloc[0]

    # Compute Global Ranks
    rev_rank = int(df["Revenue (USD)"].rank(ascending=False, method="min").loc[row.name])
    prof_rank = (
        int(df["Profit (USD)"].rank(ascending=False, method="min").loc[row.name])
        if pd.notna(row["Profit (USD)"])
        else None
    )
    emp_rank = int(df["Employees"].rank(ascending=False, method="min").loc[row.name])
    margin_rank = (
        int(df["Profit Margin (%)"].rank(ascending=False, method="min").loc[row.name])
        if pd.notna(row["Profit Margin (%)"])
        else None
    )

    # Industry Averages
    ind_df = df[df["Industry"] == row["Industry"]]
    ind_avg_rev = float(ind_df["Revenue (USD)"].mean())
    ind_avg_prof = float(ind_df["Profit (USD)"].mean(skipna=True))
    ind_avg_emp = float(ind_df["Employees"].mean())
    ind_avg_margin = float(ind_df["Profit Margin (%)"].mean(skipna=True))

    # Global Medians
    global_med_rev = float(df["Revenue (USD)"].median())
    global_med_prof = float(df["Profit (USD)"].median(skipna=True))
    global_med_emp = float(df["Employees"].median())
    global_med_margin = float(df["Profit Margin (%)"].median(skipna=True))

    return {
        "Rank": int(row["Rank"]),
        "Company": row["Company"],
        "Country": row["Country"],
        "Industry": row["Industry"],
        "Revenue": float(row["Revenue (USD)"]),
        "Profit": float(row["Profit (USD)"]) if pd.notna(row["Profit (USD)"]) else None,
        "Employees": int(row["Employees"]),
        "Margin": float(row["Profit Margin (%)"]) if pd.notna(row["Profit Margin (%)"]) else None,
        "Rev_per_Emp": float(row["Revenue per Employee ($)"]),
        "Profit_per_Emp": float(row["Profit per Employee ($)"]) if pd.notna(row["Profit per Employee ($)"]) else None,
        "ISO_Alpha3": row["ISO_Alpha3"],
        "Ranks": {
            "Revenue": rev_rank,
            "Profit": prof_rank,
            "Employees": emp_rank,
            "Margin": margin_rank,
        },
        "Industry_Avg": {
            "Revenue": ind_avg_rev,
            "Profit": ind_avg_prof,
            "Employees": ind_avg_emp,
            "Margin": ind_avg_margin,
        },
        "Global_Median": {
            "Revenue": global_med_rev,
            "Profit": global_med_prof,
            "Employees": global_med_emp,
            "Margin": global_med_margin,
        },
    }


def chart_company_profile_benchmark(df: pd.DataFrame, company_name: str, dark_mode: bool = False) -> go.Figure:
    """Benchmark an individual enterprise against Sector Average and Global Median."""
    theme = get_theme(dark_mode)

    prof = get_company_profile(df, company_name)
    metrics = ["Revenue ($B)", "Profit ($B)", "Margin (%)", "Rev/Worker ($k)"]

    c_vals = [
        prof["Revenue"],
        prof["Profit"] if prof["Profit"] is not None else 0.0,
        prof["Margin"] if prof["Margin"] is not None else 0.0,
        prof["Rev_per_Emp"] / 1000.0,
    ]

    ind_vals = [
        prof["Industry_Avg"]["Revenue"],
        prof["Industry_Avg"]["Profit"] if pd.notna(prof["Industry_Avg"]["Profit"]) else 0.0,
        prof["Industry_Avg"]["Margin"] if pd.notna(prof["Industry_Avg"]["Margin"]) else 0.0,
        (prof["Industry_Avg"]["Revenue"] * 1e9 / prof["Industry_Avg"]["Employees"]) / 1000.0 if prof["Industry_Avg"]["Employees"] > 0 else 0.0,
    ]

    med_vals = [
        prof["Global_Median"]["Revenue"],
        prof["Global_Median"]["Profit"] if pd.notna(prof["Global_Median"]["Profit"]) else 0.0,
        prof["Global_Median"]["Margin"] if pd.notna(prof["Global_Median"]["Margin"]) else 0.0,
        (prof["Global_Median"]["Revenue"] * 1e9 / prof["Global_Median"]["Employees"]) / 1000.0 if prof["Global_Median"]["Employees"] > 0 else 0.0,
    ]

    fig = go.Figure(
        data=[
            go.Bar(name=company_name, x=metrics, y=c_vals, marker_color=theme["blue_primary"]),
            go.Bar(name=f"Sector Avg ({prof['Industry']})", x=metrics, y=ind_vals, marker_color=theme["emerald"]),
            go.Bar(name="Global Median", x=metrics, y=med_vals, marker_color=theme["text_muted"]),
        ]
    )

    fig = apply_executive_layout(
        fig,
        title_text=f"{company_name} vs. Sector & Global Benchmarks",
        xaxis_title="",
        yaxis_title="Metric Value ($B / % / $k)",
        height=360,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9, color=theme["text_secondary"]),
        ),
    )
    return fig


def compare_companies(
    df: pd.DataFrame,
    comp1_name: str,
    comp2_name: str,
    dark_mode: bool = False,
) -> Tuple[go.Figure, pd.DataFrame]:
    """Side-by-side grouped bar chart and structured comparison table for two companies."""
    theme = get_theme(dark_mode)

    c1 = df[df["Company"] == comp1_name].iloc[0]
    c2 = df[df["Company"] == comp2_name].iloc[0]

    metrics = ["Revenue ($B)", "Profit ($B)", "Margin (%)", "Employees (k)", "Rev/Worker ($k)"]

    c1_vals = [
        c1["Revenue (USD)"],
        c1["Profit (USD)"] if pd.notna(c1["Profit (USD)"]) else 0,
        c1["Profit Margin (%)"] if pd.notna(c1["Profit Margin (%)"]) else 0,
        c1["Employees"] / 1000.0,
        c1["Revenue per Employee ($)"] / 1000.0,
    ]

    c2_vals = [
        c2["Revenue (USD)"],
        c2["Profit (USD)"] if pd.notna(c2["Profit (USD)"]) else 0,
        c2["Profit Margin (%)"] if pd.notna(c2["Profit Margin (%)"]) else 0,
        c2["Employees"] / 1000.0,
        c2["Revenue per Employee ($)"] / 1000.0,
    ]

    fig = go.Figure(
        data=[
            go.Bar(name=comp1_name, x=metrics, y=c1_vals, marker_color=theme["blue_primary"]),
            go.Bar(name=comp2_name, x=metrics, y=c2_vals, marker_color=theme["emerald"]),
        ]
    )

    fig = apply_executive_layout(
        fig,
        title_text=f"Direct Comparison: {comp1_name} vs. {comp2_name}",
        height=350,
        show_yaxis_grid=True,
        dark_mode=dark_mode,
    )
    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=theme["text_secondary"]),
        ),
    )

    comp_df = pd.DataFrame(
        {
            "Attribute": [
                "Global Revenue Rank",
                "Headquarters Country",
                "Industry Classification",
                "Annual Revenue (USD)",
                "Annual Net Profit (USD)",
                "Net Profit Margin (%)",
                "Total Workforce",
                "Revenue per Worker",
                "Profit per Worker",
            ],
            comp1_name: [
                f"#{c1['Rank']}",
                c1["Country"],
                c1["Industry"],
                f"${c1['Revenue (USD)']:,.1f}B",
                f"${c1['Profit (USD)']:,.1f}B" if pd.notna(c1["Profit (USD)"]) else "N/A (Private)",
                f"{c1['Profit Margin (%)']:.2f}%" if pd.notna(c1["Profit Margin (%)"]) else "N/A",
                f"{c1['Employees']:,}",
                f"${c1['Revenue per Employee ($)']:,.0f}",
                f"${c1['Profit per Employee ($)']:,.0f}" if pd.notna(c1["Profit per Employee ($)"]) else "N/A",
            ],
            comp2_name: [
                f"#{c2['Rank']}",
                c2["Country"],
                c2["Industry"],
                f"${c2['Revenue (USD)']:,.1f}B",
                f"${c2['Profit (USD)']:,.1f}B" if pd.notna(c2["Profit (USD)"]) else "N/A (Private)",
                f"{c2['Profit Margin (%)']:.2f}%" if pd.notna(c2["Profit Margin (%)"]) else "N/A",
                f"{c2['Employees']:,}",
                f"${c2['Revenue per Employee ($)']:,.0f}",
                f"${c2['Profit per Employee ($)']:,.0f}" if pd.notna(c2["Profit per Employee ($)"]) else "N/A",
            ],
        }
    )

    return fig, comp_df


# =========================================================================
# PROFESSIONAL EXCEL DATA EXPORT SYSTEM (OPENPYXL)
# =========================================================================

def get_export_filename(
    countries: List[str] | None = None,
    industries: List[str] | None = None,
    search: str = "",
    ext: str = "xlsx",
) -> str:
    """Generate a clean, professional, dynamic export filename reflecting active filter criteria."""
    parts = ["global50"]
    if search and search.strip():
        clean_s = "".join(c for c in search.strip().lower() if c.isalnum() or c in "_-")[:15]
        parts.append(clean_s)
    if countries and len(countries) == 1:
        clean_c = "".join(c for c in countries[0].replace(" ", "_") if c.isalnum() or c == "_")
        parts.append(clean_c)
    elif countries and len(countries) > 1:
        parts.append(f"{len(countries)}_nations")
    if industries and len(industries) == 1:
        clean_i = "".join(c for c in industries[0].replace(" ", "_").replace("/", "_") if c.isalnum() or c == "_")[:20]
        parts.append(clean_i)
    elif industries and len(industries) > 1:
        parts.append(f"{len(industries)}_sectors")

    if len(parts) == 1:
        parts.append("all_companies")
    else:
        parts.append("filtered")

    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    return f"{'_'.join(parts)}_{timestamp}.{ext}"


def generate_excel_export(
    df: pd.DataFrame,
    active_filters_desc: str = "All Companies (Full Universe)",
) -> io.BytesIO:
    """
    Generate a professional multi-sheet Excel workbook using openpyxl.
    Sheets:
    1. Company Data (Formatted Excel Table with Auto-Filters, Freeze Panes, Data Bars)
    2. Executive Summary (Dynamic KPI Scorecards)
    3. Benchmarks (Industry and Country Aggregations)
    4. Charts (Native Excel Bar Charts for Top Revenue and Net Profit)
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.table import Table, TableStyleInfo
    from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
    from openpyxl.chart import BarChart, Reference

    wb = openpyxl.Workbook()
    ws_data = wb.active
    ws_data.title = "Company Data"

    # Corporate styling tokens
    font_title = Font(name="Segoe UI", size=14, bold=True, color="0F172A")
    font_subtitle = Font(name="Segoe UI", size=9, italic=True, color="64748B")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=10, color="0F172A")
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    border_thin = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )

    # -------------------------------------------------------------------------
    # SHEET 1: COMPANY DATA
    # -------------------------------------------------------------------------
    ws_data.views.sheetView[0].showGridLines = True

    # Title Block
    ws_data["A1"] = "GLOBAL 50 — CORPORATE INTELLIGENCE"
    ws_data["A1"].font = font_title
    ws_data["A2"] = f"Filtered Dataset Export · Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} · Filters: {active_filters_desc}"
    ws_data["A2"].font = font_subtitle

    # Table Headers at Row 4
    headers = [
        "Rank",
        "Company",
        "Country",
        "Industry",
        "Revenue ($B)",
        "Profit ($B)",
        "Employees",
        "Profit Margin",
        "Revenue per Employee ($)",
    ]

    start_row = 4
    for col_idx, h in enumerate(headers, 1):
        cell = ws_data.cell(row=start_row, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center" if col_idx in [1, 3] else ("left" if col_idx in [2, 4] else "right"), vertical="center")

    ws_data.row_dimensions[start_row].height = 24

    req_cols = [
        "Rank",
        "Company",
        "Country",
        "Industry",
        "Revenue (USD)",
        "Profit (USD)",
        "Employees",
        "Profit Margin (%)",
        "Revenue per Employee ($)",
    ]

    current_row = start_row + 1
    if not df.empty:
        export_df = df[req_cols].copy()
        for _, r in export_df.iterrows():
            ws_data.cell(row=current_row, column=1, value=int(r["Rank"]))
            ws_data.cell(row=current_row, column=2, value=str(r["Company"]))
            ws_data.cell(row=current_row, column=3, value=str(r["Country"]))
            ws_data.cell(row=current_row, column=4, value=str(r["Industry"]))

            # Revenue ($B)
            c_rev = ws_data.cell(row=current_row, column=5, value=float(r["Revenue (USD)"]))
            c_rev.number_format = "$#,##0.0"

            # Profit ($B)
            if pd.notna(r["Profit (USD)"]):
                c_prof = ws_data.cell(row=current_row, column=6, value=float(r["Profit (USD)"]))
                c_prof.number_format = "$#,##0.0"
            else:
                c_prof = ws_data.cell(row=current_row, column=6, value="N/A")
                c_prof.alignment = Alignment(horizontal="right")

            # Employees
            c_emp = ws_data.cell(row=current_row, column=7, value=int(r["Employees"]))
            c_emp.number_format = "#,##0"

            # Profit Margin (decimal representation for percentage format)
            if pd.notna(r["Profit Margin (%)"]):
                c_mar = ws_data.cell(row=current_row, column=8, value=float(r["Profit Margin (%)"]) / 100.0)
                c_mar.number_format = "0.0%"
            else:
                c_mar = ws_data.cell(row=current_row, column=8, value="N/A")
                c_mar.alignment = Alignment(horizontal="right")

            # Rev per Worker
            c_rpw = ws_data.cell(row=current_row, column=9, value=float(r["Revenue per Employee ($)"]))
            c_rpw.number_format = "$#,##0"

            ws_data.cell(row=current_row, column=1).alignment = Alignment(horizontal="center")
            ws_data.cell(row=current_row, column=2).alignment = Alignment(horizontal="left")
            ws_data.cell(row=current_row, column=3).alignment = Alignment(horizontal="left")
            ws_data.cell(row=current_row, column=4).alignment = Alignment(horizontal="left")

            for col_idx in range(1, 10):
                c = ws_data.cell(row=current_row, column=col_idx)
                c.font = font_data
                c.border = border_thin

            ws_data.row_dimensions[current_row].height = 20
            current_row += 1

        end_row = current_row - 1
        tab = Table(displayName="CompanyDataTable", ref=f"A{start_row}:I{end_row}")
        tab.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        ws_data.add_table(tab)

        # Conditional Formatting: Data bars for Revenue and Profit
        rule_rev = DataBarRule(start_type="min", end_type="max", color="60A5FA", showValue=None, minLength=None, maxLength=None)
        ws_data.conditional_formatting.add(f"E{start_row+1}:E{end_row}", rule_rev)

        # 3-color scale for Profit Margin
        rule_margin = ColorScaleRule(
            start_type="min", start_color="FEE2E2",
            mid_type="percentile", mid_value=50, mid_color="FEF9C3",
            end_type="max", end_color="DCFCE7",
        )
        ws_data.conditional_formatting.add(f"H{start_row+1}:H{end_row}", rule_margin)

    else:
        ws_data.cell(row=start_row + 1, column=1, value="No companies match current filter selection.")
        end_row = start_row + 1

    # Freeze Panes on Header
    ws_data.freeze_panes = "A5"

    # Intelligent column widths
    col_widths = {1: 8, 2: 26, 3: 18, 4: 26, 5: 16, 6: 15, 7: 15, 8: 15, 9: 20}
    for col_idx, width in col_widths.items():
        ws_data.column_dimensions[get_column_letter(col_idx)].width = width

    # -------------------------------------------------------------------------
    # SHEET 2: EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    ws_sum = wb.create_sheet(title="Executive Summary")
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "GLOBAL 50 — EXECUTIVE SUMMARY"
    ws_sum["A1"].font = font_title
    ws_sum["A2"] = f"Key Corporate Performance Indicators · Cohort Size: {len(df)} Enterprises"
    ws_sum["A2"].font = font_subtitle

    kpis = get_kpis(df, df)

    summary_items = [
        ("Total Companies Analyzed", len(df), "#,##0"),
        ("Aggregate Revenue Pool ($B)", kpis["total_revenue_b"], "$#,##0.0"),
        ("Average Revenue per Firm ($B)", kpis["avg_revenue_b"], "$#,##0.0"),
        ("Aggregate Net Profit ($B)", kpis["total_profit_b"], "$#,##0.0"),
        ("Average Net Profit per Firm ($B)", kpis["avg_profit_b"], "$#,##0.0"),
        ("Total Global Workforce", kpis["total_employees"], "#,##0"),
        ("Highest Revenue Organization", f"{kpis['highest_revenue_company']} (#{kpis['highest_revenue_rank']})", "@"),
        ("Highest Revenue Value ($B)", kpis["highest_revenue_val"], "$#,##0.0"),
        ("Top Net Profit Engine", f"{kpis['highest_profit_company']} (#{kpis['highest_profit_rank']})", "@"),
        ("Top Net Profit Value ($B)", kpis["highest_profit_val"], "$#,##0.0"),
        ("Largest Employer Organization", f"{kpis['largest_employer_company']} (#{kpis['largest_employer_rank']})", "@"),
        ("Largest Workforce Headcount", kpis["largest_employer_count"], "#,##0"),
    ]

    ws_sum.cell(row=4, column=1, value="Metric Indicator").font = font_header
    ws_sum.cell(row=4, column=1).fill = fill_header
    ws_sum.cell(row=4, column=2, value="Cohort Value").font = font_header
    ws_sum.cell(row=4, column=2).fill = fill_header
    ws_sum.row_dimensions[4].height = 24

    for idx, (label, val, fmt) in enumerate(summary_items, 5):
        c1 = ws_sum.cell(row=idx, column=1, value=label)
        c1.font = font_bold
        c1.border = border_thin
        c1.fill = fill_meta if idx % 2 == 0 else PatternFill(fill_type=None)

        c2 = ws_sum.cell(row=idx, column=2, value=val)
        c2.font = font_data
        c2.number_format = fmt
        c2.border = border_thin
        c2.alignment = Alignment(horizontal="right" if fmt != "@" else "left")
        ws_sum.row_dimensions[idx].height = 20

    ws_sum.column_dimensions["A"].width = 34
    ws_sum.column_dimensions["B"].width = 24

    # -------------------------------------------------------------------------
    # SHEET 3: BENCHMARKS
    # -------------------------------------------------------------------------
    ws_bench = wb.create_sheet(title="Benchmarks")
    ws_bench.views.sheetView[0].showGridLines = True

    ws_bench["A1"] = "GLOBAL 50 — BENCHMARK INTELLIGENCE"
    ws_bench["A1"].font = font_title
    ws_bench["A2"] = "Industry Sector and Sovereign Aggregations"
    ws_bench["A2"].font = font_subtitle

    # Table 1: Industry Benchmarks
    ind_df = get_industry_benchmarks(df)
    ws_bench["A4"] = "INDUSTRY SECTOR BENCHMARKS"
    ws_bench["A4"].font = Font(name="Segoe UI", size=11, bold=True, color="1E3A8A")

    ind_headers = ["Industry Sector", "Firms", "Total Rev ($B)", "Avg Rev ($B)", "Total Profit ($B)", "Avg Profit ($B)", "Avg Margin"]
    for col_idx, h in enumerate(ind_headers, 1):
        c = ws_bench.cell(row=5, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal="left" if col_idx == 1 else "right")
    ws_bench.row_dimensions[5].height = 22

    r_idx = 6
    if not ind_df.empty:
        for _, row in ind_df.iterrows():
            ws_bench.cell(row=r_idx, column=1, value=str(row["Industry"])).alignment = Alignment(horizontal="left")
            ws_bench.cell(row=r_idx, column=2, value=int(row["Company_Count"])).number_format = "#,##0"
            ws_bench.cell(row=r_idx, column=3, value=float(row["Total_Revenue"])).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=4, value=float(row["Avg_Revenue"])).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=5, value=float(row["Total_Profit"]) if pd.notna(row["Total_Profit"]) else 0.0).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=6, value=float(row["Avg_Profit"]) if pd.notna(row["Avg_Profit"]) else 0.0).number_format = "$#,##0.0"
            c_m = ws_bench.cell(row=r_idx, column=7, value=float(row["Avg_Margin"]) / 100.0 if pd.notna(row["Avg_Margin"]) else 0.0)
            c_m.number_format = "0.0%"

            for c_i in range(1, 8):
                cell = ws_bench.cell(row=r_idx, column=c_i)
                cell.font = font_data
                cell.border = border_thin

            ws_bench.row_dimensions[r_idx].height = 19
            r_idx += 1

        tab_ind = Table(displayName="IndustryBenchmarkTable", ref=f"A5:G{r_idx-1}")
        tab_ind.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws_bench.add_table(tab_ind)

    # Table 2: Country Benchmarks
    cnt_df = get_country_benchmarks(df)
    r_idx += 2
    ws_bench.cell(row=r_idx, column=1, value="SOVEREIGN JURISDICTION BENCHMARKS").font = Font(name="Segoe UI", size=11, bold=True, color="1E3A8A")
    r_idx += 1

    cnt_headers = ["Country", "Firms", "Total Rev ($B)", "Avg Rev ($B)", "Total Profit ($B)", "Avg Profit ($B)", "Avg Margin"]
    cnt_start_row = r_idx
    for col_idx, h in enumerate(cnt_headers, 1):
        c = ws_bench.cell(row=cnt_start_row, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal="left" if col_idx == 1 else "right")
    ws_bench.row_dimensions[cnt_start_row].height = 22

    r_idx += 1
    if not cnt_df.empty:
        for _, row in cnt_df.iterrows():
            ws_bench.cell(row=r_idx, column=1, value=str(row["Country"])).alignment = Alignment(horizontal="left")
            ws_bench.cell(row=r_idx, column=2, value=int(row["Company_Count"])).number_format = "#,##0"
            ws_bench.cell(row=r_idx, column=3, value=float(row["Total_Revenue"])).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=4, value=float(row["Avg_Revenue"])).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=5, value=float(row["Total_Profit"]) if pd.notna(row["Total_Profit"]) else 0.0).number_format = "$#,##0.0"
            ws_bench.cell(row=r_idx, column=6, value=float(row["Avg_Profit"]) if pd.notna(row["Avg_Profit"]) else 0.0).number_format = "$#,##0.0"
            c_m = ws_bench.cell(row=r_idx, column=7, value=float(row["Avg_Margin"]) / 100.0 if pd.notna(row["Avg_Margin"]) else 0.0)
            c_m.number_format = "0.0%"

            for c_i in range(1, 8):
                cell = ws_bench.cell(row=r_idx, column=c_i)
                cell.font = font_data
                cell.border = border_thin

            ws_bench.row_dimensions[r_idx].height = 19
            r_idx += 1

        tab_cnt = Table(displayName="CountryBenchmarkTable", ref=f"A{cnt_start_row}:G{r_idx-1}")
        tab_cnt.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws_bench.add_table(tab_cnt)

    ws_bench.column_dimensions["A"].width = 24
    ws_bench.column_dimensions["B"].width = 10
    ws_bench.column_dimensions["C"].width = 16
    ws_bench.column_dimensions["D"].width = 16
    ws_bench.column_dimensions["E"].width = 16
    ws_bench.column_dimensions["F"].width = 16
    ws_bench.column_dimensions["G"].width = 14

    # -------------------------------------------------------------------------
    # SHEET 4: CHARTS (Native Excel Bar Charts)
    # -------------------------------------------------------------------------
    ws_charts = wb.create_sheet(title="Charts")
    ws_charts.views.sheetView[0].showGridLines = True

    ws_charts["A1"] = "GLOBAL 50 — VISUAL CHARTS SUMMARY"
    ws_charts["A1"].font = font_title
    ws_charts["A2"] = "Native Excel visual representations of revenue and profitability"
    ws_charts["A2"].font = font_subtitle

    if not df.empty and len(df) >= 2:
        top_n = min(10, len(df))
        # 1. Chart: Top Revenue
        chart1 = BarChart()
        chart1.type = "bar"
        chart1.style = 10
        chart1.title = "Top Companies by Revenue ($B)"
        chart1.y_axis.title = "Company"
        chart1.x_axis.title = "Revenue (USD Billions)"
        chart1.height = 14
        chart1.width = 20

        data_ref1 = Reference(ws_data, min_col=5, min_row=4, max_row=4 + top_n)
        cats1 = Reference(ws_data, min_col=2, min_row=5, max_row=4 + top_n)
        chart1.add_data(data_ref1, titles_from_data=True)
        chart1.set_categories(cats1)
        chart1.legend = None
        ws_charts.add_chart(chart1, "A4")

        # 2. Chart: Top Profit
        chart2 = BarChart()
        chart2.type = "bar"
        chart2.style = 13
        chart2.title = "Top Companies by Net Profit ($B)"
        chart2.y_axis.title = "Company"
        chart2.x_axis.title = "Net Profit (USD Billions)"
        chart2.height = 14
        chart2.width = 20

        data_ref2 = Reference(ws_data, min_col=6, min_row=4, max_row=4 + top_n)
        chart2.add_data(data_ref2, titles_from_data=True)
        chart2.set_categories(cats1)
        chart2.legend = None
        ws_charts.add_chart(chart2, "M4")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# =========================================================================
# BUSINESS QUESTIONS TAXONOMY MAPPING
# =========================================================================

BUSINESS_QUESTIONS_MAP = {
    "Revenue Leaders": {
        "group": "FINANCIAL",
        "page": "Business Questions",
        "anchor": "sec_rev_leaders",
        "question": "Which companies generate the highest revenue?",
        "target_desc": "Executive Overview · Top 10 Revenue Rankings",
    },
    "Profit Leaders": {
        "group": "FINANCIAL",
        "page": "Business Questions",
        "anchor": "sec_prof_leaders",
        "question": "Which companies generate the highest profit?",
        "target_desc": "Executive Overview · Top 10 Net Profit Engines",
    },
    "Profitability": {
        "group": "FINANCIAL",
        "page": "Business Questions",
        "anchor": "sec_profitability",
        "question": "Which companies have the strongest profit margins?",
        "target_desc": "Profitability Analysis · Top Margins & Sector Spreads",
    },
    "Country Revenue": {
        "group": "GEOGRAPHIC",
        "page": "Business Questions",
        "anchor": "sec_country_rev",
        "question": "Which countries generate the most revenue?",
        "target_desc": "Revenue Distribution by Sovereign Nation",
    },
    "Country Benchmarking": {
        "group": "GEOGRAPHIC",
        "page": "Business Questions",
        "anchor": "sec_country_bench",
        "question": "How do sovereign jurisdictions compare in corporate scale?",
        "target_desc": "Country Benchmarking & Global Choropleth Footprint",
    },
    "Industry Revenue": {
        "group": "INDUSTRY",
        "page": "Business Questions",
        "anchor": "sec_ind_rev",
        "question": "Which industries generate the most revenue?",
        "target_desc": "Revenue Distribution across Industry Sectors",
    },
    "Industry Profitability": {
        "group": "INDUSTRY",
        "page": "Business Questions",
        "anchor": "sec_ind_profitability",
        "question": "Which industries are the strongest in profitability?",
        "target_desc": "Industry Benchmarking Matrix & Margin Dispersion",
    },
    "Revenue per Employee": {
        "group": "EFFICIENCY",
        "page": "Business Questions",
        "anchor": "sec_rev_per_emp",
        "question": "Which companies have the highest revenue per employee?",
        "target_desc": "Workforce Productivity · Rev/Worker Rankings",
    },
    "Workforce vs Revenue": {
        "group": "EFFICIENCY",
        "page": "Business Questions",
        "anchor": "sec_workforce_corr",
        "question": "Does workforce size relate to revenue and profitability?",
        "target_desc": "Workforce Scaling Correlation & Capital Efficiency",
    },
    "Revenue Concentration": {
        "group": "CONCENTRATION",
        "page": "Business Questions",
        "anchor": "sec_concentration",
        "question": "How concentrated is global corporate revenue?",
        "target_desc": "Pareto Concentration Curve & Oligopoly Thresholds",
    },
}


