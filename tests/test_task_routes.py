from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService


class StubPriorityAdvisor:
    """Fixed advisor to keep tests deterministic."""

    def suggest_priority(self, title: str, description: str | None) -> int:
        return 4


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Creates a client with isolated service/repository per test."""
    from app.api import task_routes

    base_dir = Path("tests") / "_runtime_db"
    base_dir.mkdir(parents=True, exist_ok=True)
    db_file = base_dir / f"routes_{uuid4()}.db"

    repository = TaskRepository(db_path=str(db_file))
    service = TaskService(repository=repository, priority_advisor=StubPriorityAdvisor())
    monkeypatch.setattr(task_routes, "_service", service)

    return TestClient(app)


def test_create_task_should_return_201(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Create endpoint",
            "description": "Implement CRUD",
            "priority": "baixa",
            "status": "pendente",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Create endpoint"
    assert body["priority"] == "alta"


def test_list_tasks_should_return_200(client: TestClient) -> None:
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "Description 1",
            "priority": "media",
            "status": "pendente",
        },
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_task_should_return_204(client: TestClient) -> None:
    created = client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "description": "Description",
            "priority": "media",
            "status": "pendente",
        },
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_get_task_with_nonexistent_id_should_return_404(client: TestClient) -> None:
    response = client.get(f"/tasks/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_create_task_with_missing_required_field_should_return_422(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Missing description",
            "priority": "media",
            "status": "pendente",
        },
    )

    assert response.status_code == 422


def test_create_task_with_invalid_priority_should_return_422(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Invalid task",
            "description": "Priority out of domain",
            "priority": "urgent",
            "status": "pendente",
        },
    )

    assert response.status_code == 422


def test_get_task_with_invalid_uuid_should_return_422(client: TestClient) -> None:
    response = client.get("/tasks/not-a-uuid")

    assert response.status_code == 422
