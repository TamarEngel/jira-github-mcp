from __future__ import annotations

from typing import Any, Dict, Optional
import requests
from requests.auth import HTTPBasicAuth
from src.providers.jira.jira_logs import write_log
from src.config.jira_config import get_jira_config
import json

def _safe_json_response(resp) -> Dict[str, Any]:
    """
    Jira sometimes returns 204 No Content (empty body), especially for transitions.
    This helper avoids JSON parse errors.
    """
    # 204 = success with no content
    if resp.status_code == 204:
        return {"ok": True, "status_code": 204}

    text = (resp.text or "").strip()
    if not text:
        return {"ok": True, "status_code": resp.status_code}

    # Try parse JSON; if fails, return raw text
    try:
        return resp.json()
    except Exception:
        return {"ok": True, "status_code": resp.status_code, "raw_text": text}


def _build_url(endpoint: str, use_agile_api: bool) -> str:
    cfg = get_jira_config()
    base_api_path = "/rest/agile/1.0" if use_agile_api else "/rest/api/3"
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    return f"{cfg.base_url}{base_api_path}{endpoint}"


def jira_api_get(
    endpoint: str,
    *,
    log_prefix: str | None = None,
    use_agile_api: bool = False,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    cfg = get_jira_config()
    url = _build_url(endpoint, use_agile_api)

    r = requests.get(
        url,
        auth=HTTPBasicAuth(cfg.email, cfg.api_token),
        headers={"Accept": "application/json"},
        params=params,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Jira GET error {r.status_code}: {r.text}")
    return r.json()


def jira_api_post(
    endpoint: str,
    *,
    log_prefix: str | None = None,
    use_agile_api: bool = False,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    cfg = get_jira_config()
    url = _build_url(endpoint, use_agile_api)

    r = requests.post(
        url,
        auth=HTTPBasicAuth(cfg.email, cfg.api_token),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        params=params,
        json=json_body,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Jira POST error {r.status_code}: {r.text}")
    # return r.json()
    return _safe_json_response(r)

