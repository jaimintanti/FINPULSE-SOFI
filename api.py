from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to FinPulse API!"}


@app.get("/stocks")

def get_stocks():

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT company,
               symbol,
               price,
               market_cap,
               pe_ratio,
               eps
        FROM stocks
    """)

    rows = cursor.fetchall()

    connection.close()

    stocks = []

    for row in rows:
        stocks.append({
            "company": row[0],
            "symbol": row[1],
            "price": row[2],
            "market_cap": row[3],
            "pe_ratio": row[4],
            "eps": row[5]
        })

    return stocks

@app.get("/stock/{symbol}")
def get_stock(symbol: str):

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT company,
               symbol,
               price,
               market_cap,
               pe_ratio,
               eps
        FROM stocks
        WHERE symbol = ?
    """, (symbol,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {"error": "Company not found"}

    return {
        "company": row[0],
        "symbol": row[1],
        "price": row[2],
        "market_cap": row[3],
        "pe_ratio": row[4],
        "eps": row[5]
    }