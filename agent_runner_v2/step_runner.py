#!/usr/bin/env python3
"""
step_runner.py — Core step execution contract for agent_runner_v2.

Single responsibility: invoke coder → read meta.json → validate artifacts → enrich sidecar.

Related: IMPL-20260422-04

Key v2 differences from v1:
- meta.json sidecar is the ONLY communication channel (no fallbacks, no stdout JSON parsing)
- No pre-invocation sidecar writes
- No recovery functions
- Raises exceptions on failure; caller routes them
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any

from .artifact_paths import compute_paths
from .coder_adapters import CoderInvocationError, dataclass_dict, invoke_coder
from .exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError
from .runtime_context import RUNNER_ROOT, ARTIFACT_ROOT, PathProxy, get_workflow_module


RESULT_SCHEMA_PATH = PathProxy(lambda: Path(RUNNER_ROOT) / "llm_response_schema.json")


def _workflow_module():
    module = get_workflow_module()
    if module is None:
        from . import template_groups as module  # type: ignore[no-redef]
    return module


# ---------------------------------------------------------------------------
# StepResult — the single return type from run_step()
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict[str, str]
    reject_code: str | None
    meta_json_path: str   # repo-relative path of the meta.json that was read
    usage_data: dict      # from InvocationResult.usage


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_step(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    coder: str,
    coder_config: dict | None,
    prompt_text: str,
    checksum: str,
    step_dir: Path,
    project_root: Path,
    context: dict[str, str],
) -> StepResult:
    """Invoke coder, read meta.json contract, validate artifacts, enrich sidecar.

    Raises:
        CoderInvocationError  — coder process failed (caller routes to failure)
        MetaJsonMissingError  — coder did not write meta.json (hard failure)
        MetaJsonInvalidError  — meta.json present but schema invalid (hard failure)
        ArtifactMissingError  — meta.json references paths that don't exist on disk
    """
    invoked_at = _now_iso()

    # Resolve meta.json path before invocation so it can be used as an early-exit signal.
    # Safe to compute here — context is pre-built and immutable; we do NOT call build_context() again.
    meta_path = _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root, step_dir=step_dir)

    try:
        invocation = invoke_coder(
            coder=coder,
            step=step,
            prompt_text=prompt_text,
            cwd=project_root,
            schema_path=RESULT_SCHEMA_PATH,
            prompt_checksum=checksum,
            now_iso_fn=_now_iso,
            coder_config=coder_config,
            sidecar_path=meta_path,
        )
        print(
            f"[{_now_iso()}] coder={coder} step={step} status=COMPLETE "
            f"return_code={invocation.return_code}",
            flush=True,
        )
    except CoderInvocationError as exc:
        print(
            f"[{_now_iso()}] coder={coder} step={step} status=ERROR "
            f"return_code={exc.return_code}",
            flush=True,
        )
        _save_debug_failure(
            step_dir=step_dir,
            command=exc.command,
            return_code=exc.return_code,
            stdout=exc.stdout,
            stderr=exc.stderr,
            raw_events=exc.raw_events,
            error_message=str(exc),
        )
        raise

    finished_at = _now_iso()

    # Save invocation artefacts
    _save_text(step_dir / "raw_output.txt", invocation.stdout)
    if invocation.stderr:
        _save_text(step_dir / "stderr.txt", invocation.stderr)
    _save_json_atomic(step_dir / "usage.json", dataclass_dict(invocation.usage))
    _save_json_atomic(step_dir / "step_manifest.json", dataclass_dict(invocation.manifest))
    _write_raw_events_jsonl(step_dir / "raw_events.jsonl", invocation.raw_events)

    # Read and validate meta.json — raises on failure (no fallbacks)
    meta = _read_and_validate_meta_json(meta_path)
    coder_result = meta["coder_result"]

    # Validate artifact files exist on disk
    artifacts = dict(coder_result.get("artifacts") or {})
    _validate_artifact_files_exist(artifacts=artifacts, project_root=project_root)

    # Validate template conformance if template_ref is configured
    template_ref = step_cfg.get("template_ref")
    if template_ref:
        _validate_template_conformance(
            template_ref=template_ref,
            artifacts=artifacts,
            project_root=project_root,
            step=step,
        )

    # Print Doc ID and sidecar file path to console for visibility
    result_key = step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context", "")
    artifact_path = artifacts.get(result_key, "") if result_key else ""
    meta_rel = str(meta_path.relative_to(project_root))
    print(f"[step_runner] step={step} result_key={result_key}", flush=True)
    if artifact_path:
        print(f"[step_runner] Doc ID PATH: {artifact_path}", flush=True)
    print(f"[step_runner] Sidecar PATH: {meta_rel}", flush=True)

    # Enrich sidecar with runner_data (atomic — never touches coder_result)
    enrich_sidecar(
        meta_path=meta_path,
        step=step,
        coder_used=coder,
        invoked_at=invoked_at,
        finished_at=finished_at,
        prompt_checksum=checksum,
        project_root=project_root,
    )

    return StepResult(
        status=coder_result["status"],
        remark=str(coder_result.get("remark") or ""),
        artifacts=artifacts,
        reject_code=coder_result.get("reject_code") or None,
        meta_json_path=str(meta_path.relative_to(project_root)),
        usage_data=dataclass_dict(invocation.usage),
    )


# ---------------------------------------------------------------------------
# Action step execution (non-coder steps)
# ---------------------------------------------------------------------------

def run_action(
    *,
    action_name: str,
    state: dict,
    step: str,
    step_cfg: dict,
    project_root: Path,
    context: dict[str, str],
) -> StepResult:
    """Execute a runner action (non-coder step).

    The action function writes its own meta.json and returns an ActionResult.
    We then validate, enrich, and return a StepResult — same contract as run_step().

    Raises:
        Exception — action-specific failures (caller routes to failure).
    """
    from .runner_actions import execute as execute_action

    invoked_at = _now_iso()

    # Resolve meta.json path so the action can use it from context.
    meta_path = _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)

    # Execute the action
    result = execute_action(
        action_name=action_name,
        context=context,
        state=state,
        step_cfg=step_cfg,
        step=step,
        project_root=project_root,
    )

    finished_at = _now_iso()

    # Validate the action wrote a meta.json
    meta = _read_and_validate_meta_json(meta_path)
    coder_result = meta["coder_result"]

    # Validate artifact files exist on disk
    artifacts = dict(coder_result.get("artifacts") or {})
    _validate_artifact_files_exist(artifacts=artifacts, project_root=project_root)

    # Enrich sidecar with runner_data
    enrich_sidecar(
        meta_path=meta_path,
        step=step,
        coder_used="action",
        invoked_at=invoked_at,
        finished_at=finished_at,
        prompt_checksum="n/a",
        project_root=project_root,
    )

    return StepResult(
        status=coder_result["status"],
        remark=str(coder_result.get("remark") or ""),
        artifacts=artifacts,
        reject_code=coder_result.get("reject_code") or None,
        meta_json_path=str(meta_path.relative_to(project_root)),
        usage_data={},
    )


# ---------------------------------------------------------------------------
# Meta.json contract
# ---------------------------------------------------------------------------

def _resolve_meta_json_path(
    *,
    step_cfg: dict,
    context: dict[str, str],
    project_root: Path,
    step_dir: Path | None = None,
) -> Path:
    """Resolve absolute path of the meta.json to read after coder invocation.

    Priority:
    1. result_meta_key_from_context — context variable holds the artifact path;
       derive meta.json by replacing extension.
    2. result_meta_key — use the precomputed {KEY}_METAJSON context variable.
    3. step_dir fallback — for producing steps where artifact doesn't exist yet.
    """
    from_ctx_key = step_cfg.get("result_meta_key_from_context")
    if from_ctx_key:
        artifact_path_str = context.get(from_ctx_key, "")
        if artifact_path_str:
            p = PurePath(artifact_path_str)
            meta_rel = str(p.parent / f"{p.stem}.meta.json")
            return project_root / meta_rel

    result_key = step_cfg.get("result_meta_key")
    if result_key:
        meta_rel = context.get(f"{result_key}_METAJSON", "")
        if meta_rel:
            return project_root / meta_rel

    # Fallback: use step directory for producing steps (artifact not yet created)
    if step_dir is not None:
        fallback = step_dir / "meta.json"
        print(f"[step_runner] meta.json fallback to step dir: {fallback.relative_to(project_root)}", flush=True)
        return fallback

    raise MetaJsonMissingError(
        f"Step config has neither 'result_meta_key' nor 'result_meta_key_from_context' "
        f"and no step_dir fallback available — cannot locate meta.json"
    )


def _read_and_validate_meta_json(path: Path) -> dict:
    """Read and validate coder-written meta.json.

    Accepts both:
    - v2 format: schema_version = "v2"
    - legacy format: sidecar_version = "artifact_meta_v1"

    Raises MetaJsonMissingError if file absent.
    Raises MetaJsonInvalidError with descriptive message on any schema failure.
    """
    if not path.exists() or not path.is_file():
        raise MetaJsonMissingError(
            f"Coder did not write meta.json to expected path: {path}"
        )

    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise MetaJsonInvalidError(
            f"meta.json at {path} is not valid JSON: {exc}"
        ) from exc

    if not isinstance(meta, dict):
        raise MetaJsonInvalidError(f"meta.json at {path} is not a JSON object")

    # Accept both schema versions during transition
    schema_v = str(meta.get("schema_version") or "").strip()
    sidecar_v = str(meta.get("sidecar_version") or "").strip()
    if schema_v not in ("v2",) and sidecar_v not in ("artifact_meta_v1",):
        raise MetaJsonInvalidError(
            f"meta.json at {path} has unrecognised version: "
            f"schema_version={schema_v!r}, sidecar_version={sidecar_v!r}. "
            "Expected schema_version='v2' or sidecar_version='artifact_meta_v1'."
        )

    coder_result = meta.get("coder_result")
    if not isinstance(coder_result, dict):
        raise MetaJsonInvalidError(
            f"meta.json at {path} is missing coder_result object"
        )

    status = str(coder_result.get("status") or "").strip().upper()
    if status not in ("APPROVED", "REJECTED"):
        raise MetaJsonInvalidError(
            f"meta.json at {path} has invalid coder_result.status: {status!r}. "
            "Must be 'APPROVED' or 'REJECTED'."
        )
    coder_result["status"] = status  # normalise case in-place

    if not isinstance(coder_result.get("artifacts"), dict):
        raise MetaJsonInvalidError(
            f"meta.json at {path} is missing coder_result.artifacts object"
        )

    recorded_at = str(coder_result.get("recorded_at") or "").strip()
    if not recorded_at:
        raise MetaJsonInvalidError(
            f"meta.json at {path} is missing coder_result.recorded_at"
        )

    return meta


def _validate_artifact_files_exist(
    *,
    artifacts: dict[str, str],
    project_root: Path,
) -> None:
    """Raise ArtifactMissingError if any artifact path in the dict doesn't exist."""
    missing = [
        path_str
        for path_str in artifacts.values()
        if path_str and not (project_root / path_str).exists()
    ]
    if missing:
        raise ArtifactMissingError(
            f"Artifact files claimed in meta.json do not exist on disk: {missing}",
            missing=missing,
        )


def _backend_artifact_rules(state: dict[str, Any]) -> dict[str, Any]:
    rules = state.get("backend_artifact_rules") or {}
    return rules if isinstance(rules, dict) else {}


def _resolve_backend_artifact_rule_path(*, state: dict, artifact_key: str, step: str, prefer_final: bool = False) -> str:
    rules = _backend_artifact_rules(state)
    rule = rules.get(artifact_key) if isinstance(rules, dict) else None
    if not isinstance(rule, dict):
        return ""
    template = rule.get("final_path_template") if prefer_final else rule.get("working_path_template")
    if not template:
        template = rule.get("working_path_template") or rule.get("final_path_template")
    if not template:
        return ""
    run_id = str(state.get("job_id") or state.get("workflow_run_id") or "backend-run")
    steps = _workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", [])
    try:
        step_index = steps.index(step) + 1
    except ValueError:
        step_index = 1
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    step_sequence = int(state.get("backend_step_sequence") or step_index)
    step_dir_name = PurePath(step_dir_rel).name if step_dir_rel else f"{step_sequence:02d}_{step}"
    return str(template).format(
        workflow_name=str(state.get("template_group") or ""),
        template_group=str(state.get("template_group") or ""),
        job_id=run_id,
        run_code=run_id,
        step_name=step,
        step_order=step_sequence,
        step_dir=step_dir_name,
        step_dir_rel=step_dir_rel,
    )


def _set_backend_artifact_rule_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> bool:
    rules = _backend_artifact_rules(state)
    if not rules:
        return False
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    for artifact_key, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        is_produced = artifact_key in produces
        artifact_value = artifacts.get(artifact_key) or ""
        if not artifact_value:
            artifact_value = _resolve_backend_artifact_rule_path(
                state=state,
                artifact_key=artifact_key,
                step=step,
                prefer_final=not is_produced,
            )
        if artifact_value:
            ctx[f"{artifact_key}_PATH"] = str(artifact_value)
        meta_strategy = str(rule.get("meta_path_strategy") or "artifact_sidecar")
        if meta_strategy == "step_shared_meta" and step_dir_rel:
            meta_path = f"{step_dir_rel}/meta.json"
        else:
            p = PurePath(str(artifact_value))
            meta_path = str(p.parent / f"{p.stem}.meta.json") if artifact_value else ""
        if meta_path:
            ctx[f"{artifact_key}_METAJSON"] = meta_path
        if is_produced and not artifacts.get(artifact_key) and artifact_value:
            ctx[artifact_key] = str(artifact_value)
            ctx[f"{artifact_key}_PATH"] = str(artifact_value)
            if meta_path:
                ctx[f"{artifact_key}_METAJSON"] = meta_path
    return True



DELIVERY_SCAFFOLD_OUTPUT_PATHS: dict[str, str] = {
    "PROJECT_ANALYSIS": "{step_dir_rel}/project_analysis.md",
    "DELIVERY_SOP": "{step_dir_rel}/WORKFLOW_SOP_v1.md",
    "DELIVERY_STATUS_RULES": "{step_dir_rel}/DELIVERY_STATUS_RULES_v1.md",
    "DELIVERY_TEMPLATE_REGISTRY": "{step_dir_rel}/template_registry.md",
    "DELIVERY_INITIATIVE_TEMPLATE": "{step_dir_rel}/01_initiative.template.md",
    "DELIVERY_PLAN_TEMPLATE": "{step_dir_rel}/02_plan.template.md",
    "DELIVERY_TASK_GRAPH_TEMPLATE": "{step_dir_rel}/02b_task_graph.template.md",
    "DELIVERY_TASK_TEMPLATE": "{step_dir_rel}/03_task.template.md",
    "DELIVERY_IMPL_TEMPLATE": "{step_dir_rel}/04_implementation_plan.template.md",
    "DELIVERY_REVIEW_TEMPLATE": "{step_dir_rel}/04_review.template.md",
    "DELIVERY_MEMORY_TEMPLATE": "{step_dir_rel}/06_memory.template.md",
    "DELIVERY_AGENTS_MD": "docs/delivery/08_agents/AGENTS.md",
    "DELIVERY_AGENT_PLANNER": "docs/delivery/08_agents/AGENT-planner.md",
    "DELIVERY_AGENT_TASK_DECOMPOSER": "docs/delivery/08_agents/AGENT-task-decomposer.md",
    "DELIVERY_AGENT_IMPL_PLANNER": "docs/delivery/08_agents/AGENT-implementation-planner.md",
    "DELIVERY_AGENT_EXECUTOR": "docs/delivery/08_agents/AGENT-executor.md",
    "DELIVERY_AGENT_REVIEWER": "docs/delivery/08_agents/AGENT-reviewer.md",
    "DELIVERY_AGENT_MEMORY_MANAGER": "docs/delivery/08_agents/AGENT-memory-manager.md",
    "DELIVERY_FOLDER_MAP": "docs/delivery/DELIVERY_FOLDER_MAP.json",
}


def _delivery_scaffold_output_path(*, state: dict, artifact_key: str, step: str) -> str:
    template = DELIVERY_SCAFFOLD_OUTPUT_PATHS.get(artifact_key)
    if not template:
        return ""
    run_id = str(state.get("job_id") or state.get("workflow_run_id") or "delivery-scaffold-run")
    steps = _workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", [])
    try:
        step_index = steps.index(step) + 1
    except ValueError:
        step_index = 1
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    return template.format(run_id=run_id, step=step, step_index=step_index, step_dir_rel=step_dir_rel)


def _set_delivery_scaffold_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> None:
    if _set_backend_artifact_rule_aliases(ctx=ctx, state=state, step=step, artifacts=artifacts, produces=produces):
        return
    if not str(state.get("template_group") or "").startswith("delivery_scaffold"):
        return

    step_names = list(_workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", []))
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    step_dir_meta = f"{step_dir_rel}/meta.json" if step_dir_rel else ""
    run_id = str(state.get("job_id") or state.get("workflow_run_id") or "delivery-scaffold-run")
    step_index = (step_names.index(step) + 1) if step in step_names else 1

    for artifact_key, rel_path in DELIVERY_SCAFFOLD_OUTPUT_PATHS.items():
        artifact_value = artifacts.get(artifact_key) or rel_path.format(
            run_id=run_id,
            step=step,
            step_index=step_index,
            step_dir_rel=step_dir_rel,
        )
        ctx[f"{artifact_key}_PATH"] = str(artifact_value)
        p = PurePath(str(artifact_value))
        default_meta = step_dir_meta if artifact_key in produces and step_dir_meta else str(p.parent / f"{p.stem}.meta.json")
        ctx[f"{artifact_key}_METAJSON"] = default_meta

    for artifact_key in produces:
        if artifact_key in DELIVERY_SCAFFOLD_OUTPUT_PATHS and not artifacts.get(artifact_key):
            output_path = _delivery_scaffold_output_path(state=state, artifact_key=artifact_key, step=step)
            if output_path:
                ctx[artifact_key] = output_path
                ctx[f"{artifact_key}_PATH"] = output_path
                ctx[f"{artifact_key}_METAJSON"] = step_dir_meta or str(PurePath(output_path).parent / f"{PurePath(output_path).stem}.meta.json")


def _validate_template_conformance(
    *,
    template_ref: dict[str, Any],
    artifacts: dict[str, str],
    project_root: Path,
    step: str,
) -> None:
    """Validate generated artifact conforms to the expected template structure.

    If the template artifact (from DELIVERY_*_TEMPLATE) is available on disk,
    read it to extract required sections and metadata fields. If not available,
    fall back to the inline required_sections/required_metadata_fields config.

    Raises ArtifactMissingError if the artifact doesn't conform to the template.
    """
    doc_type = template_ref.get("type", "")
    template_artifact_key = template_ref.get("template_artifact_key", "")
    inline_sections = template_ref.get("required_sections", [])
    inline_metadata = template_ref.get("required_metadata_fields", [])

    # Determine which artifact path to validate (use result_meta_key artifact if available)
    artifact_path = None
    if template_artifact_key and template_artifact_key in artifacts:
        artifact_path = artifacts[template_artifact_key]
    elif artifacts:
        # Use the first non-None artifact path
        for v in artifacts.values():
            if v:
                artifact_path = v
                break

    if not artifact_path:
        # No artifact to validate — skip (coder may have rejected)
        return

    full_path = project_root / artifact_path
    if not full_path.exists():
        return  # Artifact existence already validated by _validate_artifact_files_exist

    # Read the generated artifact
    content = full_path.read_text(encoding="utf-8")

    # Try to load template artifact for richer validation
    template_path = None
    if template_artifact_key:
        template_rel = artifacts.get(template_artifact_key)
        if template_rel:
            template_path = project_root / template_rel

    # Gather required sections and metadata from template file or inline config
    required_sections = list(inline_sections) if inline_sections else []
    required_metadata = list(inline_metadata) if inline_metadata else []

    if template_path and template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")
        # Extract sections from template as a secondary check
        # The template's section headings serve as the canonical required sections
        import re as _re
        template_headings = _re.findall(r'^#+\s+(.+)$', template_content, _re.MULTILINE)
        if template_headings and not required_sections:
            # Use template headings as required sections
            required_sections = [h.strip().strip('#').strip() for h in template_headings if h.strip()]

    if not required_sections and not required_metadata:
        return  # Nothing to validate

    # Check required sections
    missing_sections = []
    for section in required_sections:
        if not _has_section(content, section):
            missing_sections.append(section)

    # Check required metadata fields
    missing_metadata = []
    for field in required_metadata:
        if not _has_metadata_field(content, field):
            missing_metadata.append(field)

    if missing_sections or missing_metadata:
        issues = []
        if missing_sections:
            issues.append(f"missing sections: {', '.join(missing_sections)}")
        if missing_metadata:
            issues.append(f"missing metadata fields: {', '.join(missing_metadata)}")
        raise ArtifactMissingError(
            f"Template conformance failed for step {step!r} ({doc_type}): {'; '.join(issues)}"
        )

    print(f"[step_runner] template conformance OK for step={step} type={doc_type}", flush=True)


def _has_section(content: str, section: str) -> bool:
    """Check if markdown content contains a section heading (case-insensitive)."""
    import re as _re
    pattern = _re.compile(rf'^#+\s+.*{_re.escape(section)}', _re.MULTILINE | _re.IGNORECASE)
    return bool(pattern.search(content))


def _has_metadata_field(content: str, field: str) -> bool:
    """Check if metadata block contains a field."""
    import re as _re
    pattern = _re.compile(rf'^\s*-?\s*{_re.escape(field)}\s*[:：]', _re.MULTILINE)
    return bool(pattern.search(content))


# ---------------------------------------------------------------------------
# Sidecar enrichment
# ---------------------------------------------------------------------------

def enrich_sidecar(
    *,
    meta_path: Path,
    step: str,
    coder_used: str,
    invoked_at: str,
    finished_at: str,
    prompt_checksum: str,
    project_root: Path,
) -> None:
    """Atomically append runner_data section to existing meta.json.

    Never modifies coder_result. Idempotent — overwrites runner_data if present.
    """
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return  # Best-effort; should not happen after _read_and_validate_meta_json

    meta["runner_data"] = {
        "step": step,
        "coder_used": coder_used,
        "invoked_at": invoked_at,
        "finished_at": finished_at,
        "prompt_checksum": f"sha256:{prompt_checksum}",
        "enriched_at": _now_iso(),
        "runner_version": "v2",
    }

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=meta_path.parent, prefix=".tmp_", suffix=".json"
    )
    try:
        with open(tmp_fd, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2, ensure_ascii=False)
        Path(tmp_path).replace(meta_path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# Context building (prompt template variable resolution)
# ---------------------------------------------------------------------------

def build_context(
    state: dict,
    *,
    step: str = "",
    step_cfg: dict | None = None,
) -> dict[str, str]:
    """Build the full context dict for prompt rendering."""
    bundle = _workflow_module()
    ctx: dict[str, str] = dict(bundle.REFERENCE_FILES)
    artifacts = state.get("artifacts") or {}

    for key in bundle.ARTIFACT_KEYS:
        value = artifacts.get(key)
        if value:
            ctx[key] = value
            ctx[f"{key}_ABS_PATH"] = str(ARTIFACT_ROOT / value)
            p = PurePath(value)
            ctx[f"{key}_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")
        else:
            ctx[f"{key}_ABS_PATH"] = ""
            ctx[f"{key}_METAJSON"] = ""
        fp = _build_file_fingerprint(value)
        ctx[f"{key}_CHECKSUM"] = fp["checksum"]
        ctx[f"{key}_BYTES"] = str(fp["bytes"] if fp["bytes"] is not None else "")
        ctx[f"{key}_MTIME"] = str(fp["mtime"] if fp["mtime"] is not None else "")

    # For producing steps where the artifact doesn't exist yet, compute the step
    # directory meta.json path so the prompt can tell the coder where to write it.
    if step and step_cfg:
        result_key = step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context", "")
        if result_key and not ctx.get(f"{result_key}_METAJSON"):
            step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
            if not step_dir_rel:
                steps = _workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", [])
                try:
                    idx = steps.index(step) + 1
                except ValueError:
                    idx = 1
                template_group = state.get("template_group", "")
                job_id = state.get("job_id", "")
                step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"
            ctx[f"{result_key}_METAJSON"] = f"{step_dir_rel}/meta.json"
            print(f"[step_runner] Producing step {step}: {result_key}_METAJSON -> {ctx[f'{result_key}_METAJSON']}", flush=True)

    ctx["ARTIFACT_FINGERPRINTS"] = _format_artifact_fingerprint_block(artifacts)

    # Context-pack explicit path alias: CONTEXT_PACK_FILE_PATH mirrors CONTEXT_PACK_FILE
    # (the generic loop above produces CONTEXT_PACK_FILE_ABS_PATH but prompts expect _PATH)
    ctx_pack = artifacts.get("CONTEXT_PACK_FILE")
    if ctx_pack:
        ctx["CONTEXT_PACK_FILE_PATH"] = ctx_pack
    else:
        ctx["CONTEXT_PACK_FILE_PATH"] = ""

    # Task ID starting sequence: scan existing task docs to avoid collision
    task_dir = ARTIFACT_ROOT / "docs/delivery/03_tasks"
    date_code = dt.datetime.now().strftime("%Y%m%d")
    highest_task_seq = 0
    if task_dir.exists():
        for existing in task_dir.glob(f"TASK-{date_code}-*.md"):
            m = re.match(rf"TASK-{date_code}-(\d+)_", existing.stem)
            if m:
                highest_task_seq = max(highest_task_seq, int(m.group(1)))
    ctx["TASK_ID_START_SEQ"] = str(highest_task_seq + 1)  # next available sequence number

    loop_ctx = state.get("loop_context") or {}
    ctx["LOOP_ACTIVE"] = "true" if loop_ctx.get("active") else "false"
    ctx["LOOP_STEP"] = str(loop_ctx.get("loop_step") or "")
    ctx["LOOP_ITERATION"] = str(loop_ctx.get("loop_iteration") or 0)

    review_suggested = _suggested_review_file_path(state=state, step=step, step_cfg=step_cfg)
    ctx["REVIEW_FILE_SUGGESTED"] = review_suggested
    ctx["REVIEW_FILE_PATH"] = review_suggested
    # Provide meta.json path for the suggested review file
    if review_suggested:
        p = PurePath(review_suggested)
        ctx["REVIEW_FILE_SUGGESTED_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")
        ctx["REVIEW_FILE_METAJSON"] = ctx["REVIEW_FILE_SUGGESTED_METAJSON"]
        print(f"[step_runner] REVIEW PATH: {review_suggested}", flush=True)
        print(f"[step_runner] REVIEW Sidecar PATH: {ctx['REVIEW_FILE_SUGGESTED_METAJSON']}", flush=True)
    else:
        ctx["REVIEW_FILE_SUGGESTED_METAJSON"] = ""
        ctx["REVIEW_FILE_METAJSON"] = ""

    produces = (step_cfg or {}).get("produces", [])
    if "VALIDATION_FILE" in produces:
        validation_path = _build_validation_file_path(state=state, step=step, step_cfg=step_cfg)
        ctx["VALIDATION_FILE_PATH"] = validation_path
        if validation_path:
            p = PurePath(validation_path)
            ctx["VALIDATION_FILE_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")
        else:
            ctx["VALIDATION_FILE_METAJSON"] = ""
    else:
        ctx.setdefault("VALIDATION_FILE_PATH", "")
        ctx.setdefault("VALIDATION_FILE_METAJSON", "")

    replan_ctx = state.get("replan_context") or {}
    ctx["REPLAN_ACTIVE"] = "true" if replan_ctx.get("active") else "false"
    ctx["REPLAN_TRIGGER_REASON"] = str(replan_ctx.get("trigger_reason") or "")
    ctx["REPLAN_BLOCKING_ISSUES"] = "\n".join(
        f"- {issue}" for issue in replan_ctx.get("blocking_issues", [])
    )

    # Task queue / execution binding
    backend_ctx = state.get("backend_context_payload") or {}
    backend_item = backend_ctx.get("current_item") if isinstance(backend_ctx.get("current_item"), dict) else {}

    current_queue_item_id = str(
        backend_item.get("queue_item_id")
        or backend_ctx.get("CURRENT_QUEUE_ITEM_ID")
        or ""
    )
    current_task_id = str(
        backend_item.get("task_id")
        or backend_item.get("task_node_id")
        or backend_ctx.get("CURRENT_TASK_ID")
        or backend_ctx.get("CURRENT_TASK_NODE_ID")
        or ""
    )
    current_task_node_id = str(
        backend_item.get("task_node_id")
        or backend_ctx.get("CURRENT_TASK_NODE_ID")
        or current_task_id
    )
    current_task_title = str(
        backend_item.get("title")
        or backend_ctx.get("CURRENT_TASK_TITLE")
        or ""
    )

    if not (current_queue_item_id or current_task_id or current_task_node_id or current_task_title):
        from .job_state import task_queue_current_item, task_execution_binding_current_item
        current_item = task_queue_current_item(state) or task_execution_binding_current_item(state)
        current_queue_item_id = str((current_item or {}).get("queue_item_id") or "")
        current_task_id = str(
            (current_item or {}).get("task_id")
            or (current_item or {}).get("task_node_id")
            or ""
        )
        current_task_node_id = str(
            (current_item or {}).get("task_node_id") or current_task_id
        )
        current_task_title = str((current_item or {}).get("title") or "")

    ctx["CURRENT_QUEUE_ITEM_ID"] = current_queue_item_id
    ctx["CURRENT_TASK_ID"] = current_task_id
    ctx["CURRENT_TASK_NODE_ID"] = current_task_node_id
    ctx["CURRENT_TASK_TITLE"] = current_task_title

    backend_task_file_path = str(backend_ctx.get("TASK_FILE_PATH") or "")
    backend_task_file_meta = str(backend_ctx.get("TASK_FILE_METAJSON") or "")
    if backend_task_file_path:
        ctx["TASK_FILE_PATH"] = backend_task_file_path
        ctx["TASK_FILE_METAJSON"] = backend_task_file_meta or str(PurePath(backend_task_file_path).parent / f"{PurePath(backend_task_file_path).stem}.meta.json")
    elif current_task_node_id:
        task_path, meta_path = compute_paths(
            node_id=current_task_node_id,
            title=current_task_title,
            output_dir="docs/delivery/03_tasks",
        )
        ctx["TASK_FILE_PATH"] = task_path
        ctx["TASK_FILE_METAJSON"] = meta_path

    # Pre-compute output paths for steps that create NEW files.
    # When the artifact is already in artifacts (refine/replan/executor), the loop above
    # already populated METAJSON from the existing path — no override needed.
    produces = (step_cfg or {}).get("produces", [])

    _set_delivery_scaffold_aliases(
        ctx=ctx,
        state=state,
        step=step,
        artifacts=artifacts,
        produces=produces,
    )

    # Print expected output paths BEFORE the agent starts (for visibility)
    if produces:
        print(f"[step_runner] step={step} produces={produces}", flush=True)

    if "PRE_INIT_FILE" in produces and not artifacts.get("PRE_INIT_FILE"):
        pre_init_path = str(backend_ctx.get("PRE_INIT_FILE_PATH") or "")
        if not pre_init_path:
            pre_init_path = _build_pre_init_file_path(state=state)
        if pre_init_path:
            ctx["PRE_INIT_FILE_PATH"] = pre_init_path
            pre_init_meta = str(backend_ctx.get("PRE_INIT_FILE_METAJSON") or "")
            p = PurePath(pre_init_path)
            ctx["PRE_INIT_FILE_METAJSON"] = pre_init_meta or str(p.parent / f"{p.stem}.meta.json")
            print(f"[step_runner] PRE_INIT PATH: {pre_init_path}", flush=True)
            print(f"[step_runner] PRE_INIT Sidecar PATH: {ctx['PRE_INIT_FILE_METAJSON']}", flush=True)

    if "PLAN_FILE" in produces and not artifacts.get("PLAN_FILE"):
        plan_path = str(backend_ctx.get("PLAN_FILE_PATH") or "")
        if not plan_path:
            plan_path = _build_plan_file_path(state=state)
        if plan_path:
            ctx["PLAN_FILE_PATH"] = plan_path
            plan_meta = str(backend_ctx.get("PLAN_FILE_METAJSON") or "")
            p = PurePath(plan_path)
            ctx["PLAN_FILE_METAJSON"] = plan_meta or str(p.parent / f"{p.stem}.meta.json")
            stem_match = re.match(r"(PLAN-\d{8}-\d+)", p.stem)
            ctx["PLAN_ID"] = str(backend_ctx.get("PLAN_ID") or (stem_match.group(1) if stem_match else ""))
            print(f"[step_runner] PLAN ID: {ctx['PLAN_ID']}", flush=True)
            print(f"[step_runner] PLAN PATH: {plan_path}", flush=True)
            print(f"[step_runner] PLAN Sidecar PATH: {ctx['PLAN_FILE_METAJSON']}", flush=True)

    if "TASK_GRAPH_FILE" in produces and not artifacts.get("TASK_GRAPH_FILE"):
        tg_path = str(backend_ctx.get("TASK_GRAPH_FILE_PATH") or "")
        if not tg_path:
            tg_path = _build_task_graph_file_path(state=state)
        if tg_path:
            ctx["TASK_GRAPH_FILE_PATH"] = tg_path
            tg_meta = str(backend_ctx.get("TASK_GRAPH_FILE_METAJSON") or "")
            p = PurePath(tg_path)
            ctx["TASK_GRAPH_FILE_METAJSON"] = tg_meta or str(p.parent / f"{p.stem}.meta.json")
            print(f"[step_runner] TASK_GRAPH PATH: {tg_path}", flush=True)
            print(f"[step_runner] TASK_GRAPH Sidecar PATH: {ctx['TASK_GRAPH_FILE_METAJSON']}", flush=True)

    if "TASK_FILE" in produces and not artifacts.get("TASK_FILE"):
        task_path = ctx.get("TASK_FILE_PATH", "")
        task_meta = ctx.get("TASK_FILE_METAJSON", "")
        if task_path:
            task_node = ctx.get("CURRENT_TASK_NODE_ID", "")
            print(f"[step_runner] TASK ID: {task_node}", flush=True)
            print(f"[step_runner] TASK PATH: {task_path}", flush=True)
            print(f"[step_runner] TASK Sidecar PATH: {task_meta}", flush=True)

    if "IMPL_FILE" in produces and not artifacts.get("IMPL_FILE"):
        impl_path = str(backend_ctx.get("IMPL_FILE_PATH") or "")
        if not impl_path:
            impl_path = _build_impl_file_path(state=state)
        if impl_path:
            ctx["IMPL_FILE_PATH"] = impl_path
            impl_meta = str(backend_ctx.get("IMPL_FILE_METAJSON") or "")
            p = PurePath(impl_path)
            ctx["IMPL_FILE_METAJSON"] = impl_meta or str(p.parent / f"{p.stem}.meta.json")
            print(f"[step_runner] IMPL PATH: {impl_path}", flush=True)
            print(f"[step_runner] IMPL Sidecar PATH: {ctx['IMPL_FILE_METAJSON']}", flush=True)

    if "IMAGE_DESC_FOLDER" in produces and not artifacts.get("IMAGE_DESC_FOLDER"):
        image_folder = artifacts.get("IMAGE_FOLDER")
        if image_folder:
            ctx["IMAGE_DESC_FOLDER"] = image_folder
            ctx["IMAGE_DESC_FOLDER_METAJSON"] = str(Path(image_folder) / "meta.json")
            print(f"[step_runner] IMAGE_DESC FOLDER: {image_folder}", flush=True)
            print(f"[step_runner] IMAGE_DESC METAJSON PATH: {ctx['IMAGE_DESC_FOLDER_METAJSON']}", flush=True)

    # IMAGE_CSV path resolution — always compute context variables so prompt templates
    # can reference {IMAGE_CSV_RUN_DIR} and {IMAGE_CSV_JSON_METAJSON} on both new and
    # refine steps.  Reuse existing artifact path when available to keep the same
    # date-stamped run directory across refine-loop iterations.
    if "IMAGE_CSV_JSON" in produces:
        existing_csv_json = artifacts.get("IMAGE_CSV_JSON")
        if existing_csv_json:
            # Reuse the run directory from a prior step (gen_prompts already ran).
            p = PurePath(existing_csv_json)
            # existing_csv_json is typically "source_csv/YYYYMMDD-NNN/"
            run_dir = p.name.rstrip("/") or p.parts[-1] if p.parts else ""
            if run_dir:
                ctx["IMAGE_CSV_RUN_DIR"] = str(p.parent / run_dir)
                ctx["IMAGE_CSV_JSON_METAJSON"] = str(p.parent / run_dir / "meta.json")
        else:
            # First run — compute next sequential run number for today.
            image_folder = artifacts.get("IMAGE_FOLDER")
            if image_folder:
                date_code = dt.datetime.now().strftime("%Y%m%d")
                csv_root = ARTIFACT_ROOT / "source_csv"
                highest_run = 0
                if csv_root.exists():
                    for existing in csv_root.glob(f"{date_code}-*"):
                        if existing.is_dir():
                            m = re.match(rf"{date_code}-(\d+)$", existing.name)
                            if m:
                                highest_run = max(highest_run, int(m.group(1)))
                run_num = f"{highest_run + 1:03d}"
                run_dir = f"{date_code}-{run_num}"
                ctx["IMAGE_CSV_RUN_DIR"] = str(Path("source_csv") / run_dir)
                ctx["IMAGE_CSV_JSON_METAJSON"] = str(Path("source_csv") / run_dir / "meta.json")
        if ctx.get("IMAGE_CSV_RUN_DIR"):
            print(f"[step_runner] IMAGE_CSV RUN_DIR: {ctx['IMAGE_CSV_RUN_DIR']}", flush=True)
            print(f"[step_runner] IMAGE_CSV METAJSON PATH: {ctx['IMAGE_CSV_JSON_METAJSON']}", flush=True)

    # Task source traceability
    task_meta = _task_source_traceability_metadata(state)
    ctx["SOURCE_TASK_GRAPH_ID"] = str(task_meta.get("Source Task Graph ID") or "")
    ctx["SOURCE_TASK_NODE_ID"] = str(task_meta.get("Source Task Node ID") or "")

    # Review step metadata
    if step_cfg:
        review_target = (step_cfg.get("on_reject_refine") or {}).get("artifact", "")
        ctx["REVIEW_TARGET_ARTIFACT"] = str(review_target or "")
        ctx.update(_review_prompt_metadata_context(state=state, step=step, step_cfg=step_cfg))

    # ComfyUI submission context
    produces = (step_cfg or {}).get("produces", [])
    if "IMAGE_CSV_SUBMIT_RESULT" in produces:
        run_dir = ctx.get("IMAGE_CSV_RUN_DIR", "")
        if not run_dir:
            # Fallback: derive from existing IMAGE_CSV_JSON artifact (produced by gen_prompts)
            existing = artifacts.get("IMAGE_CSV_JSON", "")
            if existing:
                p = PurePath(existing)
                run_dir = p.name.rstrip("/") or p.parts[-1] if p.parts else ""
                if run_dir:
                    run_dir = str(p.parent / run_dir)
        if run_dir:
            ctx["IMAGE_CSV_RUN_DIR"] = run_dir
            ctx["IMAGE_CSV_SUBMIT_RESULT_PATH"] = str(Path(run_dir) / "submission_results.json")
            ctx["IMAGE_CSV_SUBMIT_RESULT_METAJSON"] = str(Path(run_dir) / "submission_results.meta.json")
            print(f"[step_runner] SUBMIT RESULT PATH: {ctx['IMAGE_CSV_SUBMIT_RESULT_PATH']}", flush=True)
            print(f"[step_runner] SUBMIT METAJSON PATH: {ctx['IMAGE_CSV_SUBMIT_RESULT_METAJSON']}", flush=True)
        else:
            ctx["IMAGE_CSV_SUBMIT_RESULT_PATH"] = ""
            ctx["IMAGE_CSV_SUBMIT_RESULT_METAJSON"] = ""

    return ctx


def render_prompt(template_text: str, context: dict[str, str]) -> str:
    rendered = template_text
    for key, value in context.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def prompt_checksum(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def resolve_prompt_path(*, step_cfg: dict, coder: str, model_id: str | None = None) -> Path:
    """Resolve prompt file path with three-level fallback.

    Resolution order:
      1. {stem}_{model_id}{suffix}  e.g. 06_task_deepseek-chat.txt  (if model_id given)
      2. {stem}_{coder}{suffix}     e.g. 06_task_qwen.txt
      3. {stem}{suffix}             e.g. 06_task.txt  (default)
    """
    default_path = RUNNER_ROOT / step_cfg["prompt_file"]
    path_obj = Path(step_cfg["prompt_file"])

    if model_id:
        model_specific = RUNNER_ROOT / str(
            path_obj.parent / f"{path_obj.stem}_{model_id}{path_obj.suffix}"
        )
        if model_specific.exists():
            print(f"[step_runner] Using model-id-specific prompt: {model_specific.relative_to(RUNNER_ROOT)}", flush=True)
            return model_specific

    coder_specific = RUNNER_ROOT / str(
        path_obj.parent / f"{path_obj.stem}_{coder}{path_obj.suffix}"
    )
    if coder_specific.exists():
        print(f"[step_runner] Using coder-specific prompt: {coder_specific.relative_to(RUNNER_ROOT)}", flush=True)
        return coder_specific

    print(f"[step_runner] Using default prompt: {default_path.relative_to(RUNNER_ROOT)}", flush=True)
    return default_path


# ---------------------------------------------------------------------------
# Review / validation path helpers
# ---------------------------------------------------------------------------

def _review_target_artifact_key(step_cfg: dict) -> str | None:
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    if on_reject_refine.get("artifact"):
        return str(on_reject_refine["artifact"])
    produces = step_cfg.get("produces", [])
    if step_cfg.get("requires_human_approval_after") and produces:
        return str(produces[0])
    return None


def _review_filename_date_code() -> str:
    return dt.datetime.now().strftime("%y%m%d")


def _review_step_code(step: str) -> str:
    return {
        "review_impl": "rimpl",
        "review_pre_init": "rpre",
        "review_planner": "rplan",
        "review_task": "rtask",
        "review_task_graph": "rtg",
        "review_prompts": "rcsv",
    }.get(step, "")


def _normalize_review_slug(value: str, *, max_length: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.strip().lower().replace("_", "-").replace(" ", "-"))
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return (slug[:max_length].rstrip("-") if len(slug) > max_length else slug) or "review"


def _derive_review_slug_from_artifact_path(path_value: str) -> str:
    stem = Path(path_value).stem
    for pattern in [
        r"^PRE-INIT-\d{8}-\d+[_-]?",
        r"^INIT-\d{8}-\d+[_-]?",
        r"^PLAN-\d{8}-\d+[_-]?",
        r"^TASK-GRAPH-\d{8}-PLAN-\d{8}-\d+[_-]?",
        r"^TASK-\d{8}-\d+[_-]?",
        r"^IMPL-\d{8}-TASK-\d{8}-\d+[_-]?",
        r"^IMPL-\d{8}-\d+[_-]?",
    ]:
        stem = re.sub(pattern, "", stem, count=1)
    return _normalize_review_slug(stem)


def _build_review_target_identifier(*, artifact_key: str, artifact_path: str) -> str:
    name = Path(artifact_path).name
    matches = re.findall(r"(\d{8})-(\d+)", name)
    if matches:
        yyyymmdd, seq = matches[-1]
        mmdd, seq = yyyymmdd[4:8], seq.zfill(2)
    else:
        mmdd, seq = "0000", "00"
    prefix = {"PRE_INIT_FILE": "I", "INIT_FILE": "I", "PLAN_FILE": "P",
               "TASK_GRAPH_FILE": "G", "TASK_FILE": "T", "IMPL_FILE": "M",
               "IMAGE_CSV_JSON": "C"}.get(artifact_key, "R")
    return f"{prefix}-{mmdd}-{seq}"


def _build_new_review_file_path(*, state: dict, step: str, step_cfg: dict) -> str:
    artifact_key = _review_target_artifact_key(step_cfg)
    if not artifact_key:
        return ""
    artifact_path = (state.get("artifacts") or {}).get(artifact_key)
    if not artifact_path:
        return ""
    step_code = _review_step_code(step)
    if not step_code:
        return ""
    tid = _build_review_target_identifier(artifact_key=artifact_key, artifact_path=artifact_path)
    slug = _derive_review_slug_from_artifact_path(artifact_path)
    review_dir = ARTIFACT_ROOT / "docs/delivery/05_reviews"
    date_code = _review_filename_date_code()

    # Find highest sequence number already used for this date (any slug/step/tid)
    highest_seq = 0
    for existing in review_dir.glob(f"REV-{date_code}-*.md"):
        m = re.match(rf"REV-{date_code}-(\d+)_", existing.stem)
        if m:
            highest_seq = max(highest_seq, int(m.group(1)))

    seq = highest_seq + 1
    while True:
        candidate = review_dir / f"REV-{date_code}-{seq:02d}_{step_code}_{tid}_{slug}.md"
        if not candidate.exists():
            p = PurePath(str(candidate.relative_to(ARTIFACT_ROOT)))
            return str(p)
        seq += 1


def _suggested_review_file_path(
    *, state: dict, step: str, step_cfg: dict | None = None
) -> str:
    ctx = state.get("loop_context") or {}
    if not ctx.get("active") or step != ctx.get("loop_step") or not ctx.get("loop_source_review"):
        if step_cfg:
            return _build_new_review_file_path(state=state, step=step, step_cfg=step_cfg)
        return ""
    next_iteration = int(ctx.get("loop_iteration", 0)) + 1
    review_path = Path(ctx["loop_source_review"])
    stem = review_path.stem
    stem = (
        re.sub(r"_iter\d+$", f"_iter{next_iteration}", stem)
        if re.search(r"_iter\d+$", stem)
        else f"{stem}_iter{next_iteration}"
    )
    return str(review_path.with_name(f"{stem}{review_path.suffix}"))


def _build_validation_file_path(*, state: dict, step: str, step_cfg: dict) -> str:
    impl_path = (state.get("artifacts") or {}).get("IMPL_FILE")
    if not impl_path:
        return ""
    tid = _build_review_target_identifier(artifact_key="IMPL_FILE", artifact_path=impl_path)
    slug = _derive_review_slug_from_artifact_path(impl_path)
    review_dir = ARTIFACT_ROOT / "docs/delivery/05_reviews"
    seq = 1
    while True:
        candidate = review_dir / f"VALIDATION-{_review_filename_date_code()}-{tid}_{slug}.md"
        if seq > 1:
            candidate = review_dir / f"VALIDATION-{_review_filename_date_code()}-{seq}-{tid}_{slug}.md"
        if not candidate.exists():
            return str(PurePath(str(candidate.relative_to(ARTIFACT_ROOT))))
        seq += 1


def _build_pre_init_file_path(*, state: dict) -> str:
    """Compute collision-free path for a new pre-init artifact.

    Sequence number is global per date (not per-slug) to avoid ID collisions.
    """
    draft_path = (state.get("artifacts") or {}).get("DRAFT_INIT_FILE", "")
    slug = _derive_review_slug_from_artifact_path(draft_path) if draft_path else "pre-init"
    pre_init_dir = ARTIFACT_ROOT / "docs/delivery/01_initiatives/pre_init"
    date_code = dt.datetime.now().strftime("%Y%m%d")

    # Find highest sequence number already used for this date (any slug)
    highest_seq = 0
    for existing in pre_init_dir.glob(f"PRE-INIT-{date_code}-*.md"):
        m = re.match(rf"PRE-INIT-{date_code}-(\d+)_", existing.stem)
        if m:
            highest_seq = max(highest_seq, int(m.group(1)))

    seq = highest_seq + 1
    while True:
        candidate = pre_init_dir / f"PRE-INIT-{date_code}-{seq:02d}_{slug}.md"
        if not candidate.exists():
            return str(PurePath(str(candidate.relative_to(ARTIFACT_ROOT))))
        seq += 1


def _build_plan_file_path(*, state: dict) -> str:
    """Compute collision-free path for a new plan artifact.

    Sequence number is global per date (not per-slug) so that the Plan ID
    embedded in the document metadata never collides across different plans
    created on the same day.
    """
    init_path = (state.get("artifacts") or {}).get("INIT_FILE", "")
    slug = _derive_review_slug_from_artifact_path(init_path) if init_path else "plan"
    plan_dir = ARTIFACT_ROOT / "docs/delivery/02_plans"
    date_code = dt.datetime.now().strftime("%Y%m%d")

    # Find highest sequence number already used for this date (any slug)
    highest_seq = 0
    for existing in plan_dir.glob(f"PLAN-{date_code}-*.md"):
        m = re.match(rf"PLAN-{date_code}-(\d+)_", existing.stem)
        if m:
            highest_seq = max(highest_seq, int(m.group(1)))

    seq = highest_seq + 1
    while True:
        candidate = plan_dir / f"PLAN-{date_code}-{seq:02d}_{slug}.md"
        if not candidate.exists():
            return str(PurePath(str(candidate.relative_to(ARTIFACT_ROOT))))
        seq += 1


def _build_task_graph_file_path(*, state: dict) -> str:
    """Compute path for a task graph artifact.

    Naming: TASK-GRAPH-{YYYYMMDD}-{PLAN-YYYYMMDD-NN}.md
    The task graph is unique per plan — no -seq fallback needed.
    If the file already exists from a prior aborted run, the agent overwrites it.
    """
    plan_path = (state.get("artifacts") or {}).get("PLAN_FILE", "")
    if not plan_path:
        return ""
    plan_stem = Path(plan_path).stem  # e.g. "PLAN-20260413-01_slug"
    m = re.match(r"(PLAN-\d{8}-\d+)", plan_stem)
    plan_id = m.group(1) if m else "PLAN-00000000-00"
    tg_dir = ARTIFACT_ROOT / "docs/delivery/02_plans/artifacts"
    date_code = dt.datetime.now().strftime("%Y%m%d")
    candidate = tg_dir / f"TASK-GRAPH-{date_code}-{plan_id}.md"
    return str(PurePath(str(candidate.relative_to(ARTIFACT_ROOT))))


def _build_impl_file_path(*, state: dict) -> str:
    """Compute a collision-free path for a new implementation plan file.

    Naming: docs/delivery/04_implementation_plans/IMPL-YYYYMMDD-NN_title-slug.md
    Sequence number is global per date (not per-slug) to avoid ID collisions.
    """
    from .job_state import task_execution_binding_current_item, task_queue_current_item

    current_item = task_queue_current_item(state) or task_execution_binding_current_item(state)
    title = str((current_item or {}).get("title") or "")
    slug = _normalize_review_slug(title, max_length=60) if title else "impl"
    impl_dir = ARTIFACT_ROOT / "docs/delivery/04_implementation_plans"
    date_code = dt.datetime.now().strftime("%Y%m%d")  # YYYYMMDD — matches existing naming convention

    # Find highest sequence number already used for this date (any slug)
    highest_seq = 0
    for existing in impl_dir.glob(f"IMPL-{date_code}-*.md"):
        m = re.match(rf"IMPL-{date_code}-(\d+)_", existing.stem)
        if m:
            highest_seq = max(highest_seq, int(m.group(1)))

    seq = highest_seq + 1
    while True:
        candidate = impl_dir / f"IMPL-{date_code}-{seq:02d}_{slug}.md"
        if not candidate.exists():
            return str(PurePath(str(candidate.relative_to(ARTIFACT_ROOT))))
        seq += 1


def _review_prompt_metadata_context(*, state: dict, step: str, step_cfg: dict) -> dict[str, str]:
    artifact_key = _review_target_artifact_key(step_cfg)
    if not artifact_key:
        return {}
    artifact_path = (state.get("artifacts") or {}).get(artifact_key)
    if not artifact_path:
        return {}
    path = ARTIFACT_ROOT / artifact_path
    if not path.exists() or not path.is_file():
        return {}

    content = path.read_text(encoding="utf-8")
    raw_status = _extract_document_status(content) or ""
    normalized_status = re.sub(r"\s+", "_", raw_status.strip().lower().replace("-", "_"))

    review_decision = (_extract_metadata_value(content, "Review Decision") or "").strip()
    model_reviewer = (_extract_metadata_value(content, "Model Reviewer") or "").strip()
    reviewed_at = (_extract_metadata_value(content, "Reviewed At") or "").strip()

    active_review_placeholders_valid = (
        normalized_status == "in_review"
        and review_decision.upper() == "PENDING"
        and reviewed_at.upper() == "TBD"
    )

    return {
        "REVIEW_TARGET_STATUS_RAW": raw_status or "MISSING",
        "REVIEW_TARGET_STATUS_NORMALIZED": normalized_status or "missing",
        "REVIEW_TARGET_STATUS_IS_ALLOWED": "true" if normalized_status in {
            "draft", "in_review", "changes_requested", "pending_human_approval"
        } else "false",
        "REVIEW_METADATA_REVIEW_DECISION": review_decision or "MISSING",
        "REVIEW_METADATA_MODEL_REVIEWER": model_reviewer or "MISSING",
        "REVIEW_METADATA_REVIEWED_AT": reviewed_at or "MISSING",
        "REVIEW_METADATA_IS_ACTIVE_REVIEW_CONTEXT": "true" if normalized_status == "in_review" else "false",
        "REVIEW_METADATA_PLACEHOLDERS_VALID": "true" if active_review_placeholders_valid else "false",
        "REVIEW_METADATA_BOOKKEEPING_ONLY": (
            "Review metadata fields are runner-managed workflow bookkeeping. "
            "Do not reject based on them alone when REVIEW_METADATA_PLACEHOLDERS_VALID=true."
        ),
        "REVIEW_STATUS_NORMALIZATION_NOTE": (
            "Treat case and underscore/space variants as equivalent lifecycle values. "
            "Canonical machine form is snake_case, e.g. IN_REVIEW == in_review."
        ),
    }


# ---------------------------------------------------------------------------
# Fingerprint helpers
# ---------------------------------------------------------------------------

def _build_file_fingerprint(path_value: str | None) -> dict:
    fp: dict = {"checksum": "", "bytes": None, "mtime": None}
    if not path_value:
        return fp
    path = ARTIFACT_ROOT / path_value
    if not path.exists() or not path.is_file():
        return fp
    stat = path.stat()
    fp["checksum"] = hashlib.sha256(path.read_bytes()).hexdigest()
    fp["bytes"] = stat.st_size
    fp["mtime"] = stat.st_mtime_ns
    return fp


def _format_artifact_fingerprint_block(artifacts: dict) -> str:
    lines = []
    bundle = _workflow_module()
    for key in bundle.ARTIFACT_KEYS:
        value = artifacts.get(key)
        if not value:
            continue
        fp = _build_file_fingerprint(value)
        if fp["checksum"]:
            lines.append(
                f"- {key}: checksum={fp['checksum']}, bytes={fp['bytes']}, mtime={fp['mtime']}"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Task traceability
# ---------------------------------------------------------------------------

def _task_source_traceability_metadata(state: dict) -> dict[str, str | None]:
    task_graph_file = str((state.get("artifacts") or {}).get("TASK_GRAPH_FILE") or "").strip()
    source_task_graph_id: str | None = None
    if task_graph_file:
        tgp = ARTIFACT_ROOT / task_graph_file
        if tgp.exists() and tgp.is_file():
            content = tgp.read_text(encoding="utf-8")
            source_task_graph_id = (_extract_metadata_value(content, "Task Graph ID") or "").strip() or None

    from .job_state import task_queue_current_item, task_execution_binding_current_item
    current_item = task_queue_current_item(state) or task_execution_binding_current_item(state)
    source_task_node_id = str(
        (current_item or {}).get("task_node_id") or (current_item or {}).get("task_id") or ""
    ).strip() or None

    return {"Source Task Graph ID": source_task_graph_id, "Source Task Node ID": source_task_node_id}


# ---------------------------------------------------------------------------
# Document metadata helpers
# ---------------------------------------------------------------------------

def _extract_document_status(content: str) -> str | None:
    val = _extract_metadata_value(content, "Status")
    if val is not None:
        return val
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("status:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _extract_metadata_value(content: str, key: str) -> str | None:
    pattern = re.compile(
        rf"^\s*[-*]\s*(?:\*\*)?{re.escape(key)}(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    for line in content.splitlines():
        m = pattern.match(line.strip())
        if m:
            return m.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save_text(path: Path, content: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def _save_json_atomic(path: Path, data: Any) -> None:
    _ensure_dir(path.parent)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".tmp_", suffix=".json")
    try:
        with open(tmp_fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        Path(tmp_path).replace(path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def _save_debug_failure(
    *,
    step_dir: Path,
    command: list | None = None,
    return_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
    raw_events: list | None = None,
    error_message: str = "",
) -> None:
    _ensure_dir(step_dir)
    if stdout:
        _save_text(step_dir / "raw_output.txt", stdout)
    if stderr:
        _save_text(step_dir / "stderr.txt", stderr)
    if raw_events:
        _write_raw_events_jsonl(step_dir / "raw_events.jsonl", raw_events)
    payload = {
        "error_message": error_message,
        "command": command,
        "return_code": return_code,
    }
    _save_json_atomic(step_dir / "invoke_error.json", payload)


def _write_raw_events_jsonl(path: Path, lines: list | None) -> None:
    if not lines:
        return
    _ensure_dir(path.parent)
    path.write_text("\n".join(lines), encoding="utf-8")
