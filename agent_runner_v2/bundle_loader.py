from __future__ import annotations

"""Workflow bundle loading and bootstrap helpers."""

import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

from .bundle_taxonomy import (
    CORE_BUNDLE_NAME,
    DEFAULT_BUNDLE_PROFILE,
    DEFAULT_DOMAIN_BUNDLE,
    bundle_manifest,
    bundle_manifest_path,
)
from .bundle_governance import (
    generate_bundle_governance_adapters,
    load_bundle_governance,
)
from .constants import all_artifact_keys
from .doc_paths import system_doc_rel
from .runtime_context import DEFAULT_RUNNER_HOME, PACKAGE_ROOT
from .workflow_packages.loader import (
    bundle_to_template_group_dict,
    load_workflow_package,
)


GLOBAL_RUNNER_HOME = Path.home() / DEFAULT_RUNNER_HOME
BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"
BOOTSTRAP_SOURCE_ROOT = Path(system_doc_rel())
PACKAGE_BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "bundles" / CORE_BUNDLE_NAME / "current"
PACKAGED_BOOTSTRAP_EXCLUDE_PATTERNS = (
    "*-bootstrap-change-log.md",
    "*-bootstrap-validation.md",
    "*-bootstrap-summary.md",
    "*.meta.json",
)
PACKAGED_BOOTSTRAP_EXCLUDED_WORKFLOWS = {
    "00_core_governance_bootstrap_v1",
}


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


def _reset_tree(target_root: Path) -> None:
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)


def _tree_has_files(root: Path) -> bool:
    if not root.exists():
        return False
    return any(path.is_file() for path in root.rglob("*"))


def _cleanup_packaged_bootstrap(root: Path) -> None:
    for pattern in PACKAGED_BOOTSTRAP_EXCLUDE_PATTERNS:
        for candidate in root.rglob(pattern):
            if candidate.is_file():
                candidate.unlink()


def _copy_plugin_workflows_to_bootstrap(
    plugin_root: Path,
    bootstrap_wf_root: Path,
) -> list[Path]:
    """Copy plugin workflow packages from *plugin_root* into bootstrap workflows/default/.

    Each subdirectory containing a ``workflow.toml`` manifest is copied as-is
    (preserving ``workflow.toml``, ``prompts/``, ``actions.py``,
    ``context_extensions.py``, etc.).

    Returns the list of destination paths that were copied.
    """
    if not plugin_root.is_dir():
        return []

    copied: list[Path] = []
    for candidate in sorted(plugin_root.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        pkg_name = candidate.name
        if pkg_name in PACKAGED_BOOTSTRAP_EXCLUDED_WORKFLOWS:
            stale_dest = bootstrap_wf_root / pkg_name
            if stale_dest.exists():
                shutil.rmtree(stale_dest)
            continue
        _generate_bundle_governance_docs(candidate)
        dest = bootstrap_wf_root / pkg_name
        _replace_tree(candidate, dest)
        _generate_bundle_governance_docs(dest)
        copied.append(dest)

    return copied


def _copy_shared_registry(
    registry_root: Path,
    target_workflow_root: Path,
) -> Path | None:
    """Copy shared workflow registry folder into the target workflow root."""
    if not registry_root.is_dir():
        return None
    dest = target_workflow_root / "_registry"
    _replace_tree(registry_root, dest)
    return dest


def _discover_template_groups_from_packages(workflow_root: Path) -> dict[str, dict]:
    template_groups: dict[str, dict] = {}
    if not workflow_root.is_dir():
        return template_groups

    for candidate in sorted(workflow_root.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        bundle = load_workflow_package(candidate)
        template_groups[bundle.name] = bundle_to_template_group_dict(bundle)

    return template_groups


def _build_workflow_module_from_packages(workflow_root: Path, workflow_name: str) -> ModuleType:
    template_groups = _discover_template_groups_from_packages(workflow_root)
    if not template_groups:
        raise FileNotFoundError(
            f"No workflow packages found under {workflow_root}. Expected one or more "
            "subdirectories containing workflow.toml."
        )

    module = ModuleType(f"agent_runner_v2.workflow.{workflow_name}")
    module.__file__ = str(workflow_root)
    module.TEMPLATE_GROUPS = template_groups
    module.ARTIFACT_KEYS = all_artifact_keys()
    return module


def _generate_bundle_governance_docs(bundle_root: Path) -> dict[str, str]:
    governance = load_bundle_governance(bundle_root)
    if governance is None:
        return {}
    rendered = generate_bundle_governance_adapters(
        governance,
        bundle_name=bundle_root.name,
        bundle_label=bundle_root.name,
    )
    return {name: str(path) for name, path in rendered.items()}


def publish_bootstrap_bundle(
    workspace_root: Path,
    *,
    source_root: Path | None = None,
    package_root: Path | None = None,
    plugin_workflows_root: Path | None = None,
) -> dict:
    workspace_root = workspace_root.resolve()
    source_root = (source_root or bootstrap_source_root(workspace_root)).resolve()
    package_root = (package_root or package_bootstrap_root()).resolve()
    plugin_workflows_root = (plugin_workflows_root or workspace_root / "workflows").resolve()
    shared_registry_root = (workspace_root / "workflows" / "_registry").resolve()

    # 1. Copy governance docs when present; otherwise create an empty packaged
    # bootstrap root so workflow package publishing can still proceed.
    source_docs_included = source_root.exists()
    if source_docs_included:
        _replace_tree(source_root, package_root)
        _cleanup_packaged_bootstrap(package_root)
    else:
        _reset_tree(package_root)

    # 2. Rebuild bootstrap workflows/default/ from repo-root workflows/
    bootstrap_wf_root = BOOTSTRAP_ROOT
    _reset_tree(bootstrap_wf_root)
    copied_registry = _copy_shared_registry(shared_registry_root, bootstrap_wf_root)
    copied = _copy_plugin_workflows_to_bootstrap(plugin_workflows_root, bootstrap_wf_root)

    publish_manifest = {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "source_docs_included": source_docs_included,
        "shared_registry_copied": bool(copied_registry),
        "plugin_workflows_copied": [p.name for p in copied],
    }
    (package_root / "bootstrap_publish_manifest.json").write_text(
        json.dumps(publish_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "package_bootstrap_root": str(package_root),
        "bundle_name": CORE_BUNDLE_NAME,
        "source_docs_included": source_docs_included,
        "shared_registry_copied": bool(copied_registry),
        "plugin_workflows_copied": [p.name for p in copied],
        "plugin_governance_docs_generated": {
            p.name: _generate_bundle_governance_docs(p) for p in copied
        },
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
    wf_root = resolve_workflow_root(workspace_root, workflow_name, config=config)
    return _build_workflow_module_from_packages(wf_root, workflow_name)


def seed_workflow_bundle(target_root: Path, workflow_name: str = "example") -> Path:
    """Copy the entire bootstrap workflows/default/ tree into the target global workflow location.

    This is a wholesale copy — ``bootstrap/workflows/default/`` already contains
    legacy files (``template_groups.py``, schemas), prompt templates, and any
    plugin workflow packages published via ``publish_bootstrap_bundle()``.
    """
    wf_root = target_root / workflow_name
    if wf_root.exists():
        shutil.rmtree(wf_root)
    shutil.copytree(BOOTSTRAP_ROOT, wf_root)
    return wf_root


def seed_workflow_packages(workspace_root: Path, workflow_name: str = "default") -> list[Path]:
    """Copy plugin workflow packages from the repo into the global runner home.

    Scans ``<workspace_root>/workflows/`` for directories that contain a
    ``workflow.toml`` manifest and copies each one into the active workflow
    bundle at ``%USERPROFILE%/.ukbe-runner/workflows/<workflow_name>/<name>/``.

    This is the plugin-package analogue of ``seed_workflow_bundle()``.
    """
    repo_packages_dir = (workspace_root / "workflows").resolve()
    if not repo_packages_dir.is_dir():
        return []

    # Plugin packages live inside the active workflow bundle directory,
    # alongside template_groups.py — e.g. workflows/default/<pkg_name>/
    bundle_root = global_workflow_root(workflow_name)
    bundle_root.mkdir(parents=True, exist_ok=True)
    _copy_shared_registry((workspace_root / "workflows" / "_registry").resolve(), bundle_root)
    seeded: list[Path] = []

    for candidate in sorted(repo_packages_dir.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        pkg_name = candidate.name
        dest = bundle_root / pkg_name
        _replace_tree(candidate, dest)
        _generate_bundle_governance_docs(dest)
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

    # Seed the example workflow bundle (copied from bootstrap/workflows/default/)
    wf_root = seed_workflow_bundle(workflows_dir, workflow_name="example")

    # Also seed plugin workflow packages from repo into the example bundle
    seeded_plugins = seed_workflow_packages(workspace_root, workflow_name="example")

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
        "plugin_workflows_seeded": sorted(
            d.name for d in wf_root.iterdir()
            if d.is_dir() and (d / "workflow.toml").is_file()
        ),
        "config_path": str(config_path(workspace_root)),
        "config_example_path": str(config_example_dst) if config_example_dst.exists() else None,
    }
