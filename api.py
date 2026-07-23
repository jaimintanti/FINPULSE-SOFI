from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI()

companies = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "BHARTIARTL.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "ASIANPAINT.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "BAJFINANCE.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
    "NTPC.NS"
]


@app.get("/")
def home():
    return {"message": "Welcome to FinPulse API!"}


def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)

        fast = stock.fast_info

        # Latest market price
        price = fast.get("lastPrice")

        if price is None:
            history = stock.history(period="1d")
            if history.empty:
                return None
            price = float(history["Close"].iloc[-1])

        info = stock.info

        return {
            "company": info.get("longName", symbol),
            "symbol": symbol,
            "price": round(float(price), 2),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps")
        }

    except Exception:
        return None


@app.get("/stocks")
def get_stocks():

    stocks = []

    for symbol in companies:

        data = get_stock_data(symbol)

        if data:
            stocks.append(data)

    return stocks


@app.get("/stocks/{symbol}")
def get_stock(symbol: str):

    symbol = symbol.upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    data = get_stock_data(symbol)

    if data:
        return data

    raise HTTPException(
        status_code=404,
        detail="Stock not found"
    )


@app.get("/top-stocks")
def get_top_stocks():

    stocks = []

    for symbol in companies:

        data = get_stock_data(symbol)

        if data:
            stocks.append(data)

    stocks.sort(
        key=lambda x: x["price"],
        reverse=True
    )

    return stocks[:5]