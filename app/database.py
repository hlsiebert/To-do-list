"""Database helpers for SQLite connection and initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

DEFAULT_DB_PATH = "app/data/tasks.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Creates a SQLite connection with dict-like rows."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _column_exists(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Checks whether a column exists in a SQLite table."""
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def _get_column_type(connection: sqlite3.Connection, table_name: str, column_name: str) -> str | None:
    """Returns the declared SQL type for a table column."""
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    for row in rows:
        if row[1] == column_name:
            return str(row[2]).upper()
    return None


def _migrate_id_to_uuid(connection: sqlite3.Connection) -> None:
    """Migrates tasks table id from integer to UUID text when necessary."""
    id_type = _get_column_type(connection, "tasks", "id")
    if id_type is None or "TEXT" in id_type:
        return

    connection.execute(
        """
        CREATE TABLE tasks_new (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            priority_suggested TEXT,
            priority_source TEXT NOT NULL DEFAULT 'manual',
            status TEXT NOT NULL DEFAULT 'pendente',
            created_at TEXT NOT NULL,
            updated_at TEXT,
            due_date TEXT
        )
        """
    )

    rows = connection.execute(
        """
        SELECT title, description, priority, status, created_at, updated_at, due_date
        FROM tasks
        """
    ).fetchall()

    for row in rows:
        connection.execute(
            """
            INSERT INTO tasks_new (
                id,
                title,
                description,
                priority,
                priority_suggested,
                priority_source,
                status,
                created_at,
                updated_at,
                due_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                row["title"],
                row["description"],
                row["priority"],
                None,
                "manual",
                row["status"] if "status" in row.keys() else "pendente",
                row["created_at"],
                row["updated_at"],
                row["due_date"],
            ),
        )

    connection.execute("DROP TABLE tasks")
    connection.execute("ALTER TABLE tasks_new RENAME TO tasks")


def initialize_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """Ensures the core tasks table exists and required columns are present."""
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                priority_suggested TEXT,
                priority_source TEXT NOT NULL DEFAULT 'manual',
                status TEXT NOT NULL DEFAULT 'pendente',
                created_at TEXT NOT NULL,
                updated_at TEXT,
                due_date TEXT
            )
            """
        )

        if not _column_exists(connection, "tasks", "status"):
            connection.execute("ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'pendente'")
        if not _column_exists(connection, "tasks", "priority_suggested"):
            connection.execute("ALTER TABLE tasks ADD COLUMN priority_suggested TEXT")
        if not _column_exists(connection, "tasks", "priority_source"):
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN priority_source TEXT NOT NULL DEFAULT 'manual'"
            )

        _migrate_id_to_uuid(connection)
        connection.commit()
