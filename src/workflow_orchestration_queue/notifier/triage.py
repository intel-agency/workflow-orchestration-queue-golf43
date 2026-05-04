"""
Event Triage Logic.

Determines whether an incoming GitHub webhook event is actionable
and maps it to a WorkItem if so. This module isolates the triage
decision logic from the webhook transport layer.
"""

from typing import Any, Optional

from workflow_orchestration_queue.models.work_item import TaskType, WorkItem, WorkItemStatus


def triage_event(event_type: str, payload: dict[str, Any]) -> Optional[WorkItem]:
    """Triage a GitHub webhook event and return a WorkItem if actionable.

    Args:
        event_type: The X-GitHub-Event header value (e.g., "issues", "pull_request").
        payload: The parsed JSON payload from the webhook.

    Returns:
        A WorkItem if the event is actionable, or None if it should be ignored.
    """
    if event_type == "issues":
        return _triage_issues_event(payload)

    # Future: add triage for pull_request, issue_comment, etc.
    return None


def _triage_issues_event(payload: dict[str, Any]) -> Optional[WorkItem]:
    """Triage an 'issues' event.

    Currently handles:
    - Newly opened issues with [Application Plan] in the title or agent:plan label
    - Newly opened issues with other actionable labels

    Args:
        payload: The parsed JSON payload.

    Returns:
        A WorkItem if the issue is actionable, or None.
    """
    action = payload.get("action")
    if action != "opened":
        return None

    issue = payload.get("issue", {})
    labels = [label["name"] for label in issue.get("labels", [])]
    title = issue.get("title", "")

    # Determine task type from labels/title
    if "[Application Plan]" in title or "agent:plan" in labels:
        task_type = TaskType.PLAN
    elif "bug" in labels:
        task_type = TaskType.BUGFIX
    else:
        # Default: treat as implementation task if it has the agent:queued label
        # or has a recognizable trigger pattern
        return None

    return WorkItem(
        id=str(issue["id"]),
        issue_number=issue["number"],
        source_url=issue["html_url"],
        target_repo_slug=payload["repository"]["full_name"],
        task_type=task_type,
        context_body=issue.get("body") or "",
        status=WorkItemStatus.QUEUED,
        node_id=issue["node_id"],
    )
