import json
import os
from datetime import datetime, timezone

REQUEST_LOG_PATH = os.getenv("REQUEST_LOG_PATH", "/tmp/helixdesk_requests.jsonl")


def append_request_log(entry: dict) -> None:
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(REQUEST_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass
