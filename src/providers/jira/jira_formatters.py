# src/providers/jira_formatters.py
from __future__ import annotations
from typing import Any, Dict, List

from src.providers.jira.jira_adf import adf_to_text

def format_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw Jira issue JSON into a compact, LLM-friendly structure.
    """

    if not isinstance(issue, dict):
        return {"error": "invalid_issue_item", "value": str(issue)}

    fields = issue.get("fields", {}) or {}

    def safe_get(obj: Any, path: List[str]) -> Any:
        cur = obj
        for p in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(p)
        return cur

    # Basic fields
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

    # Subtasks: compact list
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
    Convert Jira search/list payload (with 'issues') into compact, LLM-friendly structure.
    Expects payload like: {"issues":[{issue},{issue}], "isLast":..., "nextPageToken":...}
    """
    if not isinstance(payload, dict):
        return {"error": "invalid_payload", "value": str(payload)}
        
    issues = payload.get("issues", []) or []

    formatted = [format_issue(issue) for issue in issues]

    return {
        "count": len(formatted),
        "issues": formatted,
        "is_last": payload.get("isLast"),
        "next_page_token": payload.get("nextPageToken"),
    }
