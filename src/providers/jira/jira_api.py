"""
Jira API Client Module

Provides low-level HTTP client for interacting with Jira REST APIs.
Handles authentication, URL construction, and edge-case response handling.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import httpx
from src.config.jira_config import get_jira_config
from src.providers.jira.jira_logs import write_log


def _json_response(resp: httpx.Response, *, allow_empty: bool) -> Any:
    """
    Parse Jira responses as JSON, safely handling Jira-specific edge cases.

    - GET (allow_empty=False): response must be valid JSON; otherwise an error is raised.
    - POST (allow_empty=True): some operations (e.g., transitions) may return 204 No Content
    or an empty body, which is treated as a successful response instead of failing.
    """

    if allow_empty and resp.status_code == 204:
        return {"ok": True, "status_code": 204}

    text = (resp.text or "").strip()
    if allow_empty and not text:
        return {"ok": True, "status_code": resp.status_code}

    try:
        return resp.json()
    except ValueError as e:
        snippet = (resp.text or "")[:500]
        raise RuntimeError(
            f"Expected JSON but got non-JSON response (status={resp.status_code}). "
            f"Body snippet: {snippet!r}"
        ) from e
        

def _build_url(endpoint: str, use_agile_api: bool) -> str:
    """
    Build complete Jira API URL from endpoint and config.
    
    Jira has two APIs: REST API (/rest/api/3) for general operations,
    and Agile API (/rest/agile/1.0) for sprint operations.
    """
    cfg = get_jira_config()
    # Choose API based on operation type
    base_api_path = "/rest/agile/1.0" if use_agile_api else "/rest/api/3"
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    return f"{cfg.base_url}{base_api_path}{endpoint}"


async def jira_api_get(
    endpoint: str,
    *,
    log_prefix: str | None = None,
    use_agile_api: bool = False,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Make authenticated GET request to Jira API (async).
    
    Used for retrieving data from Jira (fetch issues, projects, etc.).
    Uses _json_response() to safely parse responses and handle JSON parse errors.

    Args:
        endpoint: API endpoint path (e.g., "/issue/KAN-1")
        use_agile_api: Use Agile API if True, REST API if False
        params: Query parameters (e.g., fields to retrieve)
        
    Returns:
        Parsed JSON response from Jira
    """
    cfg = get_jira_config()
    url = _build_url(endpoint, use_agile_api)

    async with httpx.AsyncClient(timeout=30) as client:  
        r = await client.get(  
            url,
            auth=(cfg.email, cfg.api_token),  
            headers={"Accept": "application/json"},
            params=params,
        )

    if r.status_code >= 400:  
        raise RuntimeError(f"Jira GET error {r.status_code}: {r.text}")

    # Log successful API call for debugging
    if log_prefix:
        write_log(log_prefix, {"endpoint": endpoint, "status": r.status_code})
    # Use safe response handler to parse JSON gracefully
    return _json_response(r, allow_empty=False)


async def jira_api_post(
    endpoint: str,
    *,
    log_prefix: str | None = None,
    use_agile_api: bool = False,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Make authenticated POST request to Jira API (async).
    
    Used for operations that modify Jira state (create, update, transition issues).
    Uses _json_response() with allow_empty=True to handle 204 No Content responses.

    Args:
        endpoint: API endpoint path (e.g., "/issue/KAN-1/transitions")
        use_agile_api: Use Agile API if True, REST API if False
        json_body: Request body as dictionary
        params: Query parameters
        
    Returns:
        Parsed JSON response or safe default for 204 responses
    """
    cfg = get_jira_config()
    url = _build_url(endpoint, use_agile_api)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            url,
            auth=(cfg.email, cfg.api_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            params=params,
            json=json_body,
        )
    
    if r.status_code >= 400:
        raise RuntimeError(f"Jira POST error {r.status_code}: {r.text}")

    # Log successful API call for debugging
    if log_prefix:
        write_log(log_prefix, {"endpoint": endpoint, "status": r.status_code})
    # Handle 204 No Content responses from operations like issue transitions
    return _json_response(r, allow_empty=True)

