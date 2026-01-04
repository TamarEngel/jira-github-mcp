"""
GitHub API Client
"""

from typing import Any, Dict, Optional
import requests
from src.config.github_config import get_github_config


def _github_request(method: str, endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """Make a request to GitHub API."""
    cfg = get_github_config()
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"token {cfg.token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.request(method, url, headers=headers, json=json_body, params=params, timeout=30)
    if not r.ok:
        raise RuntimeError(f"GitHub {method} error {r.status_code}: {r.text}")
    return r.json()


def github_api_get(endpoint: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
    """GET request to GitHub API."""
    return _github_request("GET", endpoint, params=params)


def github_api_post(endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """POST request to GitHub API."""
    return _github_request("POST", endpoint, json_body=json_body, params=params)


def github_api_put(endpoint: str, *, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """PUT request to GitHub API."""
    return _github_request("PUT", endpoint, json_body=json_body, params=params)
