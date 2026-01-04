from __future__ import annotations

from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP

from src.providers.jira.jira_api import jira_api_get, jira_api_post


def _normalize_status_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def register(mcp: FastMCP) -> None:
    @mcp.tool(name="jira_transition_issue")
    def jira_transition_issue(issue_key: str,to_status: str,comment: Optional[str] = None,raw: bool = False) -> Dict[str, Any]:
        """
        Move an issue to another status using Jira transitions (workflow-safe).
        """
        # 1) fetch available transitions
        transitions_payload = jira_api_get(f"/issue/{issue_key}/transitions")
        transitions: List[Dict[str, Any]] = transitions_payload.get("transitions", []) or []

        target = _normalize_status_name(to_status)

        # 2) find a matching transition by its target status name (transition.to.name)
        chosen = None
        for tr in transitions:
            to_obj = tr.get("to") or {}
            to_name = to_obj.get("name") or ""
            if _normalize_status_name(to_name) == target:
                chosen = tr
                break

        if chosen is None:
            # return helpful info for AI/user: what is possible right now?
            options = []
            for tr in transitions:
                to_obj = tr.get("to") or {}
                options.append({"transition_id": tr.get("id"),"transition_name": tr.get("name"),"to_status": to_obj.get("name"),})

            return {"ok": False,"error": "no_matching_transition","issue_key": issue_key,"requested_to_status": to_status,"available_transitions": options,}

        transition_id = chosen.get("id")
        # 3) perform transition
        body: Dict[str, Any] = {"transition": {"id": transition_id}}
        comment_added = False
        if comment:
            try:
                body["update"] = {
                    "comment": [{"add": {"body": comment}}]
                }
                comment_added = True
            except Exception:
                # If comment fails, continue without it
                pass

        result = jira_api_post(f"/issue/{issue_key}/transitions", json_body=body)

        if not raw:
            new_status = (chosen.get("to") or {}).get("name")
            result = {
                "ok": True,
                "issue_key": issue_key,
                "moved_to": new_status,
                "transition_used": {
                    "id": transition_id,
                    "name": chosen.get("name"),
                },
                "comment_added": bool(comment),
            }
        
        return result
