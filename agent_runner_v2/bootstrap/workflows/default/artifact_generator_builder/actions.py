"""Custom actions for Artifact Generator Builder.

This module provides action implementations for the artifact generator
builder workflow. Actions are deterministic, code-driven steps that
perform specific operations without LLM involvement.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# =============================================================================
# AGB Infrastructure Manifest
# =============================================================================
# Data-driven definition of AGB infrastructure. Domain data is merged at runtime.

COPY_MANIFEST = [
    {"src": "actions.py", "dst": "target_workflow/actions.py", "type": "file"},
    {"src": "prompts", "dst": "target_workflow/prompts", "type": "dir"},
]

INFRASTRUCTURE_MANIFEST = {
    "artifact_keys": {
        "outputs": {
            "TARGET_EXTENSIONS_FILE": "target_workflow/context_extensions.py",
            "TARGET_MANIFEST_FILE": "target_workflow/workflow.toml",
            "AGB_VALIDATION_FINDINGS": "VALIDATION_FINDINGS-{seq}.md",
            "AGB_PACKAGE_REVIEW": "PACKAGE_REVIEW-{seq}.md",
            "AGB_GATEKEEP_REPORT": "GATEKEEP_PACKAGE-{seq}.md",
            "TARGET_PACKAGE_DIR": "",
        }
    },
    "steps": [
        # Infrastructure steps are assembled by _assemble_package
        # Domain steps come from Analysis JSON
        {"name": "copy_infrastructure", "action": "_copy_infrastructure"},
        {"name": "assemble_package", "action": "_assemble_package"},
        {"name": "validate_structure", "action": "_validate_structure"},
        {"name": "review_package", "prompt_slot": "review_package"},
        {"name": "gatekeep_package", "prompt_slot": "gatekeep_package"},
        {"name": "promote_package", "action": "_promote_workflow_package"},
    ],
}


@action("_promote_workflow_package")
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote all deliverables to workflows/{codename}/.

    Packages the generated workflow package:

        workflows/{codename}/
            workflow.toml              # Infrastructure + domain steps
            context_extensions.py      # Infrastructure + domain artifact keys
            actions.py                 # Infrastructure actions (from AGB)
            prompts/                   # Infrastructure prompts (from AGB)
            impls/standard/            # Domain logic (actions, prompts, impl.yaml)
            README.md                  # Generated documentation

    The codename is read from the generated workflow.toml manifest.
    Existing target directories are backed up before overwriting.
    If README.md does not exist, one is generated from workflow.toml metadata.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Source: the directory containing workflow.toml
    manifest_path = artifacts.get("TARGET_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="TARGET_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    source_dir = Path(manifest_path).parent
    if not source_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow output directory not found: {source_dir}",
            artifacts={},
            reject_code="SOURCE_DIR_NOT_FOUND",
        )

    # Read codename from manifest
    import tomllib
    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    codename = manifest.get("workflow", {}).get("name", "")
    if not codename:
        return ActionResult(
            status="REJECTED",
            remark="Workflow name (codename) not found in workflow.toml [workflow] section.",
            artifacts={},
            reject_code="MISSING_CODENAME",
        )

    # Target: workflows/{codename}/
    target_dir = project_root / "workflows" / codename

    # Backup existing target
    backup_status = "No backup needed"
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = project_root / "workflows" / f"{codename}_bak_{timestamp}"
        shutil.copytree(target_dir, backup_dir)
        backup_status = f"Backed up existing workflow to {backup_dir}"
        print(f"[promote_workflow_package] backed up {target_dir} -> {backup_dir}", flush=True)

    target_dir.mkdir(parents=True, exist_ok=True)

    promoted = []

    # --- Generate README.md if not present ---
    readme_src = source_dir / "README.md"
    if not readme_src.exists():
        readme_content = _generate_readme(manifest, source_dir)
        readme_src.write_text(readme_content, encoding="utf-8")
        print(f"[promote_workflow_package] Generated README.md for '{codename}'", flush=True)

    # --- Workflow package files (root of workflows/{codename}/) ---
    always_copy = ["workflow.toml", "context_extensions.py", "actions.py", "README.md"]
    conditional_copy = [".env.sample", "config.json.sample"]
    copy_dirs = ["prompts"]

    for filename in always_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            promoted.append(filename)

    for filename in conditional_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            promoted.append(filename)

    for dirname in copy_dirs:
        src = source_dir / dirname
        if src.is_dir():
            dst = target_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            promoted.append(f"{dirname}/")

    # --- Domain implementation -> impls/ (always present) ---
    impls_src = source_dir / "impls"
    if impls_src.is_dir():
        impls_dst = target_dir / "impls"
        if impls_dst.exists():
            shutil.rmtree(impls_dst)
        shutil.copytree(impls_src, impls_dst)
        promoted.append("impls/")

    if not promoted:
        return ActionResult(
            status="REJECTED",
            remark=f"No files found to promote in {source_dir}",
            artifacts={},
            reject_code="NOTHING_TO_PROMOTE",
        )

    remark = (
        f"Promoted workflow '{codename}' to {target_dir}: "
        f"{', '.join(promoted)}. {backup_status}"
    )
    print(f"[promote_workflow_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"TARGET_PACKAGE_DIR": str(target_dir)},
    )


@action("_assemble_package")
def assemble_package(*, context, state, step_cfg, project_root):
    """Deterministically build workflow.toml from the Analysis JSON.

    This action is the mechanical assembler — no LLM involved. It reads the
    Analysis JSON's domain_steps and produces workflow.toml — the abstract
    step sequence with routing and artifact bindings.

    Note: context_extensions.py is generated by copy_infrastructure (step 7).
    Domain files (impls/standard/*) are written by implement_domain (step 5).
    This action ONLY produces workflow.toml.
    """
    import json
    import re

    artifacts = state.get("artifacts", {})
    analysis_path = artifacts.get("AGB_ANALYSIS_JSON", "")
    if not analysis_path:
        return ActionResult(
            status="REJECTED",
            remark="AGB_ANALYSIS_JSON artifact not found in state.",
            artifacts={},
            reject_code="MISSING_ANALYSIS_JSON",
        )

    analysis_file = Path(analysis_path)
    if not analysis_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Analysis JSON not found: {analysis_file}",
            artifacts={},
            reject_code="MISSING_ANALYSIS_JSON",
        )

    try:
        analysis = json.loads(analysis_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to parse Analysis JSON: {e}",
            artifacts={},
            reject_code="PARSE_ERROR",
        )

    identity = analysis.get("identity", {})
    domain_steps = analysis.get("domain_steps", [])
    artifact_keys = analysis.get("artifact_keys", {})

    if not identity or not domain_steps:
        return ActionResult(
            status="REJECTED",
            remark="Analysis JSON missing required 'identity' or 'domain_steps'.",
            artifacts={},
            reject_code="INVALID_ANALYSIS",
        )

    # Validate prompt steps have required role_policy
    for step in domain_steps:
        if step["type"] == "prompt" and not step.get("role_policy"):
            return ActionResult(
                status="REJECTED",
                remark=f"Prompt step '{step['name']}' is missing required 'role_policy'.",
                artifacts={},
                reject_code="MISSING_ROLE_POLICY",
            )

    # Filter out infrastructure steps — AGB pipeline actions are prefixed with "_".
    # Domain actions must NOT use the "_" prefix.
    filtered_steps = []
    for step in domain_steps:
        action_name = step.get("action_name", "")
        if step["type"] == "action" and action_name.startswith("_"):
            print(
                f"[assemble_package] WARNING: Filtering infrastructure step "
                f"'{step['name']}' (action={action_name}) from domain_steps. "
                f"AGB infrastructure actions are prefixed with '_'.",
                flush=True,
            )
        else:
            filtered_steps.append(step)
    if len(filtered_steps) != len(domain_steps):
        print(
            f"[assemble_package] Filtered {len(domain_steps) - len(filtered_steps)} "
            f"infrastructure step(s) from domain_steps. "
            f"Remaining: {len(filtered_steps)} domain step(s).",
            flush=True,
        )
    domain_steps = filtered_steps

    if not domain_steps:
        return ActionResult(
            status="REJECTED",
            remark="All domain_steps were infrastructure steps. No domain logic to assemble.",
            artifacts={},
            reject_code="NO_DOMAIN_STEPS",
        )

    # Determine output directory — job output root
    job_id = str(state.get("job_id", "unknown"))
    out_dir = Path(project_root) / "output" / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    produced = {}

    toml_lines = []
    toml_lines.append(f'# Workflow: {identity.get("label", identity["name"])}')
    toml_lines.append(f'# Auto-assembled by AGB from Analysis JSON.')
    toml_lines.append("")
    toml_lines.append("[workflow]")
    toml_lines.append(f'name = "{_toml_str(identity["name"])}"')
    toml_lines.append(f'version = "{_toml_str(identity.get("version", "1.0.0"))}"')
    toml_lines.append(f'label = "{_toml_str(identity.get("label", identity["name"]))}"')
    toml_lines.append(f'job_prefix = "{_toml_str(identity["job_prefix"])}"')
    toml_lines.append(f'init_step = "{_toml_str(domain_steps[0]["name"])}"')
    if identity.get("description"):
        toml_lines.append(f'description = "{_toml_str(identity["description"])}"')
    toml_lines.append('default_max_rejects = 3')
    toml_lines.append('visibility = "canonical"')
    toml_lines.append('layer = "layer3"')
    toml_lines.append('platform = "agent-runner-v2"')
    toml_lines.append("")

    # Implementation declarations — always include "standard" as the default
    toml_lines.append("[[workflow.implementation]]")
    toml_lines.append('name = "standard"')
    toml_lines.append(f'description = "Default implementation for {identity.get("label", identity.get("name", "workflow"))}"')
    toml_lines.append('label = "Standard"')
    toml_lines.append("")

    # Step definitions
    for i, step in enumerate(domain_steps):
        toml_lines.append("[[step]]")
        toml_lines.append(f'name = "{_toml_str(step["name"])}"')

        if step["type"] == "action":
            toml_lines.append(f'action = "{_toml_str(step["action_name"])}"')
        else:
            toml_lines.append(f'prompt = "impls/standard/prompts/{_toml_str(step["prompt_file"])}"')

        toml_lines.append("enable_notifications = false")
        toml_lines.append("requires_human_approval_after = false")

        # onsuccess: chain to next domain step, or first infrastructure step
        if i < len(domain_steps) - 1:
            toml_lines.append(f'onsuccess = "{domain_steps[i + 1]["name"]}"')
        else:
            toml_lines.append('onsuccess = "copy_infrastructure"')

        # Coder config for prompt steps
        if step["type"] == "prompt" and step.get("role_policy"):
            toml_lines.append("")
            toml_lines.append("[step.coder]")
            toml_lines.append(f'role_policy = "{step["role_policy"]}"')

        # Artifact bindings
        req_inputs = step.get("required_inputs", [])
        produces = step.get("produces", [])
        if req_inputs or produces:
            toml_lines.append("")
            toml_lines.append("[step.artifacts]")
            if req_inputs:
                keys_str = ", ".join(f'"{k}"' for k in req_inputs)
                toml_lines.append(f"required_inputs = [{keys_str}]")
            if produces:
                keys_str = ", ".join(f'"{k}"' for k in produces)
                toml_lines.append(f"produces = [{keys_str}]")
            # result_meta_key = first produced key
            if produces:
                toml_lines.append(f'result_meta_key = "{produces[0]}"')

        toml_lines.append("")

    # -------------------------------------------------------------------------
    # Infrastructure steps (only for AGB builder workflows)
    # -------------------------------------------------------------------------
    # Check if this is an AGB builder workflow (type="builder" or is_agb_builder flag)
    workflow_type = identity.get("type", "")
    is_agb_builder = identity.get("is_agb_builder", False) or workflow_type == "builder"

    if is_agb_builder:
        # Infrastructure Phase: Only for AGB builder workflows that generate other workflows
        toml_lines.append("# Infrastructure Phase")
        toml_lines.append("")
        toml_lines.append("[[step]]")
        toml_lines.append('name = "copy_infrastructure"')
        toml_lines.append('action = "_copy_infrastructure"')
        toml_lines.append("enable_notifications = false")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "assemble_package"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["AGB_ANALYSIS_JSON"]')
        toml_lines.append('produces = ["TARGET_EXTENSIONS_FILE"]')
        toml_lines.append('result_meta_key = "TARGET_EXTENSIONS_FILE"')
        toml_lines.append("")

        # Step: assemble_package
        toml_lines.append("[[step]]")
        toml_lines.append('name = "assemble_package"')
        toml_lines.append('action = "_assemble_package"')
        toml_lines.append("enable_notifications = true")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "validate_structure"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["AGB_ANALYSIS_JSON", "DOMAIN_ACTIONS_FILE", "DOMAIN_PROMPTS_DIR"]')
        toml_lines.append('produces = ["TARGET_MANIFEST_FILE"]')
        toml_lines.append('result_meta_key = "TARGET_MANIFEST_FILE"')
        toml_lines.append("")

        # Step: validate_structure
        toml_lines.append("[[step]]")
        toml_lines.append('name = "validate_structure"')
        toml_lines.append('action = "_validate_structure"')
        toml_lines.append("enable_notifications = true")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "review_package"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["TARGET_MANIFEST_FILE", "DOMAIN_ACTIONS_FILE", "TARGET_EXTENSIONS_FILE"]')
        toml_lines.append('produces = ["AGB_VALIDATION_FINDINGS"]')
        toml_lines.append('result_meta_key = "AGB_VALIDATION_FINDINGS"')
        toml_lines.append("")

        # Step: review_package (LLM)
        toml_lines.append("[[step]]")
        toml_lines.append('name = "review_package"')
        toml_lines.append('prompt = "{{ slot.review_package }}"')
        toml_lines.append("enable_notifications = true")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "gatekeep_package"')
        toml_lines.append("")
        toml_lines.append("[step.coder]")
        toml_lines.append('role_policy = "reviewer_standard"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["TARGET_MANIFEST_FILE", "DOMAIN_ACTIONS_FILE", "TARGET_EXTENSIONS_FILE", "DOMAIN_PROMPTS_DIR", "AGB_ANALYSIS_JSON"]')
        toml_lines.append('produces = ["AGB_PACKAGE_REVIEW"]')
        toml_lines.append('result_meta_key = "AGB_PACKAGE_REVIEW"')
        toml_lines.append("")
        toml_lines.append("[step.on_reject_refine]")
        toml_lines.append('step = "implement_domain"')
        toml_lines.append('artifact = "AGB_PACKAGE_REVIEW"')
        toml_lines.append("max_iterations = 2")
        toml_lines.append('exhausted_failure_code = "PACKAGE_REVIEW_EXHAUSTED"')
        toml_lines.append('exhausted_failure_class = "HUMAN_RETRY_REQUIRED"')
        toml_lines.append("")

        # Step: gatekeep_package (LLM)
        toml_lines.append("[[step]]")
        toml_lines.append('name = "gatekeep_package"')
        toml_lines.append('prompt = "{{ slot.gatekeep_package }}"')
        toml_lines.append("enable_notifications = true")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "promote_package"')
        toml_lines.append("")
        toml_lines.append("[step.coder]")
        toml_lines.append('role_policy = "gatekeeper_standard"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["TARGET_MANIFEST_FILE", "DOMAIN_ACTIONS_FILE", "AGB_VALIDATION_FINDINGS", "AGB_PACKAGE_REVIEW", "AGB_ANALYSIS_JSON"]')
        toml_lines.append('produces = ["AGB_GATEKEEP_REPORT"]')
        toml_lines.append('result_meta_key = "AGB_GATEKEEP_REPORT"')
        toml_lines.append("")
        toml_lines.append("[step.on_reject_refine]")
        toml_lines.append('step = "implement_domain"')
        toml_lines.append('artifact = "AGB_GATEKEEP_REPORT"')
        toml_lines.append("max_iterations = 2")
        toml_lines.append('exhausted_failure_code = "GATEKEEP_EXHAUSTED"')
        toml_lines.append('exhausted_failure_class = "HUMAN_RETRY_REQUIRED"')
        toml_lines.append("")

        # Step: promote_package
        toml_lines.append("[[step]]")
        toml_lines.append('name = "promote_package"')
        toml_lines.append('action = "_promote_workflow_package"')
        toml_lines.append("enable_notifications = true")
        toml_lines.append("requires_human_approval_after = false")
        toml_lines.append('onsuccess = "step_completion"')
        toml_lines.append("")
        toml_lines.append("[step.artifacts]")
        toml_lines.append('required_inputs = ["TARGET_MANIFEST_FILE", "DOMAIN_ACTIONS_FILE", "TARGET_EXTENSIONS_FILE", "DOMAIN_PROMPTS_DIR"]')
        toml_lines.append('produces = ["TARGET_PACKAGE_DIR"]')
        toml_lines.append('result_meta_key = "TARGET_PACKAGE_DIR"')
        toml_lines.append("")
        toml_lines.append("[step.config]")
        toml_lines.append('artifact_key = "TARGET_PACKAGE_DIR"')
        toml_lines.append("backup = true")
        toml_lines.append("")

    # Terminal step
    toml_lines.append("[[step]]")
    toml_lines.append('name = "step_completion"')
    toml_lines.append('action = "step_completion"')
    toml_lines.append("")

    # Write workflow.toml to target_workflow/ subdirectory
    target_workflow_dir = out_dir / "target_workflow"
    target_workflow_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_workflow_dir / "workflow.toml"
    manifest_path.write_text("\n".join(toml_lines), encoding="utf-8")
    produced["TARGET_MANIFEST_FILE"] = str(manifest_path)

    infra_count = 6 if is_agb_builder else 0
    remark = (
        f"Assembled workflow.toml for '{identity['name']}': "
        f"{len(domain_steps)} domain steps + {infra_count} infrastructure steps + terminal"
    )
    print(f"[assemble_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=produced,
    )


def _extract_filename(pattern: str, key: str) -> str:
    """Extract a filename from an artifact pattern for the two-dict convention.

    The Analysis JSON may contain patterns like:
    - "input/{filename}"       → extract "{filename}" or derive from key
    - "output/SUMMARY_FILE.md" → extract "SUMMARY_FILE.md"
    - "SUMMARY_FILE.md"        → use as-is
    - "{filename}"              → use as-is

    For input keys, returns the filename template (may contain placeholders).
    For output keys, returns the filename pattern (may contain {seq}).
    """
    if not pattern:
        return ""
    # Strip known directory prefixes
    for prefix in ("input/", "output/", "intermediate/"):
        if pattern.startswith(prefix):
            pattern = pattern[len(prefix):]
            break
    # If the pattern is just a placeholder like "{filename}", derive from key
    if pattern.startswith("{") and pattern.endswith("}"):
        placeholder_inner = pattern[1:-1]
        if placeholder_inner == "filename":
            # Derive a sensible default from the key name
            if key.endswith("_FILE"):
                return f"{key}.dat"
            elif key.endswith("_DIR"):
                return ""
            else:
                return f"{key}.dat"
        return pattern
    # Use the remaining pattern as-is (it's a filename or filename with placeholders)
    return pattern


def _to_pascal_case(name: str) -> str:
    """Convert a snake_case or hyphen-case name to PascalCase."""
    return "".join(
        word.capitalize() for word in name.replace("-", "_").split("_") if word
    )


def _toml_str(value: str) -> str:
    """Escape a string for safe embedding in a TOML basic string (double-quoted)."""
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _generate_readme(manifest: dict, source_dir: Path) -> str:
    """Generate a README.md from workflow.toml metadata."""
    wf = manifest.get("workflow", {})
    name = wf.get("name", "unknown")
    label = wf.get("label", name)
    version = wf.get("version", "1.0.0")
    description = wf.get("description", "")

    # Collect step info
    steps = manifest.get("step", [])
    step_lines = []
    for i, step in enumerate(steps, 1):
        sname = step.get("name", "?")
        if "action" in step:
            stype = "action"
            detail = step["action"]
        elif "prompt" in step:
            stype = "prompt"
            detail = step["prompt"]
        else:
            stype = "?"
            detail = ""
        step_lines.append(f"| {i} | {sname} | {stype} | {detail} |")

    # Collect implementations
    impls = manifest.get("workflow", {}).get("implementation", [])
    impl_section = ""
    if impls:
        impl_section = "\n## Implementations\n\n"
        impl_section += "| Name | Description |\n"
        impl_section += "|------|-------------|\n"
        for impl in impls:
            impl_section += f"| {impl.get('name', '?')} | {impl.get('description', '')} |\n"

    steps_table = "\n".join(step_lines) if step_lines else "| — | No steps defined | — | — |"

    return f"""# {label}

{description}

**Version:** {version}

## Pipeline Steps

| # | Step | Type | Detail |
|---|------|------|--------|
{steps_table}
{impl_section}
## Usage

```bash
ukbe-run-agent run --template-group {name}
```

## File Structure

```
{name}/
    workflow.toml              # Infrastructure + domain steps
    context_extensions.py      # Infrastructure + domain artifact keys
    actions.py                 # Infrastructure actions
    prompts/                   # Infrastructure prompts
    impls/standard/            # Domain logic (actions, prompts, impl.yaml)
    README.md
```
"""


@action("_validate_structure")
def validate_structure(*, context, state, step_cfg, project_root):
    """Run deterministic structural validation on the generated package.

    Uses workflow_package_validator.validate_package() to check:
    - TOML parse and structure
    - Python syntax
    - Artifact key bindings
    - Action implementations
    - Prompt file existence
    - Placeholder consistency

    Writes findings to {AGB_VALIDATION_FINDINGS}.
    """
    from agent_runner_v2.workflow_package_validator import (
        validate_package,
        render_report,
    )

    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    manifest_path = artifacts.get("TARGET_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="TARGET_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    extensions_path = artifacts.get("TARGET_EXTENSIONS_FILE", "")
    actions_path = artifacts.get("DOMAIN_ACTIONS_FILE", "")
    impl_path = artifacts.get("DOMAIN_IMPL_FILE", "")

    # Validate impl.yaml exists
    findings = []
    if impl_path:
        impl_yaml_path = Path(impl_path)
        if not impl_yaml_path.exists():
            findings.append({
                "level": "error",
                "code": "MISSING_IMPL_YAML",
                "message": f"impl.yaml not found at {impl_yaml_path}",
            })
        else:
            # Check it's valid YAML
            try:
                import yaml
                with open(impl_yaml_path, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
            except Exception as e:
                findings.append({
                    "level": "error",
                    "code": "INVALID_IMPL_YAML",
                    "message": f"impl.yaml is not valid YAML: {e}",
                })
    else:
        findings.append({
            "level": "error",
            "code": "MISSING_IMPL_YAML_ARTIFACT",
            "message": "DOMAIN_IMPL_FILE not declared in artifacts",
        })

    # Get root actions.py (infrastructure actions copied from AGB)
    root_actions_path = Path(manifest_path).parent / "actions.py"

    result = validate_package(
        manifest_path=Path(manifest_path),
        extensions_path=Path(extensions_path) if extensions_path else None,
        actions_path=Path(actions_path) if actions_path else None,
        infra_actions_path=root_actions_path if root_actions_path.exists() else None,
    )

    # Add impl.yaml findings to result
    if findings:
        from agent_runner_v2.workflow_package_validator import ValidationFinding
        for f in findings:
            result.findings.append(ValidationFinding(
                level=f["level"],
                code=f["code"],
                message=f["message"],
            ))

    # Use context-resolved path for the validation findings report
    job_id = str(state.get("job_id", "unknown"))
    report_path_str = context.get("AGB_VALIDATION_FINDINGS", "")
    if not report_path_str:
        report_path_str = artifacts.get("AGB_VALIDATION_FINDINGS", "")
    if report_path_str:
        report_path = Path(report_path_str)
        if not report_path.is_absolute():
            report_path = project_root / report_path
    else:
        # Fallback: construct from job_id using output/{job_id}/ convention
        run_root = project_root / "output" / job_id
        report_path = run_root / f"VALIDATION_FINDINGS-{datetime.now().strftime('%Y%m%d')}-001.md"

    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = render_report(result, job_id=job_id)
    report_path.write_text(report, encoding="utf-8")

    errors = [f for f in result.findings if f.level == "error"]
    if errors:
        error_summary = "; ".join(f"{f.code}: {f.message}" for f in errors[:5])
        return ActionResult(
            status="REJECTED",
            remark=f"Structural validation failed with {len(errors)} error(s): {error_summary}",
            artifacts={"AGB_VALIDATION_FINDINGS": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Structural validation passed. {render_report(result)}",
        artifacts={"AGB_VALIDATION_FINDINGS": str(report_path)},
    )


@action("_generate_domain_map")
def generate_domain_map(*, context, state, step_cfg, project_root):
    """Generate a domain artifact map from the Analysis JSON.

    Reads the Analysis JSON and produces a focused reference document showing:
    - All domain artifact keys (inputs, intermediate, outputs)
    - Which step produces each key
    - Which step consumes each key
    - Data flow chain

    This gives the implement_domain step a clear, readable reference for
    artifact key bindings — without exposing infrastructure files.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    analysis_path = artifacts.get("AGB_ANALYSIS_JSON", "")
    if not analysis_path:
        return ActionResult(
            status="REJECTED",
            remark="AGB_ANALYSIS_JSON artifact not found in state.",
            artifacts={},
            reject_code="MISSING_ANALYSIS_JSON",
        )

    analysis_file = Path(analysis_path)
    if not analysis_file.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Analysis JSON not found: {analysis_file}",
            artifacts={},
            reject_code="MISSING_ANALYSIS_JSON",
        )

    try:
        analysis = json.loads(analysis_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to parse Analysis JSON: {e}",
            artifacts={},
            reject_code="PARSE_ERROR",
        )

    domain_steps = analysis.get("domain_steps", [])
    artifact_keys = analysis.get("artifact_keys", {})
    identity = analysis.get("identity", {})

    # Build producer/consumer maps
    producers = {}  # key -> step name
    consumers = {}  # key -> [step names]
    for step in domain_steps:
        step_name = step.get("name", "?")
        for key in step.get("produces", []):
            producers[key] = step_name
        for key in step.get("required_inputs", []):
            consumers.setdefault(key, []).append(step_name)

    # Generate markdown
    lines = []
    lines.append(f"# Domain Artifact Map: {identity.get('label', identity.get('name', 'workflow'))}")
    lines.append("")
    lines.append(f"> Auto-generated from Analysis JSON. Domain keys only — no infrastructure artifacts.")
    lines.append("")

    # Input artifacts
    inputs = artifact_keys.get("inputs", [])
    if inputs:
        lines.append("## Input Artifacts")
        lines.append("")
        lines.append("| Key | Pattern | Consumed By |")
        lines.append("|-----|---------|-------------|")
        for entry in inputs:
            key = entry["key"]
            pattern = entry.get("pattern", "")
            consumed = ", ".join(consumers.get(key, ["(none)"]))
            lines.append(f"| `{key}` | `{pattern}` | {consumed} |")
        lines.append("")

    # Intermediate artifacts
    intermediates = artifact_keys.get("intermediate", [])
    if intermediates:
        lines.append("## Intermediate Artifacts")
        lines.append("")
        lines.append("| Key | Pattern | Produced By | Consumed By |")
        lines.append("|-----|---------|-------------|-------------|")
        for entry in intermediates:
            key = entry["key"]
            pattern = entry.get("pattern", "")
            produced = producers.get(key, "(none)")
            consumed = ", ".join(consumers.get(key, ["(none)"]))
            lines.append(f"| `{key}` | `{pattern}` | {produced} | {consumed} |")
        lines.append("")

    # Output artifacts
    outputs = artifact_keys.get("outputs", [])
    if outputs:
        lines.append("## Output Artifacts")
        lines.append("")
        lines.append("| Key | Pattern | Produced By |")
        lines.append("|-----|---------|-------------|")
        for entry in outputs:
            key = entry["key"]
            pattern = entry.get("pattern", "")
            produced = producers.get(key, "(none)")
            lines.append(f"| `{key}` | `{pattern}` | {produced} |")
        lines.append("")

    # Data flow chain
    lines.append("## Data Flow")
    lines.append("")
    lines.append("```")
    for step in domain_steps:
        step_name = step.get("name", "?")
        step_type = step.get("type", "?")
        inputs_list = step.get("required_inputs", [])
        outputs_list = step.get("produces", [])
        inputs_str = ", ".join(inputs_list) if inputs_list else "(none)"
        outputs_str = ", ".join(outputs_list) if outputs_list else "(none)"
        lines.append(f"[{step_name}] ({step_type})")
        lines.append(f"  inputs:  {inputs_str}")
        lines.append(f"  outputs: {outputs_str}")
        lines.append("")
    lines.append("```")

    # Write output
    output_path = context.get("AGB_DOMAIN_MAP", "")
    if not output_path:
        output_path = artifacts.get("AGB_DOMAIN_MAP", "")
    if output_path:
        out_file = Path(output_path)
        if not out_file.is_absolute():
            out_file = project_root / out_file
    else:
        job_id = str(state.get("job_id", "unknown"))
        out_dir = project_root / "output" / job_id
        out_file = out_dir / "AGB_DOMAIN_MAP.md"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines), encoding="utf-8")

    n_keys = len(inputs) + len(intermediates) + len(outputs)
    remark = f"Generated domain artifact map: {n_keys} keys across {len(domain_steps)} steps"
    print(f"[generate_domain_map] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"AGB_DOMAIN_MAP": str(out_file)},
    )


@action("noop")
def noop_action(*, context, state, step_cfg, project_root):
    """No-operation action — returns success immediately.
    
    Used by implementations to skip infrastructure steps when generating
    content artifacts instead of complete workflows.
    """
    return ActionResult(
        status="APPROVED",
        remark="Step skipped (no-op)",
        artifacts={},
    )


def _generate_context_extensions(
    analysis: dict,
    out_dir: Path,
) -> Path:
    """Generate context_extensions.py merging infrastructure + domain artifact keys.

    Infrastructure keys are hardcoded (same for every AGB builder).
    Domain keys come from the Analysis JSON's artifact_keys.

    Args:
        analysis: The parsed Analysis JSON dict.
        out_dir: The output directory where context_extensions.py will be written.

    Returns:
        Path to the generated context_extensions.py file.
    """
    identity = analysis.get("identity", {})
    artifact_keys = analysis.get("artifact_keys", {})

    class_name = _to_pascal_case(identity["name"]) + "Extensions"

    # --- Domain keys from Analysis JSON ---
    input_keys = {}
    for entry in artifact_keys.get("inputs", []):
        key = entry["key"]
        pattern = entry["pattern"]
        filename = _extract_filename(pattern, key)
        input_keys[key] = filename

    output_keys = {}
    for cat in ("intermediate", "outputs"):
        for entry in artifact_keys.get(cat, []):
            key = entry["key"]
            pattern = entry["pattern"]
            filename = _extract_filename(pattern, key)
            output_keys[key] = filename

    # --- Infrastructure keys (hardcoded template — same for all AGB builders) ---
    infra_output_keys = {
        "TARGET_EXTENSIONS_FILE": "context_extensions.py",
        "TARGET_MANIFEST_FILE": "workflow.toml",
        "AGB_VALIDATION_FINDINGS": "VALIDATION_FINDINGS-{seq}.md",
        "AGB_PACKAGE_REVIEW": "PACKAGE_REVIEW-{seq}.md",
        "AGB_GATEKEEP_REPORT": "GATEKEEP_PACKAGE-{seq}.md",
        "TARGET_PACKAGE_DIR": "",
    }

    # Merge: domain keys first, then infrastructure keys
    # (used in OUTPUT_ARTIFACTS dict generation below)

    ext_lines = []
    ext_lines.append(f'"""Context extensions for {identity.get("label", identity["name"])}."""')
    ext_lines.append("")
    ext_lines.append("from __future__ import annotations")
    ext_lines.append("")
    ext_lines.append("from pathlib import Path")
    ext_lines.append("from typing import Any")
    ext_lines.append("")
    ext_lines.append("from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root")
    ext_lines.append("from agent_runner_v2.workflow_packages.extensions_base import (")
    ext_lines.append("    WorkflowExtensions,")
    ext_lines.append("    resolve_input_artifacts,")
    ext_lines.append("    resolve_output_artifacts,")
    ext_lines.append(")")
    ext_lines.append("")
    ext_lines.append("")
    ext_lines.append(f"class {class_name}(WorkflowExtensions):")
    ext_lines.append(f'    workflow_name = "{identity["name"]}"')
    ext_lines.append("")

    # INPUT_ARTIFACTS dict (domain only — infrastructure has no input artifacts)
    ext_lines.append("    # -- Input artifacts: resolved to {workspace_root}/input/ --")
    ext_lines.append("    INPUT_ARTIFACTS: dict[str, str] = {")
    for key, filename in input_keys.items():
        ext_lines.append(f'        "{key}": "{filename}",')
    ext_lines.append("    }")
    ext_lines.append("")

    # OUTPUT_ARTIFACTS dict (domain + infrastructure)
    ext_lines.append("    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --")
    ext_lines.append("    OUTPUT_ARTIFACTS: dict[str, str] = {")
    ext_lines.append("        # Domain artifacts")
    for key, filename in output_keys.items():
        ext_lines.append(f'        "{key}": "{filename}",')
    ext_lines.append("        # Infrastructure artifacts")
    for key, filename in infra_output_keys.items():
        ext_lines.append(f'        "{key}": "{filename}",')
    ext_lines.append("    }")
    ext_lines.append("")

    # register_artifact_keys (backward compat)
    ext_lines.append("    def register_artifact_keys(")
    ext_lines.append('        self, *, job_id: str = "{job_id}", mode: str = "{mode}"')
    ext_lines.append("    ) -> dict[str, str]:")
    ext_lines.append("        combined: dict[str, str] = {}")
    ext_lines.append("        for key in self.INPUT_ARTIFACTS:")
    ext_lines.append('            combined[key] = "input/"')
    ext_lines.append("        for key, pattern in self.OUTPUT_ARTIFACTS.items():")
    ext_lines.append('            combined[key] = f"output/{job_id}/{pattern}"')
    ext_lines.append("        return combined")
    ext_lines.append("")

    # build_context_extensions using two resolvers
    ext_lines.append("    def build_context_extensions(")
    ext_lines.append("        self, *, state, step, step_cfg, ctx, project_root=None,")
    ext_lines.append("    ) -> dict[str, str]:")
    ext_lines.append("        result: dict[str, str] = {}")
    ext_lines.append("        workspace_root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()")
    ext_lines.append("        result[\"GOVERNANCE_RUNTIME_ROOT\"] = str(get_governance_runtime_root())")
    ext_lines.append("        result[\"PLATFORM_RUNTIME_ROOT\"] = str(get_platform_runtime_root())")
    ext_lines.append("        result[\"BASE_COMPOSITION_STANDARD\"] = str(")
    ext_lines.append("            get_governance_runtime_root() / \"BCS_v2.0.md\"")
    ext_lines.append("        )")
    ext_lines.append("        resolve_input_artifacts(result, state, workspace_root, self.INPUT_ARTIFACTS)")
    ext_lines.append("        resolve_output_artifacts(result, state, workspace_root, self.OUTPUT_ARTIFACTS)")
    ext_lines.append("        return result")
    ext_lines.append("")
    ext_lines.append("    def install_to_global(self, *, workspace_root, runner_home):")
    ext_lines.append('        return {"status": "NO_OP"}')
    ext_lines.append("")
    ext_lines.append("    def sync_to_backend(self, *, workspace_root):")
    ext_lines.append('        return {"status": "NO_OP"}')
    ext_lines.append("")

    extensions_path = out_dir / "context_extensions.py"
    extensions_path.write_text("\n".join(ext_lines), encoding="utf-8")
    return extensions_path


@action("_copy_infrastructure")
def copy_infrastructure_action(*, context, state, step_cfg, project_root):
    """Copy AGB infrastructure files and generate context_extensions.py.

    Uses COPY_MANIFEST (module-level constant) to define source->destination mappings.
    All files are written to target_workflow/ subdirectory for the final package.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))
    out_dir = project_root / "output" / job_id
    target_workflow_dir = out_dir / "target_workflow"

    agb_dir = Path(__file__).parent

    # Create target_workflow directory
    target_workflow_dir.mkdir(parents=True, exist_ok=True)

    # Copy files using module-level COPY_MANIFEST
    copied = []
    for item in COPY_MANIFEST:
        src = agb_dir / item["src"]
        dst = out_dir / item["dst"]
        is_dir = item["type"] == "dir"

        if not src.exists():
            return ActionResult(
                status="REJECTED",
                remark=f"Source not found: {src}",
                artifacts={},
                reject_code="SOURCE_NOT_FOUND",
            )

        # Ensure parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        if is_dir:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied.append(f"{item['src']} -> {item['dst']}")

    # Generate context_extensions.py in target_workflow/
    analysis_path = artifacts.get("AGB_ANALYSIS_JSON", "")
    if not analysis_path or not Path(analysis_path).exists():
        return ActionResult(
            status="REJECTED",
            remark="AGB_ANALYSIS_JSON not found.",
            artifacts={},
            reject_code="MISSING_ANALYSIS_JSON",
        )

    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    extensions_path = _generate_context_extensions(analysis, target_workflow_dir)
    copied.append("context_extensions.py -> target_workflow/")

    remark = f"Copied infrastructure: {', '.join(copied)}"
    print(f"[copy_infrastructure] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"TARGET_EXTENSIONS_FILE": str(extensions_path)},
    )


