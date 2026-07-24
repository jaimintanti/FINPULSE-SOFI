import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="FinPulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main{
    background-color:#0E1117;
}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}

h1{
    color:#4F9DFF;
    font-weight:700;
}

h2,h3{
    color:white;
}

section[data-testid="stSidebar"]{
    background-color:#161B22;
}

div[data-testid="metric-container"]{
    background:#1B2430;
    border:1px solid #2D3748;
    border-radius:15px;
    padding:18px;
    box-shadow:0px 5px 18px rgba(0,0,0,0.35);
}

.stButton>button{
    width:100%;
    border-radius:10px;
    background:#2563EB;
    color:white;
    font-weight:bold;
}

.stDownloadButton>button{
    width:100%;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO TITLE
# ---------------------------------------------------

st.title("📈 FinPulse")

st.markdown("""
###  Indian Stock Market Analytics Dashboard

Track stock prices, analyze company fundamentals,
compare leading Indian companies and visualize
historical trends in one interactive dashboard.
""")

st.divider()

# ---------------------------------------------------
# API
# ---------------------------------------------------

API_URL = "https://finpulse-sofi-omega.vercel.app/stocks"

response = requests.get(API_URL)

df = pd.DataFrame(response.json())

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("⚙ Dashboard Controls")

st.sidebar.markdown("---")

company = st.sidebar.selectbox(
    "🏢 Select Company",
    ["All Companies"] + sorted(df["company"].unique())
)

period = st.sidebar.selectbox(
    "📅 Historical Period",
    ["1mo","6mo","1y"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("📊 Compare Companies")

compare_companies = st.sidebar.multiselect(
    "Select Companies",
    sorted(df["company"].unique())
)

st.sidebar.markdown("---")

sort_option = st.sidebar.selectbox(
    "📈 Sort By",
    [
        "Price",
        "Market Cap",
        "PE Ratio"
    ]
)

# ---------------------------------------------------
# FILTERING
# ---------------------------------------------------

filtered_df = df.copy()

if company != "All Companies":

    filtered_df = filtered_df[
        filtered_df["company"] == company
    ]

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

# ---------------------------------------------------
# KPI
# ---------------------------------------------------

col1,col2,col3 = st.columns(3)

col1.metric(
    "🏢 Companies Tracked",
    len(filtered_df)
)

col2.metric(
    "💹 Highest Share Price",
    f"₹{filtered_df['price'].max():,.2f}"
)

col3.metric(
    "📊 Average PE Ratio",
    f"{filtered_df['pe_ratio'].mean():.2f}"
)

st.divider()

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------

st.subheader("📋 Company Fundamentals")

display_df = filtered_df.copy()

display_df["price"] = display_df["price"].map(lambda x:f"₹{x:,.2f}")

display_df["market_cap"] = display_df["market_cap"].map(lambda x:f"{x:,.0f}")

display_df["pe_ratio"] = display_df["pe_ratio"].map(lambda x:f"{x:.2f}")

display_df["eps"] = display_df["eps"].map(lambda x:f"{x:.2f}")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------
# VISUAL ANALYTICS
# ---------------------------------------------------

st.header("📊 Visual Analytics")

# ---------------------------------------------------
# PRICE CHART
# ---------------------------------------------------

fig1 = px.bar(
    filtered_df,
    x="company",
    y="price",
    color="price",
    color_continuous_scale="Blues",
    text_auto=".2f",
    title="Current Stock Prices"
)

fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    title_x=0.5,
    height=520,
    font=dict(size=15),
    coloraxis_showscale=False,
    xaxis_title="Company",
    yaxis_title="Share Price (₹)"
)

fig1.update_traces(
    textposition="outside",
    marker_line_width=0
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ---------------------------------------------------
# MARKET CAP
# ---------------------------------------------------

fig2 = px.bar(
    filtered_df.sort_values(
        "market_cap",
        ascending=False
    ),
    x="company",
    y="market_cap",
    color="market_cap",
    color_continuous_scale="Greens",
    title="Market Capitalization"
)

fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    title_x=0.5,
    height=520,
    coloraxis_showscale=False,
    xaxis_title="Company",
    yaxis_title="Market Cap"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------------------------------------------
# PRICE VS PE
# ---------------------------------------------------

fig3 = px.scatter(
    filtered_df,
    x="price",
    y="pe_ratio",
    size="market_cap",
    color="company",
    hover_name="company",
    size_max=45,
    title="Price vs PE Ratio"
)

fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    title_x=0.5,
    height=560,
    legend_title=""
)

fig3.update_traces(
    marker=dict(
        line=dict(
            width=1,
            color="white"
        )
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ---------------------------------------------------
# PIE CHART
# ---------------------------------------------------

top10 = filtered_df.sort_values(
    "market_cap",
    ascending=False
).head(10)

fig4 = px.pie(
    top10,
    values="market_cap",
    names="company",
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Set3,
    title="Top Companies by Market Capitalization"
)

fig4.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig4.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    title_x=0.5,
    height=650,
    legend_title=""
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
        template="plotly_dark",
    title="Candlestick Analysis",
    title_x=0.5,
    height=650,
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    xaxis_rangeslider_visible=False,
    font=dict(size=14),
    margin=dict(l=20, r=20, t=60, b=20)
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
    template="plotly_dark",
    title={
        "text": "Moving Average Analysis",
        "x": 0.5
    },
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    height=600,
    hovermode="x unified",
    margin=dict(
        l=30,
        r=30,
        t=60,
        b=30
    )
)

    st.plotly_chart(ma_fig, use_container_width=True)
    csv = history.to_csv(index=True)

    st.download_button(
    label="📥 Download Historical Data",
    data=csv,
    file_name=f"{symbol}_{period}.csv",
    mime="text/csv"
)
    # ============================================================
# COMPANY COMPARISON DASHBOARD
# ============================================================

if len(compare_companies) >= 2:

    comparison_df = df[
        df["company"].isin(compare_companies)
    ]

    st.divider()

    st.header("🏆 Company Comparison Dashboard")

    st.markdown(
        """
        Compare valuation, market capitalization,
        historical performance and pricing across
        selected companies.
        """
    )

    # ------------------------------------------------

    # Comparison Table

    # ------------------------------------------------

    display_compare = comparison_df.copy()

    display_compare["price"] = display_compare["price"].map(
        lambda x:f"₹{x:,.2f}"
    )

    display_compare["market_cap"] = display_compare["market_cap"].map(
        lambda x:f"{x:,.0f}"
    )

    display_compare["pe_ratio"] = display_compare["pe_ratio"].map(
        lambda x:f"{x:.2f}"
    )

    display_compare["eps"] = display_compare["eps"].map(
        lambda x:f"{x:.2f}"
    )

    st.dataframe(
        display_compare,
        use_container_width=True,
        hide_index=True
    )

    st.write("")

    # ------------------------------------------------

    # PRICE COMPARISON

    # ------------------------------------------------

    fig_compare = px.bar(

        comparison_df,

        x="company",

        y="price",

        color="company",

        text="price",

        color_discrete_sequence=px.colors.qualitative.Bold,

        title="Current Share Price Comparison"

    )

    fig_compare.update_traces(

        textposition="outside"

    )

    fig_compare.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0E1117",

        plot_bgcolor="#0E1117",

        title_x=0.5,

        height=520,

        showlegend=False

    )

    st.plotly_chart(

        fig_compare,

        use_container_width=True

    )

    # ------------------------------------------------

    # HISTORICAL PERFORMANCE

    # ------------------------------------------------

    st.subheader("📈 Historical Performance")

    history_df = pd.DataFrame()

    for company_name in compare_companies:

        symbol = df[
            df["company"] == company_name
        ].iloc[0]["symbol"]

        stock = yf.Ticker(symbol)

        history = stock.history(period=period)

        history_df[company_name] = history["Close"]

    line_fig = px.line(

        history_df,

        title="Historical Closing Price Comparison"

    )

    line_fig.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0E1117",

        plot_bgcolor="#0E1117",

        title_x=0.5,

        height=600,

        xaxis_title="Date",

        yaxis_title="Closing Price"

    )

    st.plotly_chart(

        line_fig,

        use_container_width=True

    )

    # ------------------------------------------------

    # PE RATIO

    # ------------------------------------------------

    st.subheader("📊 PE Ratio Comparison")

    fig_pe = px.bar(

        comparison_df,

        x="company",

        y="pe_ratio",

        color="company",

        text="pe_ratio",

        color_discrete_sequence=px.colors.qualitative.Set2

    )

    fig_pe.update_traces(

        textposition="outside"

    )

    fig_pe.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0E1117",

        plot_bgcolor="#0E1117",

        title_x=0.5,

        height=500,

        showlegend=False,

        xaxis_title="Company",

        yaxis_title="PE Ratio"

    )

    st.plotly_chart(

        fig_pe,

        use_container_width=True

    )

    # ------------------------------------------------

    # MARKET CAP

    # ------------------------------------------------

    st.subheader("💰 Market Capitalization Comparison")

    fig_market = px.bar(

        comparison_df.sort_values(

            "market_cap",

            ascending=False

        ),

        x="company",

        y="market_cap",

        color="market_cap",

        color_continuous_scale="Viridis"

    )

    fig_market.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0E1117",

        plot_bgcolor="#0E1117",

        title_x=0.5,

        height=520,

        coloraxis_showscale=False,

        xaxis_title="Company",

        yaxis_title="Market Cap"

    )

    st.plotly_chart(

        fig_market,

        use_container_width=True

    )

else:

    st.divider()

    st.info(

        "👈 Select two or more companies from the sidebar to activate the comparison dashboard."

    )