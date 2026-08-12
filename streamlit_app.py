"""Compass Invest Streamlit app.

Investor dashboard for comparing systematic funds, viewing fact sheets,
setting allocations, and exploring sector sentiment analytics.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402
import pandas as pd  # noqa: E402

st.set_page_config(page_title="Compass Invest", layout="wide")
st.title("Compass Invest")
st.caption("Systematic multi-asset funds with news sentiment analytics.")


@st.cache_data(ttl=86_400, show_spinner="Loading fund data...")
def load_fund_returns():
    return pd.read_csv("results/data/fund_returns.csv", index_col="date", parse_dates=True)


@st.cache_data(ttl=86_400, show_spinner="Loading fund weights...")
def load_fund_weights():
    return pd.read_csv("results/data/fund_weights.csv", index_col="date", parse_dates=True)


@st.cache_data(ttl=86_400, show_spinner="Loading performance metrics...")
def load_metrics():
    return pd.read_csv("results/tables/performance_metrics.csv", index_col="fund")


@st.cache_data(ttl=86_400, show_spinner="Loading sentiment data...")
def load_sector_sentiment():
    return pd.read_csv("results/data/sector_sentiment_index.csv", parse_dates=["date"])


fund_returns = load_fund_returns()
fund_weights = load_fund_weights()
metrics = load_metrics()

tab_funds, tab_allocation, tab_sentiment, tab_data = st.tabs(["Funds", "Allocation", "Sentiment", "Data"])

with tab_funds:
    st.subheader("Compare Funds")

    fund_names = fund_returns.columns.tolist()
    selected_fund = st.selectbox("Choose a fund to view its fact sheet:", fund_names)

    fact = metrics.loc[selected_fund]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annualised Return", f"{fact['annualised_return']:.2%}")
    col2.metric("Annualised Volatility", f"{fact['annualised_volatility']:.2%}")
    col3.metric("Sharpe Ratio", f"{fact['sharpe_ratio']:.2f}")
    col4.metric("Max Drawdown", f"{fact['max_drawdown']:.2%}")

    st.write("**Growth of $1**")
    growth = (1 + fund_returns[selected_fund]).cumprod()
    st.line_chart(growth)

    st.write("**Current Holdings (Most Recent Rebalance)**")
    fund_weight_rows = fund_weights[fund_weights["fund"] == selected_fund]
    latest_date = fund_weight_rows.index.max()
    latest_holdings = fund_weight_rows.loc[latest_date].drop("fund")
    latest_holdings = latest_holdings.astype(float).sort_values(ascending=False)
    top_holdings = latest_holdings.head(10)
    top_holdings = top_holdings.rename("weight")
    st.bar_chart(top_holdings)
    st.caption(f"As of {latest_date.date()}, top 10 holdings by weight.")

with tab_allocation:
    st.subheader("Set Your Allocation")
    st.write("Allocate across all available funds. The app normalises your weights to 100%.")

    fund_names = fund_returns.columns.tolist()

    raw_weights = {}
    cols = st.columns(2)
    for i, fund in enumerate(fund_names):
        with cols[i % 2]:
            raw_weights[fund] = st.slider(
                fund,
                min_value=0,
                max_value=100,
                value=int(100 / len(fund_names)),
            )

    total_weight = sum(raw_weights.values())

    if total_weight == 0:
        st.warning("Set at least one fund weight above zero.")
    else:
        weights = pd.Series(raw_weights, dtype=float) / total_weight

        st.write("**Normalised Allocation**")
        st.dataframe((weights * 100).rename("allocation_%").round(2))

        blended_returns = fund_returns.mul(weights, axis=1).sum(axis=1)
        blended_growth = (1 + blended_returns).cumprod()

        st.write("**Blended Portfolio: Growth of $1**")
        st.line_chart(blended_growth)

        ann_return = (1 + blended_returns.mean()) ** 252 - 1
        ann_vol = blended_returns.std() * (252 ** 0.5)
        sharpe = ann_return / ann_vol

        running_max = blended_growth.cummax()
        drawdown = (blended_growth - running_max) / running_max
        max_drawdown = drawdown.min()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Annualised Return", f"{ann_return:.2%}")
        col2.metric("Annualised Volatility", f"{ann_vol:.2%}")
        col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
        col4.metric("Max Drawdown", f"{max_drawdown:.2%}")

with tab_sentiment:
    st.subheader("Sector Sentiment Over Time")

    sector_sentiment = load_sector_sentiment()
    sector_pivot = sector_sentiment.pivot(index="date", columns="sector", values="sentiment_lagged")
    sector_pivot_smooth = sector_pivot.rolling(20).mean()

    selected_sectors = st.multiselect(
        "Choose sectors to display:",
        options=sector_pivot.columns.tolist(),
        default=["Energy", "Healthcare", "Tech"],
    )

    if selected_sectors:
        st.line_chart(sector_pivot_smooth[selected_sectors])
        st.caption("20-day rolling average of lagged VADER sentiment (compound score).")
    else:
        st.info("Select at least one sector to view its sentiment trend.")

with tab_data:
    st.subheader("About This Data")
    st.write(
        "Compass Invest's funds are built from 50 US equities across 10 sectors, "
        "10 major cryptocurrencies, and daily news headlines for the equities, "
        "covering 2020-2023. All fund performance shown here is backtested "
        "out-of-sample, using only information available at each rebalance date."
    )
    st.write("**Fund Performance Summary**")
    st.dataframe(metrics.style.format({
        "annualised_return": "{:.2%}",
        "annualised_volatility": "{:.2%}",
        "sharpe_ratio": "{:.2f}",
        "max_drawdown": "{:.2%}",
    }))
