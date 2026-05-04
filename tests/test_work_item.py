"""
Tests for the WorkItem model and related enums.
"""


from workflow_orchestration_queue.models.work_item import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    scrub_secrets,
)


class TestTaskType:
    """Tests for the TaskType enum."""

    def test_plan_value(self) -> None:
        assert TaskType.PLAN.value == "PLAN"

    def test_implement_value(self) -> None:
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"

    def test_bugfix_value(self) -> None:
        assert TaskType.BUGFIX.value == "BUGFIX"

    def test_is_str_enum(self) -> None:
        assert isinstance(TaskType.PLAN, str)


class TestWorkItemStatus:
    """Tests for the WorkItemStatus enum."""

    def test_queued_label(self) -> None:
        assert WorkItemStatus.QUEUED.value == "agent:queued"

    def test_in_progress_label(self) -> None:
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"

    def test_success_label(self) -> None:
        assert WorkItemStatus.SUCCESS.value == "agent:success"

    def test_error_label(self) -> None:
        assert WorkItemStatus.ERROR.value == "agent:error"

    def test_infra_failure_label(self) -> None:
        assert WorkItemStatus.INFRA_FAILURE.value == "agent:infra-failure"

    def test_all_statuses_are_agent_prefixed(self) -> None:
        """All statuses should have the 'agent:' prefix for GitHub labels."""
        for status in WorkItemStatus:
            assert status.value.startswith("agent:"), f"{status} missing 'agent:' prefix"


class TestWorkItem:
    """Tests for the WorkItem Pydantic model."""

    def test_create_work_item(self, sample_work_item: WorkItem) -> None:
        assert sample_work_item.id == "12345"
        assert sample_work_item.issue_number == 42
        assert sample_work_item.task_type == TaskType.IMPLEMENT
        assert sample_work_item.status == WorkItemStatus.QUEUED

    def test_work_item_serialization(self, sample_work_item: WorkItem) -> None:
        data = sample_work_item.model_dump()
        assert data["id"] == "12345"
        assert data["issue_number"] == 42
        assert data["task_type"] == "IMPLEMENT"

    def test_work_item_from_dict(self) -> None:
        data = {
            "id": "99999",
            "issue_number": 1,
            "source_url": "https://github.com/test/repo/issues/1",
            "context_body": "test body",
            "target_repo_slug": "test/repo",
            "task_type": "PLAN",
            "status": "agent:queued",
            "node_id": "test_node",
        }
        item = WorkItem(**data)
        assert item.task_type == TaskType.PLAN
        assert item.status == WorkItemStatus.QUEUED


class TestScrubSecrets:
    """Tests for the scrub_secrets utility."""

    def test_scrubs_github_pat(self) -> None:
        text = "Token is ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "***REDACTED***" in result

    def test_scrubs_bearer_token(self) -> None:
        text = "Authorization: Bearer abc123def456ghi789jkl012mno345pqr="
        result = scrub_secrets(text)
        assert "Bearer abc123" not in result
        assert "***REDACTED***" in result

    def test_scrubs_openai_key(self) -> None:
        text = "API_KEY=sk-ABCDEFGHIJKLMNOPQRSTUVWX"
        result = scrub_secrets(text)
        assert "sk-ABCD" not in result

    def test_preserves_normal_text(self) -> None:
        text = "This is a normal commit message with no secrets."
        result = scrub_secrets(text)
        assert result == text

    def test_custom_replacement(self) -> None:
        text = "Token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn"
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result
        assert "ghp_" not in result
