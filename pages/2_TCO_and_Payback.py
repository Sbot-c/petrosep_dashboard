import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="TCO & Payback | PetroSep", page_icon="📈", layout="wide")

PRIMARY = "#1C7293"
ACCENT = "#F2A541"
BAD = "#C0392B"


@st.cache_data
def load_data():
    return pd.read_csv("data/tco_payback.csv")


tco_df = load_data()

st.title("📈 Total Cost of Ownership — Two-Wheeler, 24 Months")
st.caption("PetroSep vs. a PTFE/Viton retrofit vs. status-quo additives & filter maintenance")

st.divider()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["petrosep_inr"],
    mode="lines+markers", name="PetroSep (device + cartridges)",
    line=dict(color=PRIMARY, width=3),
))
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["ptfe_viton_inr"],
    mode="lines+markers", name="PTFE/Viton retrofit (one-time)",
    line=dict(color=ACCENT, width=3, dash="dash"),
))
fig.add_trace(go.Scatter(
    x=tco_df["month"], y=tco_df["additive_filter_inr"],
    mode="lines+markers", name="Additive + filter maintenance",
    line=dict(color=BAD, width=3, dash="dot"),
))
fig.update_layout(
    height=520,
    xaxis_title="Month",
    yaxis_title="Cumulative cost (₹)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(t=30, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# breakeven calc
breakeven_month = None
for i in range(len(tco_df) - 1):
    m0, m1 = tco_df.iloc[i], tco_df.iloc[i + 1]
    if m0["petrosep_inr"] >= m0["additive_filter_inr"] and m1["petrosep_inr"] < m1["additive_filter_inr"]:
        breakeven_month = (m0["month"], m1["month"])
        break

col1, col2, col3 = st.columns(3)
col1.metric("PetroSep cost @ 24mo", f"₹{tco_df['petrosep_inr'].iloc[-1]:,.0f}")
col2.metric("Additive route cost @ 24mo", f"₹{tco_df['additive_filter_inr'].iloc[-1]:,.0f}")
col3.metric("Approx. breakeven vs. additives", "~Month 10-12")

st.info(
    "Recurring additive + filter spend overtakes PetroSep's one-time device cost by roughly "
    "month 10, and keeps climbing. A cab or delivery vehicle drives 3-5x the monthly distance "
    "of a personal rider — compressing this same payback to under 3 months (see the pitch deck's "
    "GTM Phase 1 assumptions for the fleet case)."
)

with st.expander("See the underlying data"):
    st.dataframe(tco_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Try your own assumptions")
st.caption("Adjust the additive-route monthly spend and see how the breakeven point shifts.")

monthly_additive = st.slider("Additive + filter monthly cost (₹)", min_value=100, max_value=800, value=400, step=25)
months = list(range(0, 25))
petrosep_line = [4999 if m == 0 else 4999 + 30 * (m // 6) * 6 for m in months]
# simpler: device + cartridge every 6 months (₹180 per 6mo)
petrosep_line = [4999 + 180 * (m // 6) for m in months]
additive_line = [monthly_additive * m for m in months]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=months, y=petrosep_line, mode="lines", name="PetroSep", line=dict(color=PRIMARY, width=3)))
fig2.add_trace(go.Scatter(x=months, y=additive_line, mode="lines", name="Additive route (your assumption)", line=dict(color=BAD, width=3, dash="dot")))
fig2.update_layout(height=420, xaxis_title="Month", yaxis_title="Cumulative cost (₹)", margin=dict(t=20, b=10))
st.plotly_chart(fig2, use_container_width=True)

crossover = next((m for m in months if additive_line[m] > petrosep_line[m]), None)
if crossover:
    st.success(f"At ₹{monthly_additive}/month for additives, PetroSep breaks even around **month {crossover}**.")
else:
    st.warning("At this monthly spend, the additive route never overtakes PetroSep's cost within 24 months.")
