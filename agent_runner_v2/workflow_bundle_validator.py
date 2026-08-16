from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .runtime_context import PACKAGE_ROOT
from .workflow_packages.loader import bundle_to_template_group_dict, load_workflow_package


DEFAULT_BOOTSTRAP_WORKFLOWS_ROOT = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"

# Regex to match BCS slot references like {{ slot.ID }}
_BCS_SLOT_PATTERN = re.compile(r"^\{\{\s*slot\.[\w-]+\s*\}\}$")


@dataclass(frozen=True)
class ValidationFinding:
    level: str
    code: str
    message: str
    path: str = ""
    step: str = ""


@dataclass(frozen=True)
class WorkflowBundleValidationReport:
    workflow_name: str
    bundle_root: Path
    valid: bool
    findings: tuple[ValidationFinding, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "bundle_root": str(self.bundle_root),
            "valid": self.valid,
            "finding_count": len(self.findings),
            "findings": [
                {
                    "level": item.level,
                    "code": item.code,
                    "message": item.message,
                    "path": item.path,
                    "step": item.step,
                }
                for item in self.findings
            ],
        }


def validate_workflow_bundle_dir(bundle_root: Path) -> WorkflowBundleValidationReport:
    findings: list[ValidationFinding] = []
    workflow_name = bundle_root.name

    try:
        bundle = load_workflow_package(bundle_root)
    except Exception as exc:
        findings.append(
            ValidationFinding(
                level="error",
                code="bundle_load_failed",
                message=str(exc),
                path=str((bundle_root / "workflow.toml").resolve()),
            )
        )
        return WorkflowBundleValidationReport(
            workflow_name=workflow_name,
            bundle_root=bundle_root.resolve(),
            valid=False,
            findings=tuple(findings),
        )

    workflow_name = bundle.name
    manifest_path = bundle.manifest_path

    if not bundle.step_order:
        findings.append(_error("empty_step_order", "Workflow bundle has no declared step order.", path=str(manifest_path)))

    if len(bundle.step_order) != len(set(bundle.step_order)):
        findings.append(_error("duplicate_step_name", "Workflow bundle contains duplicate step names.", path=str(manifest_path)))

    if bundle.init_step not in bundle.step_order:
        findings.append(
            _error(
                "missing_init_step",
                f"init_step {bundle.init_step!r} is not present in the workflow step order.",
                path=str(manifest_path),
            )
        )

    for step_name in bundle.step_order:
        step = bundle.steps.get(step_name)
        if step is None:
            findings.append(_error("missing_step_config", f"Step {step_name!r} is missing from bundle.steps.", path=str(manifest_path), step=step_name))
            continue
        if not step.prompt_file and not step.action:
            findings.append(_error("step_missing_prompt_or_action", "Step must define either a prompt or an action.", path=str(manifest_path), step=step_name))
        if step.prompt_file:
            # BCS: Skip file existence check for dynamic prompt slot references
            if not _BCS_SLOT_PATTERN.match(step.prompt_file):
                prompt_path = (bundle.bundle_root / step.prompt_file).resolve()
                if not prompt_path.is_file():
                    findings.append(_error("missing_prompt_file", f"Prompt file does not exist: {prompt_path}", path=str(prompt_path), step=step_name))
        _validate_artifact_keys(findings, step.produces, "produces", manifest_path, step_name)
        _validate_artifact_keys(findings, step.required_inputs, "required_inputs", manifest_path, step_name)
        _validate_artifact_keys(findings, step.optional_inputs, "optional_inputs", manifest_path, step_name)

    group_dict = bundle_to_template_group_dict(bundle)
    step_configs = group_dict.get("step_configs", {})
    known_steps = set(bundle.step_order)
    for step_name in bundle.step_order:
        cfg = step_configs.get(step_name, {})
        _validate_step_target(findings, known_steps, cfg.get("onsuccess"), "onsuccess_target_missing", manifest_path, step_name)
        refine_cfg = cfg.get("on_reject_refine") or {}
        if isinstance(refine_cfg, dict):
            _validate_step_target(findings, known_steps, refine_cfg.get("step"), "on_reject_refine_step_missing", manifest_path, step_name)
        coder_cfg = cfg.get("coder") or {}
        if isinstance(coder_cfg, dict) and coder_cfg.get("role_policy") is not None:
            role_policy = str(coder_cfg.get("role_policy") or "").strip()
            if not role_policy:
                findings.append(_error("empty_role_policy", "coder.role_policy must be a non-empty string when provided.", path=str(manifest_path), step=step_name))

    _validate_bundle_governance(findings, bundle)
    _validate_prompt_contract(findings, bundle)

    try:
        serializable = _strip_runtime_bundle_refs(group_dict)
        json.dumps(serializable, sort_keys=True)
    except Exception as exc:
        findings.append(_error("non_serializable_definition", f"Normalized workflow definition is not JSON-serializable: {exc}", path=str(manifest_path)))

    return WorkflowBundleValidationReport(
        workflow_name=workflow_name,
        bundle_root=bundle.bundle_root,
        valid=not any(item.level == "error" for item in findings),
        findings=tuple(findings),
    )


def validate_named_workflow_bundles(
    *,
    workflows_root: Path | None = None,
    workflow_names: list[str] | None = None,
) -> list[WorkflowBundleValidationReport]:
    root = (workflows_root or DEFAULT_BOOTSTRAP_WORKFLOWS_ROOT).resolve()
    selected = workflow_names or _discover_bundle_names(root)
    reports: list[WorkflowBundleValidationReport] = []
    for workflow_name in selected:
        reports.append(validate_workflow_bundle_dir(root / workflow_name))
    return reports


def _discover_bundle_names(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    names: list[str] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "workflow.toml").is_file():
            names.append(child.name)
    return names


def _validate_artifact_keys(
    findings: list[ValidationFinding],
    keys: list[str],
    field_name: str,
    manifest_path: Path,
    step_name: str,
) -> None:
    for key in keys:
        if not isinstance(key, str) or not key.strip():
            findings.append(
                _error(
                    "invalid_artifact_key",
                    f"{field_name} contains an empty or non-string artifact key.",
                    path=str(manifest_path),
                    step=step_name,
                )
            )


def _validate_step_target(
    findings: list[ValidationFinding],
    known_steps: set[str],
    target: Any,
    code: str,
    manifest_path: Path,
    step_name: str,
) -> None:
    if target is None:
        return
    target_name = str(target).strip()
    if not target_name:
        findings.append(_error(code, "Routing target is present but empty.", path=str(manifest_path), step=step_name))
        return
    if target_name not in known_steps:
        findings.append(
            _error(
                code,
                f"Routing target {target_name!r} is not a declared workflow step.",
                path=str(manifest_path),
                step=step_name,
            )
        )


def _strip_runtime_bundle_refs(group_dict: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(group_dict, default=str))
    for cfg in (data.get("step_configs") or {}).values():
        if isinstance(cfg, dict):
            cfg.pop("_workflow_bundle", None)
    return data


def _validate_bundle_governance(
    findings: list[ValidationFinding],
    bundle: Any,
) -> None:
    governance = getattr(bundle, "governance", None)
    if governance is None:
        return

    known_steps = set(bundle.step_order)
    if governance.include_in_prompts:
        for target in governance.prompt_targets:
            if target == "all":
                continue
            if target not in known_steps:
                findings.append(
                    _error(
                        "unknown_governance_prompt_target",
                        f"Governance prompt target {target!r} is not a declared step.",
                        path=str(governance.manifest_path),
                    )
                )

    seen_artifact_keys: set[str] = set()
    for artifact in governance.artifact_registry:
        artifact_key = str(artifact.key or "").strip()
        artifact_path = str(artifact.path or "").strip()
        if not artifact_key:
            findings.append(_error("empty_governance_artifact_key", "Bundle governance artifact registry contains an empty key.", path=str(governance.manifest_path)))
            continue
        if artifact_key in seen_artifact_keys:
            findings.append(
                _error(
                    "duplicate_governance_artifact_key",
                    f"Bundle governance artifact registry duplicates key {artifact_key!r}.",
                    path=str(governance.manifest_path),
                )
            )
        seen_artifact_keys.add(artifact_key)
        if not artifact_path:
            findings.append(
                _error(
                    "empty_governance_artifact_path",
                    f"Bundle governance artifact {artifact_key!r} has an empty path.",
                    path=str(governance.manifest_path),
                )
            )

    referenced_keys = _collect_step_artifact_references(bundle)
    declared_keys = {str(item.key).strip() for item in governance.artifact_registry if str(item.key).strip()}

    for key in sorted(referenced_keys):
        if key not in declared_keys:
            findings.append(
                _error(
                    "undeclared_governance_artifact_reference",
                    f"Workflow steps reference artifact key {key!r} but it is not declared in bundle_governance.toml.",
                    path=str(governance.manifest_path),
                )
            )

    for key in sorted(declared_keys):
        if key not in referenced_keys:
            findings.append(
                _error(
                    "unused_governance_artifact_registry_key",
                    f"Bundle governance artifact key {key!r} is declared but not referenced by any workflow step contract.",
                    path=str(governance.manifest_path),
                )
                )


def _validate_prompt_contract(
    findings: list[ValidationFinding],
    bundle: Any,
) -> None:
    contract_path = bundle.bundle_root / "bundle_governance" / "prompt_contract.json"
    if not contract_path.is_file():
        return

    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except Exception as exc:
        findings.append(
            _error(
                "invalid_prompt_contract",
                f"Prompt contract JSON could not be parsed: {exc}",
                path=str(contract_path),
            )
        )
        return

    defaults = contract.get("defaults")
    step_requirements = contract.get("step_requirements")
    if defaults is not None and not isinstance(defaults, dict):
        findings.append(_error("invalid_prompt_contract_defaults", "prompt_contract.json defaults must be an object.", path=str(contract_path)))
        return
    if step_requirements is not None and not isinstance(step_requirements, dict):
        findings.append(_error("invalid_prompt_contract_steps", "prompt_contract.json step_requirements must be an object.", path=str(contract_path)))
        return

    defaults = defaults or {}
    step_requirements = step_requirements or {}
    known_steps = set(bundle.step_order)

    for step_name in sorted(step_requirements):
        if step_name not in known_steps:
            findings.append(
                _error(
                    "unknown_prompt_contract_step",
                    f"prompt_contract.json references unknown step {step_name!r}.",
                    path=str(contract_path),
                    step=step_name,
                )
            )

    for step_name in bundle.step_order:
        step = bundle.steps.get(step_name)
        if step is None or not step.prompt_file:
            continue

        prompt_path = (bundle.bundle_root / step.prompt_file).resolve()
        if not prompt_path.is_file():
            continue

        try:
            prompt_text = prompt_path.read_text(encoding="utf-8")
        except Exception as exc:
            findings.append(
                _error(
                    "prompt_read_failed",
                    f"Prompt file could not be read as UTF-8: {exc}",
                    path=str(prompt_path),
                    step=step_name,
                )
            )
            continue

        cfg = dict(defaults)
        cfg.update(step_requirements.get(step_name) or {})
        _validate_prompt_text(findings, prompt_path, step_name, prompt_text, cfg)


def _validate_prompt_text(
    findings: list[ValidationFinding],
    prompt_path: Path,
    step_name: str,
    prompt_text: str,
    cfg: dict[str, Any],
) -> None:
    if cfg.get("ascii_only") is True and not prompt_text.isascii():
        findings.append(
            _error(
                "prompt_non_ascii",
                "Prompt file must be ASCII-only.",
                path=str(prompt_path),
                step=step_name,
            )
        )

    for field_name, code in (
        ("required_literals", "prompt_missing_required_literal"),
        ("required_ordered_literals", "prompt_missing_ordered_literal"),
        ("forbidden_literals", "prompt_contains_forbidden_literal"),
    ):
        values = cfg.get(field_name)
        if values is None:
            continue
        if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
            findings.append(
                _error(
                    "invalid_prompt_contract_field",
                    f"{field_name} must be a list of non-empty strings.",
                    path=str(prompt_path),
                    step=step_name,
                )
            )
            continue

        if field_name == "required_literals":
            for literal in values:
                if literal not in prompt_text:
                    findings.append(
                        _error(
                            code,
                            f"Prompt file is missing required literal {literal!r}.",
                            path=str(prompt_path),
                            step=step_name,
                        )
                    )
        elif field_name == "required_ordered_literals":
            start = 0
            for literal in values:
                idx = prompt_text.find(literal, start)
                if idx < 0:
                    findings.append(
                        _error(
                            code,
                            f"Prompt file is missing required ordered literal {literal!r}.",
                            path=str(prompt_path),
                            step=step_name,
                        )
                    )
                    break
                start = idx + len(literal)
        elif field_name == "forbidden_literals":
            for literal in values:
                if literal in prompt_text:
                    findings.append(
                        _error(
                            code,
                            f"Prompt file contains forbidden literal {literal!r}.",
                            path=str(prompt_path),
                            step=step_name,
                        )
                    )


def _collect_step_artifact_references(bundle: Any) -> set[str]:
    referenced: set[str] = set()
    for step_name in bundle.step_order:
        step = bundle.steps.get(step_name)
        if step is None:
            continue
        for key in step.produces:
            if isinstance(key, str) and key.strip():
                referenced.add(key.strip())
        for key in step.required_inputs:
            if isinstance(key, str) and key.strip():
                referenced.add(key.strip())
        for key in step.optional_inputs:
            if isinstance(key, str) and key.strip():
                referenced.add(key.strip())
        for key in step.immutable_inputs:
            if isinstance(key, str) and key.strip():
                referenced.add(key.strip())
        for key in (step.result_meta_key, step.result_meta_key_from_context, step.target_artifact):
            if isinstance(key, str) and key.strip():
                referenced.add(key.strip())
        for route_cfg in (step.on_reject_refine,):
            if isinstance(route_cfg, dict):
                artifact_key = route_cfg.get("artifact")
                if isinstance(artifact_key, str) and artifact_key.strip():
                    referenced.add(artifact_key.strip())
    return referenced


def _error(code: str, message: str, *, path: str = "", step: str = "") -> ValidationFinding:
    return ValidationFinding(level="error", code=code, message=message, path=path, step=step)
