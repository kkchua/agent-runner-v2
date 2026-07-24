from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..config_loader import load_runner_config
from ..runtime_context import GLOBAL_RUNNER_HOME
from .models import ConsoleConfig, GlobalSettings, RepoEntry, WorkflowEntry


DEFAULT_CONSOLE_CONFIG_PATH = GLOBAL_RUNNER_HOME / "operator-console.json"


class ConsoleConfigError(RuntimeError):
    pass


def load_global_settings() -> GlobalSettings:
    cfg = load_runner_config()
    backend_url = str(cfg.get("backend_url") or "").strip()
    worker_id = str(cfg.get("worker_id") or "").strip()
    worker_label = str(cfg.get("worker_label") or "live").strip() or "live"
    missing: list[str] = []
    if not backend_url:
        missing.append("backend_url")
    if not worker_id:
        missing.append("worker_id")
    if missing:
        raise ConsoleConfigError(
            "Missing required global runner config value(s): "
            + ", ".join(missing)
            + f". Update {GLOBAL_RUNNER_HOME / 'config.json'}."
        )
    return GlobalSettings(
        backend_url=backend_url,
        worker_id=worker_id,
        worker_label=worker_label,
    )


def resolve_console_config_path(path: str | None = None) -> Path:
    configured = path or os.environ.get("AGENT_RUNNER_CONSOLE_CONFIG") or str(DEFAULT_CONSOLE_CONFIG_PATH)
    return Path(configured).expanduser().resolve()


def load_console_config(path: str | None = None) -> ConsoleConfig:
    config_path = resolve_console_config_path(path)
    if not config_path.exists():
        raise ConsoleConfigError(
            f"Console config file not found: {config_path}. "
            "Create a JSON file with 'repos' and 'workflows' arrays."
        )
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConsoleConfigError(f"Failed to parse console config {config_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConsoleConfigError(f"Console config must be a JSON object: {config_path}")
    repos = _parse_repos(payload.get("repos"), config_path)
    return ConsoleConfig(repos=repos)


def _parse_repos(value: Any, config_path: Path) -> tuple[RepoEntry, ...]:
    if not isinstance(value, list) or not value:
        raise ConsoleConfigError(f"'repos' must be a non-empty array in {config_path}")
    repos: list[RepoEntry] = []
    names: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ConsoleConfigError(f"'repos[{index}]' must be an object in {config_path}")
        name = str(item.get("name") or "").strip()
        path = str(item.get("path") or "").strip()
        worker_id = str(item.get("worker_id") or "").strip()
        if not name or not path:
            raise ConsoleConfigError(f"'repos[{index}]' requires non-empty 'name' and 'path' in {config_path}")
        normalized = Path(path).expanduser().resolve()
        if name in names:
            raise ConsoleConfigError(f"Duplicate repo name {name!r} in {config_path}")
        names.add(name)
        workflows = _parse_repo_workflows(item.get("workflows"), config_path, name)
        repos.append(RepoEntry(name=name, path=str(normalized), worker_id=worker_id, workflows=workflows))
    return tuple(repos)


def _parse_repo_workflows(value: Any, config_path: Path, repo_name: str) -> tuple[WorkflowEntry, ...]:
    if not isinstance(value, list) or not value:
        raise ConsoleConfigError(f"'repos[{repo_name}]' must have a non-empty 'workflows' array in {config_path}")
    workflows: list[WorkflowEntry] = []
    names: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ConsoleConfigError(f"'repos[{repo_name}].workflows[{index}]' must be an object in {config_path}")
        name = str(item.get("name") or "").strip()
        workflow_name = str(item.get("workflow_name") or "").strip()
        template_group = str(item.get("template_group") or "").strip() or None
        if not name or not workflow_name:
            raise ConsoleConfigError(
                f"'repos[{repo_name}].workflows[{index}]' requires non-empty 'name' and 'workflow_name' in {config_path}"
            )
        if name in names:
            raise ConsoleConfigError(f"Duplicate workflow name {name!r} in repo {repo_name!r} in {config_path}")
        names.add(name)
        workflows.append(
            WorkflowEntry(
                name=name,
                workflow_name=workflow_name,
                template_group=template_group,
            )
        )
    return tuple(workflows)
