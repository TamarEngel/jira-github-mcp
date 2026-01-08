"""
Jira tool to retrieve issues assigned to the current user.

This module provides the get_my_issues tool that fetches the current user's assigned
issues with optional filtering by status and issue type.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_post
from src.providers.jira.jira_fields import LIST_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issues_list

def register(mcp: FastMCP) -> None:
    """
    Register the Jira get_my_issues tool with the MCP server.
    
    Allows the LLM to retrieve the current user's assigned issues with optional filtering
    by status (To Do, In Progress, etc.) and issue type (Bug, Task, Story, etc.).
    """
    @mcp.tool(name="jira_get_my_issues")
    async def jira_get_my_issues(
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        max_results: int = 50,
        fields: Optional[List[str]] = None,
        raw: bool = False
    ) -> Dict[str, Any]:
        """
        Get issues assigned to the current user with optional filters (async).
        
        Args:
            status: Filter by status (e.g., "To Do", "In Progress", "Done")
            issue_type: Filter by issue type (e.g., "Bug", "Task", "Story")
            max_results: Maximum number of results to return (default: 50)
            fields: Optional list of specific fields to include (defaults to key, summary, status, etc.)
            raw: If True, returns unformatted API response; if False, returns formatted list
            
        Returns:
            Dictionary with assigned issues list, ordered by priority and updated time via JQL
        """

        jql_parts = ['assignee = currentUser()']

        if status:
            jql_parts.append(f'status = "{status}"')
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')

        # Build JQL query and sort by priority (high first) then by recently updated
        jql = " AND ".join(jql_parts) + " ORDER BY priority DESC, updated DESC"

        body: Dict[str, Any] = {"jql": jql, "maxResults": max_results}
        
        effective_fields: List[str] = list(LIST_DEFAULT_FIELDS)

        if fields:
            for f in fields:
                if f not in effective_fields:
                    effective_fields.append(f)

        body["fields"] = effective_fields

        payload = await jira_api_post(  
            "/search/jql",
            json_body=body,
            log_prefix="jira-my-issues"
        )
        return payload if raw else format_issues_list(payload)
