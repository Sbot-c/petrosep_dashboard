import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styling import (
    PRIMARY, ACCENT, BAD, GOOD, MUTED, INK,
    inject_css, hero, section_header, metric_card, apply_chart_theme,
)

st.set_page_config(page_title="TCO & Payback | PetroSep", page_icon="📈", layout="wide")
inject_css()


@st.cache_data
def load_data():
    tco = pd.read_csv("data/tco_payback.csv")
    survey = pd.read_csv("data/survey_data.csv")
    return tco, survey


tco_df, survey_df = load_data()

hero(
    badge="Total Cost of Ownership",
    title="📈 TCO — Two-Wheeler, 24 Months",
    subtitle="PetroSep vs. a PTFE/Viton retrofit vs. status-quo additives & filter maintenance.",
)

# breakeven calc (fixed data)
breakeven_month = None
for i in range(len(tco_df) - 1):
    m0, m1 = tco_df.iloc[i], tco_df.iloc[i + 1]
    if m0["petrosep_inr"] >= m0["additive_filter_inr"] and m1["petrosep_inr"] < m1["additive_filter_inr"]:
        breakeven_month = (m0["month"], m1["month"])
        break

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(metric_card("💳", "PetroSep cost @ 24mo", f"₹{tco_df['petrosep_inr'].iloc[-1]:,.0f}", "", "neutral"), unsafe_allow_html=True)
with col2:
    st.markdown(metric_card("🧪", "Additive route cost @ 24mo", f"₹{tco_df['additive_filter_inr'].iloc[-1]:,.0f}", "", "neutral"), unsafe_allow_html=True)
with col3:
    st.markdown(metric_card("🔩", "PTFE/Viton retrofit (fixed)", f"₹{tco_df['ptfe_viton_inr'].iloc[-1]:,.0f}", "One-time, no maintenance modeled", "neutral"), unsafe_allow_html=True)
with col4:
    savings_24mo = tco_df["additive_filter_inr"].iloc[-1] - tco_df["petrosep_inr"].iloc[-1]
    st.markdown(metric_card("⏱️", "Breakeven vs. additives", "~Month 10-12", f"₹{savings_24mo:,.0f} saved by month 24", "good"), unsafe_allow_html=True)

st.divider()

section_header("Cumulative cost over 24 months")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["petrosep_inr"],
    mode="lines+markers", name="PetroSep (device + cartridges)",
    line=dict(color=PRIMARY, width=3), marker=dict(size=7),
))
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["ptfe_viton_inr"],
    mode="lines+markers", name="PTFE/Viton retrofit (one-time)",
    line=dict(color=ACCENT, width=3, dash="dash"), marker=dict(size=7),
))
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["additive_filter_inr"],
    mode="lines+markers", name="Additive + filter maintenance",
    line=dict(color=BAD, width=3, dash="dot"), marker=dict(size=7),
))
fig.update_layout(xaxis_title="Month", yaxis_title="Cumulative cost (₹)")
apply_chart_theme(fig, height=500)
st.plotly_chart(fig, use_container_width=True)

st.info(
    "Recurring additive + filter spend overtakes PetroSep's one-time device cost by roughly "
    "month 10, and keeps climbing. A cab or delivery vehicle drives 3-5x the monthly distance "
    "of a personal rider — compressing this same payback to under 3 months (see the pitch deck's "
    "GTM Phase 1 assumptions for the fleet case)."
)

with st.expander("See the underlying data"):
    st.dataframe(tco_df, use_container_width=True, hide_index=True)

st.divider()

# ---------- INTERACTIVE BREAKEVEN ----------
section_header("Try your own assumptions", "Adjust the additive-route monthly spend and see how breakeven shifts")

slider_col, chart_col = st.columns([1, 2])

with slider_col:
    if "monthly_additive_val" not in st.session_state:
        st.session_state["monthly_additive_val"] = 400

    monthly_additive = st.slider(
        "Additive + filter monthly cost (₹)",
        min_value=100, max_value=800, step=25,
        key="monthly_additive_val",
    )

    st.markdown("**Or estimate from a vehicle profile:**")
    vehicle_options = sorted(survey_df["vehicle_type"].dropna().unique())
    chosen_vehicle = st.selectbox("Vehicle type (from survey panel)", ["— none —"] + vehicle_options)

    if chosen_vehicle != "— none —":
        avg_fuel_spend = survey_df.loc[survey_df["vehicle_type"] == chosen_vehicle, "monthly_fuel_spend_inr"].mean()
        overall_avg_fuel_spend = survey_df["monthly_fuel_spend_inr"].mean()
        # scale the 400 rs/mo baseline additive assumption by how much more/less
        # this vehicle type spends on fuel than the panel average
        suggested_additive = 400 * (avg_fuel_spend / overall_avg_fuel_spend)
        suggested_additive = int(round(min(800, max(100, suggested_additive)) / 25) * 25)
        st.caption(
            f"Avg. monthly fuel spend for **{chosen_vehicle}** owners in the survey: "
            f"₹{avg_fuel_spend:,.0f} (panel avg: ₹{overall_avg_fuel_spend:,.0f}). "
            f"Suggested additive spend: **₹{suggested_additive:,.0f}/mo**."
        )
        if st.button("Apply suggested value"):
            st.session_state["monthly_additive_val"] = suggested_additive
            st.rerun()

with chart_col:
    months = list(range(0, 25))
    petrosep_line = [4999 + 180 * (m // 6) for m in months]
    additive_line = [monthly_additive * m for m in months]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=months, y=petrosep_line, mode="lines", name="PetroSep", line=dict(color=PRIMARY, width=3)))
    fig2.add_trace(go.Scatter(x=months, y=additive_line, mode="lines", name="Additive route (your assumption)", line=dict(color=BAD, width=3, dash="dot")))
    fig2.update_layout(xaxis_title="Month", yaxis_title="Cumulative cost (₹)")
    apply_chart_theme(fig2, height=420)
    st.plotly_chart(fig2, use_container_width=True)

    crossover = next((m for m in months if additive_line[m] > petrosep_line[m]), None)
    if crossover:
        st.success(f"At ₹{monthly_additive:,.0f}/month for additives, PetroSep breaks even around **month {crossover}**.")
    else:
        st.warning("At this monthly spend, the additive route never overtakes PetroSep's cost within 24 months.")
