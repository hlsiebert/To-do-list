"""SQLite repository implementation for task persistence."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from app.database import DEFAULT_DB_PATH, get_connection, initialize_database
from app.models.tasks import TaskCreate, TaskResponse, TaskUpdate


class TaskRepository:
    """Provides basic CRUD operations for tasks using SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        initialize_database(self._db_path)

    def _connect(self) -> sqlite3.Connection:
        """Creates a connection with rows accessible by column name."""
        return get_connection(self._db_path)

    def _row_to_task(self, row: sqlite3.Row) -> TaskResponse:
        """Maps a database row to a TaskResponse model."""
        return TaskResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=(
                datetime.fromisoformat(row["updated_at"])
                if row["updated_at"]
                else None
            ),
            due_date=(datetime.fromisoformat(row["due_date"]) if row["due_date"] else None),
        )

    def create(self, task: TaskCreate) -> TaskResponse:
        """Inserts a new task and returns the persisted record."""
        now = datetime.now().isoformat()
        due_date = task.due_date.isoformat() if task.due_date else None

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, description, priority, completed, created_at, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task.title, task.description, task.priority, 0, now, due_date),
            )
            task_id = cursor.lastrowid
            connection.commit()

        created_task = self.get_by_id(int(task_id))
        if created_task is None:
            raise RuntimeError("Failed to load task after creation.")
        return created_task

    def list(self) -> list[TaskResponse]:
        """Returns all tasks ordered by most recent id first."""
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_by_id(self, task_id: int) -> TaskResponse | None:
        """Returns one task by id or None when not found."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_task(row)

    def update(self, task_id: int, task_update: TaskUpdate) -> TaskResponse | None:
        """Updates task fields provided in payload and returns updated task."""
        current_task = self.get_by_id(task_id)
        if current_task is None:
            return None

        payload = task_update.model_dump(exclude_unset=True)
        if not payload:
            return current_task

        fields: list[str] = []
        values: list[object] = []

        for key, value in payload.items():
            # Keep datetime values serialized consistently in ISO-8601.
            if isinstance(value, datetime):
                value = value.isoformat()
            if isinstance(value, bool):
                value = int(value)
            fields.append(f"{key} = ?")
            values.append(value)

        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(task_id)

        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"

        with self._connect() as connection:
            connection.execute(query, values)
            connection.commit()

        return self.get_by_id(task_id)

    def delete(self, task_id: int) -> bool:
        """Deletes a task by id and returns True when a row was removed."""
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )
            connection.commit()

        return cursor.rowcount > 0
