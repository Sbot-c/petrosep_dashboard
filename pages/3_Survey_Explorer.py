import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Survey Explorer | PetroSep", page_icon="🔍", layout="wide")

PRIMARY = "#1C7293"
ACCENT = "#F2A541"


@st.cache_data
def load_data():
    return pd.read_csv("data/survey_data.csv")


df = load_data()

st.title("🔍 Survey Explorer")
st.caption("1,200 synthetic respondents — filter the panel and every chart below updates live")

# ---------- FILTERS ----------
with st.sidebar:
    st.header("Filters")

    city_tier = st.multiselect("City tier", sorted(df["city_tier"].unique()), default=None)
    region = st.multiselect("Region", sorted(df["region"].unique()), default=None)
    vehicle_type = st.multiselect("Vehicle type", sorted(df["vehicle_type"].unique()), default=None)
    price_point = st.multiselect("Price point shown (₹)", sorted(df["price_point_shown_inr"].unique()), default=None)
    income_bucket = st.multiselect("Household income", sorted(df["household_income_bucket"].unique()), default=None)
    e20_compat = st.multiselect("E20 factory compatible", sorted(df["e20_factory_compatible"].unique()), default=None)

    if st.button("Reset filters"):
        st.rerun()

filtered = df.copy()
if city_tier:
    filtered = filtered[filtered["city_tier"].isin(city_tier)]
if region:
    filtered = filtered[filtered["region"].isin(region)]
if vehicle_type:
    filtered = filtered[filtered["vehicle_type"].isin(vehicle_type)]
if price_point:
    filtered = filtered[filtered["price_point_shown_inr"].isin(price_point)]
if income_bucket:
    filtered = filtered[filtered["household_income_bucket"].isin(income_bucket)]
if e20_compat:
    filtered = filtered[filtered["e20_factory_compatible"].isin(e20_compat)]

st.caption(f"Showing **{len(filtered):,}** of {len(df):,} respondents")

if filtered.empty:
    st.warning("No respondents match this filter combination. Try loosening a filter.")
    st.stop()

# ---------- TOP-LINE METRICS ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg. purchase likelihood (1-5)", f"{filtered['purchase_likelihood_1to5'].mean():.2f}")
c2.metric("Would likely buy (4-5)", f"{(filtered['purchase_likelihood_1to5'] >= 4).mean()*100:.0f}%")
promoters = (filtered["nps_0to10"] >= 9).mean() * 100
detractors = (filtered["nps_0to10"] <= 6).mean() * 100
c3.metric("Net Promoter Score", f"{promoters - detractors:.0f}")
c4.metric("Prior awareness of separators", f"{(filtered['prior_awareness_of_separator_devices']=='Yes').mean()*100:.0f}%")

st.divider()

tab_price, tab_demo, tab_pain, tab_payment, tab_raw = st.tabs(
    ["💵 Price sensitivity", "🧑‍🤝‍🧑 Demographics", "⚠️ Pain points", "💳 Payment & motivators", "📋 Raw data"]
)

with tab_price:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Purchase likelihood by price point")
        intent = filtered.groupby("price_point_shown_inr")["purchase_likelihood_1to5"].mean().reset_index()
        fig = px.bar(intent, x="price_point_shown_inr", y="purchase_likelihood_1to5",
                     text_auto=".2f", color_discrete_sequence=[PRIMARY])
        fig.update_layout(yaxis_range=[0, 5], xaxis_title="Price shown (₹)", yaxis_title="Avg. likelihood (1-5)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Distribution of responses by price point")
        dist = filtered.groupby(["price_point_shown_inr", "purchase_likelihood_1to5"]).size().reset_index(name="count")
        fig2 = px.bar(dist, x="price_point_shown_inr", y="count", color="purchase_likelihood_1to5",
                      barmode="stack", color_continuous_scale=["#C0392B", ACCENT, "#2E8B57"])
        fig2.update_layout(xaxis_title="Price shown (₹)", yaxis_title="Respondents", legend_title="Likelihood")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("NPS by price point")
    nps_by_price = filtered.groupby("price_point_shown_inr").apply(
        lambda g: (g["nps_0to10"] >= 9).mean() * 100 - (g["nps_0to10"] <= 6).mean() * 100
    ).reset_index(name="nps")
    fig3 = px.bar(nps_by_price, x="price_point_shown_inr", y="nps", text_auto=".0f",
                  color_discrete_sequence=[ACCENT])
    fig3.update_layout(xaxis_title="Price shown (₹)", yaxis_title="NPS")
    st.plotly_chart(fig3, use_container_width=True)

with tab_demo:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Purchase intent by city tier")
        by_tier = filtered.groupby("city_tier")["purchase_likelihood_1to5"].mean().reset_index()
        fig = px.bar(by_tier, x="city_tier", y="purchase_likelihood_1to5", text_auto=".2f",
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(yaxis_range=[0, 5], xaxis_title="City tier", yaxis_title="Avg. likelihood")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Purchase intent by region")
        by_region = filtered.groupby("region")["purchase_likelihood_1to5"].mean().reset_index()
        fig = px.bar(by_region, x="region", y="purchase_likelihood_1to5", text_auto=".2f",
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(yaxis_range=[0, 5], xaxis_title="Region", yaxis_title="Avg. likelihood")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Purchase intent by vehicle type")
        by_vehicle = filtered.groupby("vehicle_type")["purchase_likelihood_1to5"].mean().reset_index()
        fig = px.bar(by_vehicle, x="vehicle_type", y="purchase_likelihood_1to5", text_auto=".2f",
                     color_discrete_sequence=[ACCENT])
        fig.update_layout(yaxis_range=[0, 5], xaxis_title="Vehicle type", yaxis_title="Avg. likelihood")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Respondents by household income")
        by_income = filtered["household_income_bucket"].value_counts().reset_index()
        by_income.columns = ["household_income_bucket", "count"]
        fig = px.pie(by_income, names="household_income_bucket", values="count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

with tab_pain:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Mileage drop reported")
        mileage = filtered["mileage_drop_bucket"].value_counts().reset_index()
        mileage.columns = ["bucket", "count"]
        fig = px.pie(mileage, names="bucket", values="count", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Government E20 handling sentiment")
        sentiment = filtered["govt_e20_handling_sentiment"].value_counts().reset_index()
        sentiment.columns = ["sentiment", "count"]
        fig = px.bar(sentiment, x="sentiment", y="count", color="sentiment",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Repair/wear increase reported")
        wear = filtered["experienced_repair_wear_increase"].value_counts().reset_index()
        wear.columns = ["reported", "count"]
        fig = px.pie(wear, names="reported", values="count", hole=0.4,
                     color_discrete_sequence=["#C0392B", "#2E8B57"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Wants E0/E10 choice back")
        choice = filtered["wants_e0_e10_choice_back"].value_counts().reset_index()
        choice.columns = ["wants_choice", "count"]
        fig = px.pie(choice, names="wants_choice", values="count", hole=0.4,
                     color_discrete_sequence=["#2E8B57", "#C0392B"])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Purchase intent: pain-affected vs. not")
    pain_compare = filtered.groupby("experienced_mileage_drop")["purchase_likelihood_1to5"].mean().reset_index()
    fig = px.bar(pain_compare, x="experienced_mileage_drop", y="purchase_likelihood_1to5", text_auto=".2f",
                 color_discrete_sequence=[PRIMARY])
    fig.update_layout(xaxis_title="Reported a mileage drop?", yaxis_title="Avg. purchase likelihood",
                       yaxis_range=[0, 5])
    st.plotly_chart(fig, use_container_width=True)

with tab_payment:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Preferred payment mode")
        payment = filtered["preferred_payment_mode"].value_counts().reset_index()
        payment.columns = ["mode", "count"]
        fig = px.bar(payment, x="count", y="mode", orientation="h", color_discrete_sequence=[PRIMARY])
        fig.update_layout(xaxis_title="Respondents", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Primary motivator for purchase")
        motivator = filtered["primary_motivator"].value_counts().reset_index()
        motivator.columns = ["motivator", "count"]
        fig = px.bar(motivator, x="count", y="motivator", orientation="h", color_discrete_sequence=[ACCENT])
        fig.update_layout(xaxis_title="Respondents", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payment mode preference by price point")
    payment_by_price = filtered.groupby(["price_point_shown_inr", "preferred_payment_mode"]).size().reset_index(name="count")
    fig = px.bar(payment_by_price, x="price_point_shown_inr", y="count", color="preferred_payment_mode",
                 barmode="stack")
    fig.update_layout(xaxis_title="Price shown (₹)", yaxis_title="Respondents", legend_title="Payment mode")
    st.plotly_chart(fig, use_container_width=True)

with tab_raw:
    st.subheader("Filtered respondent-level data")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="petrosep_survey_filtered.csv",
        mime="text/csv",
    )
