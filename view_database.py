import sqlite3

connection = sqlite3.connect("stocks.db")
cursor = connection.cursor()

cursor.execute("SELECT * FROM stocks")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()