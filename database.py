import sqlite3

# Connect to (or create) a database file
connection = sqlite3.connect("stocks.db")

# Create a cursor
cursor = connection.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stocks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    symbol TEXT,
    price REAL,
    market_cap REAL,
    pe_ratio REAL,
    eps REAL
)
""")

print("Database created successfully!")

connection.commit()
connection.close()