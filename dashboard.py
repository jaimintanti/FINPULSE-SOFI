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
# DESIGN TOKENS
# ---------------------------------------------------
# A trading-terminal inspired palette: deep indigo-navy base,
# a warm brass/gold accent (ticker, prosperity, BSE bull), a
# mint for gains and a coral for losses. Numeric data is set
# in a monospaced face so figures always align, like a real
# quote board.

INK        = "#080C16"   # page background
SURFACE    = "#10182A"   # cards / containers
SURFACE_2  = "#182338"   # hover / raised surface
BORDER     = "#243252"   # hairlines
GOLD       = "#D4AF6A"   # primary accent
GOLD_DIM   = "#8A7142"
MINT       = "#3ECF8E"   # positive / secondary accent
CORAL      = "#F2637A"   # negative / tertiary accent
BLUE       = "#5B8DEF"   # quaternary accent
LILAC      = "#A78BFA"   # quinary accent
TEXT       = "#E9ECF4"
MUTED      = "#8B93AC"

# Ordered discrete sequence used across every multi-series chart
# so the same company always reads with the same character.
BRAND_SEQUENCE = [GOLD, MINT, BLUE, LILAC, CORAL, "#7DD3E0", "#C9A87C", "#9FB8E8"]

# Custom sequential scales (dark surface -> accent) replace the
# generic Plotly Blues / Greens / Viridis defaults.
SCALE_GOLD = [[0, SURFACE_2], [1, GOLD]]
SCALE_MINT = [[0, SURFACE_2], [1, MINT]]
SCALE_BLUE = [[0, SURFACE_2], [1, BLUE]]

FONT_BODY = "Inter, -apple-system, sans-serif"
FONT_MONO = "'IBM Plex Mono', 'Courier New', monospace"

CHART_LAYOUT = dict(
    paper_bgcolor=INK,
    plot_bgcolor=INK,
    font=dict(family=FONT_BODY, color=TEXT, size=13),
    title_font=dict(family=FONT_BODY, color=TEXT, size=19),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
    hoverlabel=dict(bgcolor=SURFACE_2, font=dict(family=FONT_MONO, color=TEXT), bordercolor=BORDER),
    margin=dict(l=40, r=30, t=70, b=40),
)

AXIS_STYLE = dict(
    gridcolor=BORDER,
    zerolinecolor=BORDER,
    linecolor=BORDER,
    tickfont=dict(family=FONT_MONO, color=MUTED, size=12),
    title_font=dict(family=FONT_BODY, color=MUTED, size=13),
)


def style_fig(fig, height=520):
    """Apply the shared FinPulse chart theme without touching any data/logic."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        title_x=0.03,
        title_xanchor="left",
        **CHART_LAYOUT,
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig


# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: {FONT_BODY};
}}

.stApp {{
    background-color: {INK};
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 42px 42px;
}}

.block-container {{
    padding-top: 3.5rem;
    padding-bottom: 3rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
    max-width: 1400px;
}}

header[data-testid="stHeader"] {{
    background: {INK};
}}

/* ---------- headings ---------- */

h1 {{
    font-family: 'Space Grotesk', {FONT_BODY};
    color: {TEXT};
    font-weight: 700;
    letter-spacing: -0.01em;
}}

h2, h3 {{
    font-family: 'Space Grotesk', {FONT_BODY};
    color: {TEXT};
    font-weight: 600;
}}

h4, h5, p, span, label {{
    color: {MUTED};
}}

/* ---------- hero header ---------- */

.fp-hero {{
    display: flex;
    align-items: baseline;
    gap: 0.85rem;
    margin-bottom: 0.2rem;
}}

.fp-pulse {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {MINT};
    box-shadow: 0 0 0 0 rgba(62, 207, 142, 0.5);
    animation: fp-ping 2.6s ease-in-out infinite;
    flex-shrink: 0;
    align-self: center;
}}

@keyframes fp-ping {{
    0%   {{ box-shadow: 0 0 0 0 rgba(62, 207, 142, 0.45); }}
    70%  {{ box-shadow: 0 0 0 6px rgba(62, 207, 142, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(62, 207, 142, 0); }}
}}

.fp-title {{
    font-family: 'Space Grotesk', {FONT_BODY};
    font-size: 1.9rem;
    font-weight: 700;
    color: {TEXT};
    letter-spacing: -0.02em;
}}

.fp-title span {{
    color: {GOLD};
}}

.fp-tag {{
    font-family: {FONT_MONO};
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    color: {GOLD_DIM};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 0.15rem 0.45rem;
    text-transform: uppercase;
}}

.fp-subtitle {{
    font-family: {FONT_BODY};
    color: {MUTED};
    font-size: 1.02rem;
    max-width: 640px;
    line-height: 1.55;
    margin-top: 0.35rem;
}}

.fp-rule {{
    height: 1px;
    background: {BORDER};
    margin: 1.4rem 0 1.6rem 0;
    border: none;
    position: relative;
}}

.fp-rule::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    height: 1px;
    width: 64px;
    background: {GOLD};
}}

/* ---------- sidebar ---------- */

section[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    font-family: 'Space Grotesk', {FONT_BODY};
    color: {TEXT};
    font-size: 1.05rem;
    letter-spacing: 0.02em;
}}

section[data-testid="stSidebar"] hr {{
    border-color: {BORDER};
}}

/* ---------- inputs ---------- */

div[data-baseweb="select"] > div,
.stMultiSelect > div > div {{
    background-color: {SURFACE_2} !important;
    border-radius: 6px !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
}}

/* ---------- metric cards ---------- */

div[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-left: 2px solid {GOLD_DIM};
    border-radius: 6px;
    padding: 1rem 1.25rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.20);
}}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {{
    font-family: {FONT_BODY} !important;
    color: {MUTED} !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
}}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {{
    font-family: {FONT_MONO} !important;
    color: {GOLD} !important;
    font-weight: 600 !important;
    font-variant-numeric: tabular-nums;
}}

/* ---------- section headers ---------- */

.fp-section-eyebrow {{
    font-family: {FONT_MONO};
    font-size: 0.75rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {GOLD_DIM};
    margin-bottom: -0.4rem;
    padding-left: 0.6rem;
    border-left: 2px solid {GOLD_DIM};
}}

/* ---------- dataframe ---------- */

div[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    overflow: hidden;
}}

/* ---------- buttons ---------- */

.stButton>button {{
    width: 100%;
    border-radius: 6px;
    background: {GOLD};
    color: {INK};
    font-weight: 600;
    border: 1px solid {GOLD};
    font-family: {FONT_BODY};
    transition: filter 0.15s ease;
}}

.stButton>button:hover {{
    filter: brightness(1.08);
}}

.stDownloadButton>button {{
    width: 100%;
    border-radius: 6px;
    background: {SURFACE_2};
    color: {TEXT};
    border: 1px solid {BORDER};
    font-family: {FONT_BODY};
    font-weight: 500;
}}

.stDownloadButton>button:hover {{
    border-color: {GOLD_DIM};
    color: {GOLD};
}}

/* ---------- ticker tape ---------- */

.fp-ticker-wrap {{
    width: 100%;
    overflow: hidden;
    background: {SURFACE};
    border-top: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    padding: 0.55rem 0;
    margin-bottom: 1.4rem;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent);
    mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent);
}}

.fp-ticker-track {{
    display: inline-flex;
    white-space: nowrap;
    animation: fp-scroll 40s linear infinite;
}}

.fp-ticker-wrap:hover .fp-ticker-track {{
    animation-play-state: paused;
}}

@keyframes fp-scroll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-50%); }}
}}

.fp-ticker-item {{
    font-family: {FONT_MONO};
    font-size: 0.86rem;
    color: {TEXT};
    padding: 0 1.4rem;
    border-right: 1px solid {BORDER};
}}

.fp-ticker-price {{
    color: {MUTED};
}}

.fp-ticker-up {{
    color: {MINT};
    font-weight: 600;
}}

.fp-ticker-down {{
    color: {CORAL};
    font-weight: 600;
}}

/* ---------- alert / info box ---------- */

div[data-testid="stAlert"] {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {MUTED};
}}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API
# ---------------------------------------------------

API_URL = "https://finpulse-sofi-omega.vercel.app/stocks"

response = requests.get(API_URL)

df = pd.DataFrame(response.json())

# ---------------------------------------------------
# DAILY MOVEMENT (for the ticker tape)
# ---------------------------------------------------
# Pulls each company's last two closes so the ticker can show how
# much the price moved today, up or down. Cached for 5 minutes so
# it doesn't refetch on every widget interaction.

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_changes(symbols):
    changes = {}
    try:
        hist = yf.download(
            tickers=symbols,
            period="5d",
            interval="1d",
            group_by="ticker",
            progress=False,
            threads=True,
        )
        for sym in symbols:
            try:
                closes = hist[sym]["Close"].dropna() if len(symbols) > 1 else hist["Close"].dropna()
                if len(closes) >= 2:
                    prev, last = closes.iloc[-2], closes.iloc[-1]
                    changes[sym] = ((last - prev) / prev) * 100
            except Exception:
                continue
    except Exception:
        pass
    return changes

daily_changes = get_daily_changes(tuple(df["symbol"].tolist()))

ticker_items = []

for _, row in df.iterrows():
    pct = daily_changes.get(row["symbol"])
    if pct is None:
        continue
    direction = "fp-ticker-up" if pct >= 0 else "fp-ticker-down"
    arrow = "▲" if pct >= 0 else "▼"
    ticker_items.append(
        f'<span class="fp-ticker-item">{row["company"]} '
        f'<span class="fp-ticker-price">₹{row["price"]:,.2f}</span> '
        f'<span class="{direction}">{arrow} {abs(pct):.2f}%</span></span>'
    )

if ticker_items:
    ticker_html = "".join(ticker_items)
    st.markdown(
        f"""
        <div class="fp-ticker-wrap">
            <div class="fp-ticker-track">{ticker_html}{ticker_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------
# HERO TITLE
# ---------------------------------------------------

st.markdown("""
<div class="fp-hero">
    <div class="fp-pulse"></div>
    <div class="fp-title">Fin<span>Pulse</span></div>
    <div class="fp-tag">NSE · BSE</div>
</div>
<div class="fp-subtitle">
    Indian Stock Market Analytics — track live prices, compare fundamentals
    across leading Indian companies, and follow historical trends in one
    interactive terminal.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.markdown("### ⚙ Dashboard Controls")

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

st.sidebar.markdown("#### 📊 Compare Companies")

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

st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------

st.markdown('<div class="fp-section-eyebrow">Fundamentals</div>', unsafe_allow_html=True)
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

st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

# ---------------------------------------------------
# VISUAL ANALYTICS
# ---------------------------------------------------

st.markdown('<div class="fp-section-eyebrow">Analytics</div>', unsafe_allow_html=True)
st.header("📊 Visual Analytics")

# ---------------------------------------------------
# PRICE CHART
# ---------------------------------------------------

fig1 = px.bar(
    filtered_df,
    x="company",
    y="price",
    color="price",
    color_continuous_scale=SCALE_GOLD,
    text_auto=".2f",
    title="Current Stock Prices"
)

style_fig(fig1, height=520)

fig1.update_layout(
    coloraxis_showscale=False,
    xaxis_title="Company",
    yaxis_title="Share Price (₹)"
)

fig1.update_traces(
    textposition="outside",
    textfont=dict(family=FONT_MONO, color=TEXT, size=12),
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
    color_continuous_scale=SCALE_MINT,
    title="Market Capitalization"
)

style_fig(fig2, height=520)

fig2.update_layout(
    coloraxis_showscale=False,
    xaxis_title="Company",
    yaxis_title="Market Cap"
)

fig2.update_traces(marker_line_width=0)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------------------------------------------
# PRICE VS PE
# ---------------------------------------------------

fig3 = px.scatter(
    filtered_df.assign(
        market_cap=pd.to_numeric(filtered_df["market_cap"], errors="coerce").clip(lower=0).fillna(0)
    ),
    x="price",
    y="pe_ratio",
    size="market_cap",
    color="company",
    hover_name="company",
    size_max=45,
    color_discrete_sequence=BRAND_SEQUENCE,
    title="Price vs PE Ratio"
)

style_fig(fig3, height=560)

fig3.update_layout(
    legend_title=""
)

fig3.update_traces(
    marker=dict(
        line=dict(
            width=1,
            color=INK
        ),
        opacity=0.9
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
    hole=0.55,
    color_discrete_sequence=BRAND_SEQUENCE,
    title="Top Companies by Market Capitalization"
)

fig4.update_traces(
    textposition="inside",
    textinfo="percent+label",
    textfont=dict(family=FONT_BODY, size=12, color=INK),
    marker=dict(line=dict(color=INK, width=2))
)

style_fig(fig4, height=650)

fig4.update_layout(
    legend_title=""
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


if company != "All Companies":

    st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

    st.markdown('<div class="fp-section-eyebrow">Historical</div>', unsafe_allow_html=True)
    st.header("📈 Historical Stock Analysis")

    symbol = filtered_df.iloc[0]["symbol"]

    stock = yf.Ticker(symbol)

    history = stock.history(period=period)

    st.subheader(f"{company} ({period})")

    # Line Chart
    st.line_chart(history["Close"], color=GOLD)

    # Candlestick Chart
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Candlestick",
            increasing=dict(line=dict(color=MINT), fillcolor=MINT),
            decreasing=dict(line=dict(color=CORAL), fillcolor=CORAL),
        )
    )

    style_fig(fig, height=650)

    fig.update_layout(
        title="Candlestick Analysis",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        xaxis_rangeslider_visible=False,
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
        name="Close Price",
        line=dict(color=TEXT, width=1.6)
    )
)

    ma_fig.add_trace(
    go.Scatter(
        x=history.index,
        y=history["20 MA"],
        mode="lines",
        name="20-Day MA",
        line=dict(color=GOLD, width=1.8)
    )
)

    ma_fig.add_trace(
    go.Scatter(
        x=history.index,
        y=history["50 MA"],
        mode="lines",
        name="50-Day MA",
        line=dict(color=BLUE, width=1.8)
    )
)

    style_fig(ma_fig, height=600)

    ma_fig.update_layout(
    title="Moving Average Analysis",
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    hovermode="x unified",
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

    st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

    st.markdown('<div class="fp-section-eyebrow">Comparison</div>', unsafe_allow_html=True)
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

        color_discrete_sequence=BRAND_SEQUENCE,

        title="Current Share Price Comparison"

    )

    fig_compare.update_traces(

        textposition="outside",
        textfont=dict(family=FONT_MONO, color=TEXT, size=12),
        marker_line_width=0

    )

    style_fig(fig_compare, height=520)

    fig_compare.update_layout(

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

        title="Historical Closing Price Comparison",

        color_discrete_sequence=BRAND_SEQUENCE

    )

    line_fig.update_traces(line=dict(width=2))

    style_fig(line_fig, height=600)

    line_fig.update_layout(

        xaxis_title="Date",

        yaxis_title="Closing Price",

        legend_title=""

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
    text="pe_ratio",
    color_discrete_sequence=[GOLD],
    title="PE Ratio Comparison"

    )

    fig_pe.update_traces(

        textposition="outside",
        textfont=dict(family=FONT_MONO, color=TEXT, size=12),
        marker_line_width=0

    )

    style_fig(fig_pe)

    fig_pe.update_layout(
    xaxis_title="Company",
    yaxis_title="PE Ratio",
    showlegend=False
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

        color_continuous_scale=SCALE_BLUE,

        title="Market Capitalization Comparison"

    )

    fig_market.update_traces(marker_line_width=0)

    style_fig(fig_market, height=520)

    fig_market.update_layout(

        coloraxis_showscale=False,

        xaxis_title="Company",

        yaxis_title="Market Cap"

    )

    st.plotly_chart(

        fig_market,

        use_container_width=True

    )

else:

    st.markdown('<hr class="fp-rule">', unsafe_allow_html=True)

    st.info(

        "👈 Select two or more companies from the sidebar to activate the comparison dashboard."

    )