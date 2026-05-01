"""Pydantic models for task input and output payloads."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TaskPriority = Literal["baixa", "media", "alta", "critica"]
TaskStatus = Literal["pendente", "em_andamento", "concluida"]


class TaskCreate(BaseModel):
    """Payload for creating a new task."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=1000)
    priority: TaskPriority = "media"
    status: TaskStatus = "pendente"
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Payload for updating an existing task."""
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    """Task data returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime | None = None
    due_date: datetime | None = None
