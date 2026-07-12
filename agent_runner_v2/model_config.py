"""Model alias and coder-role resolver for the agent runner."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .runtime_context import RUNNER_ROOT


_MAPPING_CACHE: dict[Path, dict[str, Any]] = {}
_ROLE_CACHE: dict[Path, dict[str, dict[str, Any]]] = {}


def _runner_root() -> Path:
    return Path(RUNNER_ROOT)


def _mapping_path() -> Path:
    return _runner_root() / "model_mapping.json"


def _normalize_path(path: Path | str | None) -> Path:
    return Path(path) if path else _mapping_path()


def _load_json(path: Path) -> dict[str, Any]:
    if path in _MAPPING_CACHE:
        return _MAPPING_CACHE[path]
    if not path.exists():
        payload: dict[str, Any] = {}
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
    _MAPPING_CACHE[path] = payload
    return payload


def load_model_mapping(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load coder aliases from the configured model mapping file."""
    payload = _load_json(_normalize_path(path))
    return dict(payload.get("coder_aliases", {}))


def resolve_coder(name: str, *, mapping_path: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a coder alias into a full invocation config."""
    aliases = load_model_mapping(path=mapping_path)
    return aliases.get(name)


def coder_roles_path(bundle_root: Path | str | None = None) -> Path | None:
    """Return the highest-precedence coder role registry path."""
    candidates: list[Path] = []
    if bundle_root:
        root = Path(bundle_root)
        candidates.extend([root / "coder_roles.json", root / "config" / "coder_roles.json"])
    candidates.append(_runner_root() / "coder_roles.json")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def load_coder_roles(bundle_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load effective coder roles, overlaying bundle-local roles on global roles."""
    global_path = _runner_root() / "coder_roles.json"
    cache_key = coder_roles_path(bundle_root) or global_path
    if cache_key in _ROLE_CACHE:
        return dict(_ROLE_CACHE[cache_key])

    roles: dict[str, dict[str, Any]] = {}
    if global_path.exists():
        roles.update(_load_json(global_path).get("roles", {}))

    if bundle_root:
        local_path = Path(bundle_root) / "coder_roles.json"
        if local_path.exists():
            roles.update(_load_json(local_path).get("roles", {}))

    _ROLE_CACHE[cache_key] = roles
    return dict(roles)


def resolve_coder_role(role_name: str, *, bundle_root: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a semantic coder role into its alias/config wrapper."""
    return load_coder_roles(bundle_root=bundle_root).get(role_name)


def resolve_role_alias(role_name: str, *, bundle_root: Path | str | None = None) -> str | None:
    """Resolve a role name into the underlying coder alias name."""
    role = resolve_coder_role(role_name, bundle_root=bundle_root)
    if role is None:
        return None
    alias = str(role.get("alias") or "").strip()
    return alias or None


def get_api_key(coder_config: dict[str, Any]) -> str | None:
    """Retrieve the API key for a coder config from environment variables."""
    env_key = coder_config.get("openai_api_key_env")
    if env_key:
        return os.environ.get(env_key)
    return None
