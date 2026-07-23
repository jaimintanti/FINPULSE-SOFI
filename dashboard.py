import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import subprocess
import sys

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="FinPulse",
    layout="wide"
)

# -------------------------------
# Title
# -------------------------------

st.title("📈 FinPulse")

st.markdown(
"""
### Indian Stock Market Analytics Dashboard

Analyze stock prices, market capitalization, PE ratios and historical performance of leading Indian companies.
"""
)

# -------------------------------
# Refresh Button
# -------------------------------

if st.button("🔄 Refresh Live Data"):

    with st.spinner("Fetching latest market data..."):

        result = subprocess.run(
            [sys.executable, "refresh_data.py"],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:

        st.success("Database Updated Successfully!")

        st.rerun()

    else:

        st.error("Database Update Failed")

        st.code(result.stderr)

# -------------------------------
# Load Database
# -------------------------------

connection = sqlite3.connect("stocks.db")

df = pd.read_sql_query(
    "SELECT * FROM stocks",
    connection
)

connection.close()

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.header("Filters")

company = st.sidebar.selectbox(
    "Select Company",
    ["All Companies"] + sorted(df["company"].unique().tolist())
   
)
period = st.sidebar.selectbox(
    "Historical Period",
    ["1mo", "6mo", "1y"]
)

st.sidebar.subheader("📊 Company Comparison")

compare_companies = st.sidebar.multiselect(
    "Select Companies",
    sorted(df["company"].unique().tolist())
)
# -------------------------------
# Search
# -------------------------------



# -------------------------------
# Sorting
# -------------------------------

sort_option = st.selectbox(
    "Sort By",
    [
        "Price",
        "Market Cap",
        "PE Ratio"
    ]
)

# -------------------------------
# Filtering
# -------------------------------

filtered_df = df.copy()

if company != "All Companies":
    filtered_df = filtered_df[
        filtered_df["company"] == company
    ]

# -------------------------------
# Sorting Logic
# -------------------------------

if sort_option == "Price":
    filtered_df = filtered_df.sort_values(
        "price",
        ascending=False
    )

elif sort_option == "Market Cap":
    filtered_df = filtered_df.sort_values(
        "market_cap",
        ascending=False
    )

else:
    filtered_df = filtered_df.sort_values(
        "pe_ratio",
        ascending=False
    )

# -------------------------------
# KPI Cards
# -------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric(
    label="📊 Total Companies",
    value=len(filtered_df)
)

col2.metric(
    label="💰 Highest Stock Price",
    value=f"₹{filtered_df['price'].max():,.2f}"
)

col3.metric(
    label="📈 Average PE Ratio",
    value=f"{filtered_df['pe_ratio'].mean():.2f}"
)

st.divider()

# -------------------------------
# Company Table
# -------------------------------

st.subheader("📋 Stock Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# -------------------------------
# Charts
# -------------------------------

st.header("📊 Visual Analytics")

# Price Chart

fig1 = px.bar(
    filtered_df,
    x="company",
    y="price",
    title="Current Stock Prices"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# Market Cap Chart

fig2 = px.bar(
    filtered_df.sort_values(
        "market_cap",
        ascending=False
    ),
    x="company",
    y="market_cap",
    title="Market Capitalization"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# Scatter Plot

fig3 = px.scatter(
    filtered_df,
    x="price",
    y="pe_ratio",
    size="market_cap",
    hover_name="company",
    title="Price vs PE Ratio"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# Pie Chart

top10 = filtered_df.sort_values(
    "market_cap",
    ascending=False
).head(10)

fig4 = px.pie(
    top10,
    values="market_cap",
    names="company",
    title="Top Companies by Market Cap"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


if company != "All Companies":

    st.divider()

    st.header("📈 Historical Stock Analysis")

    symbol = filtered_df.iloc[0]["symbol"]

    stock = yf.Ticker(symbol)

    history = stock.history(period=period)

    st.subheader(f"{company} ({period})")

    # Line Chart
    st.line_chart(history["Close"])

    # Candlestick Chart
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Candlestick"
        )
    )

    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    st.plotly_chart(fig, use_container_width=True)
    # -------------------------------
# Moving Averages
# -------------------------------

    history["20 MA"] = history["Close"].rolling(window=20).mean()
    history["50 MA"] = history["Close"].rolling(window=50).mean()

    ma_fig = go.Figure()

    ma_fig.add_trace(
    go.Scatter(
        x=history.index,
        y=history["Close"],
        mode="lines",
        name="Close Price"
    )
)

    ma_fig.add_trace(
    go.Scatter(
        x=history.index,
        y=history["20 MA"],
        mode="lines",
        name="20-Day MA"
    )
)

    ma_fig.add_trace(
    go.Scatter(
        x=history.index,
        y=history["50 MA"],
        mode="lines",
        name="50-Day MA"
    )
)

    ma_fig.update_layout(
    title="Moving Average Analysis",
    xaxis_title="Date",
    yaxis_title="Price"
)

    st.plotly_chart(ma_fig, use_container_width=True)
    csv = history.to_csv(index=True)

    st.download_button(
    label="📥 Download Historical Data",
    data=csv,
    file_name=f"{symbol}_{period}.csv",
    mime="text/csv"
)
    # ----------------------------------------------------
# Company Comparison
# ----------------------------------------------------

if len(compare_companies) >= 2:

    comparison_df = df[
        df["company"].isin(compare_companies)
    ]

    st.divider()

    st.header("📊 Company Comparison")

    # -----------------------------
    # Comparison Table
    # -----------------------------

    st.dataframe(
        comparison_df,
        use_container_width=True
    )

    # -----------------------------
    # Price Comparison
    # -----------------------------

    fig_compare = px.bar(
        comparison_df,
        x="company",
        y="price",
        color="company",
        title="Stock Price Comparison"
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    # -----------------------------
    # Historical Comparison
    # -----------------------------

    st.subheader("📈 Historical Price Comparison")

    history_df = pd.DataFrame()

    for company_name in compare_companies:

        symbol = df[
            df["company"] == company_name
        ].iloc[0]["symbol"]

        stock = yf.Ticker(symbol)

        history = stock.history(period=period)

        history_df[company_name] = history["Close"]

    st.line_chart(history_df)

    # -----------------------------
    # PE Ratio Comparison
    # -----------------------------

    st.subheader("📊 PE Ratio Comparison")

    fig_pe = px.bar(
        comparison_df,
        x="company",
        y="pe_ratio",
        color="company",
        text="pe_ratio",
        title="PE Ratio Comparison"
    )

    fig_pe.update_traces(
        textposition="outside"
    )

    fig_pe.update_layout(
        xaxis_title="Company",
        yaxis_title="PE Ratio"
    )

    st.plotly_chart(
        fig_pe,
        use_container_width=True
    )

    # -----------------------------
    # Market Cap Comparison
    # -----------------------------

    st.subheader("💰 Market Capitalization Comparison")

    fig_market = px.bar(
        comparison_df,
        x="company",
        y="market_cap",
        color="company",
        title="Market Capitalization Comparison"
    )

    st.plotly_chart(
        fig_market,
        use_container_width=True
    )

else:

    st.divider()

    st.info("👈 Select at least 2 companies from the sidebar to compare.")
   