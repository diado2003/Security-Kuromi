from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
ADMIN_REGISTER_SECRET = os.getenv("ADMIN_REGISTER_SECRET", "admin123")


def get_conn():
    return sqlite3.connect("../users.db")


def ensure_schema():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT NOT NULL DEFAULT 'USER',
            reset_token TEXT
        )
        """
    )

    # Migrate older DBs that do not have the latest columns.
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'USER'")
    if "reset_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")

    conn.commit()
    conn.close()


ensure_schema()

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, role FROM users WHERE username=? AND password=?",
        (data.get("username", ""), data.get("password", "")),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "username": user[0], "role": user[1]})

    return jsonify({"success": False})

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "USER").upper()
    admin_secret = data.get("admin_secret") or ""

    if role not in {"USER", "ADMIN"}:
        role = "USER"

    if role == "ADMIN" and admin_secret != ADMIN_REGISTER_SECRET:
        return jsonify({"success": False, "error": "Parola de admin este gresita."}), 403

    if not username or not password:
        return jsonify({"success": False, "error": "Username si parola sunt obligatorii."}), 400

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role),
        )
        conn.commit()
        return jsonify({"success": True, "role": role})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Username already exists."})
    finally:
        conn.close()


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json or {}
    username = (data.get("username") or "").strip()

    if not username:
        return jsonify({"success": False, "error": "Username obligatoriu."}), 400

    # Intentionally weak for v1: predictable reusable token.
    token = f"reset-{username}"

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "User inexistent."}), 404

    cursor.execute("UPDATE users SET reset_token=? WHERE username=?", (token, username))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "reset_token": token})


@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"success": False, "error": "Token si parola noua sunt obligatorii."}), 400

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE reset_token=?", (token,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "Token invalid."}), 400

    # Intentionally weak for v1: token is reusable and does not expire.
    cursor.execute("UPDATE users SET password=? WHERE reset_token=?", (new_password, token))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)