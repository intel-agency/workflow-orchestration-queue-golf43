"""
Shared pytest fixtures for workflow-orchestration-queue tests.
"""

import pytest

from workflow_orchestration_queue.models.work_item import TaskType, WorkItem, WorkItemStatus


@pytest.fixture
def sample_work_item() -> WorkItem:
    """Return a sample WorkItem for testing."""
    return WorkItem(
        id="12345",
        issue_number=42,
        source_url="https://github.com/intel-agency/workflow-orchestration-queue-golf43/issues/42",
        context_body="## Task Description\nImplement the polling engine.",
        target_repo_slug="intel-agency/workflow-orchestration-queue-golf43",
        task_type=TaskType.IMPLEMENT,
        status=WorkItemStatus.QUEUED,
        node_id="MDU6SXNzdWUxMjM0NTY3ODk=",
    )


@pytest.fixture
def plan_work_item() -> WorkItem:
    """Return a WorkItem with PLAN task type."""
    return WorkItem(
        id="67890",
        issue_number=10,
        source_url="https://github.com/intel-agency/workflow-orchestration-queue-golf43/issues/10",
        context_body="[Application Plan] Create a new web service",
        target_repo_slug="intel-agency/workflow-orchestration-queue-golf43",
        task_type=TaskType.PLAN,
        status=WorkItemStatus.QUEUED,
        node_id="MDU6SXNzdWU2Nzg5MDEyMzQ1",
    )


@pytest.fixture
def bug_work_item() -> WorkItem:
    """Return a WorkItem with BUGFIX task type."""
    return WorkItem(
        id="11111",
        issue_number=7,
        source_url="https://github.com/intel-agency/workflow-orchestration-queue-golf43/issues/7",
        context_body="Bug: Poller crashes on empty response",
        target_repo_slug="intel-agency/workflow-orchestration-queue-golf43",
        task_type=TaskType.BUGFIX,
        status=WorkItemStatus.QUEUED,
        node_id="MDU6SXNzdWUxMTEyMjMzNDQ1",
    )


@pytest.fixture
def github_issue_payload() -> dict:
    """Return a sample GitHub issue webhook payload."""
    return {
        "action": "opened",
        "issue": {
            "id": 1234567890,
            "number": 42,
            "title": "[Application Plan] New Feature",
            "html_url": "https://github.com/intel-agency/workflow-orchestration-queue-golf43/issues/42",
            "body": "## Description\nThis is a test plan.",
            "node_id": "MDU6SXNzdWUxMjM0NTY3ODk=",
            "labels": [
                {"name": "agent:plan"},
                {"name": "enhancement"},
            ],
        },
        "repository": {
            "full_name": "intel-agency/workflow-orchestration-queue-golf43",
        },
    }
