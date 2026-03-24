import time
import requests
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / "users.db"

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("SELECT password FROM users")
passwords = [row[0] for row in cursor.fetchall()]
conn.close()
print("Extracted passwords from DB:", passwords)

