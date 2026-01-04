"""
GitHub Tool: Commit and Push
Stage all changes, commit with message, and push to current branch
"""

from __future__ import annotations

import os
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from src.config.github_config import get_github_config, extract_repo_info
from src.providers.github.git_operations import run_git_command


def register(mcp: FastMCP) -> None:
    """Register commit_and_push tool"""
    
    @mcp.tool(name="git_commit_and_push")
    def git_commit_and_push(message: str,local_path: str | None = None,branch: str | None = None,) -> Dict[str, Any]:
        """Stage, commit, and push changes in one command.
        Args:
            message: The commit message
            local_path: Path to the git repository (optional)
            branch: Target branch to push to (optional, defaults to current branch)
        """
        
        cfg = get_github_config()
        _, repo_name = extract_repo_info(cfg.repo_url)
        
        if not local_path:
            local_path = os.path.expanduser(f"~/{repo_name}")
        local_path = os.path.abspath(local_path)
        
        if not os.path.isdir(os.path.join(local_path, ".git")):
            return {"success": False, "error": "Not a git repo", "local_path": local_path}
        
        # Get current branch
        ok, current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=local_path)
        if not ok:
            return {"success": False, "error": f"Failed to get branch: {current_branch}"}
        
        # Use provided branch or current branch
        target_branch = branch if branch else current_branch
        
        # Stage, commit, push
        ok, _ = run_git_command(["git", "add", "."], cwd=local_path)
        if not ok:
            return {"success": False, "error": "Stage failed", "branch": target_branch}
        
        ok, commit_out = run_git_command(["git", "commit", "-m", message], cwd=local_path)
        if not ok:
            return {"success": False, "error": f"Commit failed: {commit_out}", "branch": target_branch}
        
        ok, commit_hash = run_git_command(["git", "rev-parse", "--short", "HEAD"], cwd=local_path)
        if not ok:
            commit_hash = "unknown"
        
        ok, push_out = run_git_command(["git", "push", "origin", target_branch], cwd=local_path, timeout=60)
        if not ok:
            return {"success": False, "error": f"Push failed: {push_out}", "branch": target_branch, "commit": commit_hash}
        
        return {"success": True, "branch": target_branch, "commit": commit_hash,"message": message,"local_path": local_path,}

