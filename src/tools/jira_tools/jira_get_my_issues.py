from __future__ import annotations

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_post
from src.providers.jira.jira_logs import write_log
from src.providers.jira.jira_fields import LIST_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issues_list

def register(mcp: FastMCP) -> None:
    @mcp.tool(name="jira_get_my_issues")
    def jira_get_my_issues(
        status: Optional[str] = None,        # "To Do" / "IN PROGRESS" / "IN REVIEW" / "DONE"
        issue_type: Optional[str] = None,    # "Bug" / "Task" / "Story"...
        max_results: int = 50,
        fields: Optional[List[str]] = None,
        raw: bool = False
    )-> Dict[str, Any]:
        """
        Get issues assigned to current user, with optional filters (project/status/type).
        """

        jql_parts = ['assignee = currentUser()']

        if status:
            jql_parts.append(f'status = "{status}"')
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')

        jql = " AND ".join(jql_parts) + " ORDER BY priority DESC, updated DESC"

        body: Dict[str, Any] = {"jql": jql, "maxResults": max_results,}
        
        effective_fields: List[str] = list(LIST_DEFAULT_FIELDS)

        if fields:
            for f in fields:
                if f not in effective_fields:
                    effective_fields.append(f)

        body["fields"] = effective_fields

        payload = jira_api_post("/search/jql", json_body=body, log_prefix="jira-my-issues")
        return payload if raw else format_issues_list(payload)
