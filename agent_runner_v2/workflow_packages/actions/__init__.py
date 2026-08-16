"""Pluggable action decorator and registry for workflow packages.

Usage
-----
    from agent_runner_v2.workflow_packages.actions import action

    @action("my_custom_action")
    def my_custom_action(*, context, state, step_cfg, project_root):
        # ... implementation ...
        return ActionResult(status="APPROVED", ...)

Actions registered via the decorator are automatically collected when a
workflow package's ``actions.py`` module is loaded, and the runner
dispatches to them before falling back to the global ``ACTION_REGISTRY``.
"""

from __future__ import annotations

from typing import Any, Callable

from ...action_result import ActionResult

# Type signature that every action function must match.
ActionFn = Callable[..., ActionResult]

# Global registry for decorator-registered actions.
# Key = action name (str), value = the action function.
REGISTERED_ACTIONS: dict[str, ActionFn] = {}


def action(name: str | None = None) -> Callable[[ActionFn], ActionFn]:
    """Decorator that registers a function as a runner action.

    Parameters
    ----------
    name :
        The action name used in ``workflow.toml`` ``action = "..."`` entries.
        Defaults to the function's ``__name__`` when omitted.

    Examples
    --------
    .. code-block:: python

        @action("validate_system_docs")
        def validate_system_docs(*, context, state, step_cfg, project_root):
            ...
    """
    def decorator(fn: ActionFn) -> ActionFn:
        action_name = name if name is not None else fn.__name__
        REGISTERED_ACTIONS[action_name] = fn
        return fn
    return decorator


def get_registered_actions() -> dict[str, ActionFn]:
    """Return a copy of all decorator-registered actions."""
    return dict(REGISTERED_ACTIONS)


def clear_registered_actions() -> None:
    """Clear all decorator-registered actions (useful in tests)."""
    REGISTERED_ACTIONS.clear()
