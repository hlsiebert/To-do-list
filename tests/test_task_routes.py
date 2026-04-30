from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService


class StubPriorityAdvisor:
    """Advisor fixo para manter os testes determinísticos."""

    def suggest_priority(self, title: str, description: str | None) -> int:
        return 4


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Cria cliente com service/repository isolados por teste."""
    from app.api import task_routes

    repository = TaskRepository(db_path=str(tmp_path / "routes_test.db"))
    service = TaskService(repository=repository, priority_advisor=StubPriorityAdvisor())
    monkeypatch.setattr(task_routes, "_service", service)

    return TestClient(app)


def test_create_task_should_return_201(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Criar endpoint",
            "description": "Implementar CRUD",
            "priority": "baixa",
            "status": "pendente",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Criar endpoint"
    assert body["priority"] == "alta"


def test_list_tasks_should_return_200(client: TestClient) -> None:
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "Descricao 1",
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
            "title": "Task para excluir",
            "description": "Descricao",
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
