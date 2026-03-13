import sqlite3

conn = sqlite3.connect("../users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()