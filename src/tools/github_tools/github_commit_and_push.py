"""
GitHub Tool: Commit and Push
Stage all changes, commit with message, and push to current branch
"""

from __future__ import annotations

import os
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from src.config.github_config import get_github_config, extract_repo_info
from src.providers.github.git_operations import run_git_command_async


def register(mcp: FastMCP) -> None:
    """
    Register the git_commit_and_push tool with the MCP server.
    
    Enables the LLM to commit local changes and push to remote with a single operation.
    """
    
    @mcp.tool(name="git_commit_and_push")
    async def git_commit_and_push(message: str, local_path: str | None = None, branch: str | None = None) -> Dict[str, Any]:
        """
        Stage all changes, commit with message, and push to remote branch (async).
        
        Args:
            message: The commit message describing the changes
            local_path: Path to the git repository (optional, defaults to configured repo location)
            branch: Target branch to push to (optional, defaults to current branch)
            
        Returns:
            Success object with commit hash and branch pushed to
            
        Raises:
            ValueError: If local_path is not a git repository
            RuntimeError: If git commands fail (get branch, stage, commit, or push)

        Implementation details:
            Uses run_git_command_async() to avoid blocking the async event loop during subprocess/git I/O.
        """
        
        cfg = get_github_config()
        _, repo_name = extract_repo_info(cfg.repo_url)
        
        if not local_path:
            local_path = os.path.expanduser(f"~/{repo_name}")
        local_path = os.path.abspath(local_path)
        
        if not os.path.isdir(os.path.join(local_path, ".git")):
            raise ValueError(f"Not a git repository: {local_path}")
        
        # Get current branch for fallback and validation
        ok, current_branch = await run_git_command_async(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=local_path
        )
        if not ok:
            raise RuntimeError(f"Failed to get current branch: {current_branch}")
        
        # Use provided branch or current branch
        target_branch = branch if branch else current_branch
        
        # Stage all changes (git add .) - WHY: Must stage before commit
        ok, stage_out = await run_git_command_async(
            ["git", "add", "."],
            cwd=local_path
        )
        if not ok:
            raise RuntimeError(f"Failed to stage changes: {stage_out}")
        
        # Commit with provided message
        ok, commit_out = await run_git_command_async(
            ["git", "commit", "-m", message],
            cwd=local_path
        )
        if not ok:
            if "nothing to commit" in (commit_out or "").lower():
                raise RuntimeError("Nothing to commit (working tree clean).")
            raise RuntimeError(f"Failed to commit changes: {commit_out}")
        
        # Get the short commit hash for response
        ok, commit_hash = await run_git_command_async(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=local_path
        )
        if not ok:
            commit_hash = "unknown"
        
        # Push to remote - WHY: Timeout is set to 60s to allow time for potentially slow network operations
        ok, push_out = await run_git_command_async(
            ["git", "push", "origin", target_branch],
            cwd=local_path,
            timeout=60
        )
        if not ok:
            raise RuntimeError(f"Failed to push to {target_branch}: {push_out}")
        
        return {"success": True, "branch": target_branch, "commit": commit_hash, "message": message, "local_path": local_path}

