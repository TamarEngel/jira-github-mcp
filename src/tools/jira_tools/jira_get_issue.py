from __future__ import annotations

from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_get
from src.providers.jira.jira_fields import ISSUE_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issue

def register(mcp: FastMCP) -> None:
    @mcp.tool(name="jira_get_issue")
    def jira_get_issue(issue_key: str, fields: Optional[List[str]] = None, raw: bool = False)-> Dict[str, Any]:
        """Get one Jira issue by key (e.g., KAN-1)."""
        endpoint = f"/issue/{issue_key}"
        
        effective_fields = fields or ISSUE_DEFAULT_FIELDS
        params = {"fields": ",".join(effective_fields)}

        issue = jira_api_get(endpoint, params=params)

        if raw:
            return issue

        return format_issue(issue)