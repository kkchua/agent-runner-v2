from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path
from types import ModuleType


def resolve_workflow_output_paths(
    *,
    template_group: str,
    job_id: str = "{job_id}",
    mode: str = "{mode}",
) -> dict[str, str]:
    module = _load_output_paths_module(template_group)
    if module is None or not hasattr(module, "build_output_paths"):
        return {}
    build_output_paths = getattr(module, "build_output_paths")
    output_paths = build_output_paths(job_id=job_id, mode=mode)
    if not isinstance(output_paths, dict):
        raise TypeError(
            f"{template_group}/output_paths.py build_output_paths() must return a dict."
        )
    return {str(key): str(value) for key, value in output_paths.items()}


@lru_cache(maxsize=None)
def _load_output_paths_module(template_group: str) -> ModuleType | None:
    for candidate in _output_paths_candidates(template_group):
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(
            f"agent_runner_v2.workflow_output_paths.{template_group}",
            candidate,
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def _output_paths_candidates(template_group: str) -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    return [
        repo_root / "workflows" / template_group / "output_paths.py",
        repo_root
        / "agent_runner_v2"
        / "bootstrap"
        / "workflows"
        / "default"
        / template_group
        / "output_paths.py",
    ]
