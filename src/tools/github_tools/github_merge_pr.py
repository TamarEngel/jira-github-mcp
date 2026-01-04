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
    """Register merge_pull_request tool"""
    
    @mcp.tool(name="merge_pull_request")
    def merge_pull_request(pr_number: int | str,merge_method: str = "squash",check_status: bool = False) -> Dict[str, Any]:
        """Merge PR after checking reviews and CI status.
        
        Args:
            pr_number: The PR number to merge
            merge_method: Method to use for merge (squash, merge, rebase)
            check_status: Whether to check CI status before merging (default: False)
        """

        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        try:
            # Get PR details
            pr_data = github_api_get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
            
            # Check PR state
            if pr_data.get("merged"):
                return {"success": False, "error": "PR already merged", "pr_number": pr_number}
            if pr_data.get("state") != "open":
                return {"success": False, "error": f"PR is {pr_data.get('state')}", "pr_number": pr_number}
            
            # Check CI status - but don't fail if no CI exists
            commit_sha = pr_data.get("head", {}).get("sha")
            status_data = github_api_get(f"/repos/{owner}/{repo}/commits/{commit_sha}/status")
            state = status_data.get("state", "success")  # Default to success if no CI
            
            if check_status:
                if state == "failure":
                    failing = [s.get("context") for s in status_data.get("statuses", []) if s.get("state") == "failure"]
                    return {"success": False, "error": f"CI failed: {', '.join(failing)}", "pr_number": pr_number}
                elif state == "pending":
                    return {"success": False, "error": "CI checks still pending", "pr_number": pr_number}
            
            # Check reviews
            reviews = github_api_get(f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews")
            changes_requested = [r.get("user", {}).get("login") for r in reviews if r.get("state") == "CHANGES_REQUESTED"]
            if changes_requested:
                return {"success": False, "error": f"Changes requested by: {', '.join(changes_requested)}", "pr_number": pr_number}
            
            # Perform merge
            result = github_api_put(
                f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
                json_body={
                    "merge_method": merge_method,
                    "commit_title": pr_data.get("title"),
                    "commit_message": f"Merge {pr_data.get('title')}\n\nAutomatically merged by GitHub Copilot MCP",
                }
            )
            
            return {
                "success": True,"pr_number": pr_number,"title": pr_data.get("title"),"commit_sha": result.get("sha"),"message": f"PR #{pr_number} merged successfully",
            }
        
        except RuntimeError as e:
            return {"success": False, "error": str(e), "pr_number": pr_number}
        except Exception as e:
            return {"success": False, "error": f"Merge failed: {str(e)}", "pr_number": pr_number}
