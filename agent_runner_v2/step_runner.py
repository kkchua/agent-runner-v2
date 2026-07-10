#!/usr/bin/env python3
"""
step_runner.py — Core step execution contract for agent_runner_v2.

Single responsibility: invoke coder → read meta.json → validate artifacts → enrich sidecar.

Related: IMPL-20260422-04, PLAN-20260608-01

Key v2 differences from v1:
- meta.json sidecar is the ONLY communication channel (no fallbacks, no stdout JSON parsing)
- No pre-invocation sidecar writes
- No recovery functions
- Raises exceptions on failure; caller routes them
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any

from .artifact_paths import compute_paths
from .coder_adapters import CoderInvocationError, dataclass_dict, invoke_coder
from .exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError
from .doc_paths import (
    docs_root_rel,
    architecture_site_rel,
    codebase_doc_rel,
    delivery_doc_rel,
    system_doc_rel,
)
from .constants import (
    BUG_FIX_OUTPUT_PATHS as CONSTANTS_BUG_FIX_OUTPUT_PATHS,
    FOLDER_KEY_DELIVERY_IMPLEMENTATIONS,
    FOLDER_KEY_DELIVERY_TASKS,
    FOLDER_KEY_DELIVERY_PLANS,
    FOLDER_KEY_DELIVERY_INITIATIVES,
    FOLDER_KEY_DELIVERY_REVIEWS,
    FOLDER_KEY_CODEBASE_CHANGES,
    FOLDER_KEY_SYSTEM_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,
    EXT_MD,
    EXT_JSON,
    known_artifact_paths,
    prompt_literal_substitutions,
    SIDECAR_INSTRUCTION_TEMPLATE as CONSTANTS_SIDECAR_INSTRUCTION_TEMPLATE,
    TOOL_INSTRUCTION_TEMPLATE as CONSTANTS_TOOL_INSTRUCTION_TEMPLATE,
)
from .runtime_context import (
    ARTIFACT_ROOT,
    JOBS_ROOT,
    PACKAGE_ROOT,
    RUNNER_ROOT,
    PathProxy,
    artifact_rel_to_meta_rel,
    get_workflow_module,
    resolve_repo_or_runtime_path,
)
from .documentation_guardrails import (
    MASTER_BOOTSTRAP_WORKFLOWS,
    master_bootstrap_artifact_candidates,
)


RESULT_SCHEMA_PATH = PathProxy(lambda: Path(RUNNER_ROOT) / "llm_response_schema.json")


# ---------------------------------------------------------------------------
# Automatic sidecar instruction injection template
# ---------------------------------------------------------------------------

SIDECAR_INSTRUCTION_TEMPLATE = """

═══════════════════════════════════════════════════════════
CRITICAL: RESULT REPORTING REQUIREMENT (AUTOMATED INJECTION)
═══════════════════════════════════════════════════════════

After completing your work, you MUST report results via meta.json sidecar.

**Sidecar path**: `{META_JSON_PATH}`

**Required steps**:
1. Write your artifact file(s) to disk using write_file tool
2. Verify each artifact file exists on disk
3. Create the meta.json sidecar using write_file tool with this EXACT structure:
   {{
     "schema_version": "v2",
     "coder_result": {{
       "status": "APPROVED" or "REJECTED",
       "remark": "Brief summary of what you accomplished",
       "artifacts": {{
         {ARTIFACT_ENTRIES}
       }},
       "recorded_at": "{CURRENT_TIMESTAMP}"
     }}
   }}
4. Verify meta.json exists on disk before finishing

**Status decision rule**:
- Return APPROVED only if ALL required artifacts exist on disk AND meta.json is written
- Return REJECTED if any artifact is missing or cannot be created

**Output format rule**:
- Return ONLY valid JSON matching this structure:
  {{
    "status": "APPROVED" or "REJECTED",
    "remark": "<summary>",
    "artifacts": {{
      {ARTIFACT_ENTRIES}
    }}
  }}
- Do NOT return markdown, explanations, or conversational text
- The runner reads results ONLY from meta.json and your JSON output

**Verification requirement**:
- You MUST verify files exist on disk before returning APPROVED
- Use exact artifact paths provided in context variables above

This requirement is MANDATORY — failure to follow these steps will cause workflow failure.
═══════════════════════════════════════════════════════════
"""


CODER_SOP_INSTRUCTION_TEMPLATE = """

===========================================================================
MANDATORY CODER SOP
===========================================================================
Before implementing any logic, read and follow:
{CODER_IMPLEMENTATION_SOP_PATH}

Minimum required behavior:
- Re-read the current source-of-truth files from disk before making decisions
- Inspect existing code paths before assuming runtime behavior
- Refactor duplicated execution logic toward one shared helper or transition path
- Do not add new parallel logic for workflow completion, failure, notifications, or artifacts
- Add or update tests proving all affected execution modes follow the same behavior

This SOP is repository-wide and applies to all coder backends for this step.
===========================================================================
"""


def _workflow_module():
    module = get_workflow_module()
    if module is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    return module


def _path_for_report(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


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
    _validate_step_write_contract_config(step_cfg=step_cfg, step=step)
    allowed_write_paths = _resolve_allowed_write_paths(
        step_cfg=step_cfg,
        context=context,
        state=state,
        project_root=project_root,
        meta_path=meta_path,
    )
    audit_before = _snapshot_allowed_write_roots(
        allowed_paths=allowed_write_paths,
        project_root=project_root,
    )

    try:
        timeout_seconds = step_cfg.get("coder_timeout_seconds")
        if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            timeout_seconds = None
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
            timeout_seconds_override=timeout_seconds,
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
    changed_paths = _verify_only_allowed_paths_changed(
        before=audit_before,
        allowed_paths=allowed_write_paths,
        project_root=project_root,
        step=step,
    )

    # Save invocation artefacts
    _save_text(step_dir / "raw_output.txt", invocation.stdout)
    if invocation.stderr:
        _save_text(step_dir / "stderr.txt", invocation.stderr)
    _save_json_atomic(step_dir / "usage.json", dataclass_dict(invocation.usage))
    _save_json_atomic(step_dir / "step_manifest.json", dataclass_dict(invocation.manifest))
    _write_raw_events_jsonl(step_dir / "raw_events.jsonl", invocation.raw_events)

    # Read and validate meta.json. If the coder produced a direct result object
    # instead of a wrapped v2 sidecar, repair it into the expected schema.
    meta = _repair_or_validate_meta_json(
        meta_path=meta_path,
        parsed_result=invocation.parsed_result,
    )
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

    # Validate artifacts are in the produces list (declarative protection model)
    produces = step_cfg.get("produces", [])
    _validate_artifacts_in_produces_list(
        artifacts=artifacts,
        produces=produces,
        step=step,
    )

    artifacts = _canonicalize_master_bootstrap_artifacts(
        artifacts=artifacts,
        project_root=project_root,
        state=state,
    )

    # Print Doc ID and sidecar file path to console for visibility
    result_key = step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context", "")
    artifact_path = artifacts.get(result_key, "") if result_key else ""
    try:
        meta_rel = str(meta_path.relative_to(project_root))
    except ValueError:
        meta_rel = str(meta_path)
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
        allowed_write_paths=sorted(_path_for_report(path, project_root) for path in allowed_write_paths),
        changed_paths=changed_paths,
    )

    return StepResult(
        status=coder_result["status"],
        remark=str(coder_result.get("remark") or ""),
        artifacts=artifacts,
        reject_code=coder_result.get("reject_code") or None,
        meta_json_path=_path_for_report(meta_path, project_root),
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
    step_dir: Path,
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
    meta_path = _resolve_meta_json_path(
        step_cfg=step_cfg,
        context=context,
        project_root=project_root,
        step_dir=step_dir,
    )

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

    # Write meta.json from ActionResult automatically so actions don't
    # need to manage sidecar files themselves.
    _save_json_atomic(meta_path, {
        "schema_version": "v2",
        "coder_result": {
            "status": result.status,
            "remark": result.remark,
            "artifacts": dict(result.artifacts or {}),
            "recorded_at": finished_at,
        },
    })

    # Validate the action wrote a meta.json
    meta = _read_and_validate_meta_json(meta_path)
    coder_result = meta["coder_result"]

    # Validate artifact files exist on disk
    artifacts = dict(coder_result.get("artifacts") or {})
    _validate_artifact_files_exist(artifacts=artifacts, project_root=project_root)

    # Validate artifacts are in the produces list (declarative protection model)
    produces = step_cfg.get("produces", [])
    _validate_artifacts_in_produces_list(
        artifacts=artifacts,
        produces=produces,
        step=step,
    )

    # Enrich sidecar with runner_data
    enrich_sidecar(
        meta_path=meta_path,
        step=step,
        coder_used="action",
        invoked_at=invoked_at,
        finished_at=finished_at,
        prompt_checksum="n/a",
        project_root=project_root,
        allowed_write_paths=[],
        changed_paths=[],
    )

    return StepResult(
        status=coder_result["status"],
        remark=str(coder_result.get("remark") or ""),
        artifacts=artifacts,
        reject_code=coder_result.get("reject_code") or None,
        meta_json_path=_path_for_report(meta_path, project_root),
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
        value = context.get(from_ctx_key, "")
        if value:
            if from_ctx_key.endswith("_METAJSON"):
                # Key already points to a pre-resolved .meta.json path — use directly
                meta_rel = value
            else:
                # Key points to an artifact path — derive the .meta.json sidecar path
                meta_rel = artifact_rel_to_meta_rel(value)
            return resolve_repo_or_runtime_path(meta_rel, project_root=project_root, runtime_root=JOBS_ROOT)

    result_key = step_cfg.get("result_meta_key")
    if result_key:
        meta_rel = context.get(f"{result_key}_METAJSON", "")
        if meta_rel:
            return resolve_repo_or_runtime_path(meta_rel, project_root=project_root, runtime_root=JOBS_ROOT)

    # Fallback: use step directory for producing steps (artifact not yet created)
    if step_dir is not None:
        fallback = step_dir / "meta.json"
        print(
            f"[step_runner] meta.json fallback to step dir: {_path_for_report(fallback, project_root)}",
            flush=True,
        )
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


def _coerce_direct_result_to_meta(
    *,
    payload: dict[str, Any],
    expected_meta_path: Path,
) -> dict[str, Any] | None:
    """Convert a direct coder result object into a v2 meta.json payload.

    Accepts payloads shaped like:
    {
      "status": "APPROVED|REJECTED",
      "remark": "...",
      "artifacts": {...},
      "reject_code": "..."
    }
    """
    if not isinstance(payload, dict):
        return None

    status = str(payload.get("status") or "").strip().upper()
    artifacts = payload.get("artifacts")
    if status not in ("APPROVED", "REJECTED") or not isinstance(artifacts, dict):
        return None

    coder_result: dict[str, Any] = {
        "status": status,
        "remark": str(payload.get("remark") or ""),
        "artifacts": artifacts,
        "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    reject_code = str(payload.get("reject_code") or "").strip()
    if reject_code:
        coder_result["reject_code"] = reject_code

    return {
        "schema_version": "v2",
        "coder_result": coder_result,
    }


def _repair_or_validate_meta_json(
    *,
    meta_path: Path,
    parsed_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate meta.json, repairing common direct-result sidecar mistakes when possible."""
    try:
        return _read_and_validate_meta_json(meta_path)
    except MetaJsonMissingError:
        repaired = _coerce_direct_result_to_meta(
            payload=parsed_result or {},
            expected_meta_path=meta_path,
        )
        if repaired is None:
            raise
        _save_json_atomic(meta_path, repaired)
        return _read_and_validate_meta_json(meta_path)
    except MetaJsonInvalidError as exc:
        repaired: dict[str, Any] | None = None

        if meta_path.exists() and meta_path.is_file():
            try:
                existing = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = None
            repaired = _coerce_direct_result_to_meta(
                payload=existing if isinstance(existing, dict) else {},
                expected_meta_path=meta_path,
            )

        if repaired is None:
            repaired = _coerce_direct_result_to_meta(
                payload=parsed_result or {},
                expected_meta_path=meta_path,
            )

        if repaired is None:
            raise exc

        _save_json_atomic(meta_path, repaired)
        return _read_and_validate_meta_json(meta_path)


def _validate_artifact_files_exist(
    *,
    artifacts: dict[str, str],
    project_root: Path,
) -> None:
    """Raise ArtifactMissingError if any artifact path in the dict doesn't exist.
    
    Note: Skips .meta.json files as they are sidecars, not actual artifacts.
    """
    missing = [
        path_str
        for path_str in artifacts.values()
        if path_str and not path_str.endswith('.meta.json') and not (project_root / path_str).exists()
    ]
    if missing:
        raise ArtifactMissingError(
            f"Artifact files claimed in meta.json do not exist on disk: {missing}",
            missing=missing,
        )


def _validate_artifacts_in_produces_list(
    *,
    artifacts: dict[str, str],
    produces: list[str],
    step: str,
) -> None:
    """Raise ArtifactMissingError if any artifact is not in the step's produces list.
    
    This enforces the declarative write-contract model:
    - Each step declares what it produces in template_groups.py
    - LLM can only report artifacts in that list
    - Prevents workflows from reporting undeclared outputs
    
    Note: Only explicit alias normalization is allowed:
    - REVIEW_FILE_SUGGESTED_METAJSON → REVIEW_FILE_SUGGESTED
    - REVIEW_FILE_SUGGESTED_PATH → REVIEW_FILE_SUGGESTED
    """
    if not produces:
        # Action steps or steps without declared outputs - skip validation
        return
    
    # Convert produces list to set for comparison
    allowed = set(produces)
    
    # Normalize artifacts using explicit alias suffixes only.
    normalized_artifacts = {}
    for artifact_key, artifact_path in artifacts.items():
        normalized_key = _normalize_artifact_contract_key(artifact_key)
        normalized_artifacts[normalized_key] = artifact_path
    
    # Check each normalized artifact against produces list
    unauthorized = []
    for artifact_key in normalized_artifacts.keys():
        if artifact_key not in allowed:
            unauthorized.append(artifact_key)
    
    if unauthorized:
        raise ArtifactMissingError(
            f"Step '{step}' reported artifacts not declared in 'produces' list: {unauthorized}. "
            f"Allowed artifacts: {sorted(allowed)}",
            missing=unauthorized,
        )


def _normalize_artifact_contract_key(artifact_key: str) -> str:
    key = str(artifact_key or "").strip()
    for suffix in ("_METAJSON", "_PATH"):
        if key.endswith(suffix):
            return key[:-len(suffix)]
    return key


def _declared_write_keys(step_cfg: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for raw_key in step_cfg.get("produces", []) or []:
        key = str(raw_key or "").strip()
        if key and key not in keys:
            keys.append(key)
    for raw_key in step_cfg.get("updates", []) or []:
        key = str(raw_key or "").strip()
        if key and key not in keys:
            keys.append(key)
    target_artifact = str(step_cfg.get("target_artifact") or "").strip()
    if target_artifact and target_artifact not in keys:
        keys.append(target_artifact)
    return keys


def _step_requires_write_contract(step_cfg: dict[str, Any]) -> bool:
    if step_cfg.get("action"):
        return False
    if step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context"):
        return True
    if _declared_write_keys(step_cfg):
        return True
    return False


def _validate_step_write_contract_config(*, step_cfg: dict[str, Any], step: str) -> None:
    if not _step_requires_write_contract(step_cfg):
        return
    declared = _declared_write_keys(step_cfg)
    if declared:
        return
    raise RuntimeError(
        f"Step '{step}' is write-capable but declares no write contract. "
        "Add 'produces' for created artifacts or 'updates' for in-place edits."
    )


def _resolve_contract_path_from_context(
    *,
    artifact_key: str,
    context: dict[str, str],
    state: dict[str, Any],
) -> str:
    for candidate in (
        context.get(artifact_key, ""),
        context.get(f"{artifact_key}_PATH", ""),
        (state.get("artifacts") or {}).get(artifact_key, ""),
    ):
        value = str(candidate or "").strip()
        if value:
            return value
    return ""


def _resolve_allowed_write_paths(
    *,
    step_cfg: dict[str, Any],
    context: dict[str, str],
    state: dict[str, Any],
    project_root: Path,
    meta_path: Path,
) -> set[Path]:
    allowed_paths: set[Path] = {meta_path.resolve()}
    for artifact_key in _declared_write_keys(step_cfg):
        path_str = _resolve_contract_path_from_context(
            artifact_key=artifact_key,
            context=context,
            state=state,
        )
        if not path_str:
            continue
        resolved = resolve_repo_or_runtime_path(
            path_str,
            project_root=project_root,
            runtime_root=JOBS_ROOT,
        )
        allowed_paths.add(resolved.resolve())
    return allowed_paths


def _snapshot_allowed_write_roots(*, allowed_paths: set[Path], project_root: Path) -> dict[Path, str]:
    snapshot: dict[Path, str] = {}
    for path in allowed_paths:
        resolved = path.resolve()
        if not resolved.exists() or not resolved.is_file():
            snapshot[resolved] = ""
            continue
        try:
            snapshot[resolved] = _hash_file(resolved)
        except OSError:
            snapshot[resolved] = ""
    return snapshot


def _verify_only_allowed_paths_changed(
    *,
    before: dict[Path, str],
    allowed_paths: set[Path],
    project_root: Path,
    step: str,
) -> list[str]:
    after = _snapshot_allowed_write_roots(allowed_paths=allowed_paths, project_root=project_root)
    changed_abs: list[Path] = []
    for path in sorted(allowed_paths):
        if before.get(path) != after.get(path):
            changed_abs.append(path)
    return [_path_for_report(path, project_root) for path in changed_abs]


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonicalize_master_bootstrap_artifacts(
    *,
    artifacts: dict[str, str],
    project_root: Path,
    state: dict,
) -> dict[str, str]:
    if state.get("template_group") not in MASTER_BOOTSTRAP_WORKFLOWS:
        return dict(artifacts)

    job_id = str(state.get("job_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    candidates = master_bootstrap_artifact_candidates(job_id=job_id, mode=mode)
    normalized = dict(artifacts)

    for artifact_key, path_candidates in candidates.items():
        if not path_candidates:
            continue
        canonical_rel = path_candidates[0]
        canonical_abs = project_root / canonical_rel
        current_rel = str(normalized.get(artifact_key) or "").strip()

        chosen_rel = ""
        if current_rel:
            current_abs = project_root / current_rel
            if current_abs.exists() and current_abs.is_file():
                chosen_rel = current_rel

        if not chosen_rel:
            for candidate_rel in path_candidates:
                candidate_abs = project_root / candidate_rel
                if candidate_abs.exists() and candidate_abs.is_file():
                    chosen_rel = candidate_rel
                    break

        if not chosen_rel:
            continue

        chosen_abs = project_root / chosen_rel
        if chosen_rel != canonical_rel:
            canonical_abs.parent.mkdir(parents=True, exist_ok=True)
            canonical_abs.write_text(chosen_abs.read_text(encoding="utf-8"), encoding="utf-8")
        normalized[artifact_key] = canonical_rel

    return normalized


def _backend_artifact_rules(state: dict[str, Any]) -> dict[str, Any]:
    rules = state.get("backend_artifact_rules") or {}
    return rules if isinstance(rules, dict) else {}


def _normalize_backend_job_path(path_str: str) -> str:
    if not path_str:
        return path_str
    p = Path(path_str)
    if p.is_absolute():
        return str(p)
    posix = path_str.replace("\\", "/")
    marker = ".ukbe-runner/jobs/"
    if posix.startswith(marker):
        suffix = posix[len(marker):]
        return str(JOBS_ROOT / Path(suffix))
    repo_prefixes = ("docs/", "archive/", "scripts/", "temp/")
    if posix.startswith(repo_prefixes):
        return path_str
    return str(JOBS_ROOT / Path(path_str))


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
    resolved = str(template).format(
        workflow_name=str(state.get("template_group") or ""),
        template_group=str(state.get("template_group") or ""),
        job_id=run_id,
        run_code=run_id,
        step_name=step,
        step_order=step_sequence,
        step_dir=step_dir_name,
        step_dir_rel=step_dir_rel,
    )
    return _normalize_backend_job_path(resolved)


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
        artifact_value = _normalize_backend_job_path(str(artifact_value)) if artifact_value else ""
        if artifact_value:
            ctx[f"{artifact_key}_PATH"] = str(artifact_value)
        meta_strategy = str(rule.get("meta_path_strategy") or "artifact_sidecar")
        if meta_strategy == "step_shared_meta" and step_dir_rel:
            meta_path = f"{step_dir_rel}/meta.json"
        else:
            p = PurePath(str(artifact_value))
            meta_path = str(p.parent / f"{p.stem}.meta.json") if artifact_value else ""
        meta_path = _normalize_backend_job_path(meta_path) if meta_path else ""
        if meta_path:
            ctx[f"{artifact_key}_METAJSON"] = meta_path
        if is_produced and not artifacts.get(artifact_key) and artifact_value:
            ctx[artifact_key] = str(artifact_value)
            ctx[f"{artifact_key}_PATH"] = str(artifact_value)
            if meta_path:
                ctx[f"{artifact_key}_METAJSON"] = meta_path
    return True



from .constants import get_master_docs_output_paths, delivery_scaffold_docs

MASTER_DOCS_OUTPUT_PATHS: dict[str, str] = get_master_docs_output_paths()
DELIVERY_SCAFFOLD_OUTPUT_PATHS: dict[str, str] = delivery_scaffold_docs()

BUG_FIX_OUTPUT_PATHS: dict[str, str] = {
    "BUG_REPORT_FILE": f"{FOLDER_KEY_DELIVERY_IMPLEMENTATIONS}/{{step_dir_rel}}/BUG_REPORT.md",
    "REPRO_FILE": f"{FOLDER_KEY_DELIVERY_IMPLEMENTATIONS}/{{step_dir_rel}}/BUG_REPRODUCTION.md",
    "ROOT_CAUSE_FILE": f"{FOLDER_KEY_DELIVERY_IMPLEMENTATIONS}/{{step_dir_rel}}/ROOT_CAUSE.md",
    "PATCH_FILE": f"{FOLDER_KEY_DELIVERY_IMPLEMENTATIONS}/{{step_dir_rel}}/PATCH.md",
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
    if not step_dir_rel:
        try:
            idx = steps.index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        job_id = state.get("job_id", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"
    return template.format(run_id=run_id, step=step, step_index=step_index, step_dir_rel=step_dir_rel)


def _set_delivery_scaffold_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> None:
    if _set_backend_artifact_rule_aliases(ctx=ctx, state=state, step=step, artifacts=artifacts, produces=produces):
        return
    if not str(state.get("template_group") or "").startswith("delivery_scaffold"):
        return

    step_names = list(_workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", []))
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel:
        # Local CLI mode: compute step_dir_rel from job state (same fallback
        # as build_context's producing-step logic).
        try:
            idx = step_names.index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        job_id = state.get("job_id", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"

    # Resolve step-relative paths to absolute paths in the global job directory
    step_dir_abs = _normalize_backend_job_path(step_dir_rel) if step_dir_rel else ""
    step_dir_meta = f"{step_dir_abs}/meta.json" if step_dir_rel else ""
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
                # Resolve step_dir_rel-relative paths to absolute job directory paths
                if step_dir_rel and output_path.startswith(step_dir_rel):
                    output_path = output_path.replace(step_dir_rel, step_dir_abs, 1)
                ctx[artifact_key] = output_path
                ctx[f"{artifact_key}_PATH"] = output_path
                ctx[f"{artifact_key}_METAJSON"] = step_dir_meta or str(PurePath(output_path).parent / f"{PurePath(output_path).stem}.meta.json")


def _set_bug_fix_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> None:
    # Determine if this step produces bug fix artifacts
    bug_fix_artifact_keys = {"BUG_REPORT_FILE", "REPRO_FILE", "ROOT_CAUSE_FILE", "PATCH_FILE"}
    if not any(key in produces for key in bug_fix_artifact_keys):
        return

    step_names = list(_workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", []))
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel:
        try:
            idx = step_names.index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        job_id = state.get("job_id", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"

    step_dir_abs = _normalize_backend_job_path(step_dir_rel) if step_dir_rel else ""
    step_dir_meta = f"{step_dir_abs}/meta.json" if step_dir_rel else ""
    run_id = str(state.get("job_id") or state.get("workflow_run_id") or "bug-fix-run")
    step_index = (step_names.index(step) + 1) if step in step_names else 1

    for artifact_key, rel_path in CONSTANTS_BUG_FIX_OUTPUT_PATHS.items():
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
        if artifact_key in CONSTANTS_BUG_FIX_OUTPUT_PATHS and not artifacts.get(artifact_key):
            output_path = CONSTANTS_BUG_FIX_OUTPUT_PATHS[artifact_key].format(
                run_id=run_id,
                step=step,
                step_index=step_index,
                step_dir_rel=step_dir_rel,
            )
            if step_dir_rel and output_path.startswith(step_dir_rel):
                output_path = output_path.replace(step_dir_rel, step_dir_abs, 1)
            ctx[artifact_key] = output_path
            ctx[f"{artifact_key}_PATH"] = output_path
            ctx[f"{artifact_key}_METAJSON"] = step_dir_meta or str(PurePath(output_path).parent / f"{PurePath(output_path).stem}.meta.json")


def _set_master_docs_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> None:
    if state.get("template_group") != "00_master_docs_bootstrap_v1":
        return

    step_names = list(_workflow_module().TEMPLATE_GROUPS.get(state.get("template_group", ""), {}).get("steps", []))
    step_dir_rel = str(state.get("backend_step_dir_rel") or "").strip()
    if not step_dir_rel:
        try:
            idx = step_names.index(step) + 1
        except ValueError:
            idx = 1
        template_group = state.get("template_group", "")
        job_id = state.get("job_id", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"

    step_dir_abs = _normalize_backend_job_path(step_dir_rel) if step_dir_rel else ""
    step_dir_meta = f"{step_dir_abs}/meta.json" if step_dir_rel else ""

    mode = str(
        state.get("current_step_cfg", {}).get("mode")
        or state.get("current_mode")
        or "bootstrap"
    )
    job_id = str(state.get("job_id") or "00DOC")

    for artifact_key, rel_path in MASTER_DOCS_OUTPUT_PATHS.items():
        artifact_value = artifacts.get(artifact_key) or rel_path.format(job_id=job_id, mode=mode)
        ctx[artifact_key] = str(artifact_value)
        ctx[f"{artifact_key}_PATH"] = str(artifact_value)
        if artifact_value:
            p = PurePath(str(artifact_value))
            ctx[f"{artifact_key}_METAJSON"] = step_dir_meta or str(p.parent / f"{p.stem}.meta.json")


def _set_audience_site_aliases(*, ctx: dict[str, str], state: dict, step: str, artifacts: dict[str, Any], produces: list[str]) -> None:
    """Set path aliases for audience site artifacts (markdown, HTML, PDF, manifest).

    This ensures the prompts use the correct repo-relative paths for audience
    documentation sites (41_*_doc_v1 and 51-55_*_docs_v1).
    """
    template_group = state.get("template_group", "")
    # Apply to both 41_*_doc_v1 (markdown generation) and 51-55_*_docs_v1 (site generation)
    if not any(template_group.startswith(f"{i}_") for i in [41, 51, 52, 53, 54, 55]):
        return

    from .constants import audience_site_artifacts
    site_artifacts = audience_site_artifacts()

    # Set path aliases for all audience site artifacts
    for artifact_key, rel_path in site_artifacts.items():
        artifact_value = artifacts.get(artifact_key) or rel_path
        ctx[artifact_key] = str(artifact_value)
        ctx[f"{artifact_key}_PATH"] = str(artifact_value)
        # Only set METAJSON if not already set (action steps have their own METAJSON logic)
        if artifact_value and not ctx.get(f"{artifact_key}_METAJSON"):
            p = PurePath(str(artifact_value))
            ctx[f"{artifact_key}_METAJSON"] = str(p.parent / f"{p.stem}.meta.json")


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
            f"Template conformance failed for step {step!r} ({doc_type}): {'; '.join(issues)}",
            missing=missing_sections + missing_metadata,
        )

    print(f"[step_runner] template conformance OK for step={step} type={doc_type}", flush=True)


def _has_section(content: str, section: str) -> bool:
    """Check if markdown content contains a section heading (case-insensitive)."""
    import re as _re
    pattern = _re.compile(rf'^#+\s+.*{_re.escape(section)}', _re.MULTILINE | _re.IGNORECASE)
    return bool(pattern.search(content))


def _has_metadata_field(content: str, field: str) -> bool:
    """Check if metadata block contains a field (frontmatter or markdown table)."""
    import re as _re
    escaped = _re.escape(field)
    # matches "Field: value" or "- Field: value" (frontmatter / YAML-style)
    kv_pattern = _re.compile(rf'^\s*-?\s*{escaped}\s*[:：]', _re.MULTILINE)
    # matches "| Field | value |" (markdown table row)
    table_pattern = _re.compile(rf'^\|\s*{escaped}\s*\|', _re.MULTILINE | _re.IGNORECASE)
    return bool(kv_pattern.search(content) or table_pattern.search(content))


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
    allowed_write_paths: list[str],
    changed_paths: list[str],
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
        "allowed_write_paths": allowed_write_paths,
        "changed_paths": changed_paths,
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

def _load_site_config(*, state: dict) -> dict:
    """Load sites.config from docs/sites.config in the target repo.

    Returns a dict with:
    - output_format: "html", "pdf", or "html+pdf" (default: "html")
    - additional_sections: list of custom section definitions
    - theme: theme configuration dict (name, layout_file, css_file)

    Returns empty dict if config doesn't exist or workflow not configured.
    """
    template_group = state.get("template_group", "")
    if not template_group:
        return {}

    # Look for sites.config in the artifact root (target repo's docs/)
    config_path = ARTIFACT_ROOT / "docs" / "sites.config"
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as exc:
        print(f"[step_runner] Failed to load sites.config: {exc}", flush=True)
        return {}

    workflow_config = config.get(template_group, {})
    if not isinstance(workflow_config, dict):
        return {}

    return {
        "output_format": workflow_config.get("output_format", "html"),
        "additional_sections": workflow_config.get("additional_sections", []),
        "theme": workflow_config.get("theme", {}),
    }


def _format_additional_sections(sections: list) -> str:
    """Format additional sections for prompt injection."""
    if not sections:
        return ""

    lines = [
        "## Additional Custom Sections",
        "",
        "In addition to the default sections, include the following custom sections:",
        "",
    ]
    for i, section in enumerate(sections, 1):
        title = section.get("title", f"Custom Section {i}")
        desc = section.get("description", "")
        guidelines = section.get("content_guidelines", "")
        source = section.get("source_artifacts", [])

        lines.append(f"### {i}. {title}")
        if desc:
            lines.append(f"**Purpose**: {desc}")
        if guidelines:
            lines.append(f"**Content Guidelines**: {guidelines}")
        if source:
            lines.append(f"**Source Documents**: {', '.join(source)}")
        lines.append("")

    return "\n".join(lines)


def _load_site_theme(*, site_config: dict) -> dict:
    """Load custom theme files (layout template and CSS) from the target repo.

    Args:
        site_config: The site config dict from _load_site_config()

    Returns a dict with:
    - theme_name: Name of the theme (default: "default")
    - layout_template: Full HTML template content (or empty string)
    - theme_css: Full CSS content (or empty string)
    - layout_instructions: Instructions for LLM on how to use the template
    """
    # Theme config can be a string (theme name) or dict (legacy format)
    theme_config = site_config.get("theme", "default")
    if isinstance(theme_config, str):
        theme_name = theme_config
    elif isinstance(theme_config, dict):
        theme_name = theme_config.get("name", "default")
    else:
        theme_name = "default"

    result = {
        "theme_name": theme_name,
        "layout_template": "",
        "theme_css": "",
        "layout_instructions": "",
    }

    # Load theme files from global runner home's themes directory
    # Theme location: ~/.ukbe-runner/themes/<theme_name>/
    # Falls back to package bundle location if not found in global path
    from pathlib import Path as _Path
    from .runtime_context import RUNNER_HOME

    # First try global runner home
    global_themes_root = RUNNER_HOME / "themes"
    theme_dir = global_themes_root / theme_name

    # Fall back to package bundle location if not found
    if not theme_dir.exists():
        bundle_themes_root = PACKAGE_ROOT / "bootstrap" / "themes"
        theme_dir = bundle_themes_root / theme_name

    layout_path = theme_dir / "layout.html"
    css_path = theme_dir / "theme.css"

    # Load layout template
    if layout_path.exists():
        try:
            result["layout_template"] = layout_path.read_text(encoding="utf-8")
            result["layout_instructions"] = _build_layout_instructions(str(layout_path))
        except Exception as exc:
            print(f"[step_runner] Failed to load layout template {layout_path}: {exc}", flush=True)
    else:
        print(f"[step_runner] Theme layout not found: {layout_path}, using default", flush=True)

    # Load CSS
    if css_path.exists():
        try:
            result["theme_css"] = css_path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"[step_runner] Failed to load CSS {css_path}: {exc}", flush=True)
    else:
        print(f"[step_runner] Theme CSS not found: {css_path}, using default", flush=True)

    return result


def _build_layout_instructions(layout_file: str) -> str:
    """Build instructions for LLM on how to use a custom layout template."""
    return f"""Custom Layout Template:
- A custom layout template is provided at: {layout_file}
- Use this template as the base HTML structure
- Replace these placeholders in the template:
  - {{{{TITLE}}}} → Page title (e.g., "Stakeholder Documentation")
  - {{{{SUBTITLE}}}} → Page subtitle/description
  - {{{{WORKFLOW}}}} → Workflow name (e.g., "51_stakeholder_docs_v1")
  - {{{{STEP}}}} → Step name (e.g., "generate_site")
  - {{{{NAV_LINKS}}}} → Navigation links as HTML anchor tags
  - {{{{BODY}}}} → Main content HTML (generated from markdown)
  - {{{{CSS}}}} → CSS styles (provided separately or use default)
  - {{{{THEME_NAME}}}} → Theme name identifier
  - {{{{DOWNLOAD_LINK}}}} → PDF download link (if applicable)

- The template content will be injected as {{{{SITE_LAYOUT_TEMPLATE}}}}
- The CSS content will be injected as {{{{SITE_THEME_CSS}}}}
- If {{{{SITE_LAYOUT_TEMPLATE}}}} is empty, use the standard page_shell structure
"""


def _load_additional_sections(*, state: dict, step: str) -> str:
    """Load additional sections from sites.config in the target repo.

    Kept for backward compatibility. Use _load_site_config() for full config.
    """
    config = _load_site_config(state=state)
    return _format_additional_sections(config.get("additional_sections", []))


# ---------------------------------------------------------------------------
# Workflow package context hooks
# ---------------------------------------------------------------------------

_CONTEXT_HOOK_CACHE: dict[str, object | None] = {}


def _apply_workflow_package_context_hooks(
    *,
    ctx: dict[str, str],
    state: dict,
    step: str,
    step_cfg: dict | None,
) -> None:
    """Load and run context_extensions.py from the active workflow package.

    When ``step_cfg`` carries a ``_workflow_bundle`` reference (stamped by
    ``_load_group`` in ``run_agent.py``), this function discovers and invokes
    any context hooks exported by the workflow package's ``context_extensions.py``.
    """
    if not step_cfg:
        return
    bundle = step_cfg.get("_workflow_bundle")
    if bundle is None:
        return

    ext_path = getattr(bundle, "context_extensions_path", None)
    if ext_path is None:
        return

    # Cache key: module path → loaded build_context_extensions callable (or None)
    cache_key = str(ext_path)

    if cache_key in _CONTEXT_HOOK_CACHE:
        hooks_fn = _CONTEXT_HOOK_CACHE[cache_key]
    else:
        # First load — import the module and discover the hook function
        hooks_fn = _load_context_extensions_module(ext_path, cache_key)
        _CONTEXT_HOOK_CACHE[cache_key] = hooks_fn

    if hooks_fn is not None:
        try:
            extensions = hooks_fn(state=state, step=step, step_cfg=step_cfg, ctx=ctx)
            if isinstance(extensions, dict):
                ctx.update(extensions)
        except Exception:
            import logging  # noqa: PLC0415

            logging.getLogger(__name__).exception(
                "Context extension hook failed for %s", ext_path
            )


def _load_context_extensions_module(
    ext_path: Path, cache_key: str
) -> object | None:
    """Import ``context_extensions.py`` and return the hook callable.

    Returns ``None`` when the file doesn't exist or loading fails, and
    caches that result so we don't retry on every step.
    """
    if not ext_path.is_file():
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            "workflow_context_extensions", ext_path
        )
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        return getattr(mod, "build_context_extensions", None)
    except Exception:
        import logging  # noqa: PLC0415

        logging.getLogger(__name__).exception(
            "Failed to load context extensions from %s", ext_path
        )
        return None


def build_context(
    state: dict,
    *,
    step: str = "",
    step_cfg: dict | None = None,
) -> dict[str, str]:
    """Build the full context dict for prompt rendering."""
    bundle = _workflow_module()
    ctx: dict[str, str] = dict(bundle.REFERENCE_FILES)
    ctx["SYSTEM_DOC_ROOT"] = system_doc_rel()
    ctx["DOCS_ROOT"] = docs_root_rel()
    ctx["SYSTEM_TEMPLATE_ROOT"] = FOLDER_KEY_SYSTEM_TEMPLATE_ROOT
    ctx["SYSTEM_DELIVERY_TEMPLATE_ROOT"] = FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT
    ctx["SYSTEM_CODEBASE_TEMPLATE_ROOT"] = FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT
    ctx["CODEBASE_DOC_ROOT"] = codebase_doc_rel()
    ctx["DELIVERY_DOC_ROOT"] = delivery_doc_rel()
    ctx["ARCHITECTURE_SITE_ROOT"] = architecture_site_rel()
    ctx["CODER_IMPLEMENTATION_SOP_PATH"] = "CODER_IMPLEMENTATION_SOP.md"

    # Get artifacts from state for fingerprinting
    artifacts = state.get("artifacts") or {}

    # Inject artifact values as context variables so prompt templates
    # can reference {ARTIFACT_KEY} directly (e.g., {IMAGE_FOLDER}).
    for _ak, _av in artifacts.items():
        if _av is not None:
            ctx[_ak] = str(_av)

    # For producing steps where the artifact doesn't exist yet, compute the step
    # directory meta.json path so the prompt can tell the coder where to write it.
    if step and step_cfg:
        result_key = step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context", "")
        # If result_key already ends with _METAJSON, use it directly;
        # otherwise append _METAJSON to form the context key.
        if result_key.endswith("_METAJSON"):
            meta_ctx_key = result_key
        else:
            meta_ctx_key = f"{result_key}_METAJSON"
        prefer_step_meta = bool(step_cfg.get("action"))
        if result_key and (prefer_step_meta or not ctx.get(meta_ctx_key)):
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
            ctx[meta_ctx_key] = _normalize_backend_job_path(f"{step_dir_rel}/meta.json")
            print(f"[step_runner] Producing step {step}: {meta_ctx_key} -> {ctx[meta_ctx_key]}", flush=True)

    ctx["ARTIFACT_FINGERPRINTS"] = _format_artifact_fingerprint_block(artifacts)

    # Context-pack explicit path alias: CONTEXT_PACK_FILE_PATH mirrors CONTEXT_PACK_FILE
    # (the generic loop above produces CONTEXT_PACK_FILE_ABS_PATH but prompts expect _PATH)
    ctx_pack = artifacts.get("CONTEXT_PACK_FILE")
    if ctx_pack:
        ctx["CONTEXT_PACK_FILE_PATH"] = ctx_pack
    else:
        ctx["CONTEXT_PACK_FILE_PATH"] = ""

    # Task ID starting sequence: scan existing task docs to avoid collision
    task_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_TASKS
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
        ctx["REVIEW_FILE_SUGGESTED_METAJSON"] = artifact_rel_to_meta_rel(review_suggested)
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
            ctx["VALIDATION_FILE_METAJSON"] = artifact_rel_to_meta_rel(validation_path)
        else:
            ctx["VALIDATION_FILE_METAJSON"] = ""
    else:
        ctx.setdefault("VALIDATION_FILE_PATH", "")
        ctx.setdefault("VALIDATION_FILE_METAJSON", "")

    if "CODEBASE_CHANGE_IMPACT" in produces and not artifacts.get("CODEBASE_CHANGE_IMPACT"):
        change_path = _build_codebase_change_impact_path(state=state)
        ctx["CODEBASE_CHANGE_IMPACT_PATH"] = change_path
        if change_path:
            ctx["CODEBASE_CHANGE_IMPACT_METAJSON"] = artifact_rel_to_meta_rel(change_path)
        else:
            ctx["CODEBASE_CHANGE_IMPACT_METAJSON"] = ""
    else:
        ctx.setdefault("CODEBASE_CHANGE_IMPACT_PATH", artifacts.get("CODEBASE_CHANGE_IMPACT", ""))
        ctx.setdefault("CODEBASE_CHANGE_IMPACT_METAJSON", "")

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
            output_dir=FOLDER_KEY_DELIVERY_TASKS,
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
    _set_master_docs_aliases(
        ctx=ctx,
        state=state,
        step=step,
        artifacts=artifacts,
        produces=produces,
    )
    _set_bug_fix_aliases(
        ctx=ctx,
        state=state,
        step=step,
        artifacts=artifacts,
        produces=produces,
    )
    _set_audience_site_aliases(
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
            ctx["PRE_INIT_FILE_METAJSON"] = pre_init_meta or artifact_rel_to_meta_rel(pre_init_path)
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
            ctx["PLAN_FILE_METAJSON"] = plan_meta or artifact_rel_to_meta_rel(plan_path)
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
            ctx["TASK_GRAPH_FILE_METAJSON"] = tg_meta or artifact_rel_to_meta_rel(tg_path)
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
            ctx["IMPL_FILE_METAJSON"] = impl_meta or artifact_rel_to_meta_rel(impl_path)
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
            # existing_csv_json may be a directory ("source_csv/YYYYMMDD-NNN/")
            # or a file inside that directory ("source_csv/YYYYMMDD-NNN/file.json").
            if p.suffix == ".json":
                run_dir = str(p.parent)
            else:
                run_dir = str(p)
            if run_dir:
                ctx["IMAGE_CSV_RUN_DIR"] = run_dir
                ctx["IMAGE_CSV_JSON"] = run_dir
                ctx["IMAGE_CSV_JSON_METAJSON"] = str(Path(run_dir) / "meta.json")
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
                ctx["IMAGE_CSV_JSON"] = str(Path("source_csv") / run_dir)
                ctx["IMAGE_CSV_JSON_METAJSON"] = str(Path("source_csv") / run_dir / "meta.json")
        if ctx.get("IMAGE_CSV_RUN_DIR"):
            print(f"[step_runner] IMAGE_CSV RUN_DIR: {ctx['IMAGE_CSV_RUN_DIR']}", flush=True)
            print(f"[step_runner] IMAGE_CSV JSON PATH: {ctx.get('IMAGE_CSV_JSON', '')}", flush=True)
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
                # IMAGE_CSV_JSON may be a directory ("source_csv/YYYYMMDD-NNN") or
                # a file inside that directory ("source_csv/YYYYMMDD-NNN/file.json").
                # Use the directory component as the run directory.
                if p.suffix == ".json":
                    run_dir = str(p.parent)
                else:
                    run_dir = str(p)
        if run_dir:
            ctx["IMAGE_CSV_RUN_DIR"] = run_dir
            ctx["IMAGE_CSV_SUBMIT_RESULT_PATH"] = str(Path(run_dir) / "submission_results.json")
            ctx["IMAGE_CSV_SUBMIT_RESULT_METAJSON"] = str(Path(run_dir) / "submission_results.meta.json")
            print(f"[step_runner] SUBMIT RESULT PATH: {ctx['IMAGE_CSV_SUBMIT_RESULT_PATH']}", flush=True)
            print(f"[step_runner] SUBMIT METAJSON PATH: {ctx['IMAGE_CSV_SUBMIT_RESULT_METAJSON']}", flush=True)
        else:
            ctx["IMAGE_CSV_SUBMIT_RESULT_PATH"] = ""
            ctx["IMAGE_CSV_SUBMIT_RESULT_METAJSON"] = ""

    ctx["STEP_NAME"] = step

    # Step-scoped progress.jsonl path — lives inside the step job directory.
    ctx["PROGRESS_FILE"] = _resolve_progress_file_path(state=state, step=step)

    try:
        _tools_dir = str((PACKAGE_ROOT / "tools").resolve())
        ctx["TOOLS_DIR"] = _tools_dir
    except Exception:
        ctx["TOOLS_DIR"] = ""
    ctx["PYTHON_CMD"] = sys.executable or "python3"
    ctx["TOOLS_DIR_PY"] = _python_string_literal(ctx.get("TOOLS_DIR", ""))
    ctx["PROGRESS_FILE_PY"] = _python_string_literal(ctx.get("PROGRESS_FILE", ""))
    ctx["STEP_NAME_PY"] = _python_string_literal(step)

    # Load site configuration from docs/sites.config (per-repo configuration)
    site_config = _load_site_config(state=state)
    ctx["OUTPUT_FORMAT"] = site_config.get("output_format", "html")
    ctx["ADDITIONAL_SECTIONS"] = _format_additional_sections(site_config.get("additional_sections", []))

    # Load theme configuration (layout template and CSS)
    theme = _load_site_theme(site_config=site_config)
    ctx["SITE_THEME_NAME"] = theme.get("theme_name", "default")
    ctx["SITE_LAYOUT_TEMPLATE"] = theme.get("layout_template", "")
    ctx["SITE_THEME_CSS"] = theme.get("theme_css", "")
    ctx["SITE_LAYOUT_INSTRUCTIONS"] = theme.get("layout_instructions", "")
    ctx["ALLOWED_WRITE_PATHS"] = _prompt_allowed_write_paths(
        step_cfg=step_cfg or {},
        state=state,
        context=ctx,
    )

    # Run workflow package context hooks (from context_extensions.py).
    # Runs at the very end so extensions can override any value set above.
    _apply_workflow_package_context_hooks(
        ctx=ctx,
        state=state,
        step=step,
        step_cfg=step_cfg,
    )

    return ctx


_TOOL_INSTRUCTION_TEMPLATE = """

## Workflow Rules

You MUST use the tools below for EVERY step. Do NOT skip them. Do NOT answer directly without calling them first.

CRITICAL: Do NOT ask any clarifying questions. Do NOT ask for more info. Execute immediately using the tools.

Your step ID is: {STEP_NAME}

### create_todos(step_id, todos)
Call FIRST. Break the task into concrete steps, one record per todo.
Usage: python3 -c "import sys; sys.path.insert(0, '{TOOLS_DIR}'); import os; os.environ['PROGRESS_FILE']='{PROGRESS_FILE}'; from agent_tools import create_todos; create_todos('{STEP_NAME}', ['Step 1', 'Step 2'])"

### mark_complete(step_id, index, notes='')
Call after finishing each step. 1-based index.
Usage: python3 -c "import sys; sys.path.insert(0, '{TOOLS_DIR}'); import os; os.environ['PROGRESS_FILE']='{PROGRESS_FILE}'; from agent_tools import mark_complete; mark_complete('{STEP_NAME}', 1, notes='Done')"

## Mandatory Sequence
1. create_todos(step_id) — list all your steps first
2. Execute each step, call mark_complete(step_id, i) after each
3. You MUST call mark_complete for every item before returning your final result

Example for a 3-step task:
  create_todos('{STEP_NAME}', ['Read input file', 'Generate output', 'Write result'])
  mark_complete('{STEP_NAME}', 1, notes='File read successfully')
  mark_complete('{STEP_NAME}', 2, notes='Output generated')
  mark_complete('{STEP_NAME}', 3, notes='Result written to disk')

Actually call the functions with real arguments — do NOT just describe your answer."""


def render_prompt(template_text: str, context: dict[str, str], step_cfg: dict | None = None) -> str:
    import os as _os
    from datetime import datetime as _datetime
    _src = _os.path.abspath(__file__)
    render_context = dict(context)
    render_context.setdefault("PYTHON_CMD", sys.executable or "python3")
    render_context.setdefault("TOOLS_DIR_PY", _python_string_literal(render_context.get("TOOLS_DIR", "")))
    render_context.setdefault("PROGRESS_FILE_PY", _python_string_literal(render_context.get("PROGRESS_FILE", "")))
    render_context.setdefault("STEP_NAME_PY", _python_string_literal(render_context.get("STEP_NAME", "")))
    _tools_dir = render_context.get("TOOLS_DIR", "")
    print(f"[render_prompt] step_runner={_src}", flush=True)
    print(f"[render_prompt] TOOLS_DIR={_tools_dir!r}", flush=True)
    rendered = _rewrite_prompt_literals(template_text)
    for key, value in render_context.items():
        rendered = rendered.replace(f"{{{key}}}", _stringify_prompt_value(value))
    
    # NEW: Inject standardized sidecar instructions (if this step produces artifacts)
    if step_cfg:
        result_key = step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context", "")
        if result_key:
            # If result_meta_key_from_context already ends with _METAJSON, use it directly
            if result_key.endswith("_METAJSON"):
                meta_json_path = context.get(result_key, "")
                artifact_key = result_key.replace("_METAJSON", "")
            else:
                meta_json_path = context.get(f"{result_key}_METAJSON", "")
                artifact_key = result_key
            
            artifact_path = context.get(artifact_key, "")
            
            if meta_json_path:  # Only inject if we have the path
                # Build artifact entries for JSON template
                if artifact_path:
                    artifact_entries = f'        "{result_key}": "{artifact_path}"'
                else:
                    artifact_entries = f'        "{result_key}": null'
                
                # Generate timestamp
                current_timestamp = _datetime.now().astimezone().isoformat(timespec="seconds")
                
                # Format and append sidecar instructions
                sidecar_text = CONSTANTS_SIDECAR_INSTRUCTION_TEMPLATE.format(
                    META_JSON_PATH=meta_json_path,
                    ARTIFACT_ENTRIES=artifact_entries,
                    CURRENT_TIMESTAMP=current_timestamp
                )
                rendered += sidecar_text
                print(f"[render_prompt] SIDECAR_INSTRUCTION appended for {result_key}", flush=True)
            else:
                print(f"[render_prompt] SIDECAR_INSTRUCTION skipped: {result_key}_METAJSON not in context", flush=True)
        allowed_write_paths = str(render_context.get("ALLOWED_WRITE_PATHS") or "").strip()
        if allowed_write_paths:
            rendered += (
                "\n\n## Allowed Write Paths\n\n"
                "You may create or update ONLY the exact files listed below for this step.\n"
                "Do not modify any other repository or runtime files.\n\n"
                f"{allowed_write_paths}\n"
            )
    
    if _tools_dir:
        block = CONSTANTS_TOOL_INSTRUCTION_TEMPLATE
        for key, value in render_context.items():
            block = block.replace(f"{{{key}}}", _stringify_prompt_value(value))
        rendered = rendered + block
        print("[render_prompt] TOOL_INSTRUCTION appended", flush=True)
    if render_context.get("CODER_IMPLEMENTATION_SOP_PATH"):
        sop_block = CODER_SOP_INSTRUCTION_TEMPLATE
        for key, value in render_context.items():
            sop_block = sop_block.replace(f"{{{key}}}", _stringify_prompt_value(value))
        rendered = rendered + sop_block
        print("[render_prompt] MANDATORY CODER SOP appended", flush=True)
    else:
        print("[render_prompt] CODER_IMPLEMENTATION_SOP_PATH not in context — MANDATORY CODER SOP skipped", flush=True)
    return rendered


def _rewrite_prompt_literals(template_text: str) -> str:
    """Replace artifact paths in template text with prompt placeholders.
    
    Uses ARTIFACT_PATH_* constants from constants module and placeholder() helper.
    """
    rendered = template_text
    for literal, token in sorted(prompt_literal_substitutions().items(), key=lambda item: len(item[0]), reverse=True):
        rendered = rendered.replace(literal, token)
    return rendered


def _stringify_prompt_value(value: Any) -> str:
    """Normalize prompt-context values so missing fields do not crash rendering."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _python_string_literal(value: Any) -> str:
    """Render a value as a Python string literal for inline `python -c` snippets."""
    return repr(_stringify_prompt_value(value))


def prompt_checksum(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def resolve_prompt_path(*, step_cfg: dict, coder: str, model_id: str | None = None) -> Path:
    """Resolve prompt file path with three-level fallback.

    Resolution order:
      1. {stem}_{model_id}{suffix}  e.g. 06_task_deepseek-chat.txt  (if model_id given)
      2. {stem}_{coder}{suffix}     e.g. 06_task_qwen.txt
      3. {stem}{suffix}             e.g. 06_task.txt  (default)
    """
    import os
    
    def safe_relative(path: Path, base: Path) -> str:
        """Safely compute relative path, falling back to os.path.relpath on Windows."""
        try:
            return str(path.relative_to(base))
        except ValueError:
            # Windows pathlib.relative_to() can fail even for valid subpaths
            return os.path.relpath(path, base)
    
    default_path = RUNNER_ROOT / step_cfg["prompt_file"]
    path_obj = Path(step_cfg["prompt_file"])

    if model_id:
        model_specific = RUNNER_ROOT / str(
            path_obj.parent / f"{path_obj.stem}_{model_id}{path_obj.suffix}"
        )
        if model_specific.exists():
            rel_path = safe_relative(model_specific, RUNNER_ROOT)
            print(f"[step_runner] Using model-id-specific prompt: {rel_path}", flush=True)
            return model_specific

    coder_specific = RUNNER_ROOT / str(
        path_obj.parent / f"{path_obj.stem}_{coder}{path_obj.suffix}"
    )
    if coder_specific.exists():
        rel_path = safe_relative(coder_specific, RUNNER_ROOT)
        print(f"[step_runner] Using coder-specific prompt: {rel_path}", flush=True)
        return coder_specific

    rel_path = safe_relative(default_path, RUNNER_ROOT)
    print(f"[step_runner] Using default prompt: {rel_path}", flush=True)
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
        "review_master_system_docs": "rmaster",
        "review_impl": "rimpl",
        "review_pre_init": "rpre",
        "review_planner": "rplan",
        "review_task": "rtask",
        "review_task_graph": "rtg",
        "review_prompts": "rcsv",
        "review_sop": "rsop",
        "review_templates": "rtmpl",
        "review_agents": "ragent",
        "review_markdown": "rmd",
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
    template_group = str(state.get("template_group") or "")
    if template_group in MASTER_BOOTSTRAP_WORKFLOWS and step == "05_review_master_system_docs":
        job_id = str(state.get("job_id") or "00DOC")
        return system_doc_rel(f"{job_id}-bootstrap-validation.md")

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
    review_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_REVIEWS
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
            p = PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT))))
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
    template_group = str(state.get("template_group") or "")
    
    # Handle codebase workflows
    if template_group.startswith("codebase_"):
        mode = str(step_cfg.get("mode") or ("bootstrap" if "bootstrap" in template_group else "reconcile"))
        validation_dir = ARTIFACT_ROOT / FOLDER_KEY_CODEBASE_CHANGES
        candidate = validation_dir / f"{str(state.get('job_id') or 'codebase-scan')}-{mode}-validation.md"
        seq = 2
        while candidate.exists():
            candidate = validation_dir / f"{str(state.get('job_id') or 'codebase-scan')}-{mode}-validation_{seq:02d}.md"
            seq += 1
        return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))

    # Handle delivery/task execution workflows (with IMPL_FILE)
    impl_path = (state.get("artifacts") or {}).get("IMPL_FILE")
    if impl_path:
        tid = _build_review_target_identifier(artifact_key="IMPL_FILE", artifact_path=impl_path)
        slug = _derive_review_slug_from_artifact_path(impl_path)
        review_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_REVIEWS
        seq = 1
        while True:
            candidate = review_dir / f"VALIDATION-{_review_filename_date_code()}-{tid}_{slug}.md"
            if seq > 1:
                candidate = review_dir / f"VALIDATION-{_review_filename_date_code()}-{seq}-{tid}_{slug}.md"
            if not candidate.exists():
                return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))
            seq += 1
    
    # Handle bug fix workflows (don't require IMPL_FILE)
    workflow_cfg = _workflow_module().TEMPLATE_GROUPS.get(template_group, {})
    step_configs = workflow_cfg.get("step_configs", {})
    bug_fix_artifact_keys = {"BUG_REPORT_FILE", "REPRO_FILE", "ROOT_CAUSE_FILE", "PATCH_FILE"}
    
    is_bug_fix_workflow = False
    for s_name, s_cfg in step_configs.items():
        s_produces = s_cfg.get("produces", [])
        if any(key in s_produces for key in bug_fix_artifact_keys):
            is_bug_fix_workflow = True
            break
    
    if is_bug_fix_workflow:
        # Use step_dir pattern like other bug fix artifacts
        step_names = workflow_cfg.get("steps", [])
        try:
            idx = step_names.index(step) + 1
        except ValueError:
            idx = 1
        job_id = state.get("job_id", "")
        step_dir_rel = f"{template_group}/{job_id}/{idx:02d}_{step}"
        return delivery_doc_rel(f"04_implementation_plans/{step_dir_rel}/VALIDATION.md")
    
    # No match - return empty
    return ""


def _build_pre_init_file_path(*, state: dict) -> str:
    """Compute collision-free path for a new pre-init artifact.

    Sequence number is global per date (not per-slug) to avoid ID collisions.
    """
    draft_path = (state.get("artifacts") or {}).get("DRAFT_INIT_FILE", "")
    slug = _derive_review_slug_from_artifact_path(draft_path) if draft_path else "pre-init"
    pre_init_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_INITIATIVES / "pre_init"
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
            return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))
        seq += 1


def _build_plan_file_path(*, state: dict) -> str:
    """Compute collision-free path for a new plan artifact.

    Sequence number is global per date (not per-slug) so that the Plan ID
    embedded in the document metadata never collides across different plans
    created on the same day.
    """
    init_path = (state.get("artifacts") or {}).get("INIT_FILE", "")
    slug = _derive_review_slug_from_artifact_path(init_path) if init_path else "plan"
    plan_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_PLANS
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
            return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))
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
    tg_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_PLANS / "artifacts"
    date_code = dt.datetime.now().strftime("%Y%m%d")
    candidate = tg_dir / f"TASK-GRAPH-{date_code}-{plan_id}.md"
    return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))


def _build_impl_file_path(*, state: dict) -> str:
    """Compute a collision-free path for a new implementation plan file.

    Naming: `delivery_doc_rel("04_implementation_plans")` / IMPL-YYYYMMDD-NN_title-slug.md
    Sequence number is global per date (not per-slug) to avoid ID collisions.
    """
    from .job_state import task_execution_binding_current_item, task_queue_current_item

    current_item = task_queue_current_item(state) or task_execution_binding_current_item(state)
    title = str((current_item or {}).get("title") or "")
    slug = _normalize_review_slug(title, max_length=60) if title else "impl"
    impl_dir = ARTIFACT_ROOT / FOLDER_KEY_DELIVERY_IMPLEMENTATIONS
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
            return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))
        seq += 1


def _build_codebase_change_impact_path(*, state: dict) -> str:
    """Compute a collision-free path for a codebase documentation change record."""
    template_group = str(state.get("template_group") or "")
    if template_group.startswith("codebase_"):
        mode = "bootstrap" if "bootstrap" in template_group else "reconcile"
        change_dir = ARTIFACT_ROOT / FOLDER_KEY_CODEBASE_CHANGES
        candidate = change_dir / f"{str(state.get('job_id') or 'codebase-scan')}-{mode}.md"
        seq = 2
        while candidate.exists():
            candidate = change_dir / f"{str(state.get('job_id') or 'codebase-scan')}-{mode}_{seq:02d}.md"
            seq += 1
        return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))

    from .job_state import task_execution_binding_current_item, task_queue_current_item

    current_item = task_queue_current_item(state) or task_execution_binding_current_item(state)
    task_id = str((current_item or {}).get("task_id") or (current_item or {}).get("task_node_id") or "").strip()
    title = str((current_item or {}).get("title") or "").strip()
    slug = _normalize_review_slug(title, max_length=60) if title else "codebase-doc-update"
    base = task_id or f"DOCSYNC-{dt.datetime.now().strftime('%Y%m%d')}"
    change_dir = ARTIFACT_ROOT / FOLDER_KEY_CODEBASE_CHANGES
    candidate = change_dir / f"{base}_{slug}.md"
    seq = 2
    while candidate.exists():
        candidate = change_dir / f"{base}_{slug}_{seq:02d}.md"
        seq += 1
    return str(PurePath(str(candidate.relative_to(Path(ARTIFACT_ROOT)))))


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


def _prompt_allowed_write_paths(
    *,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    context: dict[str, str],
) -> str:
    lines: list[str] = []
    for artifact_key in _declared_write_keys(step_cfg):
        path_value = _resolve_contract_path_from_context(
            artifact_key=artifact_key,
            context=context,
            state=state,
        )
        if path_value:
            lines.append(f"- {path_value}")

    result_key = str(step_cfg.get("result_meta_key") or step_cfg.get("result_meta_key_from_context") or "").strip()
    meta_value = ""
    if result_key.endswith("_METAJSON"):
        meta_value = str(context.get(result_key) or "").strip()
    elif result_key:
        meta_value = str(context.get(f"{result_key}_METAJSON") or "").strip()
    if meta_value:
        lines.append(f"- {meta_value}")

    unique_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    return "\n".join(unique_lines)


def _resolve_progress_file_path(*, state: dict[str, Any], step: str) -> str:
    step_dir_rel = str((state or {}).get("backend_step_dir_rel") or "").strip()
    if step_dir_rel:
        return _normalize_backend_job_path(str(PurePath(step_dir_rel) / "progress.jsonl"))

    template_group = str((state or {}).get("template_group") or "").strip()
    job_id = str((state or {}).get("job_id") or "").strip()
    seq = int((state or {}).get("backend_step_sequence") or (state or {}).get("backend_step_order") or 0)
    if not seq and template_group and step:
        try:
            steps = _workflow_module().TEMPLATE_GROUPS.get(template_group, {}).get("steps", [])
            try:
                seq = steps.index(step) + 1
            except ValueError:
                seq = 0
        except RuntimeError:
            seq = 0

    safe_group = template_group or "_unknown_group"
    safe_job = job_id or "_unknown_job"
    safe_seq = seq if seq > 0 else 0
    return str(Path(JOBS_ROOT) / safe_group / safe_job / f"{safe_seq:02d}_{step}" / "progress.jsonl")


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
