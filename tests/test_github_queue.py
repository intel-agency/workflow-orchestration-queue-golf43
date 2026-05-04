"""
Tests for the GitHubQueue implementation.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from workflow_orchestration_queue.models.work_item import WorkItem, WorkItemStatus
from workflow_orchestration_queue.queue.github_queue import GitHubQueue


class TestGitHubQueueInit:
    """Tests for GitHubQueue initialization."""

    def test_init_with_all_params(self) -> None:
        queue = GitHubQueue(token="test-token", org="intel-agency", repo="test-repo")
        assert queue.token == "test-token"
        assert queue.org == "intel-agency"
        assert queue.repo == "test-repo"

    def test_init_with_defaults(self) -> None:
        queue = GitHubQueue(token="test-token")
        assert queue.org == ""
        assert queue.repo == ""


class TestFetchQueuedTasks:
    """Tests for the fetch_queued_tasks method."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_org_or_repo(self) -> None:
        queue = GitHubQueue(token="test-token")
        result = await queue.fetch_queued_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_on_api_error(self) -> None:
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        queue._client = AsyncMock()
        queue._client.get = AsyncMock(return_value=mock_response)

        result = await queue.fetch_queued_tasks()
        assert result == []


class TestAddToQueue:
    """Tests for the add_to_queue method."""

    @pytest.mark.asyncio
    async def test_add_to_queue_success(self, sample_work_item: WorkItem) -> None:
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200

        queue._client = AsyncMock()
        queue._client.post = AsyncMock(return_value=mock_response)

        result = await queue.add_to_queue(sample_work_item)
        assert result is True

    @pytest.mark.asyncio
    async def test_add_to_queue_failure(self, sample_work_item: WorkItem) -> None:
        queue = GitHubQueue(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 404

        queue._client = AsyncMock()
        queue._client.post = AsyncMock(return_value=mock_response)

        result = await queue.add_to_queue(sample_work_item)
        assert result is False


class TestUpdateStatus:
    """Tests for the update_status method."""

    @pytest.mark.asyncio
    async def test_update_status_with_comment(self, sample_work_item: WorkItem) -> None:
        queue = GitHubQueue(token="test-token")

        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 200
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201

        queue._client = AsyncMock()
        queue._client.delete = AsyncMock(return_value=mock_delete_response)
        queue._client.post = AsyncMock(return_value=mock_post_response)

        await queue.update_status(sample_work_item, WorkItemStatus.SUCCESS, "Task completed")
        # Should have called delete (remove old label) and post (add new label + comment)
        assert queue._client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        queue = GitHubQueue(token="test-token")
        queue._client = AsyncMock()
        await queue.close()
        queue._client.aclose.assert_called_once()
