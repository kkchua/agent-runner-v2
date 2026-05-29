from __future__ import annotations

"""Workflow bundle loading and bootstrap helpers."""

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

from .runtime_context import DEFAULT_RUNNER_HOME, PACKAGE_ROOT


def config_path(workspace_root: Path) -> Path:
    return workspace_root / DEFAULT_RUNNER_HOME / "config.json"


def workflows_root(workspace_root: Path) -> Path:
    return workspace_root / DEFAULT_RUNNER_HOME / "workflows"


def workflow_root(workspace_root: Path, workflow_name: str) -> Path:
    return workflows_root(workspace_root) / workflow_name


def load_project_config(workspace_root: Path) -> dict:
    path = config_path(workspace_root)
    if not path.exists():
        return {
            "default_workflow": "default",
            "workflows": {
                "default": {
                    "path": str(workflow_root(workspace_root, "default").relative_to(workspace_root)),
                }
            },
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_project_config(workspace_root: Path, config: dict) -> None:
    path = config_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def load_workflow_module(
    workspace_root: Path,
    workflow_name: str,
    *,
    config: dict | None = None,
) -> ModuleType:
    workflow_cfg_map = (config or {}).get("workflows") or {}
    if config is not None and workflow_name not in workflow_cfg_map:
        valid = ", ".join(sorted(workflow_cfg_map)) or "<none>"
        raise ValueError(f"Unknown workflow {workflow_name!r}. Available workflows: {valid}")
    workflow_cfg = workflow_cfg_map.get(workflow_name) or {}
    workflow_path = workflow_cfg.get("path") or str(workflow_root(workspace_root, workflow_name).relative_to(workspace_root))
    wf_root = (workspace_root / workflow_path).resolve()
    module_path = wf_root / "template_groups.py"
    if not module_path.exists():
        raise FileNotFoundError(
            f"Workflow bundle not found at {module_path}. Run init first or create the bundle manually."
        )
    spec = importlib.util.spec_from_file_location(
        f"agent_runner_v2.workflow.{workflow_name}",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load workflow bundle from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_workflow_bundle(workspace_root: Path, workflow_name: str = "default") -> Path:
    """Copy the bundled workflow template set into the target workspace."""
    wf_root = workflow_root(workspace_root, workflow_name)
    wf_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "template_groups.py",
        "job_schema.json",
        "llm_response_schema.json",
        "model_mapping.json",
        "usage_schema.json",
    ):
        shutil.copy2(PACKAGE_ROOT / name, wf_root / name)
    prompts_src = PACKAGE_ROOT / "prompts"
    prompts_dst = wf_root / "prompts"
    if prompts_dst.exists():
        shutil.rmtree(prompts_dst)
    shutil.copytree(prompts_src, prompts_dst)
    return wf_root


def init_workspace(workspace_root: Path, workflow_name: str = "default") -> dict:
    workspace_root = workspace_root.resolve()
    runner_home = workspace_root / DEFAULT_RUNNER_HOME
    runner_home.mkdir(parents=True, exist_ok=True)
    (runner_home / "jobs").mkdir(parents=True, exist_ok=True)
    (runner_home / "logs").mkdir(parents=True, exist_ok=True)
    workflows_dir = runner_home / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    wf_root = seed_workflow_bundle(workspace_root, workflow_name=workflow_name)
    config = load_project_config(workspace_root)
    config.setdefault("workflows", {})
    if not config.get("default_workflow"):
        config["default_workflow"] = workflow_name
    config["workflows"][workflow_name] = {
        "path": str(wf_root.relative_to(workspace_root)),
    }
    save_project_config(workspace_root, config)
    return {
        "workspace_root": str(workspace_root),
        "runner_home": str(runner_home),
        "workflow_name": workflow_name,
        "workflow_root": str(wf_root),
        "config_path": str(config_path(workspace_root)),
    }
