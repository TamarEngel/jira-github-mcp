"""
GitHub API Client Module

Provides a low-level HTTP client for the GitHub REST API.
Handles authentication, URL construction, and request dispatching.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import httpx
from src.config.github_config import get_github_config


async def _github_request(method: str, endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make an authenticated request to GitHub API.
    
    Centralizes request logic to ensure consistent authentication and error handling
    across all GitHub operations. Constructs the full URL, adds authentication headers,
    and handles HTTP requests for all HTTP methods.

    Args:
        method: HTTP method (GET, POST, PUT, etc.)
        endpoint: API endpoint path (e.g., "/repos/owner/repo/issues")
        json_body: Request body as dictionary (will be JSON encoded)
        params: Query parameters for filtering, pagination, etc.
        
    Returns:
        Parsed JSON response from GitHub
        
    Raises:
        RuntimeError: If the HTTP response status is not OK (non-2xx/3xx)
    """
    cfg = get_github_config()
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"token {cfg.token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.request( 
            method,
            url,
            headers=headers,
            json=json_body,
            params=params,
        )

    if r.status_code >= 400:
        raise RuntimeError(f"GitHub {method} error {r.status_code}: {r.text}")

    if r.status_code == 204 or not r.content:
        return {"ok": True, "status_code": r.status_code}

    return r.json()


async def github_api_get(endpoint: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make GET request to GitHub API.
    
    Used for retrieving data from GitHub (fetch repos, issues, PRs, etc.).

    Args:
        endpoint: API endpoint path (e.g., "/repos/owner/repo")
        params: Query parameters for filtering, pagination, etc.
        
    Returns:
        Parsed JSON response from GitHub
    """
    return await _github_request("GET", endpoint, params=params)


async def github_api_post(endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make POST request to GitHub API.
    
    Used for operations that modify GitHub state (create branches, PRs, issues, etc.).

    Args:
        endpoint: API endpoint path (e.g., "/repos/owner/repo/git/refs")
        json_body: Request body as dictionary
        params: Query parameters
        
    Returns:
        Parsed JSON response from GitHub
    """
    return await _github_request("POST", endpoint, json_body=json_body, params=params)


async def github_api_put(endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make PUT request to GitHub API.
    
    Used for operations that update or merge GitHub resources (merge PRs, update branches, etc.).

    Args:
        endpoint: API endpoint path
        json_body: Request body as dictionary
        params: Query parameters
        
    Returns:
        Parsed JSON response from GitHub
    """
    return await _github_request("PUT", endpoint, json_body=json_body, params=params)
