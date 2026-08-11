"""Workflow bundle loading and bootstrap management for agent_runner_v2.

This module handles the bootstrap lifecycle: publishing, installing, and
seeding workflow bundles to the global runner home (~/.ukbe-runner/).

Key responsibilities:
- Publish bootstrap bundles from repo to packaged distribution
- Install bootstrap bundles (Layer 1 foundation, Layer 2 platform)
- Seed workflow packages to global runner home
- Load workflow modules for execution
- Validate workflow bundles before publishing

The module supports both repo-local development workflows and pip-installed
production deployments, with fallback paths for each scenario.

Primary entry points: publish_bootstrap_bundle(), install_bootstrap_bundle(),
init_workspace()

Related: IMPL-20260422-04
"""
from __future__ import annotations

import datetime as dt
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
from .workflow_bundle_validator import WorkflowBundleValidationReport, validate_workflow_bundle_dir


GLOBAL_RUNNER_HOME = Path.home() / DEFAULT_RUNNER_HOME
BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"
BOOTSTRAP_SOURCE_ROOT = Path(system_doc_rel())
FOUNDATION_CURRENT_ROOT_REL = "docs/system/00_governance/foundation/current"
PLATFORM_CURRENT_ROOT_REL = "docs/system/00_governance/platform"
PACKAGE_BOOTSTRAP_ROOT = PACKAGE_ROOT / "bootstrap" / "bundles" / CORE_BUNDLE_NAME / "current"
PACKAGED_BOOTSTRAP_EXCLUDED_WORKFLOWS = {
    "00_core_governance_bootstrap_v1",
}


class WorkflowBundlePublishValidationError(RuntimeError):
    """Raised when repo-root workflow bundles fail preflight validation."""

    def __init__(self, reports: list[WorkflowBundleValidationReport]) -> None:
        self.reports = reports
        names = ", ".join(report.workflow_name for report in reports)
        super().__init__(f"Workflow bundle validation failed for: {names}")


def resolve_engine_repo_root() -> Path:
    """Resolve the engine repo root using the same logic as the daemon.

    Reads ``engine_version`` from ``~/.ukbe-runner/config.json``:
    - ``"SNAPSHOT"`` → use ``repo_root`` from config (the actual repo).
    - ``"v0.7.0"`` → use ``~/.ukbe-runner/engine/versions/v0.7.0/``.
    - empty → fall back to the pip-installed package root.

    Returns a path where ``agent_runner_v2/bootstrap/`` is always accessible.
    """
    from .config_loader import load_runner_config
    cfg = load_runner_config()
    version = (cfg.get("engine_version") or "").strip()
    if not version or version.upper() == "SNAPSHOT":
        repo_root_str = str(cfg.get("repo_root") or "").strip()
        if repo_root_str:
            candidate = Path(repo_root_str).resolve()
            if candidate.is_dir():
                return candidate
        return Path.cwd().resolve()
    global_dir = (Path.home() / ".ukbe-runner" / "engine" / "versions" / version).resolve()
    if global_dir.is_dir():
        return global_dir
    return Path.cwd().resolve()


def bundles_root() -> Path:
    """Return the global bundles root (~/.ukbe-runner/bundles/)."""
    return GLOBAL_RUNNER_HOME / "bundles"


def core_bundles_root() -> Path:
    """Return the core bundles root (~/.ukbe-runner/bundles/core/)."""
    return bundles_root() / "core"


def domain_bundles_root() -> Path:
    """Return the domain bundles root (~/.ukbe-runner/bundles/domains/)."""
    return bundles_root() / "domains"


def workflow_bundles_root() -> Path:
    """Return the workflow bundles root (~/.ukbe-runner/bundles/workflows/)."""
    return bundles_root() / "workflows"


def config_path(workspace_root: Path) -> Path:
    """Return the global config.json path (~/.ukbe-runner/config.json)."""
    return GLOBAL_RUNNER_HOME / "config.json"


def workflows_root(workspace_root: Path) -> Path:
    """Return the global workflows root (alias for global_workflows_root())."""
    return global_workflows_root()


def workflow_root(workspace_root: Path, workflow_name: str) -> Path:
    """Return the path to a specific workflow bundle directory."""
    return workflows_root(workspace_root) / workflow_name


def global_workflows_root() -> Path:
    """Return the global workflows root (~/.ukbe-runner/workflows/)."""
    return GLOBAL_RUNNER_HOME / "workflows"


def global_workflow_root(workflow_name: str) -> Path:
    """Return the path to a workflow bundle in the global runner home."""
    return global_workflows_root() / workflow_name


def package_bootstrap_root() -> Path:
    """Return the packaged bootstrap bundle root (from pip install)."""
    return PACKAGE_BOOTSTRAP_ROOT


def global_bootstrap_root() -> Path:
    """Return the installed bootstrap root in the global runner home."""
    return bundles_root() / CORE_BUNDLE_NAME / "current" / "foundation"


def bootstrap_source_root(workspace_root: Path) -> Path:
    """Return the bootstrap source root under docs/system/00_governance/bootstrap/."""
    return (workspace_root / BOOTSTRAP_SOURCE_ROOT).resolve()


def _replace_tree(source_root: Path, target_root: Path) -> None:
    """Replace target directory with source directory contents."""
    if not source_root.exists():
        raise FileNotFoundError(f"Source tree does not exist: {source_root}")
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, target_root)


def _reset_tree(target_root: Path) -> None:
    """Delete and recreate a directory (empty it)."""
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)


def _tree_has_files(root: Path) -> bool:
    """Check if a directory contains any files (recursively)."""
    if not root.exists():
        return False
    return any(path.is_file() for path in root.rglob("*"))


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
        dest = bootstrap_wf_root / pkg_name
        _replace_tree(candidate, dest)
        _generate_bundle_governance_docs(dest)
        copied.append(dest)

    return copied


def _discover_repo_workflow_bundle_dirs(plugin_root: Path) -> list[Path]:
    """Discover workflow bundle directories containing workflow.toml."""
    if not plugin_root.is_dir():
        return []
    return [
        candidate
        for candidate in sorted(plugin_root.iterdir())
        if candidate.is_dir() and (candidate / "workflow.toml").is_file()
    ]


def _validate_repo_workflow_bundles(plugin_root: Path) -> list[WorkflowBundleValidationReport]:
    """Validate all workflow bundles in the plugin root directory."""
    reports: list[WorkflowBundleValidationReport] = []
    for bundle_dir in _discover_repo_workflow_bundle_dirs(plugin_root):
        if bundle_dir.name in PACKAGED_BOOTSTRAP_EXCLUDED_WORKFLOWS:
            continue
        reports.append(validate_workflow_bundle_dir(bundle_dir))
    return reports


def _ensure_repo_workflow_bundles_valid(plugin_root: Path) -> list[WorkflowBundleValidationReport]:
    """Validate all bundles and raise if any are invalid."""
    reports = _validate_repo_workflow_bundles(plugin_root)
    invalid = [report for report in reports if not report.valid]
    if invalid:
        raise WorkflowBundlePublishValidationError(invalid)
    return reports


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
    """Scan a workflow root directory and build TEMPLATE_GROUPS dict from packages."""
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


def _build_workflow_module_from_packages(
    workflow_root: Path,
    workflow_name: str,
    *,
    workspace_root: Path | None = None,
) -> ModuleType:
    """Build a runtime workflow module from discovered workflow packages."""
    template_groups = _discover_template_groups_from_packages(workflow_root)
    repo_workflow_root = (workspace_root / "workflows").resolve() if workspace_root is not None else None
    if repo_workflow_root is not None and repo_workflow_root != workflow_root.resolve():
        template_groups.update(_discover_template_groups_from_packages(repo_workflow_root))
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
    """Generate bundle governance docs (AGENTS.md, CLAUDE.md, QWEN.md) for a workflow bundle."""
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
    """Publish the repo's bootstrap bundle for pip packaging and init.

    This copies workflow packages from ./workflows/ into the packaged bootstrap
    at agent_runner_v2/bootstrap/workflows/default/, which is the source that
    run-init.bat reads from to seed the global runner home.

    Returns a manifest dict with paths and validation results.
    """
    workspace_root = workspace_root.resolve()
    source_root = (source_root or bootstrap_source_root(workspace_root)).resolve()
    package_root = (package_root or package_bootstrap_root()).resolve()
    plugin_workflows_root = (plugin_workflows_root or workspace_root / "workflows").resolve()
    shared_registry_root = (workspace_root / "workflows" / "_registry").resolve()
    if not plugin_workflows_root.is_dir():
        raise FileNotFoundError(
            f"Required workflow source folder is missing: {plugin_workflows_root}. "
            "Expected repo-local workflow bundles under ./workflows."
        )
    validation_reports = _ensure_repo_workflow_bundles_valid(plugin_workflows_root)

    source_root.mkdir(parents=True, exist_ok=True)

    # Copy L1 foundation docs into the packaged bootstrap so pip-installed
    # users get governance docs without needing the repo checkout.
    foundation_src = (workspace_root / FOUNDATION_CURRENT_ROOT_REL).resolve()
    if foundation_src.is_dir() and _tree_has_files(foundation_src):
        foundation_dest = package_root / "foundation"
        if foundation_dest.exists():
            shutil.rmtree(foundation_dest)
        shutil.copytree(str(foundation_src), str(foundation_dest))

    # Copy L2 platform docs into the packaged bootstrap.
    platform_src = (workspace_root / PLATFORM_CURRENT_ROOT_REL).resolve()
    if platform_src.is_dir():
        platform_dest = package_root / "platform"
        if platform_dest.exists():
            shutil.rmtree(platform_dest)
        shutil.copytree(str(platform_src), str(platform_dest))

    # Copy workflows to bootstrap/workflows/default/ — this is what init reads
    bootstrap_wf_root = BOOTSTRAP_ROOT
    _reset_tree(bootstrap_wf_root)
    copied_registry = _copy_shared_registry(shared_registry_root, bootstrap_wf_root)
    copied = _copy_plugin_workflows_to_bootstrap(plugin_workflows_root, bootstrap_wf_root)

    publish_manifest = {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "package_bootstrap_root": str(package_root),
        "bootstrap_workflows_root": str(bootstrap_wf_root),
        "shared_registry_copied": bool(copied_registry),
        "plugin_workflows_copied": [p.name for p in copied],
    }
    package_root.mkdir(parents=True, exist_ok=True)
    (package_root / "bootstrap_publish_manifest.json").write_text(
        json.dumps(publish_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "package_bootstrap_root": str(package_root),
        "bootstrap_workflows_root": str(bootstrap_wf_root),
        "bundle_name": CORE_BUNDLE_NAME,
        "shared_registry_copied": bool(copied_registry),
        "plugin_workflows_copied": [p.name for p in copied],
        "validated_workflows": [report.workflow_name for report in validation_reports],
    }


def install_bootstrap_bundle(
    workspace_root: Path,
    *,
    runner_home: Path | None = None,
) -> dict:
    """Install Layer 1 foundation docs to the global runner home.

    Copies from either the repo bootstrap bundle or the packaged pip bundle.
    """
    workspace_root = workspace_root.resolve()
    runner_home = (runner_home or GLOBAL_RUNNER_HOME).resolve()
    repo_root = resolve_engine_repo_root()
    source_root = (repo_root / "agent_runner_v2" / "bootstrap" / "bundles" / CORE_BUNDLE_NAME / "current" / "foundation").resolve()
    if not source_root.is_dir() or not _tree_has_files(source_root):
        source_root = PACKAGE_BOOTSTRAP_ROOT / "foundation"
    if not source_root.is_dir() or not _tree_has_files(source_root):
        return {
            "workspace_root": str(workspace_root),
            "source_root": str(source_root),
            "skipped": True,
            "reason": "Layer 1 foundation docs not found — run bootstrap-publish first.",
        }
    current_root = runner_home / "bundles" / CORE_BUNDLE_NAME / "current"
    foundation_root = current_root / "foundation"
    if current_root.exists():
        _backup_workflow_folder(current_root)
    foundation_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(source_root), str(foundation_root), dirs_exist_ok=True)
    return {
        "workspace_root": str(workspace_root),
        "source_root": str(source_root),
        "global_bootstrap_root": str(foundation_root),
        "bundle_name": CORE_BUNDLE_NAME,
    }


def install_platform_bundle(
    workspace_root: Path,
    *,
    runner_home: Path | None = None,
) -> dict:
    """Install Layer 2 platform bundles to the global runner home.

    Scans ``docs/system/00_governance/platform/`` for platform subdirectories
    and copies each ``<platform>/current/`` tree to
    ``BUNDLE_ROOT/platform/<platform>/``.

    Args:
        workspace_root: Repository root directory.
        runner_home: Override for the global runner home path.

    Returns:
        Installation result dictionary with per-platform details.
    """
    workspace_root = workspace_root.resolve()
    runner_home = (runner_home or GLOBAL_RUNNER_HOME).resolve()
    repo_root = resolve_engine_repo_root()
    platform_root = (repo_root / "agent_runner_v2" / "bootstrap" / "bundles" / CORE_BUNDLE_NAME / "current" / "platform").resolve()
    bundle_root = runner_home / "bundles" / CORE_BUNDLE_NAME / "current" / "platform"

    if not platform_root.is_dir():
        packaged_platform = PACKAGE_BOOTSTRAP_ROOT / "platform"
        if packaged_platform.is_dir():
            platform_root = packaged_platform
        else:
            return {
                "workspace_root": str(workspace_root),
                "platform_root": str(platform_root),
                "installed": [],
                "skipped": True,
                "reason": "Layer 2 platform folder not found — run the Layer 2 workflow first.",
            }

    installed = []
    for platform_dir in sorted(platform_root.iterdir()):
        if not platform_dir.is_dir():
            continue
        current_dir = platform_dir / "current"
        if not current_dir.is_dir() or not _tree_has_files(current_dir):
            continue
        dest = bundle_root / platform_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(current_dir), str(dest), dirs_exist_ok=True)
        installed.append({
            "platform": platform_dir.name,
            "source": str(current_dir),
            "destination": str(dest),
        })

    return {
        "workspace_root": str(workspace_root),
        "platform_root": str(platform_root),
        "installed": installed,
        "skipped": len(installed) == 0,
        "reason": None if installed else "No platform subdirectories with current/ found.",
    }


def install_workflow_plugins(
    workspace_root: Path,
    *,
    runner_home: Path | None = None,
) -> dict:
    """Scan workflow folders for install.py scripts and execute them.

    Each workflow can optionally provide an install.py that implements
    install_workflow(project_root, runner_home) to handle its own
    global path installation.

    Args:
        workspace_root: Repository root directory.
        runner_home: Override for the global runner home path.

    Returns:
        Installation result dictionary with per-workflow details.
    """
    import importlib.util

    runner_home = (runner_home or GLOBAL_RUNNER_HOME).resolve()

    # Scan bootstrap/workflows/default/ for workflow packages
    bootstrap_wf_root = workspace_root / "agent_runner_v2" / "bootstrap" / "workflows" / "default"
    if not bootstrap_wf_root.is_dir():
        bootstrap_wf_root = workspace_root / "workflows"

    if not bootstrap_wf_root.is_dir():
        return {
            "workspace_root": str(workspace_root),
            "workflows_scanned": 0,
            "workflows_installed": 0,
            "installed": [],
            "skipped": True,
            "reason": "No workflow folder found.",
        }

    installed = []
    for workflow_dir in sorted(bootstrap_wf_root.iterdir()):
        if not workflow_dir.is_dir():
            continue
        install_script = workflow_dir / "install.py"
        if not install_script.is_file():
            continue

        # Import and call install_workflow()
        try:
            spec = importlib.util.spec_from_file_location(
                f"{workflow_dir.name}_install",
                install_script,
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module.__name__] = module
            spec.loader.exec_module(module)

            if hasattr(module, "install_workflow"):
                result = module.install_workflow(
                    project_root=workspace_root,
                    runner_home=runner_home,
                )
                installed.append({
                    "workflow": workflow_dir.name,
                    "result": result,
                })
            else:
                installed.append({
                    "workflow": workflow_dir.name,
                    "error": "install.py found but no install_workflow() function",
                })
        except Exception as e:
            installed.append({
                "workflow": workflow_dir.name,
                "error": str(e),
            })

    return {
        "workspace_root": str(workspace_root),
        "workflows_scanned": len([d for d in bootstrap_wf_root.iterdir() if d.is_dir()]),
        "workflows_installed": len(installed),
        "installed": installed,
        "skipped": len(installed) == 0,
        "reason": None if installed else "No workflows with install.py found.",
    }


def resolve_workflow_root(workspace_root: Path, workflow_name: str, *, config: dict | None = None) -> Path:
    """Resolve the workflow bundle root, preferring global path over project-local."""
    global_root = global_workflow_root(workflow_name)
    if global_root.exists():
        return global_root.resolve()

    return global_workflow_root(workflow_name).resolve()


def load_project_config(workspace_root: Path) -> dict:
    """Load the project config.json, returning defaults if not found."""
    path = config_path(workspace_root)
    if not path.exists():
        return {
            "default_workflow": "default",
            "workflows": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_project_config(workspace_root: Path, config: dict) -> None:
    """Save the project config.json with formatted JSON."""
    path = config_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def load_workflow_module(
    workspace_root: Path,
    workflow_name: str,
    *,
    config: dict | None = None,
) -> ModuleType:
    """Load and build a workflow module from the resolved workflow root."""
    wf_root = resolve_workflow_root(workspace_root, workflow_name, config=config)
    return _build_workflow_module_from_packages(
        wf_root,
        workflow_name,
        workspace_root=workspace_root,
    )


def _backup_workflow_folder(wf_root: Path) -> None:
    """Rename existing workflow folder to backup with format YYMMDDNN."""
    date_prefix = dt.datetime.now().strftime("%y%m%d")

    for seq in range(1, 100):
        backup_name = f"{wf_root.name}_{date_prefix}{seq:02d}"
        backup_path = wf_root.parent / backup_name
        if not backup_path.exists():
            wf_root.rename(backup_path)
            return

    raise RuntimeError(f"Cannot backup {wf_root}: sequence numbers 01-99 exhausted")


def seed_workflow_bundle(target_root: Path, workflow_name: str = "default") -> Path:
    """Copy the entire bootstrap workflows/default/ tree into the target global workflow location.

    This is a wholesale copy — ``bootstrap/workflows/default/`` already contains
    legacy files (``template_groups.py``, schemas), prompt templates, and any
    plugin workflow packages published via ``publish_bootstrap_bundle()``.
    """
    wf_root = target_root / workflow_name
    if wf_root.exists():
        _backup_workflow_folder(wf_root)
    shutil.copytree(BOOTSTRAP_ROOT, wf_root)
    return wf_root


def seed_workflow_packages(
    workspace_root: Path,
    workflow_name: str = "default",
    *,
    source_root: Path | None = None,
) -> list[Path]:
    """Copy published workflow packages into the global runner home.

    Init installs workflow bundles from the published bootstrap snapshot under
    docs/system/00_governance/bootstrap/workflows, not from repo authoring
    folders directly.
    """
    repo_packages_dir = (source_root or None)
    if repo_packages_dir is None:
        repo_root = resolve_engine_repo_root()
        repo_packages_dir = (repo_root / "agent_runner_v2" / "bootstrap" / "workflows" / "default").resolve()
    if not repo_packages_dir.is_dir():
        repo_packages_dir = BOOTSTRAP_ROOT
    if not repo_packages_dir.is_dir():
        return []
    _ensure_repo_workflow_bundles_valid(repo_packages_dir)

    # Plugin packages live inside the active workflow bundle directory,
    # alongside template_groups.py — e.g. workflows/default/<pkg_name>/
    bundle_root = global_workflow_root(workflow_name)
    bundle_root.mkdir(parents=True, exist_ok=True)
    _copy_shared_registry((repo_packages_dir / "_registry").resolve(), bundle_root)
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
    """Initialize the global runner home from the bootstrap bundle.

    Creates directory structure, installs L1 foundation and L2 platform docs,
    seeds workflow packages, and writes initial config files.

    Returns a dict with installation details.
    """
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

    platform_install = install_platform_bundle(
        workspace_root,
        runner_home=runner_home,
    )

    # Install workflow plugins (workflows with install.py)
    workflow_plugins_install = install_workflow_plugins(
        workspace_root,
        runner_home=runner_home,
    )

    workflows_dir = global_workflows_root()
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Seed the default workflow bundle (copied from bootstrap/workflows/default/)
    wf_root = seed_workflow_bundle(workflows_dir, workflow_name="default")

    # Seed published workflow packages from the bootstrap snapshot into the default bundle.
    seeded_plugins = seed_workflow_packages(workspace_root, workflow_name="default")

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
        "platform_install": platform_install,
        "workflow_plugins_install": workflow_plugins_install,
        "workflow_root": str(wf_root),
        "plugin_workflows_seeded": sorted(
            d.name for d in wf_root.iterdir()
            if d.is_dir() and (d / "workflow.toml").is_file()
        ),
        "config_path": str(config_path(workspace_root)),
        "config_example_path": str(config_example_dst) if config_example_dst.exists() else None,
    }
