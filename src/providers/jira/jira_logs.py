import json
import os
from datetime import datetime
from typing import Any

def write_log(prefix: str, payload: Any) -> str:
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    name = f"{prefix}-{datetime.now().isoformat(timespec='seconds').replace(':','-')}.json"
    path = os.path.join(logs_dir, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return path
