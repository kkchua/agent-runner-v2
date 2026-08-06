from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .bundle_loader import load_project_config, load_workflow_module


AUTHORITATIVE_STEP_SPEC_KEYS = {
    "template_group",
    "step_name",
    "prompt_file",
    "action_name",
    "edit_mode",
    "result_meta_key",
    "result_meta_key_from_context",
    "template_ref",
    "target_artifact",
    "required_inputs",
    "optional_inputs",
    "immutable_inputs",
    "produces",
    "updates",
    "coder_policy",
    "raw_config",
    "job_prefix",
    "job_init_step",
    "job_init_inputs",
    "default_max_rejects",
    "reference_files",
}


TRANSPORT_RAW_CONFIG_KEYS = {
    "prompt_file",
    "action",
    "edit_mode",
    "result_meta_key",
    "result_meta_key_from_context",
    "template_ref",
    "target_artifact",
    "required_inputs",
    "optional_inputs",
    "immutable_inputs",
    "produces",
    "updates",
    "coder",
    "enable_notifications",
    "on_reject_refine",
    "requires_human_approval_after",
    "produced_document_status",
    "post_action",
}


def load_workflow_definition(
    *,
    workspace_root: Path,
    workflow_name: str = "default",
) -> tuple[Any, dict[str, Any]]:
    config = load_project_config(workspace_root)
    module = load_workflow_module(workspace_root, workflow_name, config=config)
    return module, config


def get_template_group_cfg(
    *,
    template_group: str,
    workspace_root: Path,
    workflow_name: str = "default",
) -> dict[str, Any]:
    module, _config = load_workflow_definition(
        workspace_root=workspace_root,
        workflow_name=workflow_name,
    )
    template_groups = getattr(module, "TEMPLATE_GROUPS", {}) or {}
    if template_group not in template_groups:
        valid = ", ".join(sorted(template_groups))
        raise ValueError(f"Unknown template group {template_group!r}. Valid groups: {valid}")
    return copy.deepcopy(template_groups[template_group])


def build_transport_raw_config(step_cfg: dict[str, Any]) -> dict[str, Any]:
    transport_cfg: dict[str, Any] = {}
    for key in TRANSPORT_RAW_CONFIG_KEYS:
        if key in step_cfg:
            transport_cfg[key] = copy.deepcopy(step_cfg[key])
    return transport_cfg


def build_step_execution_spec(
    *,
    template_group: str,
    step_name: str,
    group_cfg: dict[str, Any],
) -> dict[str, Any]:
    steps = list(group_cfg.get("steps") or [])
    if step_name not in steps:
        raise ValueError(f"Step {step_name!r} is not defined for template group {template_group!r}")
    step_cfg = copy.deepcopy((group_cfg.get("step_configs") or {}).get(step_name) or {})
    step_index = steps.index(step_name) + 1
    prompt_file = step_cfg.get("prompt_file")
    if isinstance(prompt_file, str) and prompt_file:
        prompt_file = str(Path(prompt_file).as_posix())
    spec: dict[str, Any] = {
        "template_group": template_group,
        "step_name": step_name,
        "step_order": step_index,
        "step_sequence_no": step_index,
        "prompt_file": prompt_file,
        "action_name": step_cfg.get("action"),
        "edit_mode": step_cfg.get("edit_mode"),
        "result_meta_key": step_cfg.get("result_meta_key"),
        "result_meta_key_from_context": step_cfg.get("result_meta_key_from_context"),
        "onsuccess": step_cfg.get("onsuccess"),
        "template_ref": step_cfg.get("template_ref"),
        "target_artifact": step_cfg.get("target_artifact"),
        "required_inputs": [{"artifact_key": key} for key in list(step_cfg.get("required_inputs") or [])],
        "optional_inputs": [{"artifact_key": key} for key in list(step_cfg.get("optional_inputs") or [])],
        "immutable_inputs": [{"artifact_key": key} for key in list(step_cfg.get("immutable_inputs") or [])],
        "produces": [{"artifact_key": key} for key in list(step_cfg.get("produces") or [])],
        "updates": [{"artifact_key": key} for key in list(step_cfg.get("updates") or [])],
        "raw_config": build_transport_raw_config(step_cfg),
        "job_prefix": group_cfg.get("job_prefix"),
        "job_init_step": group_cfg.get("job_init_step"),
        "job_init_inputs": list(group_cfg.get("job_init_inputs") or []),
        "default_max_rejects": int(group_cfg.get("default_max_rejects") or 0),
        "reference_files": dict(group_cfg.get("reference_files") or {}),
    }
    coder_cfg = step_cfg.get("coder") or {}
    if coder_cfg:
        spec["coder_policy"] = {
            "default_coder": coder_cfg.get("default"),
            "allowed_coders": list(coder_cfg.get("allowed") or []),
            "role_policy": coder_cfg.get("role_policy"),
            "default_role": coder_cfg.get("default_role"),
            "allowed_roles": list(coder_cfg.get("allowed_roles") or []),
            "must_differ_from_previous_step": bool(coder_cfg.get("must_differ_from_previous_step")),
        }
    return spec


def build_workflow_step_specs(
    *,
    template_group: str,
    workspace_root: Path,
    workflow_name: str = "default",
) -> list[dict[str, Any]]:
    group_cfg = get_template_group_cfg(
        template_group=template_group,
        workspace_root=workspace_root,
        workflow_name=workflow_name,
    )
    return [
        build_step_execution_spec(
            template_group=template_group,
            step_name=step_name,
            group_cfg=group_cfg,
        )
        for step_name in list(group_cfg.get("steps") or [])
    ]


def reconcile_step_execution_spec(
    *,
    template_group: str,
    step_name: str,
    workspace_root: Path,
    workflow_name: str = "default",
    backend_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    group_cfg = get_template_group_cfg(
        template_group=template_group,
        workspace_root=workspace_root,
        workflow_name=workflow_name,
    )
    local_spec = build_step_execution_spec(
        template_group=template_group,
        step_name=step_name,
        group_cfg=group_cfg,
    )
    reconciled = copy.deepcopy(backend_spec or {})
    for key in AUTHORITATIVE_STEP_SPEC_KEYS:
        if key in local_spec:
            reconciled[key] = copy.deepcopy(local_spec[key])
    reconciled["step_order"] = int((backend_spec or {}).get("step_order") or local_spec.get("step_order") or 1)
    reconciled["step_sequence_no"] = int((backend_spec or {}).get("step_sequence_no") or reconciled["step_order"])
    return reconciled
