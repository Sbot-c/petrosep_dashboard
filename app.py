import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.styling import (
    PRIMARY, PRIMARY_LIGHT, ACCENT, GOOD, BAD, INK, TRACK_BG,
    inject_css, hero, section_header, metric_card, stat_strip, apply_chart_theme,
)

st.set_page_config(
    page_title="PetroSep | Investor Data Room",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


@st.cache_data
def load_data():
    cost = pd.read_csv("data/cost_buildup.csv")
    pricing = pd.read_csv("data/pricing_scenarios.csv")
    tco = pd.read_csv("data/tco_payback.csv")
    payment = pd.read_csv("data/payment_structures.csv")
    survey = pd.read_csv("data/survey_data.csv")
    return cost, pricing, tco, payment, survey


cost_df, pricing_df, tco_df, payment_df, survey_df = load_data()

# ---------- SIDEBAR BRANDING ----------
with st.sidebar:
    st.markdown("### ⛽ PetroSep")
    st.caption("AquaSep Technologies")
    st.markdown("---")
    st.markdown(
        "**Data room contents**\n\n"
        "- 🏠 Overview\n"
        "- 💰 Pricing & Cost\n"
        "- 📈 TCO & Payback\n"
        "- 🔍 Survey Explorer\n"
        "- 🧮 Scenario Modeling\n"
    )
    st.markdown("---")
    st.caption("All figures illustrative & pre-diligence. Synthetic survey panel, n = 1,200.")

# ---------- HERO ----------
hero(
    badge="Investor Data Room",
    title="⛽ PetroSep — restoring petrol for India's E20 fleet",
    subtitle=(
        "PetroSep pulls ethanol back out of India's mandatory E20 petrol, restoring near-pure "
        "fuel for the 130M+ vehicles the mandate left behind. This dashboard backs the pitch "
        "deck's pricing and market claims with the underlying cost model and a 1,200-respondent "
        "synthetic market survey — filter, cross-tab, and stress-test every number yourself."
    ),
)

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

section_header("Headline numbers", "Pulled live from the cost model and the survey panel")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("🏷️", "Recommended retail price", f"₹{recommended:,.0f}", "Standard post-pilot MRP", "neutral"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("📊", "Gross margin at MRP", f"{recommended_margin*100:.1f}%", "vs. 40.1% at pilot price", "good"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("🧾", "Fully-loaded unit cost", f"₹{fully_loaded_cost:,.0f}", "BOM + assembly + logistics + reserve", "neutral"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("🧑‍🤝‍🧑", "Survey respondents", f"{len(survey_df):,}", "Synthetic panel, 2 waves", "neutral"), unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.markdown(metric_card("💡", "Avg. purchase intent (1-5)", f"{avg_purchase_intent:.2f}", "", "neutral"), unsafe_allow_html=True)
with c6:
    st.markdown(metric_card("✅", "Would likely buy (4-5 rated)", f"{top2box:.0f}%", "", "good"), unsafe_allow_html=True)
with c7:
    st.markdown(metric_card("⭐", "Avg. NPS rating (0-10)", f"{avg_nps:.1f}", "", "neutral"), unsafe_allow_html=True)
with c8:
    delta_kind = "good" if nps_score >= 0 else "bad"
    st.markdown(metric_card("📣", "Net Promoter Score", f"{nps_score:.0f}", f"{promoters:.0f}% promoters / {detractors:.0f}% detractors", delta_kind), unsafe_allow_html=True)

st.divider()

# ---------- PRICING SNAPSHOT ----------
left, right = st.columns([3, 2])

with left:
    section_header("Pricing scenarios at a glance", "Every price point sits on the same fully-loaded cost base")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Fully-loaded cost",
        x=pricing_df["price_strategy"],
        y=[fully_loaded_cost] * len(pricing_df),
        marker_color=TRACK_BG,
    ))
    fig.add_trace(go.Bar(
        name="Gross margin",
        x=pricing_df["price_strategy"],
        y=pricing_df["gross_margin_inr"],
        marker_color=PRIMARY,
        text=[f"{p*100:.0f}% margin" for p in pricing_df["gross_margin_pct"]],
        textposition="outside",
    ))
    fig.update_layout(barmode="stack", yaxis_title="₹ per unit")
    apply_chart_theme(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Every price point sits on top of the same ₹{fully_loaded_cost:,.0f} fully-loaded cost — see **Pricing & Cost** for the full BOM breakdown.")

with right:
    section_header("Purchase intent by price point", "A/B/C price test from the synthetic survey")
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
    )
    fig2.update_traces(textposition="outside")
    apply_chart_theme(fig2, height=420)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("₹3,999 / ₹4,499 / ₹5,999 price points tested across the panel.")

st.divider()

# ---------- WHY NOW ----------
section_header("Why now — the market pain backing this pitch", "Self-reported pain from E20-affected vehicle owners")

mileage_pct = (survey_df["experienced_mileage_drop"] == "Yes").mean() * 100
wear_pct = (survey_df["experienced_repair_wear_increase"] == "Yes").mean() * 100
disastrous_pct = (survey_df["govt_e20_handling_sentiment"] == "Disastrous").mean() * 100

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(stat_strip("⛽", "Report a mileage drop", f"{mileage_pct:.0f}%", BAD), unsafe_allow_html=True)
with s2:
    st.markdown(stat_strip("🔧", "Report more wear/repairs", f"{wear_pct:.0f}%", ACCENT), unsafe_allow_html=True)
with s3:
    st.markdown(stat_strip("📉", "Rate govt E20 rollout 'Disastrous'", f"{disastrous_pct:.0f}%", PRIMARY), unsafe_allow_html=True)

st.divider()

# ---------- QUICK NAV ----------
section_header("Explore the data room")
nav_items = [
    ("💰", "Pricing & Cost", "BOM waterfall, margin by scenario, payment structures", "pages/1_Pricing_and_Cost.py"),
    ("📈", "TCO & Payback", "24-month cost vs. PTFE/Viton and additives", "pages/2_TCO_and_Payback.py"),
    ("🔍", "Survey Explorer", "Full 1,200-respondent panel, live filters", "pages/3_Survey_Explorer.py"),
    ("🧮", "Scenario Modeling", "Stress-test price, cost and volume assumptions", "pages/4_Scenario_Modeling.py"),
]
nav_cols = st.columns(4)
for col, (icon, title, desc, path) in zip(nav_cols, nav_items):
    with col:
        with st.container(border=True):
            st.page_link(path, label=title, icon=icon)
            st.caption(desc)

st.caption("Data: PetroSep_Pricing_Model.xlsx and PetroSep_Synthetic_Survey.xlsx — figures are illustrative and pre-diligence.")
