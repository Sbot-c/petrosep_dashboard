import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Pricing & Cost | PetroSep", page_icon="💰", layout="wide")

PRIMARY = "#1C7293"
ACCENT = "#F2A541"


@st.cache_data
def load_data():
    cost = pd.read_csv("data/cost_buildup.csv")
    pricing = pd.read_csv("data/pricing_scenarios.csv")
    payment = pd.read_csv("data/payment_structures.csv")
    return cost, pricing, payment


cost_df, pricing_df, payment_df = load_data()

st.title("💰 Pricing & Cost Build-Up")
st.caption("Home unit — every rupee of cost, and how each price point translates into margin")

st.divider()

st.subheader("Bill of materials → fully-loaded cost")

bom = cost_df[cost_df["category"] == "BOM"]
other = cost_df[cost_df["category"] != "BOM"]

fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=["relative"] * len(cost_df) + ["total"],
    x=list(cost_df["component"]) + ["Fully-Loaded Cost"],
    y=list(cost_df["unit_cost_inr"]) + [0],
    text=[f"₹{v:,.0f}" for v in cost_df["unit_cost_inr"]] + [""],
    textposition="outside",
    connector={"line": {"color": "rgba(120,120,120,0.4)"}},
    increasing={"marker": {"color": PRIMARY}},
    totals={"marker": {"color": "#333333"}},
))
fig.update_layout(height=520, margin=dict(t=30, b=120), showlegend=False)
fig.update_xaxes(tickangle=-40)
st.plotly_chart(fig, use_container_width=True)

total_cost = cost_df["unit_cost_inr"].sum()
st.metric("Fully-loaded cost per unit", f"₹{total_cost:,.0f}")

with st.expander("See the full cost table"):
    st.dataframe(cost_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Pricing scenarios & margin")

tab1, tab2 = st.tabs(["Margin by scenario", "Full table"])

with tab1:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="Cost",
        x=pricing_df["price_strategy"],
        y=[total_cost] * len(pricing_df),
        marker_color="#B0B7BD",
        text=[f"₹{total_cost:,.0f}"] * len(pricing_df),
    ))
    fig2.add_trace(go.Bar(
        name="Margin",
        x=pricing_df["price_strategy"],
        y=pricing_df["gross_margin_inr"],
        marker_color=PRIMARY,
        text=[f"₹{v:,.0f}" for v in pricing_df["gross_margin_inr"]],
    ))
    for _, row in pricing_df.iterrows():
        fig2.add_annotation(
            x=row["price_strategy"],
            y=total_cost + row["gross_margin_inr"] + 250,
            text=f"₹{row['retail_price_inr']:,.0f} ({row['gross_margin_pct']*100:.0f}% margin)",
            showarrow=False,
            font=dict(size=13, color="#222"),
        )
    fig2.update_layout(
        barmode="stack",
        yaxis_title="₹ per unit",
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

    for _, row in pricing_df.iterrows():
        st.markdown(f"**{row['price_strategy']} — ₹{row['retail_price_inr']:,.0f}**")
        st.caption(row["rationale"])

with tab2:
    display_df = pricing_df.copy()
    display_df["gross_margin_pct"] = (display_df["gross_margin_pct"] * 100).round(1).astype(str) + "%"
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Alternative payment structures")
st.dataframe(payment_df, use_container_width=True, hide_index=True)
st.caption(
    "EMI and subscription options directly target the 'upfront cost' objection flagged in the "
    "competitive table as PetroSep's main disadvantage vs. additives — see the Survey Explorer "
    "for how payment-mode preference actually splits by price point."
)
