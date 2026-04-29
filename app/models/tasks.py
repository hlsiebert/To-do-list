"""Pydantic models for task input and output payloads."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Payload for creating a new task.(POST)"""

    title: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    priority: int = Field(default=3, ge=1, le=5)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Payload for updating an existing task.(PUT/PATCH)"""

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    priority: int | None = Field(default=None, ge=1, le=5)
    due_date: datetime | None = None
    completed: bool | None = None


class TaskResponse(BaseModel):
    """Task data returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    priority: int
    completed: bool
    created_at: datetime
    updated_at: datetime | None = None
    due_date: datetime | None = None
