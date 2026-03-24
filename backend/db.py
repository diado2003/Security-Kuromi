import sqlite3

conn = sqlite3.connect("../users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT NOT NULL DEFAULT 'USER',
    reset_token TEXT
)
""")

columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
if "role" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'USER'")
if "reset_token" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")

conn.commit()