"""
Task Queue Abstract Base Class.

Defines the interface for the work queue provider. Implementations
can target GitHub Issues, Linear, Jira, etc.

See: OS-APOW Simplification Report, S-1 / S-6
"""

from abc import ABC, abstractmethod
from typing import Optional

from workflow_orchestration_queue.models.work_item import (
    WorkItem,
    WorkItemStatus,
)


class ITaskQueue(ABC):
    """Interface for the Work Queue (e.g., GitHub Issues, Linear, Jira, etc.)."""

    @abstractmethod
    async def add_to_queue(self, item: WorkItem) -> bool:
        """Add a work item to the queue."""
        ...

    @abstractmethod
    async def fetch_queued_tasks(self) -> list[WorkItem]:
        """Fetch all pending tasks from the queue."""
        ...

    @abstractmethod
    async def update_status(self, item: WorkItem, status: WorkItemStatus, comment: Optional[str] = None) -> None:
        """Update the status of a work item, optionally posting a comment."""
        ...
