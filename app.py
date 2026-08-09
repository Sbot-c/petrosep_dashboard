import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="PetroSep | Investor Data Room",
    page_icon="⛽",
    layout="wide",
)

PRIMARY = "#1C7293"
ACCENT = "#F2A541"
GOOD = "#2E8B57"
BAD = "#C0392B"


@st.cache_data
def load_data():
    cost = pd.read_csv("data/cost_buildup.csv")
    pricing = pd.read_csv("data/pricing_scenarios.csv")
    tco = pd.read_csv("data/tco_payback.csv")
    payment = pd.read_csv("data/payment_structures.csv")
    survey = pd.read_csv("data/survey_data.csv")
    return cost, pricing, tco, payment, survey


cost_df, pricing_df, tco_df, payment_df, survey_df = load_data()

# ---------- HEADER ----------
st.title("⛽ PetroSep — Investor Data Room")
st.caption("AquaSep Technologies · Reusable water-based ethanol separator for India's E20 petrol")

st.markdown(
    """
PetroSep pulls ethanol back out of India's mandatory E20 petrol, restoring near-pure fuel
for the 130M+ vehicles the mandate left behind. This dashboard backs the pitch deck's
pricing and market claims with the underlying cost model and a 1,200-respondent
synthetic market survey — filter, cross-tab, and stress-test every number yourself.
"""
)

st.divider()

# ---------- KEY METRICS ----------
recommended = pricing_df.loc[pricing_df["price_strategy"].str.contains("Standard"), "retail_price_inr"].iloc[0]
recommended_margin = pricing_df.loc[pricing_df["price_strategy"].str.contains("Standard"), "gross_margin_pct"].iloc[0]
fully_loaded_cost = cost_df["unit_cost_inr"].sum()
avg_purchase_intent = survey_df["purchase_likelihood_1to5"].mean()
top2box = (survey_df["purchase_likelihood_1to5"] >= 4).mean() * 100
avg_nps = survey_df["nps_0to10"].mean()
promoters = (survey_df["nps_0to10"] >= 9).mean() * 100
detractors = (survey_df["nps_0to10"] <= 6).mean() * 100
nps_score = promoters - detractors

col1, col2, col3, col4 = st.columns(4)
col1.metric("Recommended retail price", f"₹{recommended:,.0f}", help="Standard post-pilot MRP")
col2.metric("Gross margin at MRP", f"{recommended_margin*100:.1f}%")
col3.metric("Fully-loaded unit cost", f"₹{fully_loaded_cost:,.0f}")
col4.metric("Survey respondents", f"{len(survey_df):,}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg. purchase intent (1-5)", f"{avg_purchase_intent:.2f}")
col6.metric("Would likely buy (4-5 rated)", f"{top2box:.0f}%")
col7.metric("Avg. NPS rating (0-10)", f"{avg_nps:.1f}")
col8.metric("Net Promoter Score", f"{nps_score:.0f}")

st.divider()

# ---------- PRICING SNAPSHOT ----------
left, right = st.columns([3, 2])

with left:
    st.subheader("Pricing scenarios at a glance")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Fully-loaded cost",
        x=pricing_df["price_strategy"],
        y=[fully_loaded_cost] * len(pricing_df),
        marker_color="#B0B7BD",
    ))
    fig.add_trace(go.Bar(
        name="Gross margin",
        x=pricing_df["price_strategy"],
        y=pricing_df["gross_margin_inr"],
        marker_color=PRIMARY,
    ))
    fig.update_layout(
        barmode="stack",
        yaxis_title="₹ per unit",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420,
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Every price point sits on top of the same ₹2,394 fully-loaded cost — see **Pricing & Cost** for the full BOM breakdown.")

with right:
    st.subheader("Purchase intent by price point")
    intent_by_price = (
        survey_df.groupby("price_point_shown_inr")["purchase_likelihood_1to5"]
        .mean()
        .reset_index()
        .sort_values("price_point_shown_inr")
    )
    fig2 = px.bar(
        intent_by_price,
        x="price_point_shown_inr",
        y="purchase_likelihood_1to5",
        text_auto=".2f",
        color_discrete_sequence=[ACCENT],
    )
    fig2.update_layout(
        xaxis_title="Price point shown (₹)",
        yaxis_title="Avg. purchase likelihood (1-5)",
        yaxis_range=[0, 5],
        height=420,
        margin=dict(t=40, b=10),
    )
    fig2.update_traces(textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("This is the A/B/C price test (₹3,999 / ₹4,499 / ₹5,999) from the synthetic survey.")

st.divider()

st.subheader("Why now — the market pain backing this pitch")
c1, c2, c3 = st.columns(3)
mileage_pct = (survey_df["experienced_mileage_drop"] == "Yes").mean() * 100
wear_pct = (survey_df["experienced_repair_wear_increase"] == "Yes").mean() * 100
disastrous_pct = (survey_df["govt_e20_handling_sentiment"] == "Disastrous").mean() * 100
c1.metric("Report a mileage drop", f"{mileage_pct:.0f}%")
c2.metric("Report more wear/repairs", f"{wear_pct:.0f}%")
c3.metric("Rate govt E20 rollout 'Disastrous'", f"{disastrous_pct:.0f}%")

st.info(
    "Use the pages in the sidebar to drill into **Pricing & Cost**, the **TCO / Payback** model, "
    "and the full **Survey Explorer** with live filters across city tier, region, vehicle type and more."
)

st.caption("Data: PetroSep_Pricing_Model.xlsx and PetroSep_Synthetic_Survey.xlsx — figures are illustrative and pre-diligence.")
