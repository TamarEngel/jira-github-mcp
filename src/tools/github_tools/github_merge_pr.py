"""
GitHub Tool: Merge Pull Request
Merges a PR to main after checking status and reviews
"""

from __future__ import annotations

from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from src.providers.github.github_api import github_api_get, github_api_put
from src.config.github_config import get_github_config, extract_repo_info


def register(mcp: FastMCP) -> None:
    """
    Register the merge_pull_request tool with the MCP server.
    
    Enables the LLM to merge pull requests with CI status and code review validation.
    Supports different merge strategies (squash, merge, rebase).
    """
    
    @mcp.tool(name="merge_pull_request")
    async def merge_pull_request(pr_number: int | str, merge_method: str = "squash", check_status: bool = False) -> Dict[str, Any]:
        """
        Merge a pull request after optional validation of CI status and reviews (async).
        
        Args:
            pr_number: The GitHub PR number to merge
            merge_method: Merge strategy - "squash" (default), "merge", or "rebase"
            check_status: If True, validates CI status (if CI exists) before merging.
            Code review status (changes requested) is always validated.

            
        Returns:
            Success object with merge commit info
            
        Raises:
            ValueError: If PR is already merged, closed, has changes requested, or CI checks fail
            RuntimeError: If merge operation fails
        """
        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        # Get PR details to validate state and get commit SHA
        pr_data = await github_api_get(
            f"/repos/{owner}/{repo}/pulls/{pr_number}"
        )

        # Check PR state - WHY: Can't merge PRs that are already merged or closed
        if pr_data.get("merged"):
            raise ValueError(f"PR #{pr_number} is already merged")
        if pr_data.get("state") != "open":
            raise ValueError(f"Cannot merge PR #{pr_number}: PR is {pr_data.get('state')}")
        
        # Validate CI status only if check_status is True (optional validation)
        if check_status:
            # Get CI status from the PR's head commit - WHY: Need SHA to fetch status
            commit_sha = pr_data.get("head", {}).get("sha")
            if not commit_sha:
                raise ValueError(f"Cannot merge PR #{pr_number}: missing head commit SHA")

            status_data = await github_api_get(f"/repos/{owner}/{repo}/commits/{commit_sha}/status")
            state = status_data.get("state", "success")  # Default to success if no CI exists

            # Validate CI status only if requested - WHY: Only raise if explicitly checked
            if state == "failure":
                failing = [s.get("context") for s in status_data.get("statuses", []) if s.get("state") == "failure"]
                raise ValueError(f"Cannot merge PR #{pr_number}: CI checks failed ({', '.join(failing)})")
            elif state == "pending":
                raise ValueError(f"Cannot merge PR #{pr_number}: CI checks still pending")
        
        # Check for requested changes from reviewers - WHY: PRs with requested changes
        # shouldn't be merged even if CI passes
        reviews = await github_api_get(f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews")
        changes_requested = [r.get("user", {}).get("login") for r in reviews if r.get("state") == "CHANGES_REQUESTED"]
        if changes_requested:
            raise ValueError(f"Cannot merge PR #{pr_number}: Changes requested by {', '.join(changes_requested)}")
        
        # Perform the merge with specified strategy
        try:
            result = await github_api_put(
                f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
                json_body={
                    "merge_method": merge_method,
                    "commit_title": pr_data.get("title"),
                    "commit_message": f"Merge PR #{pr_number}: {pr_data.get('title')}\n\nAutomatically merged by MCP Server",
                }
            )
            
            return {
                "success": True,
                "pr_number": pr_number,
                "title": pr_data.get("title"),
                "commit_sha": result.get("sha"),
                "message": f"PR #{pr_number} merged successfully with {merge_method} strategy",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to merge PR #{pr_number}: {str(e)}") from e
