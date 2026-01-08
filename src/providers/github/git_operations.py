"""
Git Operations Provider
Centralized module for running git commands safely
"""

import subprocess
import logging
import asyncio

logger = logging.getLogger(__name__)


def run_git_command(cmd: list, cwd: str | None = None, timeout: int = 30) -> tuple[bool, str]:
    """
    Run a git command safely and return success status and output.
    
    Args:
        cmd: List of command arguments (e.g., ['git', 'status'])
        cwd: Working directory for command execution (optional)
        timeout: Command timeout in seconds (default: 30)
    
    Returns:
        tuple[bool, str]: (success, output/error_message)
            - True with stdout if command succeeds
            - False with stderr or stdout if command fails
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL  # Prevent hanging on stdin
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except Exception as e:
        return False, str(e)

async def run_git_command_async(cmd: list, cwd: str | None = None, timeout: int = 30) -> tuple[bool, str]:
    """
    Run git command without blocking the async event loop.

    WHY: subprocess.run is blocking (I/O-bound). In async MCP tools we must avoid blocking,
    so we offload it to a thread using asyncio.to_thread.
    """
    return await asyncio.to_thread(run_git_command, cmd, cwd, timeout)  
