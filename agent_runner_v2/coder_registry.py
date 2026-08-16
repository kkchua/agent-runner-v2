"""Coder connection, semantic role, and role-policy resolver for the agent runner."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .exceptions import ConfigurationError, NotFoundError
from .runtime_context import RUNNER_ROOT


_JSON_CACHE: dict[Path, dict[str, Any]] = {}


def _runner_root() -> Path:
    """Return the runner root path from runtime context."""
    return Path(RUNNER_ROOT)


def _workflow_registry_root(bundle_root: Path | str | None = None) -> Path:
    """Return the workflow registry root path.

    Args:
        bundle_root: Bundle root path to derive registry from.

    Returns:
        Path to workflow _registry directory.

    Raises:
        ConfigurationError: If bundle_root is not provided.
    """
    if not bundle_root:
        raise ConfigurationError("bundle_root is required to resolve workflow registry root")
    return Path(bundle_root).resolve().parent / "_registry"


def _runtime_registry_root() -> Path:
    """Return the runtime registry root path under runner home."""
    return _runner_root() / "_registry"


def _load_json(path: Path) -> dict[str, Any]:
    """Load and cache a JSON file.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON dict, or empty dict if file doesn't exist.
    """
    if path in _JSON_CACHE:
        return _JSON_CACHE[path]
    if not path.exists():
        payload: dict[str, Any] = {}
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
    _JSON_CACHE[path] = payload
    return payload


def _registry_file(
    filename: str,
    *,
    bundle_root: Path | str | None = None,
) -> Path:
    """Resolve a registry file path with fallback.

    Checks workflow registry first, then runtime registry.

    Args:
        filename: Registry filename (e.g., coder_connections.json).
        bundle_root: Optional bundle root for workflow registry.

    Returns:
        Path to registry file (existing file or fallback).
    """
    candidates: list[Path] = []
    try:
        workflow_registry = _workflow_registry_root(bundle_root)
        candidates.append(workflow_registry / filename)
    except ConfigurationError:
        pass  # No bundle_root provided, skip workflow registry
    candidates.append(_runtime_registry_root() / filename)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_coder_connections(bundle_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load coder connections from registry.

    Args:
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Dict mapping connection names to connection configs.
    """
    payload = _load_json(
        _registry_file("coder_connections.json", bundle_root=bundle_root),
    )
    return dict(payload.get("connections", {}))


def load_role_policies(bundle_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load role policies from registry.

    Args:
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Dict mapping policy names to policy configs.
    """
    payload = _load_json(
        _registry_file("role_policies.json", bundle_root=bundle_root),
    )
    return dict(payload.get("role_policies", {}))


def coder_roles_path(bundle_root: Path | str | None = None) -> Path:
    """Return the path to coder_roles.json registry file.

    Args:
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Path to coder_roles.json file.

    Raises:
        NotFoundError: If coder_roles.json is not found in any registry.
    """
    path = _registry_file("coder_roles.json", bundle_root=bundle_root)
    if not path.exists():
        raise NotFoundError(f"coder_roles.json not found in registry (checked bundle: {bundle_root})")
    return path


def load_coder_roles(bundle_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load coder roles from registry.

    Args:
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Dict mapping role names to role configs.
    """
    payload = _load_json(_registry_file("coder_roles.json", bundle_root=bundle_root))
    return dict(payload.get("roles", {}))


def resolve_connection(connection_name: str, *, bundle_root: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a named connection configuration.

    Args:
        connection_name: Connection name to look up.
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Connection config dict, or None if not found.
    """
    return load_coder_connections(bundle_root=bundle_root).get(connection_name)


def resolve_role_policy(policy_name: str, *, bundle_root: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a named role policy.

    Args:
        policy_name: Policy name to look up.
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Policy config dict, or None if not found.
    """
    return load_role_policies(bundle_root=bundle_root).get(policy_name)


def resolve_coder_role(role_name: str, *, bundle_root: Path | str | None = None) -> dict[str, Any] | None:
    """Resolve a named coder role configuration.

    Args:
        role_name: Role name to look up.
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Role config dict, or None if not found.
    """
    return load_coder_roles(bundle_root=bundle_root).get(role_name)


def _normalize_base_url(raw_url: str) -> str:
    """Normalize a base URL by stripping trailing slashes and lowercasing.

    Args:
        raw_url: URL string to normalize.

    Returns:
        Normalized URL string.
    """
    value = str(raw_url or "").strip()
    if not value:
        return ""
    try:
        parts = urlsplit(value)
    except ValueError:
        return value.rstrip("/")
    normalized_path = parts.path.rstrip("/") or parts.path
    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        normalized_path,
        parts.query,
        parts.fragment,
    ))


def _provider_key(*, role: dict[str, Any], connection_name: str | None, connection_profile: dict[str, Any] | None) -> str | None:
    """Compute a unique provider key for coder selection.

    Args:
        role: Coder role config dict.
        connection_name: Connection name.
        connection_profile: Connection profile dict.

    Returns:
        Provider key string like 'model_id@base_url', or None.
    """
    model_id = str(role.get("model_id") or role.get("model") or "").strip()
    if not connection_profile:
        return connection_name or None

    base_url = _normalize_base_url(str(connection_profile.get("openai_base_url") or ""))
    if model_id and base_url:
        return f"{model_id}@{base_url}"
    return connection_name or None


def _effective_model(role: dict[str, Any], connection_profile: dict[str, Any] | None) -> str:
    """Compute the effective model string for coder invocation.

    Applies model_format transformation if configured.

    Args:
        role: Coder role config dict.
        connection_profile: Connection profile dict.

    Returns:
        Model string for API invocation.
    """
    model_id = str(role.get("model_id") or "").strip()
    if not model_id:
        return ""
    if not connection_profile:
        return model_id
    model_format = str(connection_profile.get("model_format") or "model_id").strip()
    if model_format == "provider/model_id":
        provider_prefix = str(connection_profile.get("provider_prefix") or "").strip()
        if not provider_prefix:
            raise ValueError("Connection requires provider_prefix for provider/model_id formatting.")
        return f"{provider_prefix}/{model_id}"
    return model_id


def resolve_effective_coder(
    *,
    role_name: str,
    bundle_root: Path | str | None = None,
) -> dict[str, Any]:
    """Resolve a coder role to an effective coder configuration.

    Combines role, connection, and model settings into a single config
    dict suitable for coder invocation.

    Args:
        role_name: Coder role name to resolve.
        bundle_root: Optional bundle root for workflow registry lookup.

    Returns:
        Dict with coder, model, connection, and auth settings.

    Raises:
        ValueError: If role, connection, or model is invalid or missing.
    """
    role = resolve_coder_role(role_name, bundle_root=bundle_root)
    if role is None:
        raise ValueError(f"Unknown coder role: {role_name!r}")

    role_payload = dict(role)
    coder = str(role_payload.get("coder") or "").strip()
    if not coder:
        raise ValueError(f"Coder role {role_name!r} is missing coder configuration.")

    connection_name = str(role_payload.get("connection") or "").strip() or None
    model_id = str(role_payload.get("model_id") or role_payload.get("model") or "").strip()
    if not model_id:
        raise ValueError(f"Coder role {role_name!r} is missing model_id.")

    if coder == "codex":
        if connection_name:
            raise ValueError(f"Codex role {role_name!r} must not define a connection.")
        connection_profile = None
    else:
        if not connection_name:
            raise ValueError(f"Coder role {role_name!r} requires a connection.")
        connection_profile = resolve_connection(connection_name, bundle_root=bundle_root)
        if connection_profile is None:
            raise ValueError(f"Unknown connection {connection_name!r} for role {role_name!r}.")
        supported = [str(item).strip() for item in list(connection_profile.get("supported_coders") or [])]
        if coder not in supported:
            raise ValueError(
                f"Coder {coder!r} is not supported by connection {connection_name!r}. Supported: {supported}"
            )

    model = _effective_model(role_payload, connection_profile)
    provider_family = None
    provider_key = None
    if isinstance(connection_profile, dict):
        provider_family = str(connection_profile.get("provider") or connection_name or "").strip() or None
        provider_key = _provider_key(
            role=role_payload,
            connection_name=connection_name,
            connection_profile=connection_profile,
        )
    resolved: dict[str, Any] = {
        "role_name": role_name,
        "coder": coder,
        "connection": connection_name,
        "connection_profile": dict(connection_profile) if isinstance(connection_profile, dict) else None,
        "model_id": model_id,
        "model": model,
        "provider_family": provider_family,
        "provider_key": provider_key,
    }
    if isinstance(connection_profile, dict):
        for key in ("auth_type", "openai_api_key_env", "openai_base_url"):
            value = connection_profile.get(key)
            if value:
                resolved[key] = value
    return resolved


def get_api_key(coder_config: dict[str, Any]) -> str | None:
    """Retrieve an API key for a resolved coder config from environment variables."""
    env_key = coder_config.get("openai_api_key_env")
    if env_key:
        return os.environ.get(env_key)
    return None
