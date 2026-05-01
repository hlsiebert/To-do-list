from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app.models.tasks import TaskCreate, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService


class StubPriorityAdvisor:
    """Simple advisor to keep tests deterministic."""

    def __init__(self, value: int = 4) -> None:
        self.value = value

    def suggest_priority(self, title: str, description: str | None) -> int:
        return self.value

    def suggest_with_source(self, title: str, description: str | None) -> tuple[int, str]:
        return self.value, "ia"


@pytest.fixture
def task_service() -> TaskService:
    """Creates TaskService with temporary SQLite per test."""
    base_dir = Path("tests") / "_runtime_db"
    base_dir.mkdir(parents=True, exist_ok=True)
    db_file = base_dir / f"service_{uuid4()}.db"

    repository = TaskRepository(db_path=str(db_file))
    advisor = StubPriorityAdvisor(value=4)
    return TaskService(repository=repository, priority_advisor=advisor)


def test_create_task_should_persist_and_return_task(task_service: TaskService) -> None:
    payload = TaskCreate(
        title="Prepare release",
        description="Validate final checklist",
        priority="baixa",
        status="pendente",
    )

    created = task_service.create_task(payload)

    assert created.id is not None
    assert created.title == payload.title
    assert created.description == payload.description
    assert created.priority == "alta"
    assert created.priority_suggested == "alta"
    assert created.priority_source == "ia"
    assert created.status == "pendente"


def test_create_task_manual_mode_should_override_suggestion(task_service: TaskService) -> None:
    payload = TaskCreate(
        title="Prepare release",
        description="Validate final checklist",
        priority_mode="manual",
        priority_manual="baixa",
        status="pendente",
    )

    created = task_service.create_task(payload)

    assert created.priority == "baixa"
    assert created.priority_suggested == "alta"
    assert created.priority_source == "manual"


def test_list_tasks_should_return_all_created_tasks(task_service: TaskService) -> None:
    first = TaskCreate(
        title="Task 1",
        description="Description 1",
        priority="media",
        status="pendente",
    )
    second = TaskCreate(
        title="Task 2",
        description="Description 2",
        priority="media",
        status="pendente",
    )

    task_service.create_task(first)
    task_service.create_task(second)

    tasks = task_service.list_tasks()

    assert len(tasks) == 2
    titles = {task.title for task in tasks}
    assert titles == {"Task 1", "Task 2"}


def test_update_task_should_change_fields(task_service: TaskService) -> None:
    created = task_service.create_task(
        TaskCreate(
            title="Old task",
            description="Old description",
            priority="baixa",
            status="pendente",
        )
    )

    updated = task_service.update_task(
        created.id,
        TaskUpdate(
            title="New task",
            description="New description",
            status="em_andamento",
            priority_mode="auto",
        ),
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "New task"
    assert updated.description == "New description"
    assert updated.status == "em_andamento"
    assert updated.priority == "alta"
    assert updated.priority_source == "ia"


def test_update_task_manual_mode_should_override_suggestion(task_service: TaskService) -> None:
    created = task_service.create_task(
        TaskCreate(
            title="Task",
            description="Description",
            status="pendente",
        )
    )

    updated = task_service.update_task(
        created.id,
        TaskUpdate(priority_mode="manual", priority_manual="critica"),
    )

    assert updated is not None
    assert updated.priority == "critica"
    assert updated.priority_source == "manual"


def test_delete_task_should_remove_existing_task(task_service: TaskService) -> None:
    created = task_service.create_task(
        TaskCreate(
            title="Task to delete",
            description="Description",
            priority="media",
            status="pendente",
        )
    )

    deleted = task_service.delete_task(created.id)
    found_after_delete = task_service.get_task_by_id(created.id)

    assert deleted is True
    assert found_after_delete is None


def test_get_task_by_id_should_return_none_for_nonexistent_id(task_service: TaskService) -> None:
    missing = task_service.get_task_by_id(uuid4())

    assert missing is None


def test_update_task_should_return_none_for_nonexistent_id(task_service: TaskService) -> None:
    updated = task_service.update_task(
        uuid4(),
        TaskUpdate(title="Does not exist"),
    )

    assert updated is None


def test_delete_task_should_return_false_for_nonexistent_id(task_service: TaskService) -> None:
    deleted = task_service.delete_task(uuid4())

    assert deleted is False
