"""
Jira tool to transition issues through workflow states.

This module provides the transition_issue tool that moves issues through their
project's workflow while respecting workflow rules and supporting comments.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP

from src.providers.jira.jira_api import jira_api_get, jira_api_post


def _normalize_status_name(name: str) -> str:
    """Normalize status names for case-insensitive, whitespace-tolerant matching."""
    return " ".join(name.strip().lower().split())


def register(mcp: FastMCP) -> None:
    """
    Register the Jira transition_issue tool with the MCP server.
    
    Enables the LLM to move issues through workflow states while respecting
    the project's workflow rules. Supports adding comments during transitions.
    """
    @mcp.tool(name="jira_transition_issue")
    async def jira_transition_issue(issue_key: str, to_status: str, comment: Optional[str] = None, raw: bool = False) -> Dict[str, Any]:
        """
        Move an issue to another status using Jira transitions (workflow-safe, async).

        Args:
            issue_key: The issue key (e.g., "KAN-1")
            to_status: Target status name (e.g., "In Progress", "Done"). Must be a valid transition target.
            comment: Optional comment to add when transitioning
            raw: If True, returns full Jira API response; if False, returns simplified status
            
        Returns:
            Success object with new status, or error object with available transition options
        """

        # Jira enforces workflow transitions; fetch allowed transitions from current state.
        transitions_payload = await jira_api_get(
            f"/issue/{issue_key}/transitions"
        )
        transitions: List[Dict[str, Any]] = transitions_payload.get("transitions", []) or []

        target = _normalize_status_name(to_status)

        # Find a matching transition by its target status name (case-insensitive)
        chosen = None
        for tr in transitions:
            to_obj = tr.get("to") or {}
            to_name = to_obj.get("name") or ""
            if _normalize_status_name(to_name) == target:
                chosen = tr
                break

        if chosen is None:
            # Return helpful error with available options for the LLM to inform the user
            options = []
            for tr in transitions:
                to_obj = tr.get("to") or {}
                options.append(
                    {
                        "transition_id": tr.get("id"),
                        "transition_name": tr.get("name"),
                        "to_status": to_obj.get("name"),
                    }
                )
    
            return {
                "ok": False,
                "error": "no_matching_transition",
                "issue_key": issue_key,
                "requested_to_status": to_status,
                "available_transitions": options,
            }

        transition_id = chosen.get("id")
        if not transition_id:
            raise RuntimeError("Selected transition has no id")

        # Build transition request body - WHY: Jira requires transition ID in a specific format,
        # and comments are added via the "update" field alongside the transition
        body: Dict[str, Any] = {"transition": {"id": transition_id}}
        comment_added = False
        if comment:
            body["update"] = {"comment": [{"add": {"body": comment}}]}
            comment_added = True

        # Perform the actual transition via Jira API
        result = await jira_api_post(
            f"/issue/{issue_key}/transitions",
            json_body=body
        )

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
                "comment_added": comment_added,
            }
        
        return result
