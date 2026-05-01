"""Pydantic models for task input and output payloads."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

TaskPriority = Literal["baixa", "media", "alta", "critica"]
TaskStatus = Literal["pendente", "em_andamento", "concluida"]
TaskPriorityMode = Literal["auto", "manual"]
TaskPrioritySource = Literal["ia", "heuristica_fallback", "manual"]


class TaskCreate(BaseModel):
    """Payload for creating a new task."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=1000)
    # Kept for backward compatibility with existing clients.
    priority: TaskPriority = "media"
    priority_mode: TaskPriorityMode = "auto"
    priority_manual: TaskPriority | None = Field(default=None)
    status: TaskStatus = "pendente"
    due_date: datetime | None = None

    @model_validator(mode="after")
    def validate_priority_mode(self) -> "TaskCreate":
        """Ensures priority fields are consistent with selected mode."""
        if self.priority_mode == "manual" and self.priority_manual is None:
            raise ValueError("priority_manual is required when priority_mode is 'manual'")
        if self.priority_mode == "auto" and self.priority_manual is not None:
            raise ValueError("priority_manual must be null when priority_mode is 'auto'")
        return self


class TaskUpdate(BaseModel):
    """Payload for updating an existing task."""
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    priority: TaskPriority | None = None
    priority_mode: TaskPriorityMode | None = None
    priority_manual: TaskPriority | None = Field(default=None, json_schema_extra={"example": None})
    status: TaskStatus | None = None
    due_date: datetime | None = None

    @model_validator(mode="after")
    def validate_priority_mode(self) -> "TaskUpdate":
        """Ensures manual mode updates include manual priority value."""
        if self.priority_mode == "manual" and self.priority_manual is None:
            raise ValueError("priority_manual is required when priority_mode is 'manual'")
        return self


class TaskResponse(BaseModel):
    """Task data returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    priority: TaskPriority
    priority_suggested: TaskPriority | None = None
    priority_source: TaskPrioritySource = "manual"
    status: TaskStatus
    created_at: datetime
    updated_at: datetime | None = None
    due_date: datetime | None = None
