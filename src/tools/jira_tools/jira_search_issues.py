from __future__ import annotations

from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.providers.jira.jira_api import jira_api_post
from src.providers.jira.jira_logs import write_log
from src.providers.jira.jira_fields import LIST_DEFAULT_FIELDS
from src.providers.jira.jira_formatters import format_issues_list

def register(mcp: FastMCP) -> None:
    @mcp.tool(name="jira_search_issues")
    def jira_search_issues(jql: str,max_results: int = 10,next_page_token: Optional[str] = None,fields: Optional[List[str]] = None,raw: bool = False)-> Dict[str, Any]:
        """
        Search Jira issues using JQL (POST /search).
        Returns issues with their key, summary, status, priority, due date, and other details.
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

        write_log("jira-search", {"endpoint": "/search/jql", "body": body})

        payload = jira_api_post("/search/jql", json_body=body, log_prefix="jira-search")
        return payload if raw else format_issues_list(payload)
