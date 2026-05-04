"""
Tests for the Sentinel polling engine.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from workflow_orchestration_queue.models.work_item import WorkItem, WorkItemStatus
from workflow_orchestration_queue.queue.github_queue import GitHubQueue
from workflow_orchestration_queue.sentinel.poller import Sentinel, run_shell_command


class TestRunShellCommand:
    """Tests for the run_shell_command helper."""

    @pytest.mark.asyncio
    async def test_successful_command(self) -> None:
        result = await run_shell_command(["echo", "hello"], timeout=10)
        assert result.returncode == 0
        assert result.stdout == "hello"

    @pytest.mark.asyncio
    async def test_failed_command(self) -> None:
        result = await run_shell_command(["false"], timeout=10)
        assert result.returncode != 0


class TestSentinelInit:
    """Tests for Sentinel initialization."""

    def test_init(self) -> None:
        queue = MagicMock(spec=GitHubQueue)
        sentinel = Sentinel(queue)
        assert sentinel.queue is queue
        assert sentinel._current_backoff == 60


class TestSentinelProcessTask:
    """Tests for the process_task method."""

    @pytest.mark.asyncio
    async def test_infra_failure_on_up_failure(self, sample_work_item: WorkItem) -> None:
        queue = AsyncMock(spec=GitHubQueue)
        sentinel = Sentinel(queue, shell_bridge_path="nonexistent-script.sh")

        # The shell command will fail since the script doesn't exist
        # The sentinel should catch this and report infra failure
        with patch("workflow_orchestration_queue.sentinel.poller.run_shell_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Script not found")

            await sentinel.process_task(sample_work_item)

            # Should have attempted to update status to INFRA_FAILURE
            queue.update_status.assert_called_once()
            call_args = queue.update_status.call_args
            assert call_args[0][1] == WorkItemStatus.INFRA_FAILURE
