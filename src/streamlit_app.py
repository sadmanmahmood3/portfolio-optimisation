import sys
from pathlib import Path

# Let this file import from the src folder, both locally and on Streamlit Cloud
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import load_results
from src.extractor import fetch_prices

st.set_page_config(page_title="Portfolio Forecast Dashboard", page_icon="📊", layout="wide")


@st.cache_data(ttl=600)  # reload from Supabase at most every 10 minutes
def get_results() -> pd.DataFrame:
    return load_results()


@st.cache_data(ttl=3600)  # reload prices at most every hour
def get_price_history(ticker: str) -> pd.DataFrame:
    start = (pd.Timestamp.today() - pd.DateOffset(months=6)).strftime("%Y-%m-%d")
    return fetch_prices([ticker], start)


st.title("📊 Portfolio Forecast Dashboard")
st.caption(
    "Daily Prophet forecasts and Markowitz-optimised portfolio weights. "
    "A learning project, not investment advice."
)

data = get_results()
if data.empty:
    st.warning("No forecasts saved yet. Run the pipeline first.")
    st.stop()

# ---------- Date picker ----------
dates = sorted(data["as_of"].unique(), reverse=True)
selected_date = st.selectbox("Forecast date", dates)
day = data[data["as_of"] == selected_date].sort_values("weight", ascending=False)

# ---------- Weights + predictions ----------
left, right = st.columns(2)

with left:
    st.subheader("Portfolio weights")
    fig = px.pie(day, names="ticker", values="weight", hole=0.4)
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Predictions")
    table = day[["ticker", "last_price", "predicted_price", "predicted_return", "weight"]].rename(
        columns={
            "ticker": "Ticker",
            "last_price": "Last price",
            "predicted_price": "Predicted price",
            "predicted_return": "Predicted return",
            "weight": "Weight",
        }
    )
    st.dataframe(
        table.style.format({
            "Last price": "${:,.2f}",
            "Predicted price": "${:,.2f}",
            "Predicted return": "{:+.2%}",
            "Weight": "{:.1%}",
        }),
        hide_index=True,
        width="stretch",
    )

# ---------- Single stock detail ----------
st.subheader("Stock detail")
ticker = st.selectbox("Choose a stock", day["ticker"])
row = day.set_index("ticker").loc[ticker]

m1, m2, m3 = st.columns(3)
m1.metric("Last price", f"${row['last_price']:,.2f}")
m2.metric("Predicted price", f"${row['predicted_price']:,.2f}", f"{row['predicted_return']:+.2%}")
m3.metric("Portfolio weight", f"{row['weight']:.1%}")

history = get_price_history(ticker)
st.line_chart(history[ticker], y_label="Price ($)")
st.caption("Last 6 months of closing prices.")