"""Model alias resolver for the agent runner.

Loads ``model_mapping.json`` from the runner root and resolves coder
aliases (e.g. ``"qwen-deepseek"``) into full invocation configs.
Plain coder names (``"claude"``, ``"codex"``, ``"qwen"``) pass
through unchanged.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .runtime_context import RUNNER_ROOT

# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------
_MAPPING: dict[str, dict[str, Any]] | None = None
_MAPPING_PATH: Path | None = None


def _runner_root() -> Path:
    return Path(RUNNER_ROOT)


def _mapping_path() -> Path:
    return _runner_root() / "model_mapping.json"


def _project_mapping_path() -> Path:
    """Project-level model_mapping.json — takes precedence over runner root."""
    try:
        from .runtime_context import PROJECT_ROOT
        return PROJECT_ROOT / ".ukbe-runner" / "model_mapping.json"
    except ImportError:
        return _runner_root() / "model_mapping.json"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model_mapping(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load the model mapping file.

    Resolution order:
    1. Explicit *path* argument (if given)
    2. Project root: PROJECT_ROOT/.ukbe-runner/model_mapping.json
    3. Runner root: RUNNER_ROOT/model_mapping.json (fallback)

    Results are cached for the lifetime of the process.
    """
    global _MAPPING, _MAPPING_PATH

    if _MAPPING is not None and _MAPPING_PATH is not None:
        return _MAPPING

    if path:
        resolved = Path(path)
    else:
        # Project-level first, runner-level fallback
        project_path = _project_mapping_path()
        if project_path.exists():
            resolved = project_path
        else:
            resolved = _mapping_path()

    _MAPPING_PATH = resolved

    if not resolved.exists():
        _MAPPING = {}
        return _MAPPING

    _MAPPING = json.loads(resolved.read_text(encoding="utf-8")).get("coder_aliases", {})
    return _MAPPING


def resolve_coder(name: str, *, mapping_path: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a coder name into a full invocation config.

    If *name* matches a key in ``coder_aliases``, returns the config dict.
    Otherwise returns ``None`` — the caller should treat *name* as a
    plain coder identifier (``"claude"``, ``"codex"``, ``"qwen"``).
    """
    aliases = load_model_mapping(path=mapping_path)
    return aliases.get(name)


def get_api_key(coder_config: dict[str, Any]) -> str | None:
    """Retrieve the API key for a coder config from environment variables."""
    env_key = coder_config.get("openai_api_key_env")
    if env_key:
        return os.environ.get(env_key)
    return None
