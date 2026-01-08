"""
Jira tool to retrieve a single issue by its key.

This module provides the get_issue tool that allows fetching detailed information
about a specific Jira issue with optional field filtering and formatting.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_get
from src.providers.jira.jira_fields import ISSUE_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issue

def register(mcp: FastMCP) -> None:
    """
    Register the Jira get_issue tool with the MCP server.
    
    This tool allows retrieval of a single Jira issue by its key with optional field
    filtering and formatting. Used by the LLM to look up issue details during workflow operations.
    """
    @mcp.tool(name="jira_get_issue")
    async def jira_get_issue(issue_key: str, fields: Optional[List[str]] = None, raw: bool = False) -> Dict[str, Any]:
        """
        Retrieve a single Jira issue by its key (async).
        
        Args:
            issue_key: The issue key (e.g., "KAN-1", "PROJ-42")
            fields: Optional list of specific fields to retrieve (defaults to summary, status, etc.)
            raw: If True, returns unformatted API response; if False, returns formatted issue
            
        Returns:
            Issue details as a dictionary (formatted by default)
        """
        endpoint = f"/issue/{issue_key}"
        
        # Use provided fields or fall back to defaults
        effective_fields = fields or ISSUE_DEFAULT_FIELDS
        params = {"fields": ",".join(effective_fields)}

        issue = await jira_api_get(endpoint, params=params)

        if raw:
            return issue

        return format_issue(issue)