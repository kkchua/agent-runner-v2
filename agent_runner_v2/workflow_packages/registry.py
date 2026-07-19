"""Workflow package registry — discovery, caching, and lookup.

The registry scans configured search paths for ``workflows/<name>/workflow.toml``
directories and returns ``WorkflowBundle`` instances on demand.
"""

from __future__ import annotations

from pathlib import Path
from typing import NoReturn

from .base import WorkflowBundle
from .loader import load_workflow_package


class WorkflowRegistry:
    """Directory of available workflow packages on local disk."""

    def __init__(self) -> None:
        self._search_paths: list[Path] = []
        self._bundles: dict[str, WorkflowBundle] = {}
        self._loaded: bool = False

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def add_search_path(self, path: str | Path) -> None:
        """Register a directory to scan for workflow packages.

        Each direct subdirectory that contains ``workflow.toml`` is treated
        as a workflow package.

        Parameters
        ----------
        path :
            An absolute or relative filesystem path. Relative paths are
            resolved against the current working directory at call-time.
        """
        resolved = Path(path).resolve()
        if resolved.is_dir():
            self._search_paths.append(resolved)

    def set_search_paths(self, paths: list[str | Path]) -> None:
        """Replace all search paths (clears previous paths)."""
        self._search_paths = []
        self._loaded = False
        for p in paths:
            self.add_search_path(p)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self) -> None:
        """Scan all search paths and index discovered workflow packages.

        This is idempotent and fast — it only checks for ``workflow.toml``
        existence, it does **not** parse every manifest eagerly.
        """
        self._bundles.clear()
        for search_path in self._search_paths:
            if not search_path.is_dir():
                continue
            for candidate in sorted(search_path.iterdir()):
                if not candidate.is_dir():
                    continue
                manifest = candidate / "workflow.toml"
                if manifest.is_file():
                    try:
                        bundle = load_workflow_package(candidate)
                        self._bundles[bundle.name] = bundle
                    except (ValueError, FileNotFoundError) as exc:
                        # Log and skip malformed packages
                        import logging  # noqa: PLC0415

                        logging.getLogger(__name__).warning(
                            "Skipping workflow package at %s: %s",
                            candidate,
                            exc,
                        )
        self._loaded = True

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> WorkflowBundle:
        """Return a previously discovered workflow bundle.

        Raises
        ------
        KeyError
            If no workflow named *name* was found during ``discover()``.
        """
        if not self._loaded:
            self.discover()
        try:
            return self._bundles[name]
        except KeyError:
            return _raise_not_found(name, list(self._bundles))

    def list_workflows(self) -> list[str]:
        """Return sorted names of all discovered workflow packages."""
        if not self._loaded:
            self.discover()
        return sorted(self._bundles)

    def has(self, name: str) -> bool:
        """Check whether a workflow package with *name* exists."""
        if not self._loaded:
            self.discover()
        return name in self._bundles

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        search_paths: list[str | Path] | None = None,
    ) -> WorkflowRegistry:
        """Factory: build a registry, add paths, and discover."""
        registry = cls()
        if search_paths:
            registry.set_search_paths(search_paths)
        registry.discover()
        return registry

    @classmethod
    def from_project_root(
        cls,
        project_root: str | Path,
        *,
        additional_paths: list[str | Path] | None = None,
    ) -> WorkflowRegistry:
        """Factory: scan ``<project_root>/workflows/`` plus any extra paths."""
        registry = cls()
        registry.add_search_path(Path(project_root) / "workflows")
        if additional_paths:
            for p in additional_paths:
                registry.add_search_path(p)
        registry.discover()
        return registry


def _raise_not_found(name: str, available: list[str]) -> NoReturn:
    msg = f"Unknown workflow package: '{name}'."
    if available:
        msg += f" Available: {', '.join(available)}"
    raise KeyError(msg)


# ---------------------------------------------------------------------------
# Module-level convenience — process-wide singleton registry
# ---------------------------------------------------------------------------

_GLOBAL_REGISTRY: WorkflowRegistry | None = None


def get_global_registry() -> WorkflowRegistry:
    """Return the process-wide singleton registry (lazily created)."""
    global _GLOBAL_REGISTRY  # noqa: PLW0603
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = WorkflowRegistry()
    return _GLOBAL_REGISTRY


def set_global_registry(registry: WorkflowRegistry) -> None:
    """Replace the process-wide singleton registry."""
    global _GLOBAL_REGISTRY  # noqa: PLW0603
    _GLOBAL_REGISTRY = registry


def discover_workflow_package(
    name: str,
    *,
    project_root: str | Path | None = None,
    workflow_root: str | Path | None = None,
) -> WorkflowBundle | None:
    """Convenience: discover a single package by name.

    Runtime search path:
    1. ``<workflow_root>/<name>/`` — global runner home workflow bundle directory
       (runtime source of truth; e.g. ``~/.ukbe-runner/workflows/default/``).
       This is the ONLY path used at runtime.
    2. ``<project_root>/workflows/<name>/`` — fallback for tests and direct
       invocation without ``workflow_root``.

    Returns ``None`` when the package is not found (no exception).
    """
    registry = get_global_registry()
    if workflow_root is not None:
        wf_root = Path(workflow_root).resolve()
        if wf_root.is_dir():
            registry.add_search_path(wf_root)
    if not registry._loaded:
        registry.discover()
    try:
        return registry.get(name)
    except KeyError:
        return None
