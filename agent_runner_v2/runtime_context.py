from __future__ import annotations

"""Process-local runtime context for the standalone agent runner."""

import datetime as dt
from dataclasses import dataclass
import json
import tempfile
from pathlib import Path
from pathlib import PurePath
from types import ModuleType
from typing import Any, Callable


PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_RUNNER_HOME = ".ukbe-runner"
GLOBAL_RUNNER_HOME = Path.home().resolve() / DEFAULT_RUNNER_HOME
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
    runner_home=GLOBAL_RUNNER_HOME,
    workflow_name=DEFAULT_WORKFLOW_NAME,
    workflow_root=GLOBAL_RUNNER_HOME / "workflows" / DEFAULT_WORKFLOW_NAME,
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
    runner_home = GLOBAL_RUNNER_HOME
    if workflow_name is None:
        workflow_name = _CTX.workflow_name
    if workflow_root is None:
        workflow_root = GLOBAL_RUNNER_HOME / "workflows" / DEFAULT_WORKFLOW_NAME
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


def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
    """Resolve a path using the repo/runtime namespace convention.

    Convention:
    - `docs/...` and other repo-owned content resolve under the project root.
    - runtime job paths resolve under the runner jobs root.
    - absolute paths are returned unchanged.
    """
    path = Path(path_str)
    if path.is_absolute():
        return path

    normalized = path_str.replace("\\", "/")
    repo_prefixes = ("docs/", "archive/", "scripts/", "temp/")
    if normalized.startswith(repo_prefixes):
        base = project_root.resolve() if project_root is not None else get_workspace_root()
        return base / path

    if normalized.startswith(".ukbe-runner/"):
        runtime_root = runtime_root or get_runner_home()
        suffix = normalized[len(".ukbe-runner/"):]
        return runtime_root / Path(suffix)

    runtime_root = runtime_root or get_jobs_root()
    return runtime_root / path


def format_report_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> str:
    """Resolve repo/runtime paths for outward-facing result payloads."""
    raw = str(path_str or "").strip()
    if not raw:
        return raw

    path = Path(raw)
    if path.is_absolute():
        return str(path.resolve())

    normalized = raw.replace("\\", "/")
    if normalized.startswith(("docs/", "archive/", "scripts/", "temp/", ".ukbe-runner/")):
        return str(
            resolve_repo_or_runtime_path(
                raw,
                project_root=project_root,
                runtime_root=runtime_root,
            ).resolve()
        )
    return raw


def format_report_artifacts(
    artifacts: dict[str, Any],
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in dict(artifacts or {}).items():
        if value is None:
            normalized[str(key)] = None
            continue
        if isinstance(value, str):
            stripped = value.strip()
            normalized[str(key)] = (
                format_report_path(
                    stripped,
                    project_root=project_root,
                    runtime_root=runtime_root,
                )
                if stripped
                else ""
            )
            continue
        normalized[str(key)] = value
    return normalized


def repo_doc_root(*parts: str) -> Path:
    return get_workspace_root() / Path("docs").joinpath(*parts)


def system_doc_root(*parts: str) -> Path:
    return repo_doc_root("system", "00_governance", "bootstrap", *parts)


def codebase_doc_root(*parts: str) -> Path:
    return repo_doc_root("repo", "codebase", *parts)


def delivery_doc_root(*parts: str) -> Path:
    return repo_doc_root("repo", "delivery", *parts)


def architecture_site_root(*parts: str) -> Path:
    return repo_doc_root("repo", "site", "architecture", *parts)


def artifact_rel_to_meta_rel(artifact_rel: str) -> str:
    """Return the meta.json sibling path for a repo/runtime-relative artifact."""
    rel = str(artifact_rel or "").strip()
    if not rel:
        return ""
    p = PurePath(rel)
    return (p.parent / f"{p.stem}.meta.json").as_posix()


def write_meta_sidecar(
    meta_path_like: str | Path,
    *,
    status: str,
    remark: str,
    artifacts: dict,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write a v2 meta.json sidecar using the shared path resolver."""
    meta_path = resolve_repo_or_runtime_path(
        str(meta_path_like),
        project_root=project_root,
        runtime_root=runtime_root,
    )
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema_version": "v2",
        "coder_result": {
            "status": status,
            "remark": remark,
            "artifacts": artifacts,
            "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    }
    if extra:
        payload.update(extra)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=meta_path.parent, prefix=".tmp_", suffix=".json")
    try:
        with open(tmp_fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        Path(tmp_path).replace(meta_path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise
    return meta_path


def resolve_step_meta_rel(
    *,
    context: dict[str, str],
    state: dict,
    context_key: str,
    default_step: str,
) -> str:
    """Resolve the meta.json relative path for a step-owned artifact.

    The returned value is a job-relative path when runtime state is available,
    or the context-provided path when the workflow already injected one.
    """
    meta_rel = str(context.get(context_key) or "").strip()
    if meta_rel:
        return meta_rel

    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel:
        template_group = str(state.get("template_group") or "").strip()
        job_id = str(state.get("job_id") or "").strip()
        step = str(state.get("current_step") or default_step).strip()
        steps: list[str] = []
        bundle = get_workflow_module()
        if bundle is not None:
            group_cfg = getattr(bundle, "TEMPLATE_GROUPS", {}).get(template_group, {})
            steps = list(group_cfg.get("steps") or [])
        if steps and step in steps:
            step_index = steps.index(step) + 1
        else:
            step_index = 1
        if template_group and job_id:
            step_dir_rel = f"{template_group}/{job_id}/{step_index:02d}_{step}"

    return f"{step_dir_rel}/meta.json" if step_dir_rel else ""


PROJECT_ROOT = PathProxy(get_workspace_root)
RUNNER_HOME = PathProxy(get_runner_home)
RUNNER_ROOT = PathProxy(get_workflow_root)
JOBS_ROOT = PathProxy(get_jobs_root)
DELIVERY_ROOT = PathProxy(lambda: get_delivery_root() or get_workspace_root())
ARTIFACT_ROOT = PathProxy(resolve_artifact_root)
