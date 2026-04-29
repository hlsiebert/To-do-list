"""Service layer for task business rules."""

from __future__ import annotations

from app.models.tasks import TaskCreate, TaskResponse, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor, PriorityAdvisorProtocol


class TaskService:
    """Coordinates repository access and task business rules."""

    def __init__(
        self,
        repository: TaskRepository,
        priority_advisor: PriorityAdvisorProtocol | None = None,
    ) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor or PriorityAdvisor()

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        """Creates a task applying automatic priority suggestion."""
        suggested_priority = self._priority_advisor.suggest_priority(
            title=payload.title,
            description=payload.description,
        )
        task_data = payload.model_copy(update={"priority": suggested_priority})
        return self._repository.create(task_data)

    def list_tasks(self) -> list[TaskResponse]:
        """Lists all persisted tasks."""
        return self._repository.list()

    def get_task_by_id(self, task_id: int) -> TaskResponse | None:
        """Returns one task by id when it exists."""
        return self._repository.get_by_id(task_id)

    def update_task(self, task_id: int, payload: TaskUpdate) -> TaskResponse | None:
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

            title = update_data.get("title", current_task.title)
            description = update_data.get("description", current_task.description)
            update_data["priority"] = self._priority_advisor.suggest_priority(
                title=title,
                description=description,
            )

        return self._repository.update(task_id, TaskUpdate(**update_data))

    def delete_task(self, task_id: int) -> bool:
        """Deletes a task by id."""
        return self._repository.delete(task_id)
