"""Parse workflow.toml manifests and adapt them to the TEMPLATE_GROUPS dict format.

Usage
-----
    bundle = load_workflow_package(Path("workflows/my_workflow_v2"))
    group_dict = bundle_to_template_group_dict(bundle)
    # group_dict is now shaped exactly like
    # TEMPLATE_GROUPS["my_workflow_v1"] — the runner consumes it identically.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ..bundle_governance import load_bundle_governance
from .base import StepConfig, WorkflowBundle

# ---------------------------------------------------------------------------
# TOML support — prefer stdlib tomllib (3.11+), fall back to tomli
# ---------------------------------------------------------------------------
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


def load_workflow_package(package_dir: Path) -> WorkflowBundle:
    """Parse *package_dir/workflow.toml* and return a validated WorkflowBundle.

    Parameters
    ----------
    package_dir :
        Root directory of the workflow package (must contain ``workflow.toml``).

    Returns
    -------
    WorkflowBundle
        A frozen, validated bundle ready for adaptation or execution.

    Raises
    ------
    FileNotFoundError
        If ``workflow.toml`` is missing.
    ValueError
        If the manifest is structurally invalid or missing required fields.
    """
    manifest_path = package_dir / "workflow.toml"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Workflow package not found at {package_dir} — "
            f"no workflow.toml in that directory."
        )

    if tomllib is None:
        raise ImportError(
            "No TOML library available. Install tomli for Python < 3.11."
        )

    raw = manifest_path.read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))

    return _parse_bundle(data, manifest_path, package_dir)


# ---------------------------------------------------------------------------
# Internal — parse raw TOML dict into WorkflowBundle
# ---------------------------------------------------------------------------


def _parse_bundle(
    data: dict[str, Any],
    manifest_path: Path,
    bundle_root: Path,
) -> WorkflowBundle:
    wf = _get_section(data, "workflow")

    name = _require(wf, "name", str)
    version = str(wf.get("version", "1"))
    label = str(wf.get("label", name))
    job_prefix = _require(wf, "job_prefix", str)
    description = str(wf.get("description", ""))
    visibility = str(wf.get("visibility", ""))

    init = _get_section(wf, "init", optional=True) or {}
    init_step = str(init.get("step", "")) or _require(wf, "init_step", str)
    init_inputs: list[str] = list(init.get("inputs", wf.get("init_inputs", [])))
    default_max_rejects = int(wf.get("default_max_rejects", 3))

    # --- Steps -----------------------------------------------------------
    raw_steps: list[dict[str, Any]] = data.get("step", [])
    if not raw_steps:
        raise ValueError(f"workflow '{name}' has no [[step]] entries")

    step_configs: dict[str, StepConfig] = {}
    step_order: list[str] = []

    for i, raw in enumerate(raw_steps):
        step_name = _require(raw, "name", str, context=f"step index {i}")
        step_order.append(step_name)

        artifact = _get_section(raw, "artifacts", optional=True) or {}
        coder_sec = _get_section(raw, "coder", optional=True) or {}
        routing = _get_section(raw, "routing", optional=True) or {}

        sc = StepConfig(
            name=step_name,
            prompt_file=_opt_str(raw, "prompt"),
            action=_opt_str(raw, "action"),
            mode=_opt_str(raw, "mode"),
            produces=list(artifact.get("produces", [])),
            required_inputs=list(artifact.get("required_inputs", [])),
            optional_inputs=list(artifact.get("optional_inputs", [])),
            result_meta_key=_opt_str(artifact, "result_meta_key"),
            result_meta_key_from_context=_opt_str(
                artifact, "result_meta_key_from_context"
            ),
            target_artifact=_opt_str(artifact, "target_artifact"),
            edit_mode=_opt_str(artifact, "edit_mode"),
            immutable_inputs=list(artifact.get("immutable_inputs", [])),
            produced_document_status=artifact.get("produced_document_status"),
            coder_default=_opt_str(coder_sec, "default"),
            coder_allowed=list(coder_sec.get("allowed", [])),
            coder_role_policy=_opt_str(coder_sec, "role_policy"),
            coder_default_role=_opt_str(coder_sec, "default_role"),
            coder_allowed_roles=list(coder_sec.get("allowed_roles", [])),
            coder_must_differ=bool(coder_sec.get("must_differ", False)),
            on_approve=_opt_str(routing, "on_approve"),
            on_reject_refine=raw.get("on_reject_refine"),
            on_exhaust_replan=raw.get("on_exhaust_replan"),
            reject_code_routes=raw.get("reject_code_routes"),
            requires_human_approval_after=bool(
                raw.get("requires_human_approval_after", False)
                or artifact.get("requires_human_approval_after", False)
            ),
            loop_returns_to=_opt_str(raw, "loop_returns_to")
                or _opt_str(artifact, "loop_returns_to"),
            replan_returns_to=_opt_str(raw, "replan_returns_to")
                or _opt_str(artifact, "replan_returns_to"),
            enable_notifications=bool(raw.get("enable_notifications", False)),
            template_ref=raw.get("template_ref"),
            post_action=_opt_str(raw, "post_action"),
            extra={k: v for k, v in raw.items() if k not in _KNOWN_STEP_KEYS},
        )
        step_configs[step_name] = sc

    # --- Context extensions -----------------------------------------------
    context_ext_file = bundle_root / "context_extensions.py"
    context_ext_path: Path | None = context_ext_file if context_ext_file.is_file() else None

    # --- Optional bundle-level governance ---------------------------------
    governance = load_bundle_governance(bundle_root)

    # --- Package-local actions ------------------------------------------
    custom_actions = _load_package_actions(bundle_root)

    return WorkflowBundle(
        name=name,
        version=version,
        label=label,
        job_prefix=job_prefix,
        manifest_path=manifest_path,
        bundle_root=bundle_root.resolve(),
        steps=step_configs,
        step_order=step_order,
        init_step=init_step,
        init_inputs=init_inputs,
        default_max_rejects=default_max_rejects,
        context_extensions_path=context_ext_path,
        governance=governance,
        custom_actions=custom_actions,
        description=description,
        visibility=visibility,
    )


# ---------------------------------------------------------------------------
# Adapter — WorkflowBundle → TEMPLATE_GROUPS dict
# ---------------------------------------------------------------------------

# Keys that are allowed in step configs (everything else goes into "extra").
_STEP_DIRECT_KEYS = {
    "prompt_file", "action", "mode", "required_inputs", "optional_inputs",
    "produces", "result_meta_key", "result_meta_key_from_context",
    "target_artifact", "edit_mode", "immutable_inputs",
    "produced_document_status", "coder", "enable_notifications",
    "on_reject_refine", "on_exhaust_replan", "reject_code_routes",
    "requires_human_approval_after", "loop_returns_to", "replan_returns_to",
    "template_ref", "post_action",
}
_KNOWN_STEP_KEYS = {
    "name", "prompt", "action", "mode",
    "artifacts", "coder", "routing",
    "on_reject_refine", "on_exhaust_replan", "reject_code_routes",
    "requires_human_approval_after", "loop_returns_to", "replan_returns_to",
    "enable_notifications", "template_ref", "post_action",
}


def bundle_to_template_group_dict(bundle: WorkflowBundle) -> dict[str, Any]:
    """Adapt a ``WorkflowBundle`` into a ``TEMPLATE_GROUPS``-style dict.

    The returned dict has the same structure as the per-workflow entries in
    ``template_groups.py`` so the existing runner pipeline can consume it
    without any changes to ``step_runner.py``, ``workflow_router.py``, etc.
    """
    step_configs: dict[str, dict[str, Any]] = {}

    for step_name in bundle.step_order:
        sc = bundle.steps[step_name]
        cfg: dict[str, Any] = {}

        # --- Prompt (resolve to absolute path) --------------------------
        if sc.prompt_file:
            prompt_abs = (bundle.bundle_root / sc.prompt_file).resolve()
            cfg["prompt_file"] = str(prompt_abs)
        if sc.action:
            cfg["action"] = sc.action
        if sc.mode:
            cfg["mode"] = sc.mode

        # --- Artifact contract ------------------------------------------
        if sc.required_inputs:
            cfg["required_inputs"] = list(sc.required_inputs)
        if sc.optional_inputs:
            cfg["optional_inputs"] = list(sc.optional_inputs)
        if sc.produces:
            cfg["produces"] = list(sc.produces)
        if sc.result_meta_key:
            cfg["result_meta_key"] = sc.result_meta_key
        if sc.result_meta_key_from_context:
            cfg["result_meta_key_from_context"] = sc.result_meta_key_from_context
        if sc.target_artifact:
            cfg["target_artifact"] = sc.target_artifact
        if sc.edit_mode:
            cfg["edit_mode"] = sc.edit_mode
        if sc.immutable_inputs:
            cfg["immutable_inputs"] = list(sc.immutable_inputs)
        if sc.produced_document_status:
            cfg["produced_document_status"] = dict(sc.produced_document_status)

        # --- Coder -------------------------------------------------------
        if sc.coder_default or sc.coder_role_policy or sc.coder_default_role or sc.coder_allowed or sc.coder_allowed_roles or sc.coder_must_differ:
            coder_cfg: dict[str, Any] = {}
            if sc.coder_default:
                coder_cfg["default"] = sc.coder_default
            if sc.coder_allowed:
                coder_cfg["allowed"] = list(sc.coder_allowed)
            if sc.coder_role_policy:
                coder_cfg["role_policy"] = sc.coder_role_policy
            if sc.coder_default_role:
                coder_cfg["default_role"] = sc.coder_default_role
            if sc.coder_allowed_roles:
                coder_cfg["allowed_roles"] = list(sc.coder_allowed_roles)
            if sc.coder_must_differ:
                coder_cfg["must_differ_from_previous_step"] = True
            cfg["coder"] = coder_cfg

        # --- Routing -----------------------------------------------------
        if sc.on_reject_refine:
            cfg["on_reject_refine"] = dict(sc.on_reject_refine)
        if sc.on_exhaust_replan:
            cfg["on_exhaust_replan"] = dict(sc.on_exhaust_replan)
        if sc.reject_code_routes:
            cfg["reject_code_routes"] = dict(sc.reject_code_routes)

        # --- Review gating -----------------------------------------------
        if sc.requires_human_approval_after:
            cfg["requires_human_approval_after"] = True
        if sc.loop_returns_to:
            cfg["loop_returns_to"] = sc.loop_returns_to
        if sc.replan_returns_to:
            cfg["replan_returns_to"] = sc.replan_returns_to

        # --- Behaviour flags --------------------------------------------
        if sc.enable_notifications:
            cfg["enable_notifications"] = True
        if sc.template_ref:
            cfg["template_ref"] = dict(sc.template_ref)
        if sc.post_action:
            cfg["post_action"] = sc.post_action

        # --- Extra / passthrough -----------------------------------------
        for k, v in sc.extra.items():
            cfg[k] = v

        step_configs[step_name] = cfg

    # Stamp the bundle reference on each step config so downstream code
    # (e.g. context hook injection in step_runner) can discover the
    # workflow package's context_extensions.py.
    for cfg in step_configs.values():
        cfg["_workflow_bundle"] = bundle

    # Build the top-level group dict
    group: dict[str, Any] = {
        "job_prefix": bundle.job_prefix,
        "job_init_step": bundle.init_step,
        "job_init_inputs": list(bundle.init_inputs),
        "default_max_rejects": bundle.default_max_rejects,
        "steps": list(bundle.step_order),
        "step_configs": step_configs,
    }
    if bundle.visibility:
        group["visibility"] = bundle.visibility

    if bundle.governance and bundle.governance.artifact_registry:
        group["artifact_registry"] = [
            {"key": a.key, "path": a.path, "required": a.required}
            for a in bundle.governance.artifact_registry
        ]

    return group


# ---------------------------------------------------------------------------
# Package-local action discovery
# ---------------------------------------------------------------------------

# Cache: bundle_root → action dict, so we don't import actions.py more than
# once per package across repeated load/adapt cycles.
_ACTION_CACHE: dict[str, dict[str, Any]] = {}


def _load_package_actions(bundle_root: Path) -> dict[str, Any]:
    """Import ``actions.py`` from the package and return its registered actions.

    Scans the workflow package directory for an ``actions.py`` module.
    When found, imports it via ``importlib`` — this triggers the ``@action()``
    decorators which register each function into
    ``workflow_packages.actions.REGISTERED_ACTIONS``. Those registrations
    are collected and returned as the ``custom_actions`` dict.

    Returns an empty dict when no ``actions.py`` exists.
    """
    actions_file = bundle_root / "actions.py"
    if not actions_file.is_file():
        return {}

    cache_key = str(bundle_root.resolve())
    if cache_key in _ACTION_CACHE:
        return dict(_ACTION_CACHE[cache_key])

    try:
        import importlib.util  # noqa: PLC0415

        from .actions import REGISTERED_ACTIONS  # noqa: PLC0415

        # Snapshot before import
        before = dict(REGISTERED_ACTIONS)

        spec = importlib.util.spec_from_file_location(
            f"{bundle_root.name}_actions", actions_file
        )
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod.__name__] = mod
        # Execute the module — this runs the @action() decorators
        spec.loader.exec_module(mod)

        # Snapshot after import — collect newly registered actions
        new_actions = {
            name: func
            for name, func in REGISTERED_ACTIONS.items()
            if name not in before or before.get(name) is not func
        }

        _ACTION_CACHE[cache_key] = dict(new_actions)
        return new_actions

    except Exception:
        import logging  # noqa: PLC0415

        logging.getLogger(__name__).exception(
            "Failed to load package actions from %s", actions_file
        )
        return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_section(
    data: dict[str, Any],
    name: str,
    *,
    optional: bool = False,
) -> dict[str, Any]:
    section = data.get(name, {})
    if section is None and optional:
        return {}
    if not isinstance(section, dict):
        raise ValueError(
            f"Expected '{name}' to be a table/section, got {type(section).__name__}"
        )
    return section


def _require(
    data: dict[str, Any],
    key: str,
    expected_type: type,
    *,
    context: str = "",
) -> Any:
    val = data.get(key)
    if val is None:
        ctx = f" ({context})" if context else ""
        raise ValueError(
            f"Missing required field '{key}'{ctx} in workflow.toml"
        )
    if not isinstance(val, expected_type):
        ctx = f" ({context})" if context else ""
        raise ValueError(
            f"Field '{key}'{ctx} must be {expected_type.__name__}, "
            f"got {type(val).__name__}"
        )
    return val


def _opt_str(data: dict[str, Any], key: str) -> str | None:
    val = data.get(key)
    if val is None:
        return None
    return str(val)
