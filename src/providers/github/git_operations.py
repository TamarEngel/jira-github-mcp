"""
Git Operations Provider
Centralized module for running git commands safely
"""

import subprocess
import logging

logger = logging.getLogger(__name__)


def run_git_command(cmd: list, cwd: str | None = None, timeout: int = 30) -> tuple[bool, str]:
    """
    Run a git command safely and return success status and output.
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
