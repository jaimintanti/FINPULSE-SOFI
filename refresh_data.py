import sqlite3
import yfinance as yf
import time

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

connection = sqlite3.connect("stocks.db")
cursor = connection.cursor()

cursor.execute("DELETE FROM stocks")

print("Updating Database...")

for symbol in companies:

    try:

        stock = yf.Ticker(symbol)

        info = stock.fast_info

        # Latest available market price
        price = info.get("lastPrice")

        # Fallback if unavailable
        if price is None:
            history = stock.history(period="5d")
            price = float(history["Close"].iloc[-1])

        full_info = stock.info

        company = full_info.get("longName", symbol)
        market_cap = full_info.get("marketCap")
        pe_ratio = full_info.get("trailingPE")
        eps = full_info.get("trailingEps")

        cursor.execute("""
        INSERT INTO stocks(
            company,
            symbol,
            price,
            market_cap,
            pe_ratio,
            eps
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            company,
            symbol,
            float(price),
            market_cap,
            pe_ratio,
            eps
        ))

        print(f"Updated: {company}")

        time.sleep(0.2)

    except Exception as e:

        print(f"Error updating: {symbol}")
        print(e)

connection.commit()
connection.close()

print("Database Updated Successfully!")