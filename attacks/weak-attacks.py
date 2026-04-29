import time
import requests
import sqlite3
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "users.db"
BASE_URL = "http://127.0.0.1:5000"


def register(base_url: str, username: str, password: str):
    response = requests.post(
        f"{base_url}/register",
        json={"email": f"{username}@example.test", "username": username, "password": password},
        timeout=10,
    )
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}
    return response.status_code, body


def dump_passwords():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows


def main():
    parser = argparse.ArgumentParser(description="PoC weak password/plaintext storage: vulnerable accepts weak passwords; fixed rejects/hashes.")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--expected", choices=["vulnerable", "fixed"], default="fixed")
    parser.add_argument("--username", default=f"weakdemo{int(time.time())}")
    parser.add_argument("--weak-password", default="123")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    print("=== Weak password and DB storage PoC ===")
    print(f"Target: {base_url}/register")
    print(f"Expected mode: {args.expected}")
    print("Vulnerable: weak password accepted and DB may contain plaintext/hash-weak values.")
    print("Fixed: weak password rejected; stored passwords are bcrypt hashes.\n")

    print(f"POST /register username={args.username!r} password={args.weak_password!r}")
    status, body = register(base_url, args.username, args.weak_password)
    print(f"Status: {status}, Response: {body}")

    print("\nDB password sample:")
    rows = dump_passwords()
    for username, password in rows[:10]:
        print(f"{username}: {password}")

    weak_accepted = status < 400 and isinstance(body, dict) and body.get("success") is True
    plaintext_seen = any(password == args.weak_password for _, password in rows)
    all_hashes = all(str(password).startswith(("$2a$", "$2b$", "$2y$")) for _, password in rows if password)

    print("\n=== Result ===")
    if args.expected == "fixed":
        print("PASS" if not weak_accepted and all_hashes else "CHECK MANUALLY: fixed mode should reject weak passwords and store bcrypt only.")
    else:
        print("PASS" if weak_accepted or plaintext_seen else "CHECK MANUALLY: vulnerable mode should show weak acceptance or unsafe storage.")


if __name__ == "__main__":
    main()

