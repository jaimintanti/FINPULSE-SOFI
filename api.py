from fastapi import FastAPI
import sqlite3

app = FastAPI()


# Endpoint 1: Check API status
@app.get("/")
def home():
    return {
        "message": "Welcome to FinPulse API!"
    }


# Endpoint 2: Get all stocks
@app.get("/stocks")
def get_stocks():

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM stocks")

    rows = cursor.fetchall()

    connection.close()

    stocks = []

    for row in rows:
        stocks.append({
            "id": row[0],
            "company": row[1],
            "symbol": row[2],
            "price": row[3],
            "market_cap": row[4],
            "pe_ratio": row[5]
        })

    return stocks



# Endpoint 3: Get specific stock by symbol
@app.get("/stocks/{symbol}")
def get_stock(symbol: str):

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM stocks WHERE symbol=?",
        (symbol,)
    )

    row = cursor.fetchone()

    connection.close()

    if row:

        return {
            "id": row[0],
            "company": row[1],
            "symbol": row[2],
            "price": row[3],
            "market_cap": row[4],
            "pe_ratio": row[5]
        }

    return {
        "message": "Stock not found"
    }



# Endpoint 4: Get top 5 stocks by price
@app.get("/top-stocks")
def get_top_stocks():

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM stocks
        ORDER BY price DESC
        LIMIT 5
        """
    )

    rows = cursor.fetchall()

    connection.close()

    top_stocks = []

    for row in rows:

        top_stocks.append({
            "company": row[1],
            "symbol": row[2],
            "price": row[3],
            "market_cap": row[4],
            "pe_ratio": row[5]
        })

    return top_stocks