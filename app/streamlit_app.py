"""Interactive executive dashboard for the generated retail marts."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

st.set_page_config(page_title="Retail Sales Analytics", page_icon="🛍️", layout="wide")
st.title("Retail Sales Analytics Command Center")
st.caption("Deterministic synthetic data · 24-month commercial view · EUR")

monthly = pd.read_csv(DATA / "monthly_kpis.csv")
categories = pd.read_csv(DATA / "category_performance.csv")
channels = pd.read_csv(DATA / "channel_performance.csv")
stores = pd.read_csv(DATA / "store_performance.csv")
products = pd.read_csv(DATA / "product_performance.csv")
segments = pd.read_csv(DATA / "customer_segments.csv")
campaigns = pd.read_csv(DATA / "campaign_performance.csv")

selected_channels = st.multiselect(
    "Sales channel",
    sorted(channels["channel"].unique()),
    default=sorted(channels["channel"].unique()),
)
channel_view = channels[channels["channel"].isin(selected_channels)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Net revenue", f"€{channel_view['revenue'].sum():,.0f}")
c2.metric("Gross profit", f"€{channel_view['gross_profit'].sum():,.0f}")
c3.metric("Gross margin", f"{channel_view['gross_profit'].sum() / max(channel_view['revenue'].sum(), 1):.1%}")
c4.metric("Latest YoY revenue", f"{monthly.iloc[-1]['yoy_revenue_pct']:.1%}")

left, right = st.columns([1.6, 1])
with left:
    st.subheader("Revenue and gross profit trend")
    trend = monthly.melt("order_month", value_vars=["revenue", "gross_profit"], var_name="metric", value_name="value")
    st.plotly_chart(px.line(trend, x="order_month", y="value", color="metric", markers=True), use_container_width=True)
with right:
    st.subheader("Category margin versus scale")
    st.plotly_chart(
        px.scatter(categories, x="revenue", y="margin_pct", size="orders", color="category", hover_name="category"),
        use_container_width=True,
    )

tab1, tab2, tab3, tab4 = st.tabs(["Channels & stores", "Products", "Customers", "Campaigns"])
with tab1:
    st.plotly_chart(px.bar(channel_view, x="channel", y=["revenue", "gross_profit"], barmode="group"), use_container_width=True)
    st.dataframe(stores.head(12), use_container_width=True, hide_index=True)
with tab2:
    st.plotly_chart(px.bar(products.head(15), x="product_name", y="gross_profit", color="category"), use_container_width=True)
    st.dataframe(products.head(25), use_container_width=True, hide_index=True)
with tab3:
    st.plotly_chart(px.treemap(segments, path=["segment"], values="customers", color="revenue_per_customer"), use_container_width=True)
    st.dataframe(segments, use_container_width=True, hide_index=True)
with tab4:
    st.plotly_chart(px.scatter(campaigns, x="spend", y="attributed_revenue", size="attributed_orders", color="marketing_channel", hover_name="campaign_name"), use_container_width=True)
    st.dataframe(campaigns, use_container_width=True, hide_index=True)

st.info("Campaign revenue is attributed association—not causal incrementality. Use randomized holdouts before making budget decisions.")
