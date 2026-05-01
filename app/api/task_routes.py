"""Task API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.models.tasks import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

_service = TaskService(repository=TaskRepository())


class ErrorResponse(BaseModel):
    """Standard error response payload."""

    detail: str


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tarefa",
    description=(
        "Cria uma nova tarefa com priorizacao assistida por IA. "
        "Use priority_mode='auto' para aceitar sugestao automatica "
        "ou priority_mode='manual' com priority_manual para sobrescrever."
    ),
    responses={
        201: {"description": "Tarefa criada com sucesso."},
        422: {"description": "Payload invalido."},
    },
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task with automatic priority suggestion."""
    return _service.create_task(payload)


@router.get(
    "",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar tarefas",
    description=(
        "Retorna tarefas cadastradas. "
        "Permite filtros opcionais por prioridade e status."
    ),
    responses={
        200: {"description": "Lista de tarefas retornada com sucesso."},
        422: {"description": "Filtro invalido."},
    },
)
def list_tasks(
    priority: TaskPriority | None = Query(default=None),
    status: TaskStatus | None = Query(default=None),
) -> list[TaskResponse]:
    """List tasks with optional priority and status filters."""
    return _service.list_tasks(priority=priority, status=status)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar tarefa por ID",
    description="Retorna uma tarefa especifica pelo UUID.",
    responses={
        200: {"description": "Tarefa encontrada."},
        404: {"model": ErrorResponse, "description": "Tarefa nao encontrada."},
        422: {"description": "UUID invalido."},
    },
)
def get_task(task_id: UUID) -> TaskResponse:
    """Get a task by UUID."""
    task = _service.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar tarefa",
    description=(
        "Atualiza a tarefa pelo UUID. "
        "Use priority_mode='auto' para recalcular sugestao "
        "ou priority_mode='manual' com priority_manual para sobrescrever."
    ),
    responses={
        200: {"description": "Tarefa atualizada com sucesso."},
        404: {"model": ErrorResponse, "description": "Tarefa nao encontrada."},
        422: {"description": "Payload ou UUID invalido."},
    },
)
def update_task(task_id: UUID, payload: TaskUpdate) -> TaskResponse:
    """Update a task by UUID."""
    task = _service.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir tarefa",
    description="Remove uma tarefa pelo UUID.",
    responses={
        204: {"description": "Tarefa excluida com sucesso."},
        404: {"model": ErrorResponse, "description": "Tarefa nao encontrada."},
        422: {"description": "UUID invalido."},
    },
)
def delete_task(task_id: UUID) -> Response:
    """Delete a task by UUID."""
    deleted = _service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
