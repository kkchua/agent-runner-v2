from __future__ import annotations

"""Process-local runtime context for the standalone agent runner."""

from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_RUNNER_HOME = ".ukbe-runner"
DEFAULT_WORKFLOW_NAME = "default"


@dataclass(frozen=True)
class RuntimeContext:
    workspace_root: Path
    runner_home: Path
    workflow_name: str
    workflow_root: Path
    workflow_module: ModuleType | None
    delivery_root: Path | None  # override root for delivery scaffold artifacts


_CTX = RuntimeContext(
    workspace_root=Path.cwd().resolve(),
    runner_home=Path.cwd().resolve() / DEFAULT_RUNNER_HOME,
    workflow_name=DEFAULT_WORKFLOW_NAME,
    workflow_root=PACKAGE_ROOT,
    workflow_module=None,
    delivery_root=None,
)


class PathProxy:
    """Lightweight Path-like proxy that resolves lazily from current context."""

    def __init__(self, factory: Callable[[], Path]):
        self._factory = factory

    def _path(self) -> Path:
        return self._factory()

    def __truediv__(self, other: object) -> Path:
        return self._path() / other  # type: ignore[arg-type]

    def __rtruediv__(self, other: object) -> Path:
        return Path(other) / self._path()

    def __fspath__(self) -> str:
        return str(self._path())

    def __str__(self) -> str:
        return str(self._path())

    def __repr__(self) -> str:
        return f"PathProxy({self._path()!r})"

    def __getattr__(self, name: str) -> Any:
        return getattr(self._path(), name)


def set_context(
    *,
    workspace_root: Path,
    workflow_name: str | None = None,
    workflow_root: Path | None = None,
    workflow_module: ModuleType | None = None,
    delivery_root: Path | None = None,
) -> RuntimeContext:
    """Set process-local runtime context and return it."""
    global _CTX
    workspace_root = workspace_root.resolve()
    runner_home = workspace_root / DEFAULT_RUNNER_HOME
    if workflow_name is None:
        workflow_name = _CTX.workflow_name
    if workflow_root is None:
        workflow_root = _CTX.workflow_root
    if delivery_root is not None:
        delivery_root = delivery_root.resolve()
    ctx = RuntimeContext(
        workspace_root=workspace_root,
        runner_home=runner_home,
        workflow_name=workflow_name,
        workflow_root=workflow_root.resolve(),
        workflow_module=workflow_module,
        delivery_root=delivery_root,
    )
    _CTX = ctx
    return ctx


def get_context() -> RuntimeContext:
    return _CTX


def get_workspace_root() -> Path:
    return _CTX.workspace_root


def get_runner_home() -> Path:
    return _CTX.runner_home


def get_jobs_root() -> Path:
    return _CTX.runner_home / "jobs"


def get_workflow_root() -> Path:
    return _CTX.workflow_root


def get_workflow_module() -> ModuleType | None:
    return _CTX.workflow_module


def set_workflow_module(module: ModuleType) -> None:
    set_context(
        workspace_root=_CTX.workspace_root,
        workflow_name=_CTX.workflow_name,
        workflow_root=_CTX.workflow_root,
        workflow_module=module,
        delivery_root=_CTX.delivery_root,
    )


def get_delivery_root() -> Path | None:
    return _CTX.delivery_root


def set_delivery_root(root: Path | None) -> None:
    set_context(
        workspace_root=_CTX.workspace_root,
        workflow_name=_CTX.workflow_name,
        workflow_root=_CTX.workflow_root,
        workflow_module=_CTX.workflow_module,
        delivery_root=root,
    )


def resolve_artifact_root() -> Path:
    """Return the root for resolving artifact paths.

    For delivery scaffold workflows, returns delivery_root if set.
    For all other workflows, returns workspace_root.
    """
    if _CTX.delivery_root is not None:
        return _CTX.delivery_root
    return _CTX.workspace_root


PROJECT_ROOT = PathProxy(get_workspace_root)
RUNNER_HOME = PathProxy(get_runner_home)
RUNNER_ROOT = PathProxy(get_workflow_root)
JOBS_ROOT = PathProxy(get_jobs_root)
DELIVERY_ROOT = PathProxy(lambda: get_delivery_root() or get_workspace_root())
ARTIFACT_ROOT = PathProxy(resolve_artifact_root)
