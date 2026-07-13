from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any


def safe_relative_to(path: Path, base: Path) -> str:
    """Safely compute relative path, falling back to os.path.relpath on Windows."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        try:
            return os.path.relpath(path, base)
        except ValueError:
            return str(path)


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")
