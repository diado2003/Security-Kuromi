from flask import Flask, request, jsonify, session
import sqlite3
import os
import bcrypt
import secrets
import hashlib
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-change-me")

ADMIN_REGISTER_SECRET = os.getenv("ADMIN_REGISTER_SECRET", "admin123")
RESET_TOKEN_TTL_MINUTES = 15
FORGOT_RESPONSE_DELAY_SECONDS = 0.35
MAX_FAILED_ATTEMPTS = 5
LOCK_WINDOW_MINUTES = 15
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)


def is_bcrypt_hash(value: str) -> bool:
    return value.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def now_utc() -> datetime:
    return datetime()


def verify_password(stored_password, candidate_password: str) -> bool:
    if stored_password is None:
        return False

    if isinstance(stored_password, bytes):
        stored_value = stored_password.decode("utf-8")
    else:
        stored_value = str(stored_password)

    # Accept only modern bcrypt hashes in fixed mode.
    if is_bcrypt_hash(stored_value):
        return bcrypt.checkpw(candidate_password.encode("utf-8"), stored_value.encode("utf-8"))

    return False

def validate_password_strength(password: str) -> bool:
    # Enforce stronger fixed policy for the project.
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special


def get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def failed_login_attempts(cursor: sqlite3.Cursor, user_id: int) -> int:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM audit_logs
        WHERE action='failed_login'
          AND resource_id=?
          AND timestamp > datetime('now', ?)
        """,
        (user_id, f"-{LOCK_WINDOW_MINUTES} minutes"),
    )
    return cursor.fetchone()[0]


def record_failed_login(cursor: sqlite3.Cursor, user_id: int, ip_address: str) -> None:
    cursor.execute(
        "INSERT INTO audit_logs (user_id, action, resource_id, ip_address) VALUES (?, 'failed_login', ?, ?)",
        (user_id, user_id, ip_address),
    )


def clear_failed_logins(cursor: sqlite3.Cursor, user_id: int) -> None:
    cursor.execute("DELETE FROM audit_logs WHERE action='failed_login' AND resource_id=?", (user_id,))


def get_conn():
    return sqlite3.connect("../users.db")


def ensure_schema():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            email TEXT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT NOT NULL DEFAULT 'USER',
            reset_token TEXT,
            locked INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            action TEXT,
            resource_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    # Migrate older DBs that do not have the latest columns.
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "email" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'USER'")
    if "reset_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    if "reset_token_hash" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_hash TEXT")
    if "reset_token_expires_at" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires_at TEXT")
    if "locked" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN locked INTEGER NOT NULL DEFAULT 0")

    conn.commit()
    conn.close()


def migrate_plaintext_passwords():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users")
    rows = cursor.fetchall()

    for user_id, stored_password in rows:
        if stored_password is None:
            continue

        if isinstance(stored_password, bytes):
            stored_value = stored_password.decode("utf-8")
        else:
            stored_value = str(stored_password)

        if is_bcrypt_hash(stored_value):
            continue

        cursor.execute(
            "UPDATE users SET password=? WHERE id=?",
            (hash_password(stored_value), user_id),
        )

    conn.commit()
    conn.close()


ensure_schema()
migrate_plaintext_passwords()

@app.route("/protected", methods=["GET"])
def protected():
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    return jsonify({"message": f"Hello {session['user']}"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    candidate_password = data.get("password") or ""
    ip_address = get_client_ip()

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role, password, locked FROM users WHERE username=?",
        (username,),
    )
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        attempts = failed_login_attempts(cursor, user_id)
        if attempts >= MAX_FAILED_ATTEMPTS:
            cursor.execute("UPDATE users SET locked=1 WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({"success": False, "error": "Invalid credentials"}), 429

    if user and verify_password(user[3], candidate_password):
        # Successful login unlocks account and clears failed-attempt history.
        cursor.execute("UPDATE users SET locked=0 WHERE id=?", (user[0],))
        clear_failed_logins(cursor, user[0])
        conn.commit()

        conn.close()
        session.clear()
        session.permanent = True
        session["user"] = username
        return jsonify({"success": True, "username": user[1], "role": user[2]})

    if user:
        record_failed_login(cursor, user[0], ip_address)
        attempts_after = failed_login_attempts(cursor, user[0])
        if attempts_after >= MAX_FAILED_ATTEMPTS:
            cursor.execute("UPDATE users SET locked=1 WHERE id=?", (user[0],))
        conn.commit()

    conn.close()
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if password and not validate_password_strength(password):
        return jsonify(
            {
                "success": False,
                "error": "Parola trebuie sa aiba cel putin 8 caractere si sa contina litera mare, litera mica, cifra si caracter special.",
            }
        ), 400
    hashed_password = hash_password(password)
    role = (data.get("role") or "USER").upper()
    admin_secret = data.get("admin_secret") or ""

    if role not in {"USER", "ADMIN"}:
        role = "USER"

    if role == "ADMIN" and admin_secret != ADMIN_REGISTER_SECRET:
        return jsonify({"success": False, "error": "Parola de admin este gresita."}), 403

    if not email or not username or not password:
        return jsonify({"success": False, "error": "Email, username si parola sunt obligatorii."}), 400

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return jsonify({"success": False, "error": "Email already exists."}), 409

        cursor.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            (email, username, hashed_password, role),
        )
        conn.commit()
        return jsonify({"success": True, "role": role})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Username already exists."})
    finally:
        conn.close()


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    start = time.perf_counter()
    data = request.json or {}
    username = (data.get("username") or "").strip()

    # Always generate a random token so response shape is constant for existing/non-existing users.
    token = secrets.token_urlsafe(32)
    token_hash = hash_reset_token(token)
    expires_at = (now_utc() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)).isoformat()

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute(
            """
            UPDATE users
            SET reset_token_hash=?, reset_token_expires_at=?, reset_token=NULL
            WHERE username=?
            """,
            (token_hash, expires_at, username),
        )
        conn.commit()

    conn.close()

    # Uniform delay to reduce timing side-channel for user enumeration.
    elapsed = time.perf_counter() - start
    if elapsed < FORGOT_RESPONSE_DELAY_SECONDS:
        time.sleep(FORGOT_RESPONSE_DELAY_SECONDS - elapsed)

    return jsonify(
        {
            "success": True,
            "message": "If the user exists, a reset token was generated.",
            "reset_token": token,
            "expires_in_minutes": RESET_TOKEN_TTL_MINUTES,
        }
    )


@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"success": False, "error": "Token si parola noua sunt obligatorii."}), 400

    if not validate_password_strength(new_password):
        return jsonify(
            {
                "success": False,
                "error": "Parola trebuie sa aiba cel putin 8 caractere si sa contina litera mare, litera mica, cifra si caracter special.",
            }
        ), 400

    token_hash = hash_reset_token(token)
    now_iso = now_utc().isoformat()

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE reset_token_hash=?
          AND reset_token_expires_at IS NOT NULL
          AND reset_token_expires_at > ?
        """,
        (token_hash, now_iso),
    )
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "Token invalid sau expirat."}), 400

    hashed_new_password = hash_password(new_password)
    cursor.execute(
        """
        UPDATE users
        SET password=?, reset_token_hash=NULL, reset_token_expires_at=NULL, reset_token=NULL
        WHERE reset_token_hash=?
        """,
        (hashed_new_password, token_hash),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)