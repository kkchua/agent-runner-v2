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
from .actions.prepare_delivery_scaffold import prepare_delivery_scaffold
from .actions.scan_repo_codebase import scan_repo_codebase
from .actions.submit_comfyui import submit_comfyui
from .actions.sync_codebase_docs import sync_codebase_docs
from .actions.sync_system_docs import sync_system_docs
from .actions.validate_codebase_docs import validate_codebase_docs
from .actions.validate_delivery_docs import validate_delivery_docs
from .actions.validate_architecture_site import validate_architecture_site
from .actions.validate_stakeholder_site import validate_stakeholder_site
from .actions.validate_developer_site import validate_developer_site
from .actions.validate_operator_site import validate_operator_site
from .actions.validate_tester_site import validate_tester_site
from .actions.validate_user_site import validate_user_site
from .actions.validate_system_docs import validate_system_docs
from .actions.execute_t2i import execute_t2i
from .actions.execute_i2v import execute_i2v
from .actions.execute_voiceover import execute_voiceover
from .actions.assemble_video import assemble_video
from .actions.publish_architecture_site import publish_architecture_site
from .actions.generate_site import generate_site
from .actions.generate_site_pdf import generate_site_pdf
from .actions.archive_previous_version import archive_previous_version

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Action registry — name → function
# ---------------------------------------------------------------------------

ACTION_REGISTRY: dict[str, Callable] = {
    "copy_artifact": copy_artifact,
    "finalize_bootstrap": finalize_bootstrap,
    "generate_site": generate_site,
    "generate_site_pdf": generate_site_pdf,
    "archive_previous_version": archive_previous_version,
    "promote_artifact": promote_artifact,
    "promote_init": promote_init,
    "prepare_delivery_scaffold": prepare_delivery_scaffold,
    "scan_repo_codebase": scan_repo_codebase,
    "submit_comfyui": submit_comfyui,
    "sync_codebase_docs": sync_codebase_docs,
    "sync_system_docs": sync_system_docs,
    "validate_codebase_docs": validate_codebase_docs,
    "validate_delivery_docs": validate_delivery_docs,
    "validate_architecture_site": validate_architecture_site,
    "validate_stakeholder_site": validate_stakeholder_site,
    "validate_developer_site": validate_developer_site,
    "validate_operator_site": validate_operator_site,
    "validate_tester_site": validate_tester_site,
    "validate_user_site": validate_user_site,
    "validate_system_docs": validate_system_docs,
    "execute_t2i": execute_t2i,
    "execute_i2v": execute_i2v,
    "execute_voiceover": execute_voiceover,
    "assemble_video": assemble_video,
    "publish_architecture_site": publish_architecture_site,
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

    Raises:
        KeyError — if action_name is not in the registry.
        Exception — action-specific failures (caller routes to failure).
    """
    fn = ACTION_REGISTRY.get(action_name)
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


def get_registered_actions() -> list[str]:
    """Return sorted list of registered action names."""
    return sorted(ACTION_REGISTRY.keys())
