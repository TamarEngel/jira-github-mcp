"""
GitHub Tool: Create Pull Request
Creates a new pull request for a Jira issue
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from src.providers.github.github_api import github_api_post, github_api_get
from src.config.github_config import get_github_config, extract_repo_info


def register(mcp: FastMCP) -> None:
    """Register the create_pull_request tool with FastMCP"""
    
    @mcp.tool(name="create_pull_request")
    def create_pull_request(issue_key: str,branch_name: str,title: Optional[str] = None,description: Optional[str] = None) -> Dict[str, Any]:
        """Create a pull request for a Jira issue."""
        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        # Use default title if not provided
        if not title:
            title = f"{issue_key}: Create feature branch"
        
        # Build description with issue link
        if not description:
            description = f"Closes #{issue_key}\n\nThis PR addresses the task in Jira issue **{issue_key}**."
        else:
            # Ensure issue reference is in description
            if issue_key not in description:
                description += f"\n\nCloses #{issue_key}"
        
        try:
            # Create PR body
            body = {
                "title": title,"body": description,"head": branch_name,  # Source branch "base": cfg.default_branch,  # Target branch (main/master)
            }
            
            # Create the PR
            result = github_api_post(
                f"/repos/{owner}/{repo}/pulls",
                json_body=body,
            )
            
            pr_number = result.get("number")
            pr_url = result.get("html_url")
            
            return {
                "success": True,"issue_key": issue_key,"pr_number": pr_number,
                "pr_url": pr_url,"branch_name": branch_name,"message": f"Pull request #{pr_number} created successfully for {issue_key}",
            }
        except Exception as e:
            return {
                "success": False,"error": str(e),"issue_key": issue_key,"branch_name": branch_name,
            }
