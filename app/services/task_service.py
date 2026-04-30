"""Service layer for task business rules."""

from __future__ import annotations

from uuid import UUID

from app.models.tasks import TaskCreate, TaskPriority, TaskResponse, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor, PriorityAdvisorProtocol


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

    def _suggest_priority_label(self, title: str, description: str) -> TaskPriority:
        """Gets numeric suggestion and converts it to domain priority label."""
        suggested_priority = self._priority_advisor.suggest_priority(
            title=title,
            description=description,
        )
        return self._normalize_priority(suggested_priority)

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
        task_data = payload.model_copy(
            update={
                "priority": self._suggest_priority_label(
                    title=payload.title,
                    description=payload.description,
                )
            }
        )
        return self._repository.create(task_data)

    def list_tasks(self) -> list[TaskResponse]:
        """Lists all persisted tasks."""
        return self._repository.list()

    def get_task_by_id(self, task_id: UUID) -> TaskResponse | None:
        """Returns one task by UUID when it exists."""
        return self._repository.get_by_id(task_id)

    def update_task(self, task_id: UUID, payload: TaskUpdate) -> TaskResponse | None:
        """Updates a task and can re-evaluate priority automatically."""
        update_data = payload.model_dump(exclude_unset=True)
        should_recalculate = (
            "priority" not in update_data
            and ("title" in update_data or "description" in update_data)
        )

        if should_recalculate:
            current_task = self._repository.get_by_id(task_id)
            if current_task is None:
                return None

            title, description = self._build_priority_context(update_data, current_task)
            update_data["priority"] = self._suggest_priority_label(
                title=title,
                description=description,
            )

        return self._repository.update(task_id, TaskUpdate(**update_data))

    def delete_task(self, task_id: UUID) -> bool:
        """Deletes a task by UUID."""
        return self._repository.delete(task_id)
