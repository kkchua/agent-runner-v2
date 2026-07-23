#!/usr/bin/env python3
"""
runner_actions.py — Registry and dispatch for non-coder step actions.

Design:
- Action steps skip LLM invocation entirely.
- Each action is a plain Python function with a standard signature.
- The runner calls execute() which dispatches to the registered function.
- Actions write their own meta.json sidecar and return a StepResult.

Adding a new action:
1. Write function in agent_runner_v2/actions/my_action.py
2. Import and register in ACTION_REGISTRY below
3. Set "action": "my_action" in the step config in template_groups.py
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from .action_result import ActionResult
from .actions.finalize_bootstrap import finalize_bootstrap
from .actions.copy_artifact import copy_artifact
from .actions.promote_artifact import promote_artifact
from .actions.promote_init import promote_init
from .actions.scan_repo_codebase import scan_repo_codebase
from .actions.sdlc_shared_actions import create_backup, generate_sync_log, commit_changes
from .actions.sync_codebase_docs import sync_codebase_docs
from .actions.sync_system_docs import sync_system_docs
from .actions.validate_codebase_docs import validate_codebase_docs
from .actions.step_completion import step_completion

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Action registry — name → function
# ---------------------------------------------------------------------------

ACTION_REGISTRY: dict[str, Callable] = {
    "copy_artifact": copy_artifact,
    "promote_artifact": promote_artifact,
    "promote_init": promote_init,
    "scan_repo_codebase": scan_repo_codebase,
    "create_backup": create_backup,
    "generate_sync_log": generate_sync_log,
    "commit_changes": commit_changes,
    "sync_codebase_docs": sync_codebase_docs,
    "sync_system_docs": sync_system_docs,
    "validate_codebase_docs": validate_codebase_docs,
    "finalize_bootstrap": finalize_bootstrap,
    "step_completion": step_completion,
}


def execute(
    *,
    action_name: str,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    step: str,
    project_root: Path,
) -> ActionResult:
    """Dispatch to a registered action function.

    Resolution order:
    1. ``step_cfg["_workflow_bundle"].custom_actions`` — package-local actions.
    2. ``ACTION_REGISTRY`` — globally registered actions.

    Raises:
        KeyError — if action_name is not found in either registry.
        Exception — action-specific failures (caller routes to failure).
    """
    fn = _resolve_action_fn(action_name, step_cfg)
    if fn is None:
        available = ", ".join(sorted(ACTION_REGISTRY.keys()))
        raise KeyError(
            f"Unknown runner action '{action_name}'. "
            f"Registered actions: {available}"
        )

    logger.info(f"[runner_actions] executing action '{action_name}' for step '{step}'")
    print(
        f"[runner_actions] step={step} action={action_name} status=STARTING",
        flush=True,
    )

    result = fn(
        context=context,
        state=state,
        step_cfg=step_cfg,
        project_root=project_root,
    )

    print(
        f"[runner_actions] step={step} action={action_name} status=COMPLETE "
        f"status_value={result.status}",
        flush=True,
    )

    return result


def _resolve_action_fn(
    action_name: str, step_cfg: dict
) -> Callable | None:
    """Resolve an action function, checking package-local actions first."""
    # 1. Package-local actions (decorator-registered in workflow package's actions.py)
    bundle = step_cfg.get("_workflow_bundle") if step_cfg else None
    if bundle is not None:
        package_actions = getattr(bundle, "custom_actions", {}) or {}
        fn = package_actions.get(action_name)
        if fn is not None:
            return fn
    # 2. Fall back to global registry
    return ACTION_REGISTRY.get(action_name)


def get_registered_actions() -> list[str]:
    """Return sorted list of registered action names."""
    return sorted(ACTION_REGISTRY.keys())
