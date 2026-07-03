from __future__ import annotations

"""Workflow bundle loading and bootstrap helpers."""

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

from .bundle_taxonomy import (
    DEFAULT_BUNDLE_PROFILE,
    DEFAULT_DOMAIN_BUNDLE,
    bundle_manifest,
    bundle_manifest_path,
)
from .runtime_context import DEFAULT_RUNNER_HOME, PACKAGE_ROOT


GLOBAL_RUNNER_HOME = Path.home() / DEFAULT_RUNNER_HOME
BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"


def bundles_root() -> Path:
    return GLOBAL_RUNNER_HOME / "bundles"


def core_bundles_root() -> Path:
    return bundles_root() / "core"


def domain_bundles_root() -> Path:
    return bundles_root() / "domains"


def workflow_bundles_root() -> Path:
    return bundles_root() / "workflows"


def config_path(workspace_root: Path) -> Path:
    return GLOBAL_RUNNER_HOME / "config.json"


def workflows_root(workspace_root: Path) -> Path:
    return global_workflows_root()


def workflow_root(workspace_root: Path, workflow_name: str) -> Path:
    return workflows_root(workspace_root) / workflow_name


def global_workflows_root() -> Path:
    return GLOBAL_RUNNER_HOME / "workflows"


def global_workflow_root(workflow_name: str) -> Path:
    return global_workflows_root() / workflow_name


def resolve_workflow_root(workspace_root: Path, workflow_name: str, *, config: dict | None = None) -> Path:
    workflow_cfg_map = (config or {}).get("workflows") or {}
    workflow_cfg = workflow_cfg_map.get(workflow_name) or {}
    workflow_path = workflow_cfg.get("path")
    if workflow_path:
        return (workspace_root / workflow_path).resolve()

    global_root = global_workflow_root(workflow_name)
    if global_root.exists():
        return global_root.resolve()

    return global_workflow_root(workflow_name).resolve()


def load_project_config(workspace_root: Path) -> dict:
    path = config_path(workspace_root)
    if not path.exists():
        return {
            "default_workflow": "default",
            "workflows": {},
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
    workflow_cfg = workflow_cfg_map.get(workflow_name) or {}
    wf_root = resolve_workflow_root(workspace_root, workflow_name, config=config)
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


def seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
    """Copy the bootstrap workflow template set into the target global workflow location."""
    wf_root = target_root / workflow_name
    wf_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "template_groups.py",
        "job_schema.json",
        "llm_response_schema.json",
        "model_mapping.json",
        "usage_schema.json",
    ):
        shutil.copy2(BOOTSTRAP_ROOT / name, wf_root / name)
    prompts_src = BOOTSTRAP_ROOT / "prompts"
    prompts_dst = wf_root / "prompts"
    if prompts_dst.exists():
        shutil.rmtree(prompts_dst)
    shutil.copytree(prompts_src, prompts_dst)
    return wf_root


def init_workspace(
    workspace_root: Path,
    workflow_name: str = "default",
    *,
    domain: str = DEFAULT_DOMAIN_BUNDLE,
    bundle_profile: str = DEFAULT_BUNDLE_PROFILE,
) -> dict:
    workspace_root = workspace_root.resolve()
    runner_home = GLOBAL_RUNNER_HOME
    runner_home.mkdir(parents=True, exist_ok=True)
    (runner_home / "jobs").mkdir(parents=True, exist_ok=True)
    (runner_home / "logs").mkdir(parents=True, exist_ok=True)
    (runner_home / "runtime").mkdir(parents=True, exist_ok=True)
    bundles_dir = runner_home / "bundles"
    bundles_dir.mkdir(parents=True, exist_ok=True)
    core_dir = bundles_dir / "core"
    domain_dir = bundles_dir / "domains"
    workflow_dir = bundles_dir / "workflows"
    core_dir.mkdir(parents=True, exist_ok=True)
    domain_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    workflows_dir = global_workflows_root()
    workflows_dir.mkdir(parents=True, exist_ok=True)
    wf_root = seed_workflow_bundle(workflows_dir, workflow_name="example")

    (core_dir / "current").mkdir(parents=True, exist_ok=True)
    (domain_dir / domain / "current").mkdir(parents=True, exist_ok=True)
    (workflow_dir / workflow_name / "current").mkdir(parents=True, exist_ok=True)

    manifest = bundle_manifest(workflow_name=workflow_name, domain=domain, profile=bundle_profile)
    manifest_path = bundle_manifest_path(runner_home)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    config = load_project_config(workspace_root)
    config.setdefault("workflows", {})
    if not config.get("default_workflow"):
        config["default_workflow"] = workflow_name
    config["bundle_profile"] = bundle_profile
    config["bundle_domain"] = domain
    config["bundle_manifest"] = str(manifest_path.relative_to(runner_home).as_posix())
    save_project_config(workspace_root, config)
    return {
        "workspace_root": str(workspace_root),
        "runner_home": str(runner_home),
        "workflow_name": workflow_name,
        "bundle_profile": bundle_profile,
        "bundle_domain": domain,
        "bundle_manifest": str(manifest_path),
        "workflow_root": str(wf_root),
        "config_path": str(config_path(workspace_root)),
    }
