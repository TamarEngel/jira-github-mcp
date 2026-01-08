"""
Jira Response Formatters
Converts raw Jira API responses into compact, LLM-friendly structures.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.providers.jira.jira_adf import adf_to_text

def format_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw Jira issue JSON into a compact, LLM-friendly structure.
    
    Args:
        issue: Raw Jira issue object from API
    
    Returns:
        Dict with formatted issue data (key, summary, status, etc.)
    
    Raises:
        ValueError: If input is not a valid issue dict
    """

    if not isinstance(issue, dict):
        raise ValueError(f"Invalid issue item: expected dict, got {type(issue).__name__}")

    fields = issue.get("fields", {}) or {}

    def safe_get(obj: Any, path: List[str]) -> Any:
        """Safely navigate nested dict paths - WHY: Jira API has deeply nested fields."""
        cur = obj
        for p in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(p)
        return cur

    # Extract basic fields - WHY: These are the most commonly needed issue attributes
    key = issue.get("key")
    summary = fields.get("summary")
    status = safe_get(fields, ["status", "name"])
    priority = safe_get(fields, ["priority", "name"])
    issuetype = safe_get(fields, ["issuetype", "name"])
    assignee = safe_get(fields, ["assignee", "displayName"])
    reporter = safe_get(fields, ["reporter", "displayName"])
    duedate = fields.get("duedate")

    created = fields.get("created")
    updated = fields.get("updated")

    # Description: ADF -> text
    description_adf = fields.get("description")
    description_text = adf_to_text(description_adf)

    # Subtasks: Extract minimal info for each subtask
    subtasks_out = []
    for st in fields.get("subtasks", []) or []:
        st_fields = st.get("fields", {}) or {}
        subtasks_out.append({
            "key": st.get("key"),
            "summary": st_fields.get("summary"),
            "status": (st_fields.get("status", {}) or {}).get("name"),
            "issuetype": (st_fields.get("issuetype", {}) or {}).get("name"),
        })

    return {
        "key": key,
        "summary": summary,
        "issuetype": issuetype,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "reporter": reporter,
        "duedate": duedate,
        "created": created,
        "updated": updated,
        "description_text": description_text,
        "subtasks": subtasks_out,
    }

def format_issues_list(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Jira search/list payload into compact, LLM-friendly structure.
    
    Args:
        payload: Jira API search response with structure:
            {"issues": [issue1, issue2, ...], "isLast": bool, "nextPageToken": str}
    
    Returns:
        Dict with count, formatted issues list, and pagination info
    
    Raises:
        ValueError: If payload is not a valid dict
    """
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid payload: expected dict, got {type(payload).__name__}")
        
    issues = payload.get("issues", []) or []

    # Format each issue using format_issue helper
    formatted = [format_issue(issue) for issue in issues]

    return {
        "count": len(formatted),
        "issues": formatted,
        "is_last": payload.get("isLast"),
        "next_page_token": payload.get("nextPageToken"),
    }
