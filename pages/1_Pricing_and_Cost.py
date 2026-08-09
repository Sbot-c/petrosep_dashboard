import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.styling import (
    PRIMARY, PRIMARY_DARK, ACCENT, GOOD, BAD, MUTED, INK, CATEGORY_COLORS, TRACK_BG,
    inject_css, hero, section_header, metric_card, apply_chart_theme,
)

st.set_page_config(page_title="Pricing & Cost | PetroSep", page_icon="💰", layout="wide")
inject_css()


@st.cache_data
def load_data():
    cost = pd.read_csv("data/cost_buildup.csv")
    pricing = pd.read_csv("data/pricing_scenarios.csv")
    payment = pd.read_csv("data/payment_structures.csv")
    return cost, pricing, payment


cost_df, pricing_df, payment_df = load_data()
total_cost = cost_df["unit_cost_inr"].sum()

hero(
    badge="Cost Model",
    title="💰 Pricing & Cost Build-Up",
    subtitle="Home unit — every rupee of cost, and how each price point translates into margin.",
)

# ---------- TOP METRICS ----------
bom_total = cost_df.loc[cost_df["category"] == "BOM", "unit_cost_inr"].sum()
non_bom_total = total_cost - bom_total
best_margin = pricing_df["gross_margin_pct"].max()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(metric_card("🧾", "Fully-loaded cost", f"₹{total_cost:,.0f}", "", "neutral"), unsafe_allow_html=True)
with m2:
    st.markdown(metric_card("🔩", "BOM cost", f"₹{bom_total:,.0f}", f"{bom_total/total_cost*100:.0f}% of total", "neutral"), unsafe_allow_html=True)
with m3:
    st.markdown(metric_card("🏭", "Assembly + logistics + reserve", f"₹{non_bom_total:,.0f}", f"{non_bom_total/total_cost*100:.0f}% of total", "neutral"), unsafe_allow_html=True)
with m4:
    st.markdown(metric_card("📈", "Best-case margin", f"{best_margin*100:.1f}%", "Premium bundle scenario", "good"), unsafe_allow_html=True)

st.divider()

# ---------- WATERFALL + CATEGORY DONUT ----------
wf_col, donut_col = st.columns([3, 2])

with wf_col:
    section_header("Bill of materials → fully-loaded cost", "Cumulative build-up across every component")
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(cost_df) + ["total"],
        x=list(cost_df["component"]) + ["Fully-Loaded Cost"],
        y=list(cost_df["unit_cost_inr"]) + [0],
        text=[f"₹{v:,.0f}" for v in cost_df["unit_cost_inr"]] + [f"₹{total_cost:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgba(120,120,120,0.35)"}},
        increasing={"marker": {"color": PRIMARY}},
        totals={"marker": {"color": INK}},
    ))
    apply_chart_theme(fig, height=520)
    fig.update_layout(showlegend=False, margin=dict(t=40, b=140, l=10, r=10))
    fig.update_xaxes(tickangle=-40)
    st.plotly_chart(fig, use_container_width=True)

with donut_col:
    section_header("Cost by category", "Where the ₹ actually goes")
    cat_summary = cost_df.groupby("category")["unit_cost_inr"].sum().reset_index()
    fig_d = px.pie(
        cat_summary, names="category", values="unit_cost_inr", hole=0.55,
        color="category", color_discrete_map=CATEGORY_COLORS,
    )
    fig_d.update_traces(textinfo="label+percent", textfont_size=12)
    apply_chart_theme(fig_d, height=340)
    fig_d.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_d, use_container_width=True)
    st.markdown(
        f"<div style='text-align:center;margin-top:-1.4rem;'>"
        f"<span style='font-size:1.6rem;font-weight:800;color:{INK};'>₹{total_cost:,.0f}</span><br>"
        f"<span style='color:{MUTED};font-size:0.85rem;'>fully-loaded / unit</span></div>",
        unsafe_allow_html=True,
    )

with st.expander("See the full cost table"):
    st.dataframe(cost_df, use_container_width=True, hide_index=True)

st.divider()

# ---------- PRICING SCENARIOS ----------
section_header("Pricing scenarios & margin")

tab1, tab2 = st.tabs(["📊 Margin by scenario", "📋 Full table"])

with tab1:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="Cost",
        x=pricing_df["price_strategy"],
        y=[total_cost] * len(pricing_df),
        marker_color=TRACK_BG,
        hovertext=[f"Cost: ₹{total_cost:,.0f}"] * len(pricing_df),
        hoverinfo="text",
    ))
    fig2.add_trace(go.Bar(
        name="Margin",
        x=pricing_df["price_strategy"],
        y=pricing_df["gross_margin_inr"],
        marker_color=PRIMARY,
        hovertext=[f"Margin: ₹{v:,.0f}" for v in pricing_df["gross_margin_inr"]],
        hoverinfo="text",
    ))
    # values are shown once, clearly, in the annotation above each bar rather
    # than as small in-bar labels that lose contrast against the fill color
    for _, row in pricing_df.iterrows():
        fig2.add_annotation(
            x=row["price_strategy"],
            y=total_cost + row["gross_margin_inr"] + 250,
            text=f"₹{row['retail_price_inr']:,.0f} ({row['gross_margin_pct']*100:.0f}% margin)",
            showarrow=False,
            font=dict(size=13, color=INK),
        )
    fig2.update_layout(barmode="stack", yaxis_title="₹ per unit")
    apply_chart_theme(fig2, height=480)
    fig2.update_layout(margin=dict(t=70, b=10, l=10, r=10))
    st.plotly_chart(fig2, use_container_width=True)

    cols = st.columns(len(pricing_df))
    for col, (_, row) in zip(cols, pricing_df.iterrows()):
        with col:
            st.markdown(
                f"""
                <div class="ps-card">
                    <div class="ps-label">{row['price_strategy'].split('(')[0].strip()}</div>
                    <div class="ps-value">₹{row['retail_price_inr']:,.0f}</div>
                    <div class="ps-delta good">{row['gross_margin_pct']*100:.1f}% margin</div>
                    <div style="color:{MUTED};font-size:0.82rem;margin-top:0.5rem;">{row['rationale']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tab2:
    display_df = pricing_df.copy()
    display_df["gross_margin_pct"] = (display_df["gross_margin_pct"] * 100).round(1).astype(str) + "%"
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# ---------- INTERACTIVE MARGIN CALCULATOR ----------
section_header("🧮 Live margin calculator", "Stress-test your own price and cost-inflation assumptions")

calc_left, calc_right = st.columns([1, 2])
with calc_left:
    custom_price = st.slider("Retail price (₹)", min_value=2999, max_value=7999, value=int(pricing_df["retail_price_inr"].iloc[1]), step=50)
    cost_inflation = st.slider("Cost inflation vs. current BOM (%)", min_value=-20, max_value=40, value=0, step=1,
                                help="Simulates supply-chain cost changes (steel, resin, electronics) on top of the fully-loaded cost.")
    stressed_cost = total_cost * (1 + cost_inflation / 100)
    stressed_margin_inr = custom_price - stressed_cost
    stressed_margin_pct = stressed_margin_inr / custom_price if custom_price else 0

    delta_kind = "good" if stressed_margin_pct >= 0.4 else ("neutral" if stressed_margin_pct >= 0.2 else "bad")
    st.markdown(metric_card("💵", "Stressed unit cost", f"₹{stressed_cost:,.0f}", f"{cost_inflation:+d}% vs. base", "neutral"), unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    st.markdown(metric_card("📐", "Resulting gross margin", f"{stressed_margin_pct*100:.1f}%", f"₹{stressed_margin_inr:,.0f} / unit", delta_kind), unsafe_allow_html=True)

with calc_right:
    price_range = list(range(3000, 8001, 100))
    margin_curve = [(p - stressed_cost) / p * 100 for p in price_range]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=price_range, y=margin_curve, mode="lines", line=dict(color=PRIMARY, width=3), name="Margin %"))
    fig3.add_trace(go.Scatter(x=[custom_price], y=[stressed_margin_pct * 100], mode="markers",
                               marker=dict(color=ACCENT, size=14, line=dict(color=PRIMARY_DARK, width=2)),
                               name="Your scenario"))
    fig3.add_hline(y=0, line_dash="dot", line_color=BAD, annotation_text="Breakeven")
    fig3.update_layout(xaxis_title="Retail price (₹)", yaxis_title="Gross margin (%)", showlegend=False)
    apply_chart_theme(fig3, height=340)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("The marker shows your slider inputs plotted against margin % across the full price range.")

st.divider()

# ---------- PAYMENT STRUCTURES ----------
section_header("Alternative payment structures")
pc1, pc2 = st.columns(2)
for col, (_, row) in zip([pc1, pc2], payment_df.iterrows()):
    with col:
        st.markdown(
            f"""
            <div class="ps-card">
                <div class="ps-label">{row['structure']}</div>
                <div class="ps-value">₹{row['monthly_inr']:,.0f}<span style="font-size:0.9rem;font-weight:600;color:{MUTED};">/mo</span></div>
                <div style="color:{MUTED};font-size:0.82rem;margin-top:0.5rem;">Basis: ₹{row['basis_inr']:,.0f} · {row['notes']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.caption(
    "EMI and subscription options directly target the 'upfront cost' objection flagged in the "
    "competitive table as PetroSep's main disadvantage vs. additives — see the Survey Explorer "
    "for how payment-mode preference actually splits by price point."
)
