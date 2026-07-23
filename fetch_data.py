import sqlite3
import yfinance as yf

# Connect to database
connection = sqlite3.connect("stocks.db")
cursor = connection.cursor()

# List of 20 companies
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
    "MARUTI.NS",
    "KOTAKBANK.NS",
    "ASIANPAINT.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "BAJFINANCE.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
    "NTPC.NS"
]

# Remove old data before inserting fresh data
cursor.execute("DELETE FROM stocks")

# Fetch and store data
for company in companies:

    stock = yf.Ticker(company)
    info = stock.info

    company_name = info.get("longName", "N/A")
    price = info.get("currentPrice", 0)
    market_cap = info.get("marketCap", 0)
    pe_ratio = info.get("trailingPE", 0)
    eps = info.get("trailingEps", 0)

    cursor.execute("""
        INSERT INTO stocks
        (company, symbol, price, market_cap, pe_ratio, eps)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        company_name,
        company,
        price,
        market_cap,
        pe_ratio,
        eps
    ))

    print(f"Saved {company_name}")

# Save everything
connection.commit()

# Close database
connection.close()

print("\nAll companies stored successfully!")


