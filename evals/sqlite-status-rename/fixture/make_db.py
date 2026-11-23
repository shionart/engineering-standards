import sqlite3

conn = sqlite3.connect("shop.db")
conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
conn.executemany("INSERT INTO orders (status) VALUES (?)", [("pending",), ("pending",), ("shipped",)])
conn.commit()
conn.close()
