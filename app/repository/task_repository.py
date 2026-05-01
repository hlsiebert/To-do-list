"""SQLite repository implementation for task persistence."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from uuid import UUID, uuid4

from app.database import DEFAULT_DB_PATH, get_connection, initialize_database
from app.models.tasks import (
    TaskCreate,
    TaskPriority,
    TaskPrioritySource,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)


class TaskRepository:
    """Provides basic CRUD operations for tasks using SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        initialize_database(self._db_path)

    def _connect(self) -> sqlite3.Connection:
        """Creates a connection with rows accessible by column name."""
        return get_connection(self._db_path)

    def _task_id_param(self, task_id: UUID) -> str:
        """Converts UUID to SQL parameter format."""
        return str(task_id)

    def _serialize_datetime(self, value: datetime | None) -> str | None:
        """Serializes datetime to ISO-8601 string."""
        return value.isoformat() if value else None

    def _build_update_statement(
        self,
        payload: dict[str, object],
    ) -> tuple[str, list[object]]:
        """Builds dynamic SQL fragment and values for task update."""
        fields: list[str] = []
        values: list[object] = []

        for key, value in payload.items():
            if isinstance(value, datetime):
                value = value.isoformat()
            fields.append(f"{key} = ?")
            values.append(value)

        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        return ", ".join(fields), values

    def _row_to_task(self, row: sqlite3.Row) -> TaskResponse:
        """Maps a database row to a TaskResponse model."""
        return TaskResponse(
            id=UUID(row["id"]),
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            priority_suggested=row["priority_suggested"],
            priority_source=row["priority_source"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=(
                datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None
            ),
            due_date=(datetime.fromisoformat(row["due_date"]) if row["due_date"] else None),
        )

    def create(
        self,
        task: TaskCreate,
        *,
        priority: TaskPriority,
        priority_suggested: TaskPriority | None,
        priority_source: TaskPrioritySource,
    ) -> TaskResponse:
        """Inserts a new task and returns the persisted record."""
        now = datetime.now().isoformat()
        due_date = self._serialize_datetime(task.due_date)
        task_id = uuid4()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    id,
                    title,
                    description,
                    priority,
                    priority_suggested,
                    priority_source,
                    status,
                    created_at,
                    due_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self._task_id_param(task_id),
                    task.title,
                    task.description,
                    priority,
                    priority_suggested,
                    priority_source,
                    task.status,
                    now,
                    due_date,
                ),
            )
            connection.commit()

        created_task = self.get_by_id(task_id)
        if created_task is None:
            raise RuntimeError("Failed to load task after creation.")
        return created_task

    def list(
        self,
        *,
        priority: TaskPriority | None = None,
        status: TaskStatus | None = None,
    ) -> list[TaskResponse]:
        """Returns tasks filtered by priority/status and ordered by recent creation."""
        filters: list[str] = []
        values: list[object] = []

        if priority is not None:
            filters.append("priority = ?")
            values.append(priority)
        if status is not None:
            filters.append("status = ?")
            values.append(status)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        query = f"SELECT * FROM tasks {where_clause} ORDER BY created_at DESC"

        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_by_id(self, task_id: UUID) -> TaskResponse | None:
        """Returns one task by UUID or None when not found."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (self._task_id_param(task_id),),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_task(row)

    def update(
        self,
        task_id: UUID,
        task_update: TaskUpdate,
        *,
        priority: TaskPriority | None = None,
        priority_suggested: TaskPriority | None = None,
        priority_source: TaskPrioritySource | None = None,
    ) -> TaskResponse | None:
        """Updates task fields provided in payload and returns updated task."""
        current_task = self.get_by_id(task_id)
        if current_task is None:
            return None

        payload = task_update.model_dump(
            exclude_unset=True,
            exclude={"priority_mode", "priority_manual"},
        )
        if priority is not None:
            payload["priority"] = priority
        if priority_suggested is not None:
            payload["priority_suggested"] = priority_suggested
        if priority_source is not None:
            payload["priority_source"] = priority_source
        if not payload:
            return current_task

        set_clause, values = self._build_update_statement(payload)
        values.append(self._task_id_param(task_id))
        query = f"UPDATE tasks SET {set_clause} WHERE id = ?"

        with self._connect() as connection:
            connection.execute(query, values)
            connection.commit()

        return self.get_by_id(task_id)

    def delete(self, task_id: UUID) -> bool:
        """Deletes a task by UUID and returns True when a row was removed."""
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (self._task_id_param(task_id),),
            )
            connection.commit()

        return cursor.rowcount > 0
