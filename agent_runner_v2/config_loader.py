from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_runner_config() -> dict[str, Any]:
    """Load the single global runner config from ~/.ukbe-runner/config.json."""
    path = Path.home() / ".ukbe-runner" / "config.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}
