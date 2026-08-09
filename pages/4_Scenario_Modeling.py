import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styling import (
    PRIMARY, PRIMARY_DARK, ACCENT, GOOD, BAD, MUTED, INK,
    inject_css, hero, section_header, metric_card, apply_chart_theme,
)

st.set_page_config(page_title="Scenario Modeling | PetroSep", page_icon="🧮", layout="wide")
inject_css()


@st.cache_data
def load_data():
    cost = pd.read_csv("data/cost_buildup.csv")
    survey = pd.read_csv("data/survey_data.csv")
    return cost, survey


cost_df, survey_df = load_data()
total_cost = cost_df["unit_cost_inr"].sum()

hero(
    badge="What-If Tool",
    title="🧮 Scenario Modeling",
    subtitle=(
        "Combine the cost model with the survey's price-response curve to project revenue, "
        "margin, and units at any price point and addressable-market size you assume."
    ),
)

# ---------- DEMAND CURVE FROM SURVEY ----------
# purchase_likelihood_1to5 >= 4 ("would likely buy") rate at each tested price point,
# used as a simple top-2-box conversion proxy. We interpolate/extrapolate linearly
# across the requested price range so the tool responds smoothly to any price.
intent_by_price = (
    survey_df.groupby("price_point_shown_inr")["purchase_likelihood_1to5"]
    .apply(lambda s: (s >= 4).mean())
    .reset_index()
    .sort_values("price_point_shown_inr")
)
known_prices = intent_by_price["price_point_shown_inr"].to_numpy()
known_conv = intent_by_price["purchase_likelihood_1to5"].to_numpy()


def conversion_rate(price):
    """Linear interpolation/extrapolation over the surveyed top-2-box conversion rate."""
    rate = np.interp(price, known_prices, known_conv)
    return float(np.clip(rate, 0.01, 0.95))


section_header(
    "Step 1 — set your market and price assumptions",
    "Conversion rate is interpolated from the survey's top-2-box ('would likely buy') response at each tested price point",
)

s1, s2, s3 = st.columns(3)
with s1:
    tam = st.number_input(
        "Addressable riders reached (TAM × reach)", min_value=10_000, max_value=50_000_000,
        value=1_000_000, step=50_000,
        help="Number of E20-affected riders your GTM plan actually reaches with awareness (not all 130M+ vehicles).",
    )
with s2:
    price = st.slider("Retail price (₹)", min_value=2999, max_value=7999, value=4999, step=50)
with s3:
    cost_inflation = st.slider("Cost inflation vs. base BOM (%)", min_value=-20, max_value=40, value=0, step=1)

stressed_cost = total_cost * (1 + cost_inflation / 100)
conv = conversion_rate(price)
est_units = tam * conv
est_revenue = est_units * price
est_margin_per_unit = price - stressed_cost
est_gross_profit = est_units * est_margin_per_unit
est_margin_pct = est_margin_per_unit / price if price else 0

st.divider()
section_header("Step 2 — projected outcome at this price point")

r1, r2, r3, r4 = st.columns(4)
with r1:
    st.markdown(metric_card("🎯", "Estimated conversion (survey-derived)", f"{conv*100:.1f}%", "Top-2-box @ this price", "neutral"), unsafe_allow_html=True)
with r2:
    st.markdown(metric_card("📦", "Estimated units sold", f"{est_units:,.0f}", "", "neutral"), unsafe_allow_html=True)
with r3:
    st.markdown(metric_card("💰", "Estimated revenue", f"₹{est_revenue:,.0f}", "", "neutral"), unsafe_allow_html=True)
with r4:
    delta_kind = "good" if est_margin_pct >= 0.4 else ("neutral" if est_margin_pct >= 0.2 else "bad")
    st.markdown(metric_card("📊", "Estimated gross profit", f"₹{est_gross_profit:,.0f}", f"{est_margin_pct*100:.1f}% margin/unit", delta_kind), unsafe_allow_html=True)

st.caption(
    "⚠️ Illustrative only: conversion is extrapolated from a 1,200-respondent synthetic survey "
    "with 3 tested price points, and assumes 100% of 'would likely buy' respondents convert to a sale. "
    "Treat as a directional sensitivity tool, not a revenue forecast."
)

st.divider()

# ---------- REVENUE & MARGIN CURVES ACROSS PRICE RANGE ----------
section_header("Revenue and gross profit across the full price range", "Where does the model suggest revenue and profit peak?")

price_range = np.arange(2999, 8000, 50)
conv_curve = np.array([conversion_rate(p) for p in price_range])
units_curve = tam * conv_curve
revenue_curve = units_curve * price_range
profit_curve = units_curve * (price_range - stressed_cost)

best_rev_price = price_range[np.argmax(revenue_curve)]
best_profit_price = price_range[np.argmax(profit_curve)]

fig = go.Figure()
fig.add_trace(go.Scatter(x=price_range, y=revenue_curve, name="Estimated revenue (₹)", line=dict(color=PRIMARY, width=3), yaxis="y1"))
fig.add_trace(go.Scatter(x=price_range, y=profit_curve, name="Estimated gross profit (₹)", line=dict(color=GOOD, width=3, dash="dash"), yaxis="y1"))
fig.add_trace(go.Scatter(x=[price], y=[est_revenue], mode="markers", name="Your price", marker=dict(color=ACCENT, size=14, line=dict(color=PRIMARY_DARK, width=2))))
fig.update_layout(xaxis_title="Retail price (₹)", yaxis_title="₹")
apply_chart_theme(fig, height=440)
st.plotly_chart(fig, use_container_width=True)

b1, b2 = st.columns(2)
with b1:
    st.markdown(metric_card("🏆", "Revenue-maximizing price", f"₹{best_rev_price:,.0f}", "", "neutral"), unsafe_allow_html=True)
with b2:
    st.markdown(metric_card("🏆", "Profit-maximizing price", f"₹{best_profit_price:,.0f}", "", "good"), unsafe_allow_html=True)

st.divider()

# ---------- CONVERSION CURVE FROM SURVEY ----------
section_header("The underlying conversion curve", "Raw survey signal used to drive the projections above")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=known_prices, y=known_conv * 100, mode="markers+lines", name="Surveyed price points",
    line=dict(color=MUTED, width=2, dash="dot"), marker=dict(size=12, color=PRIMARY),
))
fig2.add_trace(go.Scatter(
    x=price_range, y=conv_curve * 100, mode="lines", name="Interpolated curve",
    line=dict(color=ACCENT, width=2),
))
fig2.update_layout(xaxis_title="Retail price (₹)", yaxis_title="Top-2-box conversion (%)")
apply_chart_theme(fig2, height=360)
st.plotly_chart(fig2, use_container_width=True)
st.caption(
    "Solid markers are the actual ₹3,999 / ₹4,499 / ₹5,999 tests from the survey panel; the line "
    "is a linear interpolation/extrapolation used to price anything in between or beyond."
)
