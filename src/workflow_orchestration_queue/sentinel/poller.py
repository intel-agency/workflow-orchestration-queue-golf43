"""
Sentinel Polling Engine.

Background service that polls GitHub for queued tasks and dispatches
them to the worker. Implements the core orchestration loop:

1. Poll for issues labeled 'agent:queued'.
2. Claim the task using assign-then-verify distributed locking.
3. Manage the worker lifecycle via the shell bridge.
4. Post heartbeat comments during long-running tasks.
5. Report progress and results back to GitHub.
"""

import asyncio
import logging
import os
import random
import signal
import subprocess
import sys
import uuid
from typing import Optional

import httpx

from workflow_orchestration_queue.config import get_settings
from workflow_orchestration_queue.models.work_item import TaskType, WorkItem, WorkItemStatus
from workflow_orchestration_queue.queue.github_queue import GitHubQueue

# --- Configuration ---

POLL_INTERVAL = 60  # seconds between polling cycles
MAX_BACKOFF = 960  # 16 minutes max backoff on rate limits
SENTINEL_ID = f"sentinel-{uuid.uuid4().hex[:8]}"
HEARTBEAT_INTERVAL = 300  # 5 min between heartbeat comments
SUBPROCESS_TIMEOUT = 5700  # 95 min safety net

logger = logging.getLogger("OS-APOW-Sentinel")

# Graceful shutdown flag
_shutdown_requested = False


def _handle_signal(signum: int, frame: object) -> None:
    """Set shutdown flag on SIGTERM/SIGINT so the current task can finish."""
    global _shutdown_requested
    sig_name = signal.Signals(signum).name
    logger.info(f"Received {sig_name} — will shut down after current task finishes")
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


async def run_shell_command(args: list[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess[str]:
    """Invoke the local shell bridge (devcontainer-opencode.sh).

    Args:
        args: Command and arguments.
        timeout: Maximum seconds to wait. None = no limit.
    """
    try:
        logger.info(f"Executing Bridge: {' '.join(args)}")
        process = await asyncio.create_subprocess_exec(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Shell command timed out after {timeout}s — killing")
            process.kill()
            stdout, stderr = await process.communicate()
            return subprocess.CompletedProcess(
                args=args,
                returncode=-1,
                stdout=stdout.decode().strip() if stdout else "",
                stderr=f"TIMEOUT after {timeout}s\n" + (stderr.decode().strip() if stderr else ""),
            )

        return subprocess.CompletedProcess(
            args=args,
            returncode=process.returncode or 0,
            stdout=stdout.decode().strip() if stdout else "",
            stderr=stderr.decode().strip() if stderr else "",
        )
    except Exception as e:
        logger.error(f"Critical shell execution error: {str(e)}")
        raise


class Sentinel:
    """Sentinel orchestrator — polls for tasks and manages worker lifecycle."""

    def __init__(self, queue: GitHubQueue, shell_bridge_path: str = "./scripts/devcontainer-opencode.sh"):
        self.queue = queue
        self.shell_bridge_path = shell_bridge_path
        self._current_backoff = POLL_INTERVAL

    async def _heartbeat_loop(self, item: WorkItem, start_time: float) -> None:
        """Post periodic heartbeat comments while a task is running."""
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            elapsed = int(asyncio.get_event_loop().time() - start_time)
            await self.queue.post_heartbeat(item, SENTINEL_ID, elapsed)

    async def process_task(self, item: WorkItem) -> None:
        """Process a single work item through the shell bridge."""
        logger.info(f"Processing Task #{item.issue_number}...")
        start_time = asyncio.get_event_loop().time()

        # Launch heartbeat as a background task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop(item, start_time))

        try:
            # Step 1: Initialize Infrastructure
            res_up = await run_shell_command([self.shell_bridge_path, "up"], timeout=300)
            if res_up.returncode != 0:
                err = f"Infrastructure Failure during `up` stage:\n```\n{res_up.stderr}\n```"
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 2: Start Opencode Server
            res_start = await run_shell_command([self.shell_bridge_path, "start"], timeout=120)
            if res_start.returncode != 0:
                err = f"Infrastructure Failure starting `opencode-server`:\n```\n{res_start.stderr}\n```"
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 3: Trigger Agent Workflow
            workflow_map = {
                TaskType.PLAN: "create-app-plan.md",
                TaskType.IMPLEMENT: "perform-task.md",
                TaskType.BUGFIX: "recover-from-error.md",
            }
            workflow = workflow_map.get(item.task_type, "perform-task.md")
            instruction = f"Execute workflow {workflow} for context: {item.source_url}"

            res_prompt = await run_shell_command(
                [self.shell_bridge_path, "prompt", instruction],
                timeout=SUBPROCESS_TIMEOUT,
            )

            # Step 4: Handle Completion
            if res_prompt.returncode == 0:
                success_msg = (
                    f"Workflow Complete\nSentinel successfully executed `{workflow}`. Please review Pull Requests."
                )
                await self.queue.update_status(item, WorkItemStatus.SUCCESS, success_msg)
            else:
                log_tail = res_prompt.stderr[-1500:] if res_prompt.stderr else "No error output captured."
                fail_msg = f"Execution Error during `{workflow}`:\n```\n...{log_tail}\n```"
                await self.queue.update_status(item, WorkItemStatus.ERROR, fail_msg)

        except Exception as e:
            logger.exception(f"Internal Sentinel Error on Task #{item.issue_number}")
            await self.queue.update_status(
                item,
                WorkItemStatus.INFRA_FAILURE,
                f"Sentinel encountered an unhandled exception: {str(e)}",
            )
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

            # Environment reset between tasks
            logger.info("Resetting environment (stop)")
            await run_shell_command([self.shell_bridge_path, "stop"], timeout=60)

    async def run_forever(self) -> None:
        """Main polling loop — runs until shutdown is requested."""
        logger.info(f"Sentinel {SENTINEL_ID} entering polling loop (interval: {POLL_INTERVAL}s)")

        while not _shutdown_requested:
            try:
                tasks = await self.queue.fetch_queued_tasks()
                if tasks:
                    logger.info(f"Found {len(tasks)} queued task(s).")
                    for task in tasks:
                        if _shutdown_requested:
                            break
                        if await self.queue.claim_task(task, SENTINEL_ID, os.getenv("SENTINEL_BOT_LOGIN", "")):
                            await self.process_task(task)
                            break

                # Reset backoff on successful poll
                self._current_backoff = POLL_INTERVAL

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status in (403, 429):
                    # Jittered exponential backoff
                    jitter = random.uniform(0, self._current_backoff * 0.1)
                    wait = min(self._current_backoff + jitter, MAX_BACKOFF)
                    logger.warning(f"Rate limited ({status}) — backing off {wait:.0f}s")
                    self._current_backoff = min(self._current_backoff * 2, MAX_BACKOFF)
                    await asyncio.sleep(wait)
                    continue
                else:
                    logger.error(f"GitHub API error: {exc}")
            except Exception as e:
                logger.error(f"Polling cycle error: {str(e)}")

            await asyncio.sleep(self._current_backoff)

        logger.info("Shutdown flag set — exiting polling loop")


async def _main() -> None:
    """Entry point for the sentinel polling engine."""
    settings = get_settings()

    required = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
    env_values = {
        "GITHUB_TOKEN": settings.github_token,
        "GITHUB_OWNER": settings.github_owner,
        "GITHUB_REPO": settings.github_repo,
    }
    missing = [v for v in required if not env_values.get(v)]
    if missing:
        logger.error(f"Critical Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    if not settings.sentinel_bot_login:
        logger.warning(
            "SENTINEL_BOT_LOGIN is not set — assign-then-verify locking is disabled. "
            "Set it to the GitHub login of the bot account for concurrency safety."
        )

    logging.basicConfig(
        level=settings.log_level,
        format=f"%(asctime)s [%(levelname)s] {SENTINEL_ID} - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    gh_queue = GitHubQueue(settings.github_token, settings.github_owner, settings.github_repo)
    sentinel = Sentinel(gh_queue)

    try:
        await sentinel.run_forever()
    finally:
        await gh_queue.close()
        logger.info("Sentinel shut down.")


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        logger.info("Sentinel shutting down gracefully.")
