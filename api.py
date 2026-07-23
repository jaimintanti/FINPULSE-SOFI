from fastapi import FastAPI
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


@app.get("/stocks")
def get_stocks():

    stocks = []

    for symbol in companies:

        try:
            stock = yf.Ticker(symbol)

            info = stock.fast_info
            full_info = stock.info

            price = info.get("lastPrice")

            if price is None:
                history = stock.history(period="5d")
                price = float(history["Close"].iloc[-1])

            stocks.append(
                {
                    "company": full_info.get("longName", symbol),
                    "symbol": symbol,
                    "price": float(price),
                    "market_cap": full_info.get("marketCap"),
                    "pe_ratio": full_info.get("trailingPE"),
                    "eps": full_info.get("trailingEps"),
                }
            )

        except Exception:
            stocks.append(
                {
                    "company": symbol,
                    "symbol": symbol,
                    "price": None,
                    "market_cap": None,
                    "pe_ratio": None,
                    "eps": None,
                }
            )

    return stocks


@app.get("/stock/{symbol}")
def get_stock(symbol: str):

    try:

        stock = yf.Ticker(symbol)

        info = stock.fast_info
        full_info = stock.info

        price = info.get("lastPrice")

        if price is None:
            history = stock.history(period="5d")
            price = float(history["Close"].iloc[-1])

        return {
            "company": full_info.get("longName", symbol),
            "symbol": symbol,
            "price": float(price),
            "market_cap": full_info.get("marketCap"),
            "pe_ratio": full_info.get("trailingPE"),
            "eps": full_info.get("trailingEps"),
        }

    except Exception:

        return {"error": "Company not found"}