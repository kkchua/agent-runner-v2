from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .step_runner import StepResult


@dataclass
class PreparedStepExecution:
    step_dir: Path
    action_name: str = ""
    post_action: str = ""
    coder_used: str = "action"
    coder_alias: str | None = None
    coder_role: str | None = None
    coder_config: dict[str, Any] | None = None
    context: dict[str, str] = field(default_factory=dict)
    prompt_path: Path | None = None
    prompt_text: str = ""
    checksum: str = ""


def prepare_step_execution(
    *,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    workflow_key_override: str = "",
    cli_coder: str | None = None,
    hooks: Any,
) -> PreparedStepExecution:
    missing_required = hooks._missing_artifacts(step_cfg.get("required_inputs", []), state)
    if missing_required:
        raise FileNotFoundError(
            f"Cannot run step {step!r}. Missing required input artifact(s): {', '.join(missing_required)}"
        )

    hooks.check_preflight_artifact_status(step_cfg=step_cfg, state=state)
    hooks.ensure_planning_task_queue_integrity(state, step=step)
    hooks.ensure_execution_task_binding_integrity(state, step=step)

    step_dir = hooks.make_step_dir(group_cfg, state, step)
    state["backend_step_dir_rel"] = str(step_dir)

    context = hooks.build_context(state, step=step, step_cfg=step_cfg)
    context["WORKFLOW_KEY_OVERRIDE"] = workflow_key_override or ""

    meta_from_ctx = step_cfg.get("result_meta_key_from_context")
    if not meta_from_ctx:
        result_key = step_cfg.get("result_meta_key", "")
        if result_key:
            meta_ctx_key = result_key if result_key.endswith("_METAJSON") else f"{result_key}_METAJSON"
            context[meta_ctx_key] = str(step_dir / "meta.json")

    loop_ctx = state.get("loop_context", {})
    if step_cfg.get("loop_returns_to") and loop_ctx.get("active") and loop_ctx.get("loop_source_review"):
        context["REVIEW_FILE"] = loop_ctx["loop_source_review"]

    action_name = str(step_cfg.get("action") or "")
    if action_name:
        return PreparedStepExecution(
            step_dir=step_dir,
            action_name=action_name,
            coder_used="action",
            context=context,
        )

    resolved = hooks._resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        cli_coder=cli_coder,
    )
    coder_used, coder_alias, coder_role, coder_config = _normalize_resolved_coder(resolved)

    model_id = (coder_config or {}).get("model") or None
    prompt_path = hooks.resolve_prompt_path(step_cfg=step_cfg, coder=coder_used, model_id=model_id)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    template_text = prompt_path.read_text(encoding="utf-8")
    template_text = augment_generated_doc_prompt(
        template_text,
        template_group=template_group,
        step=step,
        step_cfg=step_cfg,
        state=state,
        hooks=hooks,
    )
    prompt_text = hooks.render_prompt(template_text, context, step_cfg=step_cfg)
    checksum = hooks.prompt_checksum(prompt_text)
    hooks._save_text(step_dir / "prompt.txt", prompt_text)

    return PreparedStepExecution(
        step_dir=step_dir,
        coder_used=coder_used,
        coder_alias=coder_alias,
        coder_role=coder_role,
        coder_config=coder_config,
        context=context,
        prompt_path=prompt_path,
        prompt_text=prompt_text,
        checksum=checksum,
        post_action=str(step_cfg.get("post_action") or ""),
    )


def _normalize_resolved_coder(resolved: Any) -> tuple[str, str | None, str | None, dict[str, Any] | None]:
    if not isinstance(resolved, tuple):
        raise TypeError("Resolved coder payload must be a tuple.")
    if len(resolved) == 4:
        coder_used, coder_alias, coder_role, coder_config = resolved
        return str(coder_used), coder_alias, coder_role, coder_config
    if len(resolved) == 2:
        coder_used, coder_config = resolved
        return str(coder_used), None, None, coder_config
    raise ValueError(f"Unexpected resolved coder tuple shape: {len(resolved)}")


def augment_generated_doc_prompt(
    template_text: str,
    *,
    template_group: str,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    hooks: Any,
) -> str:
    if template_group not in hooks.MASTER_BOOTSTRAP_WORKFLOWS and template_group not in hooks.EXECUTION_SCAFFOLD_WORKFLOWS:
        return template_text

    banner = hooks.managed_banner(workflow=template_group, step=step)
    manifest = hooks.generated_doc_manifest(template_group=template_group, state=state)
    frontmatter_contract = generated_doc_frontmatter_contract(
        template_group=template_group,
        step=step,
        step_cfg=step_cfg,
        state=state,
        hooks=hooks,
    )
    return (
        template_text
        + "\n\n## Workflow-Generated Document Rule\n\n"
        + "- Every markdown document written by this step is workflow-generated and protected.\n"
        + f"- Add this exact banner immediately after the frontmatter of each generated markdown file:\n\n{banner}"
        + "- If the file uses frontmatter, include `managed_by: workflow-generated` in that frontmatter.\n"
        + "- Do not rename the target files.\n"
        + frontmatter_contract
        + "- Use the generated-doc inventory below as the authoritative protected set for this workflow.\n\n"
        + manifest
    )


def generated_doc_frontmatter_contract(
    *,
    template_group: str,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    hooks: Any,
) -> str:
    if template_group not in hooks.MASTER_BOOTSTRAP_WORKFLOWS:
        return ""

    contract_rows = master_bootstrap_frontmatter_rows(step_cfg=step_cfg, state=state, hooks=hooks)
    if not contract_rows:
        return ""

    lines = [
        "",
        "- Every generated markdown file for this step MUST include YAML frontmatter with these exact fields:",
        "  - `template_id`",
        "  - `version: \"1.0.0\"`",
        "  - `doc_type`",
        "  - `managed_by: \"workflow-generated\"`",
        "  - `generated_at: <ISO timestamp>`",
        f"  - `workflow: \"{template_group}\"`",
        f"  - `step: \"{step}\"`",
        "  - `change_id: <job id from context>`",
        "- Do not use `created`, `generated`, or `status` as substitutes for `version`, `doc_type`, or `generated_at`.",
        "- Use this exact YAML shape at the top of every generated markdown file:",
        "",
        "```yaml",
        "---",
        "template_id: \"TEMPLATE-ID\"",
        "version: \"1.0.0\"",
        "doc_type: \"system-or-codebase\"",
        "managed_by: \"workflow-generated\"",
        "generated_at: \"<ISO timestamp>\"",
        f"workflow: \"{template_group}\"",
        f"step: \"{step}\"",
        "change_id: \"<job id>\"",
        "---",
        "```",
        "",
        "- For this step, use these exact frontmatter identifiers:",
    ]
    for rel_path, template_id, doc_type in contract_rows:
        lines.append(f"  - `{rel_path}` -> `template_id: \"{template_id}\"`, `doc_type: \"{doc_type}\"`")
    lines.append("")
    return "\n".join(lines)


def master_bootstrap_frontmatter_rows(
    *,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    hooks: Any,
) -> list[tuple[str, str, str]]:
    metadata_by_artifact = {
        "PROJECT_ANALYSIS": ("SYS-00-PA", "system"),
        "SYSTEM_DOCS_INDEX": ("SYS-00-IDX", "system"),
        "SYSTEM_DOC_STANDARD": ("SYS-00-DS", "system"),
        "BUNDLE_TAXONOMY": ("SYS-00-BT", "system"),
        "BUNDLE_MIGRATION_PLAN": ("SYS-00-BMP", "system"),
        "SYSTEM_OVERVIEW": ("SYS-00-SO", "system"),
        "BUSINESS_CAPABILITIES": ("SYS-00-BC", "system"),
        "FUNCTIONAL_SPEC": ("SYS-00-FS", "system"),
        "NON_FUNCTIONAL_REQUIREMENTS": ("SYS-00-NFR", "system"),
        "SYSTEM_CONTEXT": ("SYS-03-CTX", "system"),
        "COMPONENT_ARCHITECTURE": ("SYS-03-CA", "system"),
        "DECISION_LOG": ("SYS-03-DL", "system"),
        "SYSTEM_FILE_STRUCTURE": ("SYS-03-SF", "system"),
        "DEVELOPER_GUIDE": ("ENG-01-DG", "system"),
        "RUNBOOK": ("OPS-01-RB", "system"),
        "EXISTING_REPO_WORKFLOW_SOP": ("SYS-00-ERWS", "system"),
        "SYSTEM_DOCS_CHANGE_LOG": ("SYS-00-CL", "system"),
        "INTEGRATION_MAP": ("CB-04-IM", "codebase"),
        "FAILURE_MODES": ("CB-04-FM", "codebase"),
        "ARCHITECTURE_FLOW": ("CB-04-AF", "codebase"),
    }
    job_id = str(state.get("job_id") or "{job_id}")
    mode = str((step_cfg.get("mode") or state.get("current_mode") or "bootstrap"))
    output_paths = hooks.get_master_docs_output_paths(job_id=job_id, mode=mode)
    default_paths = hooks.known_artifact_paths()
    rows: list[tuple[str, str, str]] = []
    for artifact_key in list(step_cfg.get("produces") or []):
        metadata = metadata_by_artifact.get(str(artifact_key))
        rel_path = output_paths.get(str(artifact_key)) or default_paths.get(str(artifact_key))
        if metadata is None or not rel_path or not str(rel_path).endswith(".md"):
            continue
        rows.append((str(rel_path), metadata[0], metadata[1]))
    return rows


def execute_prepared_step(
    *,
    prepared: PreparedStepExecution,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    effective_root: Path,
    hooks: Any,
) -> StepResult:
    if prepared.action_name:
        return hooks.run_action(
            action_name=prepared.action_name,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_dir=prepared.step_dir,
            project_root=effective_root,
            context=prepared.context,
        )

    result = hooks.run_step(
        group_name=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        coder=prepared.coder_used,
        coder_config=prepared.coder_config,
        prompt_text=prepared.prompt_text,
        checksum=prepared.checksum,
        step_dir=prepared.step_dir,
        project_root=effective_root,
        context=prepared.context,
    )

    if prepared.post_action and result.status == "APPROVED":
        print(f"[step_runner] Running post_action={prepared.post_action} after LLM step", flush=True)
        post_result = hooks.run_action(
            action_name=prepared.post_action,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_dir=prepared.step_dir,
            project_root=effective_root,
            context=prepared.context,
        )
        if post_result.artifacts:
            result.artifacts.update(post_result.artifacts)
        if post_result.status != "APPROVED":
            result.status = post_result.status
            result.remark = f"{result.remark}; post_action: {post_result.remark}"
            if post_result.reject_code:
                result.reject_code = post_result.reject_code

    return result


def resolve_step_coder(
    *,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    cli_coder: str | None,
    hooks: Any,
) -> tuple[str, str | None, str | None, dict[str, Any] | None]:
    coder_cfg = step_cfg.get("coder", {})
    bundle = step_cfg.get("_workflow_bundle")
    bundle_root = getattr(bundle, "bundle_root", None)
    default_role = coder_cfg.get("default_role")
    allowed_roles = list(coder_cfg.get("allowed_roles") or [])
    default_coder = coder_cfg.get("default")
    allowed_coders = list(coder_cfg.get("allowed") or [])
    chosen = cli_coder.strip() if cli_coder else (default_role or default_coder)
    if not chosen:
        raise ValueError(f"No coder specified and no default coder configured for step {step!r}")

    original = chosen
    resolved_role: str | None = None
    role_alias = hooks.resolve_role_alias(original, bundle_root=bundle_root)
    if role_alias:
        resolved_role = original
        chosen = role_alias

    resolved_config = hooks.resolve_coder(chosen)
    if resolved_config is not None:
        actual_coder = resolved_config.get("coder", chosen)
        hooks.log_resolver(original, f"{actual_coder} (model={resolved_config.get('model', '')})", is_alias=True)
        if shutil.which(actual_coder) is None:
            raise FileNotFoundError(f"Coder executable not found: {actual_coder!r} (alias {original!r})")
        chosen = actual_coder
    else:
        hooks.log_resolver(original, original, is_alias=False)
        if shutil.which(chosen) is None:
            raise FileNotFoundError(f"Coder executable not found in PATH: {chosen!r}")

    check_name = original if original != chosen else chosen
    if allowed_roles:
        role_name = resolved_role or check_name
        if role_name not in allowed_roles:
            raise ValueError(f"Coder role {role_name!r} is not allowed for step {step!r}. Allowed roles: {allowed_roles}")
    elif allowed_coders and check_name not in allowed_coders:
        raise ValueError(f"Coder {check_name!r} is not allowed for step {step!r}. Allowed: {allowed_coders}")
    if coder_cfg.get("must_differ_from_previous_step"):
        idx = group_cfg["steps"].index(step)
        if idx > 0:
            prev_step = group_cfg["steps"][idx - 1]
            prev_coder = state.get("step_coders", {}).get(prev_step)
            if prev_coder and chosen == prev_coder:
                raise ValueError(
                    f"Coder {chosen!r} is not allowed for step {step!r} because it matches previous step {prev_step!r}"
                )
    return chosen, original if original != chosen else None, resolved_role, resolved_config
