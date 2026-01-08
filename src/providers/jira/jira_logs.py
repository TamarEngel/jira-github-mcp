"""
Jira Logging Module
Writes JSON payloads to log files with timestamped filenames.
"""

import json
import os
from datetime import datetime
from typing import Any

def write_log(prefix: str, payload: Any) -> str:
    """
    Write a JSON payload to a timestamped log file.
    
    Args:
        prefix: Log filename prefix (e.g., 'jira-search')
        payload: Data to serialize as JSON
    
    Returns:
        str: Full path to the created log file
    """
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    name = f"{prefix}-{datetime.now().isoformat(timespec='seconds').replace(':','-')}.json"
    path = os.path.join(logs_dir, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return path
