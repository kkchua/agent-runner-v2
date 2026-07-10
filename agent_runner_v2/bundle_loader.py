from __future__ import annotations

"""Workflow bundle loading and bootstrap helpers."""

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

from .bundle_taxonomy import (
    CORE_BUNDLE_NAME,
    DEFAULT_BUNDLE_PROFILE,
    DEFAULT_DOMAIN_BUNDLE,
    bundle_manifest,
    bundle_manifest_path,
)
from .doc_paths import system_doc_rel
from .runtime_context import DEFAULT_RUNNER_HOME, PACKAGE_ROOT


GLOBAL_RUNNER_HOME = Path.home() / DEFAULT_RUNNER_HOME
BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"
BOOTSTRAP_SOURCE_ROOT = Path(system_doc_rel())
PACKAGE_BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "bundles" / CORE_BUNDLE_NAME / "current"


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


def package_bootstrap_root() -> Path:
    return PACKAGE_BOOTSTRAP_ROOT


def global_bootstrap_root() -> Path:
    return bundles_root() / CORE_BUNDLE_NAME / "current"


def bootstrap_source_root(workspace_root: Path) -> Path:
    return (workspace_root / BOOTSTRAP_SOURCE_ROOT).resolve()


def _replace_tree(source_root: Path, target_root: Path) -> None:
    if not source_root.exists():
        raise FileNotFoundError(f"Source tree does not exist: {source_root}")
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, target_root)


def _tree_has_files(root: Path) -> bool:
    if not root.exists():
        return False
    return any(path.is_file() for path in root.rglob("*"))


def publish_bootstrap_bundle(
    workspace_root: Path,
    *,
    source_root: Path | None = None,
    package_root: Path | None = None,
) -> dict:
    workspace_root = workspace_root.resolve()
    source_root = (source_root or bootstrap_source_root(workspace_root)).resolve()
    package_root = (package_root or package_bootstrap_root()).resolve()
    _replace_tree(source_root, package_root)
    return {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "package_bootstrap_root": str(package_root),
        "bundle_name": CORE_BUNDLE_NAME,
    }


def install_bootstrap_bundle(
    workspace_root: Path,
    *,
    package_root: Path | None = None,
    runner_home: Path | None = None,
) -> dict:
    workspace_root = workspace_root.resolve()
    package_root = (package_root or package_bootstrap_root()).resolve()
    runner_home = (runner_home or GLOBAL_RUNNER_HOME).resolve()
    if not _tree_has_files(package_root):
        source_root = bootstrap_source_root(workspace_root)
        if source_root.exists():
            publish_bootstrap_bundle(
                workspace_root,
                source_root=source_root,
                package_root=package_root,
            )
    if not _tree_has_files(package_root):
        raise FileNotFoundError(
            f"Packaged bootstrap bundle is missing or empty: {package_root}. "
            "Run bootstrap-publish first or install a package build that includes the bundle."
        )
    global_root = runner_home / "bundles" / CORE_BUNDLE_NAME / "current"
    _replace_tree(package_root, global_root)
    return {
        "workspace_root": str(workspace_root),
        "package_bootstrap_root": str(package_root),
        "global_bootstrap_root": str(global_root),
        "bundle_name": CORE_BUNDLE_NAME,
    }


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


def seed_workflow_packages(workspace_root: Path) -> list[Path]:
    """Copy plugin workflow packages from the repo into the global runner home.

    Scans ``<workspace_root>/workflows/`` for directories that contain a
    ``workflow.toml`` manifest and copies each one to
    ``%USERPROFILE%/.ukbe-runner/workflows/<name>/``.

    This is the plugin-package analogue of ``seed_workflow_bundle()``.
    """
    repo_packages_dir = (workspace_root / "workflows").resolve()
    if not repo_packages_dir.is_dir():
        return []

    global_root = global_workflows_root()
    global_root.mkdir(parents=True, exist_ok=True)
    seeded: list[Path] = []

    for candidate in sorted(repo_packages_dir.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        pkg_name = candidate.name
        dest = global_root / pkg_name
        _replace_tree(candidate, dest)
        seeded.append(dest)

    return seeded


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

    bootstrap_install = install_bootstrap_bundle(
        workspace_root,
        runner_home=runner_home,
    )

    workflows_dir = global_workflows_root()
    workflows_dir.mkdir(parents=True, exist_ok=True)
    wf_root = seed_workflow_bundle(workflows_dir, workflow_name="example")

    # Seed plugin workflow packages (workflow.toml-based) from the repo
    seeded_packages = seed_workflow_packages(workspace_root)

    (core_dir / "current").mkdir(parents=True, exist_ok=True)
    (domain_dir / domain / "current").mkdir(parents=True, exist_ok=True)
    (workflow_dir / workflow_name / "current").mkdir(parents=True, exist_ok=True)

    # Copy config.json.example to runner home if it doesn't exist
    config_example_src = package_bootstrap_root() / "config.json.example"
    config_example_dst = runner_home / "config.json.example"
    if config_example_src.exists() and not config_example_dst.exists():
        shutil.copy2(config_example_src, config_example_dst)

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
        "bootstrap_install": bootstrap_install,
        "workflow_root": str(wf_root),
        "seeded_packages": [str(p) for p in seeded_packages],
        "config_path": str(config_path(workspace_root)),
        "config_example_path": str(config_example_dst) if config_example_dst.exists() else None,
    }
