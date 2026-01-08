"""
GitHub Tool: Create Branch for Jira Issue
Creates a new Git branch based on Jira issue key
"""

from __future__ import annotations

from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from src.providers.github.github_api import github_api_post, github_api_get
from src.config.github_config import get_github_config, extract_repo_info


def register(mcp: FastMCP) -> None:
    """
    Register the create_branch_for_issue tool with the MCP server.
    
    Enables the LLM to create feature branches for Jira issues with standard naming convention.
    """
    
    @mcp.tool(name="create_branch_for_issue")
    async def create_branch_for_issue(
        issue_key: str,
        branch_name: str | None = None,
    ) -> Dict[str, Any]:
        """
        Create a new Git branch for a Jira issue.
        
        Args:
            issue_key: The Jira issue key (e.g., "KAN-1") - used in default branch naming
            branch_name: Optional custom branch name. If not provided, defaults to "feature/{issue_key}"
            
        Returns:
            Dictionary with success flag, branch data (issue_key, branch_name, ref), and checkout instructions

        Raises:
            RuntimeError: If unable to fetch base branch SHA or create the branch
        """
        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        # Use custom branch name or default to feature/{issue_key}
        if not branch_name:
            branch_name = f"feature/{issue_key.lower()}"
        
        # Get the default branch SHA as base point for new branch - WHY: GitHub creates branches
        # by pointing a ref to a specific commit SHA, must fetch this first
        try:
            default_branch_data = await github_api_get(  
                f"/repos/{owner}/{repo}/git/refs/heads/{cfg.default_branch}"
            )
            base_sha = default_branch_data["object"]["sha"]
        except Exception as e:
            raise RuntimeError(f"Failed to get base branch SHA for {cfg.default_branch}: {str(e)}") from e
        
        # Create new branch at the base SHA
        try:
            body = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
            
            result = await github_api_post(
                f"/repos/{owner}/{repo}/git/refs",
                json_body=body,
            )
            return {
                "success": True,
                "data": {
                    "issue_key": issue_key,
                    "branch_name": branch_name,
                    "ref": result.get("ref"),
                },
                "message": f"Branch {branch_name} created successfully.",
                "next_step": f"git checkout {branch_name}",
            }

        except Exception as e:
            raise RuntimeError(f"Failed to create branch {branch_name}: {str(e)}") from e
