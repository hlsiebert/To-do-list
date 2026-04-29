"""Task API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.models.tasks import TaskCreate, TaskResponse, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

_service = TaskService(repository=TaskRepository())


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task with automatic priority suggestion."""
    return _service.create_task(payload)


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def list_tasks() -> list[TaskResponse]:
    """List all tasks."""
    return _service.list_tasks()


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: UUID) -> TaskResponse:
    """Get a task by UUID."""
    task = _service.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: UUID, payload: TaskUpdate) -> TaskResponse:
    """Update a task by UUID."""
    task = _service.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID) -> Response:
    """Delete a task by UUID."""
    deleted = _service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
