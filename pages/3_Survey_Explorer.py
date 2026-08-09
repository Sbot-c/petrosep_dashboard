import pandas as pd
import plotly.express as px
import streamlit as st

from utils.styling import (
    PRIMARY, ACCENT, GOOD, BAD, MUTED, INK,
    inject_css, hero, section_header, metric_card, apply_chart_theme,
)

st.set_page_config(page_title="Survey Explorer | PetroSep", page_icon="🔍", layout="wide")
inject_css()


@st.cache_data
def load_data():
    return pd.read_csv("data/survey_data.csv")


df = load_data()

hero(
    badge="Market Survey",
    title="🔍 Survey Explorer",
    subtitle="1,200 synthetic respondents. Each tab below has its own filters, scoped to what that tab shows.",
)


def local_filters(base_df, dims, key_prefix, help_text=None):
    """
    Renders a small filter row scoped to a single tab (not the whole page).
    dims: list of (label, column_name) tuples relevant to that tab's charts.
    Returns the filtered dataframe; also prints active-filter pills + a count.
    """
    with st.expander("🔧 Filter this view", expanded=False):
        if help_text:
            st.caption(help_text)
        selections = {}
        cols = st.columns(len(dims))
        for col, (label, colname) in zip(cols, dims):
            with col:
                selections[colname] = st.multiselect(
                    label, sorted(base_df[colname].unique()), key=f"{key_prefix}_{colname}"
                )

    result = base_df.copy()
    active = []
    for label, colname in dims:
        vals = selections[colname]
        if vals:
            result = result[result[colname].isin(vals)]
            active.append(f"{label}: {', '.join(str(v) for v in vals)}")

    if active:
        pills = "".join(f'<span class="ps-pill">{f}</span>' for f in active)
        st.markdown(pills, unsafe_allow_html=True)
    st.caption(f"Showing **{len(result):,}** of {len(base_df):,} respondents in this view")
    return result


# ---------- PANEL-WIDE HEADLINE (always the full 1,200, unfiltered) ----------
section_header("Panel headline", "Whole 1,200-respondent panel — each tab below narrows from here independently")

promoters = (df["nps_0to10"] >= 9).mean() * 100
detractors = (df["nps_0to10"] <= 6).mean() * 100
nps = promoters - detractors

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("💡", "Avg. purchase likelihood (1-5)", f"{df['purchase_likelihood_1to5'].mean():.2f}", "", "neutral"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("✅", "Would likely buy (4-5)", f"{(df['purchase_likelihood_1to5'] >= 4).mean()*100:.0f}%", "", "good"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("📣", "Net Promoter Score", f"{nps:.0f}", "", "good" if nps >= 0 else "bad"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("👁️", "Prior awareness of separators", f"{(df['prior_awareness_of_separator_devices']=='Yes').mean()*100:.0f}%", "", "neutral"), unsafe_allow_html=True)

st.divider()

tab_price, tab_demo, tab_pain, tab_payment, tab_cross, tab_raw = st.tabs(
    ["💵 Price sensitivity", "🧑‍🤝‍🧑 Demographics", "⚠️ Pain points", "💳 Payment & motivators", "🧩 Cross-tab builder", "📋 Raw data"]
)

# ---------- PRICE SENSITIVITY ----------
with tab_price:
    filtered = local_filters(
        df,
        [("City tier", "city_tier"), ("Vehicle type", "vehicle_type"), ("Household income", "household_income_bucket")],
        key_prefix="price",
    )
    if filtered.empty:
        st.warning("No respondents match this filter combination. Try loosening a filter.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            section_header("Purchase likelihood by price point")
            intent = filtered.groupby("price_point_shown_inr")["purchase_likelihood_1to5"].mean().reset_index()
            fig = px.bar(intent, x="price_point_shown_inr", y="purchase_likelihood_1to5",
                         text_auto=".2f", color_discrete_sequence=[PRIMARY])
            fig.update_layout(yaxis_range=[0, 5], xaxis_title="Price shown (₹)", yaxis_title="Avg. likelihood (1-5)")
            apply_chart_theme(fig, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            section_header("Distribution of responses by price point")
            dist = filtered.groupby(["price_point_shown_inr", "purchase_likelihood_1to5"]).size().reset_index(name="count")
            fig2 = px.bar(dist, x="price_point_shown_inr", y="count", color="purchase_likelihood_1to5",
                          barmode="stack", color_continuous_scale=[BAD, ACCENT, GOOD])
            fig2.update_layout(xaxis_title="Price shown (₹)", yaxis_title="Respondents", legend_title="Likelihood")
            apply_chart_theme(fig2, height=380)
            st.plotly_chart(fig2, use_container_width=True)

        section_header("NPS by price point")
        nps_by_price = filtered.groupby("price_point_shown_inr").apply(
            lambda g: (g["nps_0to10"] >= 9).mean() * 100 - (g["nps_0to10"] <= 6).mean() * 100
        ).reset_index(name="nps")
        fig3 = px.bar(nps_by_price, x="price_point_shown_inr", y="nps", text_auto=".0f",
                      color_discrete_sequence=[ACCENT])
        fig3.update_layout(xaxis_title="Price shown (₹)", yaxis_title="NPS")
        apply_chart_theme(fig3, height=340)
        st.plotly_chart(fig3, use_container_width=True)

# ---------- DEMOGRAPHICS ----------
with tab_demo:
    filtered = local_filters(
        df,
        [("Price point shown (₹)", "price_point_shown_inr"), ("E20 factory compatible", "e20_factory_compatible")],
        key_prefix="demo",
    )
    if filtered.empty:
        st.warning("No respondents match this filter combination. Try loosening a filter.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            section_header("Purchase intent by city tier")
            by_tier = filtered.groupby("city_tier")["purchase_likelihood_1to5"].mean().reset_index()
            fig = px.bar(by_tier, x="city_tier", y="purchase_likelihood_1to5", text_auto=".2f",
                         color_discrete_sequence=[PRIMARY])
            fig.update_layout(yaxis_range=[0, 5], xaxis_title="City tier", yaxis_title="Avg. likelihood")
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

            section_header("Purchase intent by region")
            by_region = filtered.groupby("region")["purchase_likelihood_1to5"].mean().reset_index()
            fig = px.bar(by_region, x="region", y="purchase_likelihood_1to5", text_auto=".2f",
                         color_discrete_sequence=[PRIMARY])
            fig.update_layout(yaxis_range=[0, 5], xaxis_title="Region", yaxis_title="Avg. likelihood")
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            section_header("Purchase intent by vehicle type")
            by_vehicle = filtered.groupby("vehicle_type")["purchase_likelihood_1to5"].mean().reset_index()
            fig = px.bar(by_vehicle, x="vehicle_type", y="purchase_likelihood_1to5", text_auto=".2f",
                         color_discrete_sequence=[ACCENT])
            fig.update_layout(yaxis_range=[0, 5], xaxis_title="Vehicle type", yaxis_title="Avg. likelihood")
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

            section_header("Respondents by household income")
            by_income = filtered["household_income_bucket"].value_counts().reset_index()
            by_income.columns = ["household_income_bucket", "count"]
            fig = px.pie(by_income, names="household_income_bucket", values="count", hole=0.45,
                         color_discrete_sequence=px.colors.sequential.Teal)
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

# ---------- PAIN POINTS ----------
with tab_pain:
    filtered = local_filters(
        df,
        [("City tier", "city_tier"), ("Vehicle type", "vehicle_type")],
        key_prefix="pain",
    )
    if filtered.empty:
        st.warning("No respondents match this filter combination. Try loosening a filter.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            section_header("Mileage drop reported")
            mileage = filtered["mileage_drop_bucket"].value_counts().reset_index()
            mileage.columns = ["bucket", "count"]
            fig = px.pie(mileage, names="bucket", values="count", hole=0.45,
                         color_discrete_sequence=px.colors.sequential.Teal)
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

            section_header("Government E20 handling sentiment")
            sentiment = filtered["govt_e20_handling_sentiment"].value_counts().reset_index()
            sentiment.columns = ["sentiment", "count"]
            fig = px.bar(sentiment, x="sentiment", y="count", color="sentiment",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            section_header("Repair/wear increase reported")
            wear = filtered["experienced_repair_wear_increase"].value_counts().reset_index()
            wear.columns = ["reported", "count"]
            fig = px.pie(wear, names="reported", values="count", hole=0.45,
                         color_discrete_sequence=[BAD, GOOD])
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

            section_header("Wants E0/E10 choice back")
            choice = filtered["wants_e0_e10_choice_back"].value_counts().reset_index()
            choice.columns = ["wants_choice", "count"]
            fig = px.pie(choice, names="wants_choice", values="count", hole=0.45,
                         color_discrete_sequence=[GOOD, BAD])
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

        section_header("Purchase intent: pain-affected vs. not")
        pain_compare = filtered.groupby("experienced_mileage_drop")["purchase_likelihood_1to5"].mean().reset_index()
        fig = px.bar(pain_compare, x="experienced_mileage_drop", y="purchase_likelihood_1to5", text_auto=".2f",
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(xaxis_title="Reported a mileage drop?", yaxis_title="Avg. purchase likelihood",
                           yaxis_range=[0, 5])
        apply_chart_theme(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)

# ---------- PAYMENT & MOTIVATORS ----------
with tab_payment:
    filtered = local_filters(
        df,
        [("City tier", "city_tier"), ("Price point shown (₹)", "price_point_shown_inr")],
        key_prefix="payment",
    )
    if filtered.empty:
        st.warning("No respondents match this filter combination. Try loosening a filter.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            section_header("Preferred payment mode")
            payment = filtered["preferred_payment_mode"].value_counts().reset_index()
            payment.columns = ["mode", "count"]
            fig = px.bar(payment, x="count", y="mode", orientation="h", color_discrete_sequence=[PRIMARY])
            fig.update_layout(xaxis_title="Respondents", yaxis_title="")
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            section_header("Primary motivator for purchase")
            motivator = filtered["primary_motivator"].value_counts().reset_index()
            motivator.columns = ["motivator", "count"]
            fig = px.bar(motivator, x="count", y="motivator", orientation="h", color_discrete_sequence=[ACCENT])
            fig.update_layout(xaxis_title="Respondents", yaxis_title="")
            apply_chart_theme(fig, height=340)
            st.plotly_chart(fig, use_container_width=True)

        section_header("Payment mode preference by price point")
        payment_by_price = filtered.groupby(["price_point_shown_inr", "preferred_payment_mode"]).size().reset_index(name="count")
        fig = px.bar(payment_by_price, x="price_point_shown_inr", y="count", color="preferred_payment_mode",
                     barmode="stack")
        fig.update_layout(xaxis_title="Price shown (₹)", yaxis_title="Respondents", legend_title="Payment mode")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

# ---------- CROSS-TAB BUILDER ----------
with tab_cross:
    filtered = local_filters(
        df,
        [("City tier", "city_tier"), ("Vehicle type", "vehicle_type")],
        key_prefix="cross",
        help_text="Narrow the panel before pivoting, if you want.",
    )

    if filtered.empty:
        st.warning("No respondents match this filter combination. Try loosening a filter.")
    else:
        section_header("Build your own cross-tab", "Pick any two dimensions and a metric to pivot this view")

        dim_options = {
            "City tier": "city_tier",
            "Region": "region",
            "Vehicle type": "vehicle_type",
            "Household income": "household_income_bucket",
            "E20 factory compatible": "e20_factory_compatible",
            "Preferred payment mode": "preferred_payment_mode",
            "Primary motivator": "primary_motivator",
            "Govt E20 sentiment": "govt_e20_handling_sentiment",
            "Price point shown": "price_point_shown_inr",
        }
        metric_options = {
            "Avg. purchase likelihood (1-5)": "purchase_likelihood_1to5",
            "Avg. NPS rating (0-10)": "nps_0to10",
            "Avg. monthly fuel spend (₹)": "monthly_fuel_spend_inr",
            "Respondent count": None,
        }

        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            row_dim_label = st.selectbox("Rows", list(dim_options.keys()), index=0)
        with cc2:
            col_dim_label = st.selectbox("Columns", list(dim_options.keys()), index=2)
        with cc3:
            metric_label = st.selectbox("Metric", list(metric_options.keys()), index=0)

        row_dim, col_dim, metric_col = dim_options[row_dim_label], dim_options[col_dim_label], metric_options[metric_label]

        if row_dim == col_dim:
            st.warning("Pick two different dimensions for rows and columns.")
        else:
            if metric_col is None:
                pivot = filtered.pivot_table(index=row_dim, columns=col_dim, values="respondent_id", aggfunc="count", fill_value=0)
            else:
                pivot = filtered.pivot_table(index=row_dim, columns=col_dim, values=metric_col, aggfunc="mean")

            fig_heat = px.imshow(
                pivot, text_auto=".1f", aspect="auto",
                color_continuous_scale=[BAD, ACCENT, GOOD] if metric_col else "Blues",
            )
            fig_heat.update_layout(xaxis_title=col_dim_label, yaxis_title=row_dim_label)
            apply_chart_theme(fig_heat, height=460)
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption(f"{metric_label} — {row_dim_label} × {col_dim_label}, this view (n={len(filtered):,})")

            with st.expander("See pivot table"):
                st.dataframe(pivot.round(2), use_container_width=True)

# ---------- RAW DATA ----------
with tab_raw:
    filtered = local_filters(
        df,
        [
            ("City tier", "city_tier"), ("Region", "region"), ("Vehicle type", "vehicle_type"),
            ("Price point shown (₹)", "price_point_shown_inr"), ("Household income", "household_income_bucket"),
            ("E20 factory compatible", "e20_factory_compatible"),
        ],
        key_prefix="raw",
        help_text="The full filter set lives here for building a precise export.",
    )
    section_header("Filtered respondent-level data")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="petrosep_survey_filtered.csv",
        mime="text/csv",
    )
