"""Service layer for task business rules."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.models.tasks import (
    TaskCreate,
    TaskPriority,
    TaskPrioritySource,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)
from app.repository.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor, PriorityAdvisorProtocol


@dataclass(frozen=True, slots=True)
class PriorityDecision:
    """Represents suggested and applied priority values."""

    final_priority: TaskPriority
    suggested_priority: TaskPriority | None
    source: TaskPrioritySource


class TaskService:
    """Coordinates repository access and task business rules."""
    _PRIORITY_MAP: dict[int, TaskPriority] = {
        1: "baixa",
        2: "baixa",
        3: "media",
        4: "alta",
        5: "critica",
    }

    def __init__(
        self,
        repository: TaskRepository,
        priority_advisor: PriorityAdvisorProtocol | None = None,
    ) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor or PriorityAdvisor()

    def _normalize_priority(self, value: int) -> TaskPriority:
        """Maps numeric priority from advisor into domain priority labels."""
        return self._PRIORITY_MAP.get(value, "media")

    def _suggest_priority_decision(self, title: str, description: str) -> PriorityDecision:
        """Returns both suggested and final priority for automatic mode."""
        value, source = self._priority_advisor.suggest_with_source(
            title=title,
            description=description,
        )
        normalized = self._normalize_priority(value)
        return PriorityDecision(
            final_priority=normalized,
            suggested_priority=normalized,
            source=source,
        )

    def _build_priority_context(
        self,
        update_data: dict[str, object],
        current_task: TaskResponse,
    ) -> tuple[str, str]:
        """Builds title/description context used for priority recalculation."""
        title = str(update_data.get("title", current_task.title))
        description = str(update_data.get("description", current_task.description))
        return title, description

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        """Creates a task applying automatic priority suggestion."""
        if payload.priority_mode == "manual":
            assert payload.priority_manual is not None  # validated by model
            suggested = self._suggest_priority_decision(
                title=payload.title,
                description=payload.description,
            )
            return self._repository.create(
                payload,
                priority=payload.priority_manual,
                priority_suggested=suggested.suggested_priority,
                priority_source="manual",
            )

        decision = self._suggest_priority_decision(
            title=payload.title,
            description=payload.description,
        )
        return self._repository.create(
            payload,
            priority=decision.final_priority,
            priority_suggested=decision.suggested_priority,
            priority_source=decision.source,
        )

    def list_tasks(
        self,
        *,
        priority: TaskPriority | None = None,
        status: TaskStatus | None = None,
    ) -> list[TaskResponse]:
        """Lists persisted tasks with optional priority/status filters."""
        return self._repository.list(priority=priority, status=status)

    def get_task_by_id(self, task_id: UUID) -> TaskResponse | None:
        """Returns one task by UUID when it exists."""
        return self._repository.get_by_id(task_id)

    def update_task(self, task_id: UUID, payload: TaskUpdate) -> TaskResponse | None:
        """Updates a task and can re-evaluate priority automatically."""
        update_data = payload.model_dump(exclude_unset=True)
        priority_mode = update_data.get("priority_mode")
        priority_manual = update_data.get("priority_manual")

        if priority_mode == "manual":
            assert priority_manual is not None  # validated by model
            return self._repository.update(
                task_id,
                payload,
                priority=priority_manual,
                priority_source="manual",
            )

        should_recalculate = (
            priority_mode == "auto"
            or (
                priority_mode is None
                and "priority" not in update_data
                and ("title" in update_data or "description" in update_data)
            )
        )
        if should_recalculate:
            current_task = self._repository.get_by_id(task_id)
            if current_task is None:
                return None

            title, description = self._build_priority_context(update_data, current_task)
            decision = self._suggest_priority_decision(
                title=title,
                description=description,
            )
            return self._repository.update(
                task_id,
                payload,
                priority=decision.final_priority,
                priority_suggested=decision.suggested_priority,
                priority_source=decision.source,
            )

        # Backward-compatible behavior for manual priority updates in old payloads.
        if "priority" in update_data and priority_mode is None:
            return self._repository.update(
                task_id,
                payload,
                priority=update_data["priority"],
                priority_source="manual",
            )

        return self._repository.update(task_id, payload)

    def delete_task(self, task_id: UUID) -> bool:
        """Deletes a task by UUID."""
        return self._repository.delete(task_id)
