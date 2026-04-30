from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app.models.tasks import TaskCreate, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService


class StubPriorityAdvisor:
    """Advisor simples para manter testes determinísticos."""

    def __init__(self, value: int = 4) -> None:
        self.value = value

    def suggest_priority(self, title: str, description: str | None) -> int:
        return self.value


@pytest.fixture
def task_service(tmp_path: Path) -> TaskService:
    """Cria TaskService com SQLite temporário por teste."""
    db_path = tmp_path / "tasks_test.db"
    repository = TaskRepository(db_path=str(db_path))
    advisor = StubPriorityAdvisor(value=4)
    return TaskService(repository=repository, priority_advisor=advisor)


def test_create_task_should_persist_and_return_task(task_service: TaskService) -> None:
    payload = TaskCreate(
        title="Preparar release",
        description="Validar checklist final",
        priority="baixa",
        status="pendente",
    )

    created = task_service.create_task(payload)

    assert created.id is not None
    assert created.title == payload.title
    assert created.description == payload.description
    assert created.priority == "alta"
    assert created.status == "pendente"


def test_list_tasks_should_return_all_created_tasks(task_service: TaskService) -> None:
    first = TaskCreate(
        title="Task 1",
        description="Descricao 1",
        priority="media",
        status="pendente",
    )
    second = TaskCreate(
        title="Task 2",
        description="Descricao 2",
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
            title="Task antiga",
            description="Descricao antiga",
            priority="baixa",
            status="pendente",
        )
    )

    updated = task_service.update_task(
        created.id,
        TaskUpdate(
            title="Task nova",
            description="Descricao nova",
            status="em_andamento",
        ),
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "Task nova"
    assert updated.description == "Descricao nova"
    assert updated.status == "em_andamento"


def test_delete_task_should_remove_existing_task(task_service: TaskService) -> None:
    created = task_service.create_task(
        TaskCreate(
            title="Task para excluir",
            description="Descricao",
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
        TaskUpdate(title="Nao existe"),
    )

    assert updated is None


def test_delete_task_should_return_false_for_nonexistent_id(task_service: TaskService) -> None:
    deleted = task_service.delete_task(uuid4())

    assert deleted is False
