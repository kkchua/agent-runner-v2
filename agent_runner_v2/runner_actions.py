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
from .actions.submit_comfyui import submit_comfyui
from .actions.validate_delivery_docs import validate_delivery_docs

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Action registry — name → function
# ---------------------------------------------------------------------------

ACTION_REGISTRY: dict[str, Callable] = {
    "submit_comfyui": submit_comfyui,
    "validate_delivery_docs": validate_delivery_docs,
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
