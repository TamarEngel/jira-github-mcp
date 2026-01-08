"""
GitHub Tool: Create Pull Request
Creates a new pull request for a Jira issue
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from src.providers.github.github_api import github_api_post
from src.config.github_config import get_github_config, extract_repo_info


def register(mcp: FastMCP) -> None:
    """
    Register the create_pull_request tool with the MCP server.
    
    Enables the LLM to open pull requests for Jira issues with automatic linking
    and standard formatting.
    """
    
    @mcp.tool(name="create_pull_request")
    async def create_pull_request(issue_key: str, branch_name: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a pull request for a Jira issue (async).
        
        Args:
            issue_key: The Jira issue key (e.g., "KAN-1") - auto-linked in PR description
            branch_name: The source branch containing the changes (feature branch)
            title: Optional PR title. If not provided, defaults to "{issue_key}: Create feature branch"
            description: Optional PR description. Issue key is auto-appended if not present.
            
        Returns:
            Dictionary with success flag, PR data, and creation message  

        Raises:
            RuntimeError: If PR creation fails
        """
        
        cfg = get_github_config()
        owner, repo = extract_repo_info(cfg.repo_url)
        
        # Use default title if not provided
        if not title:
            title = f"{issue_key}: Pull request"
        
        # Build description with issue key reference for linking - WHY: GitHub recognizes
        # "Closes #KEY" syntax to auto-link PRs to Jira issues
        if not description:
            description = f"Closes #{issue_key}\n\nThis PR addresses the task in Jira issue **{issue_key}**."
        else:
            # Ensure issue key is mentioned in description for cross-linking
            if issue_key not in description:
                description += f"\n\nCloses #{issue_key}"
        
        try:
            # Create PR body
            body = {
                "title": title,
                "body": description,
                "head": branch_name,  # Source branch
                "base": cfg.default_branch,  # Target branch (main/master)
            }
            
            # Create the pull request via GitHub API
            result = await github_api_post(
                f"/repos/{owner}/{repo}/pulls",
                json_body=body,
            )

            pr_number = result.get("number")
            pr_url = result.get("html_url")
            return {
                "success": True,
                "data": {
                    "issue_key": issue_key,
                    "branch_name": branch_name,
                    "pr_number": pr_number,
                    "pr_url": pr_url,
                },
                "message": f"Pull request #{pr_number} created successfully for {issue_key}",
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to create pull request from {branch_name}: {str(e)}") from e
