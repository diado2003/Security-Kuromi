import sqlite3
import bcrypt

DB_PATH = "../users.db"


def is_bcrypt_hash(value: str) -> bool:
    return value.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def ensure_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT NOT NULL DEFAULT 'USER',
            reset_token TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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

    columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "password" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
    if "reset_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    if "locked" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN locked INTEGER NOT NULL DEFAULT 0")

    # Backward compatibility: if an older schema used hashed_password, copy it.
    if "hashed_password" in columns:
        cursor.execute(
            """
            UPDATE users
            SET password = COALESCE(password, hashed_password)
            WHERE password IS NULL
            """
        )


def migrate_plaintext_passwords(cursor: sqlite3.Cursor) -> int:
    cursor.execute("SELECT id, password FROM users WHERE password IS NOT NULL")
    rows = cursor.fetchall()
    migrated = 0

    for user_id, stored_password in rows:
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
        migrated += 1

    return migrated


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ensure_schema(cursor)
    migrated_count = migrate_plaintext_passwords(cursor)

    conn.commit()
    conn.close()

    print(f"DB schema verified. Migrated {migrated_count} plaintext passwords to bcrypt.")


if __name__ == "__main__":
    main()
