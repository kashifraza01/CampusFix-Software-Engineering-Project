import hashlib
import os
import sqlite3

from datetime import datetime
from pathlib import Path

from config import DB_NAME


BASE_DIR=Path(__file__).resolve().parent
DB_PATH=BASE_DIR/DB_NAME

def _connect():
    c=sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

def hash_password(password:str)->str:
    password_bytes=password.encode("utf-8")

    return hashlib.sha256(password_bytes).hexdigest()


def initialize_database():
    with _connect() as c:

        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('User', 'Admin')),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                priority TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Submitted',
                assigned_to TEXT DEFAULT '',
                admin_note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_complaints_user
            ON complaints(user_id);

            CREATE INDEX IF NOT EXISTS idx_complaints_status
            ON complaints(status);

            CREATE INDEX IF NOT EXISTS idx_complaints_priority
            ON complaints(priority);
            """
        )

        user_count = c.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        if user_count == 0:
            current_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            demo_users = [
                (
                    "Campus Administrator",
                    "admin@campusfix.local",
                    hash_password("admin123"),
                    "Admin",
                    current_time
                ),
                (
                    "Demo Student",
                    "student@campusfix.local",
                    hash_password("student123"),
                    "User",
                    current_time
                )
            ]

            c.executemany(
                """
                INSERT INTO users (
                    full_name,
                    email,
                    password_hash,
                    role,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                demo_users
            )


def authenticate(email: str, password: str):
    with _connect() as c:

        user = c.execute(
            """
            SELECT id, full_name, email, role
            FROM users
            WHERE lower(email) = lower(?)
            AND password_hash = ?
            """,
            (
                email.strip(),
                hash_password(password)
            )
        ).fetchone()

        if user:
            return dict(user)

        return None


def register_user(full_name: str, email: str, password: str):
    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:
        with _connect() as c:

            c.execute(
                """
                INSERT INTO users (
                    full_name,
                    email,
                    password_hash,
                    role,
                    created_at
                )
                VALUES (?, ?, ?, 'User', ?)
                """,
                (
                    full_name.strip(),
                    email.strip().lower(),
                    hash_password(password),
                    current_time
                )
            )

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def add_complaint(
    user_id: int,
    title: str,
    category: str,
    location: str,
    priority: str,
    description: str
):
    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with _connect() as c:

        cursor = c.execute(
            """
            INSERT INTO complaints (
                user_id,
                title,
                category,
                location,
                priority,
                description,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Submitted', ?, ?)
            """,
            (
                user_id,
                title.strip(),
                category,
                location,
                priority,
                description.strip(),
                current_time,
                current_time
            )
        )

        return cursor.lastrowid


def get_user_complaints(user_id: int):
    with _connect() as c:

        complaints = c.execute(
            """
            SELECT
                id,
                title,
                category,
                location,
                priority,
                status,
                assigned_to,
                created_at,
                updated_at
            FROM complaints
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

        return [dict(complaint) for complaint in complaints]


def get_all_complaints(status_filter="All", search_text=""):
    query = """
        SELECT
            c.id,
            c.title,
            c.category,
            c.location,
            c.priority,
            c.status,
            c.assigned_to,
            c.created_at,
            u.full_name AS reporter,
            u.email AS reporter_email
        FROM complaints c
        JOIN users u ON u.id = c.user_id
        WHERE 1=1
    """

    parameters = []

    if status_filter and status_filter != "All":
        query += " AND c.status = ?"
        parameters.append(status_filter)

    if search_text.strip():
        query += """
            AND (
                lower(c.title) LIKE ?
                OR lower(u.full_name) LIKE ?
                OR lower(c.category) LIKE ?
                OR CAST(c.id AS TEXT) LIKE ?
            )
        """

        search_term = f"%{search_text.strip().lower()}%"

        parameters.extend([
            search_term,
            search_term,
            search_term,
            search_term
        ])

    query += """
        ORDER BY
        CASE c.priority
            WHEN 'Urgent' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
            ELSE 4
        END,
        c.id DESC
    """

    with _connect() as c:

        complaints = c.execute(
            query,
            parameters
        ).fetchall()

        return [dict(complaint) for complaint in complaints]


def get_complaint(complaint_id: int):
    with _connect() as c:

        complaint = c.execute(
            """
            SELECT
                c.*,
                u.full_name AS reporter,
                u.email AS reporter_email
            FROM complaints c
            JOIN users u ON u.id = c.user_id
            WHERE c.id = ?
            """,
            (complaint_id,)
        ).fetchone()

        if complaint:
            return dict(complaint)

        return None


def update_complaint(
    complaint_id: int,
    status: str,
    assigned_to: str,
    admin_note: str
):
    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with _connect() as c:

        c.execute(
            """
            UPDATE complaints
            SET
                status = ?,
                assigned_to = ?,
                admin_note = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                assigned_to.strip(),
                admin_note.strip(),
                current_time,
                complaint_id
            )
        )


def get_dashboard_stats(user_id=None):
    with _connect() as c:

        if user_id is None:

            total = c.execute(
                "SELECT COUNT(*) FROM complaints"
            ).fetchone()[0]

            open_count = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE status NOT IN ('Resolved', 'Closed')
                """
            ).fetchone()[0]

            resolved = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE status IN ('Resolved', 'Closed')
                """
            ).fetchone()[0]

            urgent = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE priority = 'Urgent'
                AND status NOT IN ('Resolved', 'Closed')
                """
            ).fetchone()[0]

        else:

            total = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()[0]

            open_count = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE user_id = ?
                AND status NOT IN ('Resolved', 'Closed')
                """,
                (user_id,)
            ).fetchone()[0]

            resolved = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE user_id = ?
                AND status IN ('Resolved', 'Closed')
                """,
                (user_id,)
            ).fetchone()[0]

            urgent = c.execute(
                """
                SELECT COUNT(*)
                FROM complaints
                WHERE user_id = ?
                AND priority = 'Urgent'
                AND status NOT IN ('Resolved', 'Closed')
                """,
                (user_id,)
            ).fetchone()[0]

        return {
            "total": total,
            "open": open_count,
            "resolved": resolved,
            "urgent": urgent
        }


def delete_database_for_testing():
    if DB_PATH.exists():
        os.remove(DB_PATH)
