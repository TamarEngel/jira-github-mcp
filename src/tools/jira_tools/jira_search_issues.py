"""
Jira tool to search for issues using JQL (Jira Query Language).

This module provides the search_issues tool that enables querying across Jira issues
with support for pagination and field customization.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_post
from src.providers.jira.jira_fields import LIST_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issues_list

def register(mcp: FastMCP) -> None:
    """
    Register the Jira search_issues tool with the MCP server.
    
    Enables the LLM to search for issues across projects using Jira Query Language (JQL).
    Supports pagination and field customization.
    """
    @mcp.tool(name="jira_search_issues")
    async def jira_search_issues(
        jql: str,
        max_results: int = 10,
        next_page_token: Optional[str] = None,
        fields: Optional[List[str]] = None,
        raw: bool = False
    ) -> Dict[str, Any]:
        """
        Search Jira issues using JQL (POST /search) (async).
        
        Args:
            jql: JQL query string (e.g., 'project = "KAN" AND status = "Open"')
            max_results: Maximum number of results to return (default: 10)
            next_page_token: Pagination token from previous search for next page
            fields: Optional list of specific fields to include (defaults to key, summary, status, etc.)
            raw: If True, returns unformatted API response; if False, returns formatted list
            
        Returns:
            Dictionary with issues list and pagination info (formatted by default)
        """

        jql = jql.strip()
        body: Dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results
        }

        if next_page_token:
            body["nextPageToken"] = next_page_token

        effective_fields: List[str] = list(LIST_DEFAULT_FIELDS)

        if fields:
            for f in fields:
                if f not in effective_fields:
                    effective_fields.append(f)

        body["fields"] = effective_fields

        payload = await jira_api_post(
            "/search/jql",
            json_body=body,
            log_prefix="jira-search"
        )
        return payload if raw else format_issues_list(payload)
