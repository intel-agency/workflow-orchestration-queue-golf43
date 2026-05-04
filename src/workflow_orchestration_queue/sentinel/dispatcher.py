"""
Shell-Bridge Dispatcher.

Manages the worker lifecycle through the shell bridge script.
Handles environment setup, server start, prompt execution, and teardown.
"""

import asyncio
import logging
import subprocess
from typing import Optional

logger = logging.getLogger("OS-APOW-Dispatcher")


class Dispatcher:
    """Dispatches tasks to the opencode worker via the shell bridge."""

    def __init__(self, shell_bridge_path: str = "./scripts/devcontainer-opencode.sh"):
        self.shell_bridge_path = shell_bridge_path

    async def run_command(self, args: list[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess[str]:
        """Execute a shell bridge command.

        Args:
            args: Command arguments to pass to the shell bridge.
            timeout: Maximum seconds to wait.

        Returns:
            CompletedProcess with captured stdout/stderr.
        """
        full_args = [self.shell_bridge_path] + args
        logger.info(f"Dispatching: {' '.join(full_args)}")

        process = await asyncio.create_subprocess_exec(*full_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Command timed out after {timeout}s: {' '.join(args)}")
            process.kill()
            stdout, stderr = await process.communicate()
            return subprocess.CompletedProcess(
                args=full_args,
                returncode=-1,
                stdout=stdout.decode().strip() if stdout else "",
                stderr=f"TIMEOUT after {timeout}s",
            )

        return subprocess.CompletedProcess(
            args=full_args,
            returncode=process.returncode or 0,
            stdout=stdout.decode().strip() if stdout else "",
            stderr=stderr.decode().strip() if stderr else "",
        )

    async def bring_up(self, timeout: int = 300) -> subprocess.CompletedProcess[str]:
        """Bring up the devcontainer environment."""
        return await self.run_command(["up"], timeout=timeout)

    async def start_server(self, timeout: int = 120) -> subprocess.CompletedProcess[str]:
        """Start the opencode server."""
        return await self.run_command(["start"], timeout=timeout)

    async def send_prompt(self, prompt: str, timeout: int = 5700) -> subprocess.CompletedProcess[str]:
        """Send a prompt to the opencode agent."""
        return await self.run_command(["prompt", prompt], timeout=timeout)

    async def tear_down(self, timeout: int = 60) -> subprocess.CompletedProcess[str]:
        """Stop the devcontainer environment."""
        return await self.run_command(["stop"], timeout=timeout)
