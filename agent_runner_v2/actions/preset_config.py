"""Merge implementation preset.json into a workflow's runtime config.

Provides :func:`merge_preset_into_config` — a reusable helper that any
workflow action can call to overlay the selected implementation's
``preset.json`` on top of the workspace config.

The platform injects ``IMPLEMENTATION_NAME`` and ``WORKFLOW_BUNDLE_ROOT``
into the action context automatically (see ``step_execution_runtime.py``).
This helper reads those keys, loads the preset, and merges its
``actions`` section over the config's ``actions`` section.

Usage::

    from agent_runner_v2.actions.preset_config import merge_preset_into_config

    config = _load_config(config_path)
    config = merge_preset_into_config(config, context)
    provider = config["actions"]["render_video"]
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def merge_preset_into_config(config: dict, context: dict) -> dict:
    """Merge implementation preset.json over a workflow config dict.

    Reads ``IMPLEMENTATION_NAME`` and ``WORKFLOW_BUNDLE_ROOT`` from
    *context*, loads ``impls/{impl_name}/preset.json`` from the bundle,
    and merges its ``actions`` section into ``config["actions"]``.

    If either key is missing or the preset file doesn't exist, the
    config is returned unchanged (no error).

    Parameters
    ----------
    config : dict
        Workflow config (typically loaded from workspace config.json).
        Must be mutable — it is updated in place and also returned.
    context : dict
        Action context dict (contains IMPLEMENTATION_NAME,
        WORKFLOW_BUNDLE_ROOT injected by the platform).

    Returns
    -------
    dict
        The (possibly modified) config dict.
    """
    impl_name = context.get("IMPLEMENTATION_NAME", "")
    bundle_root = context.get("WORKFLOW_BUNDLE_ROOT", "")
    if not impl_name or not bundle_root:
        return config

    preset_path = Path(bundle_root) / "impls" / impl_name / "preset.json"
    if not preset_path.is_file():
        logger.debug("No preset.json at %s — using workspace config as-is", preset_path)
        return config

    try:
        with open(preset_path, "r", encoding="utf-8") as f:
            preset = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load preset.json at %s: %s", preset_path, exc)
        return config

    preset_actions = preset.get("actions", {})
    if preset_actions:
        config.setdefault("actions", {}).update(preset_actions)
        logger.info(
            "Merged implementation preset '%s' into config: actions=%s",
            impl_name,
            preset_actions,
        )

    return config
