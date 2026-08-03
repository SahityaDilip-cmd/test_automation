"""SQLite helpers for the practice app."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "practice.db"

# Demo users seeded on first run
DEMO_USERS = (
    ("admin", "admin123", "Admin User"),
    ("tester", "test123", "QA Tester"),
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables and seed demo users if the database is empty."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if user_count == 0:
            conn.executemany(
                "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
                DEMO_USERS,
            )


def get_user_by_credentials(username: str, password: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def list_tasks(user_id: int | None = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        if user_id is None:
            return conn.execute(
                """
                SELECT t.*, u.username
                FROM tasks t
                JOIN users u ON u.id = t.user_id
                ORDER BY t.id DESC
                """
            ).fetchall()
        return conn.execute(
            """
            SELECT t.*, u.username
            FROM tasks t
            JOIN users u ON u.id = t.user_id
            WHERE t.user_id = ?
            ORDER BY t.id DESC
            """,
            (user_id,),
        ).fetchall()


def get_task(task_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT t.*, u.username
            FROM tasks t
            JOIN users u ON u.id = t.user_id
            WHERE t.id = ?
            """,
            (task_id,),
        ).fetchone()


def create_task(user_id: int, title: str, description: str = "", status: str = "open") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (user_id, title, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, title, description, status),
        )
        return int(cursor.lastrowid)


def update_task_status(task_id: int, status: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id),
        )
        return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def row_to_task_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"],
    }
