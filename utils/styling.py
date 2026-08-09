"""
Shared design system for the PetroSep investor data room.
Import and call inject_css() at the top of every page, then use the
helper builders below instead of bare st.metric() for a consistent look.

Dark theme: chart canvases are pinned to the same dark elevated surface
as the rest of the UI (CARD_BG) with light text/gridlines, rather than
transparent. A transparent background would let the page's dark color
bleed unpredictably behind the plot, and every label below is drawn in
a light ink color for contrast against that dark canvas — so pinning
the surface keeps every label legible regardless of chart type.
"""

import streamlit as st

# ---------- PALETTE ----------
PRIMARY = "#3AAAD1"       # brightened teal-blue (brand) — pops on dark surfaces
PRIMARY_DARK = "#0A3F52"
PRIMARY_LIGHT = "#7FCBE0"
ACCENT = "#F2A541"        # amber
ACCENT_DARK = "#D8862A"
GOOD = "#33C97F"
BAD = "#F26A5D"
INK = "#E8EEF3"           # primary light text (was dark ink for light theme)
MUTED = "#93A5B8"         # secondary light-muted text
TEXT_ON_ACCENT = "#152431"  # dark text for use on light/accent-colored fills
CARD_BG = "#141B29"
CARD_BORDER = "#2A3A4E"
PAGE_BG = "#0B1420"
TRACK_BG = "#3C4B60"      # neutral baseline/track color for background bars

CHART_TEMPLATE = "plotly_dark"
CHART_BG = CARD_BG
CHART_GRID = "rgba(232, 238, 243, 0.08)"
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

CATEGORY_COLORS = {
    "BOM": PRIMARY,
    "Assembly": ACCENT,
    "Logistics": PRIMARY_LIGHT,
    "Reserve": MUTED,
}


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: {FONT_FAMILY};
        }}

        .stApp {{
            background: {PAGE_BG};
        }}

        /* ---- kill default top padding a bit ---- */
        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1300px;
        }}

        /* ---- hero banner ---- */
        .ps-hero {{
            background: linear-gradient(120deg, {PRIMARY_DARK} 0%, #0F6A88 55%, {PRIMARY} 100%);
            border-radius: 18px;
            padding: 2.1rem 2.4rem;
            color: white;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        }}
        .ps-hero h1 {{
            margin: 0 0 0.35rem 0;
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: white;
        }}
        .ps-hero p {{
            margin: 0;
            font-size: 1.02rem;
            color: rgba(255,255,255,0.88);
            max-width: 900px;
            line-height: 1.5;
        }}
        .ps-hero .ps-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.32);
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }}

        /* ---- section header ---- */
        .ps-section-title {{
            font-size: 1.28rem;
            font-weight: 700;
            color: {INK};
            margin: 0 0 0.15rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .ps-section-sub {{
            color: {MUTED};
            font-size: 0.92rem;
            margin-bottom: 0.9rem;
        }}
        .ps-accent-bar {{
            width: 42px;
            height: 4px;
            border-radius: 4px;
            background: {ACCENT};
            margin: 0.35rem 0 1.1rem 0;
        }}

        /* ---- metric cards ---- */
        .ps-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 14px;
            padding: 1.05rem 1.2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
            height: 100%;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }}
        .ps-card:hover {{
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
            transform: translateY(-1px);
        }}
        .ps-card .ps-label {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {MUTED};
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.3rem;
        }}
        .ps-card .ps-value {{
            font-size: 1.55rem;
            font-weight: 800;
            color: {INK};
            line-height: 1.1;
        }}
        .ps-card .ps-delta {{
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 0.35rem;
        }}
        .ps-card .ps-delta.good {{ color: {GOOD}; }}
        .ps-card .ps-delta.bad {{ color: {BAD}; }}
        .ps-card .ps-delta.neutral {{ color: {MUTED}; }}
        .ps-card .ps-icon {{
            font-size: 1.3rem;
            margin-bottom: 0.25rem;
            display: block;
        }}

        /* ---- accent-colored strip cards ---- */
        .ps-stat-strip {{
            border-radius: 14px;
            padding: 1.0rem 1.2rem;
            color: white;
            height: 100%;
        }}
        .ps-stat-strip .ps-label {{
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            opacity: 0.9;
            margin-bottom: 0.3rem;
        }}
        .ps-stat-strip .ps-value {{
            font-size: 1.65rem;
            font-weight: 800;
        }}

        /* ---- nav cards (page links) ---- */
        .ps-nav-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.6rem;
            color: {INK};
        }}

        /* ---- pill badges for rationale / tags ---- */
        .ps-pill {{
            display: inline-block;
            background: {PRIMARY}26;
            color: {PRIMARY_LIGHT};
            border-radius: 999px;
            padding: 0.15rem 0.65rem;
            font-size: 0.76rem;
            font-weight: 600;
            margin-right: 0.35rem;
        }}

        /* ---- plotly chart card frame ---- */
        [data-testid="stPlotlyChart"] {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 14px;
            padding: 0.6rem 0.6rem 0.2rem 0.6rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
            margin-bottom: 0.6rem;
        }}

        /* ---- dataframe polish ---- */
        [data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {CARD_BORDER};
        }}

        /* ---- sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: {PRIMARY_DARK};
        }}
        section[data-testid="stSidebar"] * {{
            color: #EAF2F5 !important;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            background: {ACCENT};
            color: {TEXT_ON_ACCENT} !important;
            border: none;
            font-weight: 700;
        }}

        /* ---- divider tighten ---- */
        hr {{
            margin: 1.4rem 0;
            border-color: {CARD_BORDER};
        }}

        /* ---- tabs ---- */
        button[data-baseweb="tab"] {{
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(badge: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="ps-hero">
            <div class="ps-badge">{badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = ""):
    sub_html = f'<div class="ps-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="ps-section-title">{title}</div>
        {sub_html}
        <div class="ps-accent-bar"></div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(icon: str, label: str, value: str, delta: str = "", delta_kind: str = "neutral"):
    delta_html = f'<div class="ps-delta {delta_kind}">{delta}</div>' if delta else ""
    return f"""
        <div class="ps-card">
            <span class="ps-icon">{icon}</span>
            <div class="ps-label">{label}</div>
            <div class="ps-value">{value}</div>
            {delta_html}
        </div>
    """


def stat_strip(icon: str, label: str, value: str, color: str):
    return f"""
        <div class="ps-stat-strip" style="background:{color};">
            <span class="ps-icon">{icon}</span>
            <div class="ps-label">{label}</div>
            <div class="ps-value">{value}</div>
        </div>
    """


def apply_chart_theme(fig, height=420):
    """
    Charts are pinned to an OPAQUE dark canvas (CHART_BG, same surface as
    the metric cards) on purpose, matching the dashboard's dark theme. A
    transparent background would let the page bleed through unpredictably,
    and every label here is drawn in a light ink color for contrast — so a
    fixed dark canvas keeps every label legible everywhere it's used.
    """
    fig.update_layout(
        template=CHART_TEMPLATE,
        font=dict(family=FONT_FAMILY, color=INK, size=13),
        height=height,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        margin=dict(t=50, b=20, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(color=INK, size=12),
        ),
        hoverlabel=dict(bgcolor=CARD_BORDER, font_size=13, font_family=FONT_FAMILY, font_color=INK),
        coloraxis_colorbar=dict(tickfont=dict(color=INK), title_font=dict(color=INK)),
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        tickfont=dict(color=INK), title_font=dict(color=INK),
        linecolor=CARD_BORDER,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=CHART_GRID, zeroline=False,
        tickfont=dict(color=INK), title_font=dict(color=INK),
        linecolor=CARD_BORDER,
    )
    # Any text drawn directly on bars (text_auto, explicit text=) needs an
    # explicit color or it inherits the surrounding page theme — and if it
    # lands *inside* a light-filled bar (e.g. the amber accent), light ink
    # text would disappear into it. Forcing "outside" always places the
    # label on the dark canvas instead, where light ink stays legible.
    fig.update_traces(
        selector=dict(type="bar"),
        textfont=dict(color=INK, family=FONT_FAMILY, size=12),
        textposition="outside",
        cliponaxis=False,
    )
    return fig
