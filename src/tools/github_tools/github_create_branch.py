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
    """Register the create_branch_for_issue tool with FastMCP"""
    
    @mcp.tool(name="create_branch_for_issue")
    def create_branch_for_issue(
        issue_key: str,
        branch_name: str | None = None,
    ) -> Dict[str, Any]:
        """
        Create a new Git branch for a Jira issue.
        """
        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        # Use custom branch name or default
        if not branch_name:
            branch_name = f"feature/{issue_key.lower()}"
        
        # Get the default branch SHA to create from
        try:
            default_branch_data = github_api_get(
                f"/repos/{owner}/{repo}/git/refs/heads/{cfg.default_branch}"
            )
            base_sha = default_branch_data["object"]["sha"]
        except Exception as e:
            return {
                "success": False,"error": f"Failed to get base branch SHA: {str(e)}","issue_key": issue_key,"branch_name": branch_name,
            }
        
        # Create new branch
        try:
            body = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
            
            result = github_api_post(
                f"/repos/{owner}/{repo}/git/refs",
                json_body=body,
            )
            
            return {
                "success": True,"issue_key": issue_key,"branch_name": branch_name,"ref": result.get("ref"),"message": f"Branch feature/{issue_key} created!\nSWITCH TO IT: git checkout feature/{issue_key}","next_step": f"git checkout feature/{issue_key}"
            }
        except Exception as e:
            return {
                "success": False,"error": str(e),"issue_key": issue_key,"branch_name": branch_name,
            }
