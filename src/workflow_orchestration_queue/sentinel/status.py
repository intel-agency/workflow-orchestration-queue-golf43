"""
Status Feedback Module.

Manages GitHub labels and comments for task status updates.
Provides the status machine transitions used by the sentinel.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from workflow_orchestration_queue.models.work_item import WorkItem, WorkItemStatus
from workflow_orchestration_queue.queue.github_queue import GitHubQueue

logger = logging.getLogger("OS-APOW-Status")


async def transition_status(
    queue: GitHubQueue,
    item: WorkItem,
    new_status: WorkItemStatus,
    comment: Optional[str] = None,
) -> None:
    """Transition a work item to a new status.

    Args:
        queue: The GitHub queue instance.
        item: The work item to update.
        new_status: The target status.
        comment: Optional comment to post with the transition.
    """
    logger.info(f"Transitioning #{item.issue_number}: {item.status.value} -> {new_status.value}")
    await queue.update_status(item, new_status, comment)


async def report_success(queue: GitHubQueue, item: WorkItem, summary: str) -> None:
    """Report successful task completion."""
    msg = f"**Task Complete**\n- **Completed at:** {datetime.now(timezone.utc).isoformat()}\n- **Summary:** {summary}"
    await transition_status(queue, item, WorkItemStatus.SUCCESS, msg)


async def report_error(queue: GitHubQueue, item: WorkItem, error: str) -> None:
    """Report a task execution error."""
    msg = (
        f"**Execution Error**\n"
        f"- **Failed at:** {datetime.now(timezone.utc).isoformat()}\n"
        f"- **Error:**\n```\n{error[:1500]}\n```"
    )
    await transition_status(queue, item, WorkItemStatus.ERROR, msg)


async def report_infra_failure(queue: GitHubQueue, item: WorkItem, error: str) -> None:
    """Report an infrastructure failure."""
    msg = (
        f"**Infrastructure Failure**\n"
        f"- **Failed at:** {datetime.now(timezone.utc).isoformat()}\n"
        f"- **Error:**\n```\n{error[:1500]}\n```"
    )
    await transition_status(queue, item, WorkItemStatus.INFRA_FAILURE, msg)
