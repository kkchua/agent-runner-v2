"""Scanner and lifecycle hook dispatcher for workflow extensions.

Discovers :class:`WorkflowExtensions` subclasses from each workflow
package's ``context_extensions.py`` and invokes their hook methods.

The scanner is triggered by CLI commands (``init``, ``run``), not at
import time.  Loaded extensions are cached so repeated lookups are free.

Backward compatibility: when a workflow's ``context_extensions.py`` does
not define a ``WorkflowExtensions`` subclass, the scanner falls back to
the legacy free-function ``build_context_extensions()`` pattern.
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any

from .extensions_base import WorkflowExtensions

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

# extension instance cache: workflow_name → WorkflowExtensions | None
_EXT_CACHE: dict[str, WorkflowExtensions | None] = {}

# module cache: ext_path_str → module (prevents double-import)
_MOD_CACHE: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _load_extension_module(ext_path: Path, cache_key: str) -> Any | None:
    """Import ``context_extensions.py`` and return the module (or None)."""
    if cache_key in _MOD_CACHE:
        return _MOD_CACHE[cache_key]

    if not ext_path.is_file():
        _MOD_CACHE[cache_key] = None
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            f"workflow_ext_{ext_path.parent.name}", ext_path
        )
        if spec is None or spec.loader is None:
            _MOD_CACHE[cache_key] = None
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MOD_CACHE[cache_key] = mod
        return mod
    except Exception:
        logger.exception("Failed to load context_extensions from %s", ext_path)
        _MOD_CACHE[cache_key] = None
        return None


def _find_extension_class(mod: Any) -> type[WorkflowExtensions] | None:
    """Find the first WorkflowExtensions subclass in *mod*."""
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, WorkflowExtensions)
            and attr is not WorkflowExtensions
        ):
            return attr
    return None


def get_extension(template_group: str) -> WorkflowExtensions | None:
    """Return the cached extension instance for a workflow.

    Searches the global workflow registry for the package, loads its
    ``context_extensions.py``, and finds the ``WorkflowExtensions``
    subclass.  Returns ``None`` when no subclass is found (the workflow
    uses the legacy free-function pattern or has no extensions).

    Parameters:
        template_group: Workflow package name (e.g. ``"sdlc_10_requirement_v1"``).

    Returns:
        A ``WorkflowExtensions`` instance, or ``None``.
    """
    if template_group in _EXT_CACHE:
        return _EXT_CACHE[template_group]

    # Resolve the context_extensions.py path from the registry
    from .registry import get_global_registry

    registry = get_global_registry()

    ext_path: Path | None = None

    # Try the registry first (workflow packages discovered at startup)
    if registry.has(template_group):
        bundle = registry.get(template_group)
        candidate = bundle.bundle_root / "context_extensions.py"
        if candidate.is_file():
            ext_path = candidate

    # Fallback: scan standard locations
    if ext_path is None:
        from ..runtime_context import get_workspace_root

        workspace = get_workspace_root()
        if workspace:
            candidate = Path(workspace) / "workflows" / template_group / "context_extensions.py"
            if candidate.is_file():
                ext_path = candidate

    if ext_path is None:
        _EXT_CACHE[template_group] = None
        return None

    mod = _load_extension_module(ext_path, str(ext_path))
    if mod is None:
        _EXT_CACHE[template_group] = None
        return None

    cls = _find_extension_class(mod)
    if cls is None:
        _EXT_CACHE[template_group] = None
        return None

    instance = cls()
    _EXT_CACHE[template_group] = instance
    return instance


def get_legacy_context_hook(template_group: str) -> Any | None:
    """Return the legacy free-function ``build_context_extensions`` (or None).

    This is the backward-compatibility path for workflows that have not
    yet migrated to the ``WorkflowExtensions`` base class.
    """
    from .registry import get_global_registry

    registry = get_global_registry()
    ext_path: Path | None = None

    if registry.has(template_group):
        bundle = registry.get(template_group)
        candidate = bundle.bundle_root / "context_extensions.py"
        if candidate.is_file():
            ext_path = candidate

    if ext_path is None:
        from ..runtime_context import get_workspace_root

        workspace = get_workspace_root()
        if workspace:
            candidate = Path(workspace) / "workflows" / template_group / "context_extensions.py"
            if candidate.is_file():
                ext_path = candidate

    if ext_path is None:
        return None

    mod = _load_extension_module(ext_path, str(ext_path))
    if mod is None:
        return None

    return getattr(mod, "build_context_extensions", None)


# ---------------------------------------------------------------------------
# Bulk scanners
# ---------------------------------------------------------------------------


def _all_discovered_extensions() -> dict[str, WorkflowExtensions]:
    """Return extensions for every discovered workflow that has one."""
    from .registry import get_global_registry

    registry = get_global_registry()
    result: dict[str, WorkflowExtensions] = {}

    for name in registry.list_workflows():
        ext = get_extension(name)
        if ext is not None:
            result[name] = ext

    return result


def scan_all(hook_name: str, **kwargs: Any) -> dict[str, Any]:
    """Call *hook_name* on every discovered workflow's Extensions class.

    Only workflows that define a ``WorkflowExtensions`` subclass are
    included.  Workflows without the new interface are silently skipped.

    Parameters:
        hook_name: Method name on ``WorkflowExtensions`` (e.g.
            ``"register_artifact_keys"``).
        **kwargs: Arguments forwarded to the hook method.

    Returns:
        Dict mapping workflow_name to the hook's return value.
    """
    results: dict[str, Any] = {}
    for name, ext in _all_discovered_extensions().items():
        method = getattr(ext, hook_name, None)
        if method is None:
            continue
        try:
            results[name] = method(**kwargs)
        except Exception:
            logger.exception(
                "Hook %s failed for workflow %s", hook_name, name
            )
    return results


def register_all_artifact_keys(*, job_id: str, mode: str) -> None:
    """Call ``register_artifact_keys()`` on all workflows.

    Merges results into the global ``ARTIFACT_PATHS`` dict in
    :mod:`constants`.
    """
    from ..constants import register_artifact_paths

    for name, paths in scan_all(
        "register_artifact_keys", job_id=job_id, mode=mode
    ).items():
        if isinstance(paths, dict):
            register_artifact_paths(paths)
        else:
            logger.warning(
                "register_artifact_keys() for %s returned %s, expected dict",
                name,
                type(paths).__name__,
            )


def init_all(*, workspace_root: Path, runner_home: Path) -> None:
    """Call ``init()`` on all workflows."""
    scan_all(
        "init", workspace_root=workspace_root, runner_home=runner_home
    )


# ---------------------------------------------------------------------------
# Cache management (for tests)
# ---------------------------------------------------------------------------


def clear_cache() -> None:
    """Clear all cached extensions and modules.

    Intended for test use only — production code should not need this.
    """
    _EXT_CACHE.clear()
    _MOD_CACHE.clear()
