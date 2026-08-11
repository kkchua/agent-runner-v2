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


@action("promote_workflow_package")
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote all deliverables to workflows/{codename}/.

    Packages the generated workflow package:

        workflows/{codename}/
            workflow.toml
            context_extensions.py
            actions.py
            prompts/
            README.md
            impls/              (optional — only if alternative impls exist)

    The codename is read from the generated workflow.toml manifest.
    Existing target directories are backed up before overwriting.
    If README.md does not exist, one is generated from workflow.toml metadata.

    EXTEND MODE: If EXISTING_WORKFLOW_DIR is provided, merge new implementations
    into the existing workflow instead of overwriting. Only new impls/ are added,
    and workflow.toml is updated in place.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)
    existing_workflow_dir = artifacts.get("EXISTING_WORKFLOW_DIR", "")
    extend_mode = bool(existing_workflow_dir)

    # Source: the directory containing workflow.toml
    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
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

    # -------------------------------------------------------------------------
    # EXTEND MODE: Merge new implementations into existing workflow
    # -------------------------------------------------------------------------
    if extend_mode:
        existing_dir = Path(existing_workflow_dir)
        if not existing_dir.exists():
            return ActionResult(
                status="REJECTED",
                remark=f"Existing workflow directory not found: {existing_dir}",
                artifacts={},
                reject_code="EXISTING_WORKFLOW_NOT_FOUND",
            )

        # If target_dir doesn't exist yet, copy from existing_dir first
        if not target_dir.exists():
            shutil.copytree(existing_dir, target_dir)
            print(f"[promote_workflow_package] Initialized target from existing: {existing_dir} -> {target_dir}", flush=True)

        # Update workflow.toml (replace with merged version from source_dir)
        src_toml = source_dir / "workflow.toml"
        if src_toml.exists():
            shutil.copy2(src_toml, target_dir / "workflow.toml")
            print(f"[promote_workflow_package] Updated workflow.toml with new impl declarations", flush=True)

        # Merge new impls/ into existing impls/
        src_impls = source_dir / "impls"
        dst_impls = target_dir / "impls"
        if src_impls.exists():
            dst_impls.mkdir(parents=True, exist_ok=True)
            # Copy each new impl directory
            for impl_dir in src_impls.iterdir():
                if impl_dir.is_dir():
                    dst_impl_dir = dst_impls / impl_dir.name
                    if dst_impl_dir.exists():
                        shutil.rmtree(dst_impl_dir)
                    shutil.copytree(impl_dir, dst_impl_dir)
                    print(f"[promote_workflow_package] Added new impl: {impl_dir.name}", flush=True)

        remark = f"Extended workflow '{codename}' at {target_dir} with new implementations."
        print(f"[promote_workflow_package] {remark}", flush=True)

        return ActionResult(
            status="APPROVED",
            remark=remark,
            artifacts={"WORKFLOW_PACKAGE_DIR": str(target_dir)},
        )

    # -------------------------------------------------------------------------
    # NEW WORKFLOW MODE: Full promotion with backup
    # -------------------------------------------------------------------------

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
    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
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

    # --- Alternative implementations -> impls/ (optional) ---
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
        artifacts={"WORKFLOW_PACKAGE_DIR": str(target_dir)},
    )


@action("assemble_package")
def assemble_package(*, context, state, step_cfg, project_root):
    """Deterministically build workflow.toml, context_extensions.py, and impl.yaml
    from the Analysis JSON produced by analyze_requirement.

    This action is the mechanical assembler — no LLM involved. It reads the
    Analysis JSON and produces the structural files that plug domain-specific
    actions and prompts into the predefined platform infrastructure.
    """
    import json
    import re

    artifacts = state.get("artifacts", {})
    analysis_path = artifacts.get("ANALYSIS_JSON_FILE", "")
    if not analysis_path:
        return ActionResult(
            status="REJECTED",
            remark="ANALYSIS_JSON_FILE artifact not found in state.",
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
    implementations = analysis.get("implementations", [])
    extend_mode = analysis.get("extend_mode", False)
    existing_workflow_dir = artifacts.get("EXISTING_WORKFLOW_DIR", "")

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

    # Determine output directory (same dir as actions.py)
    actions_path = artifacts.get("WORKFLOW_ACTIONS_FILE", "")
    if actions_path:
        out_dir = Path(actions_path).parent
    else:
        job_id = str(state.get("job_id", "unknown"))
        out_dir = (
            Path(project_root)
            / "output"
            / job_id
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    produced = {}

    # -------------------------------------------------------------------------
    # EXTEND MODE: Copy existing workflow files and add new implementation
    # -------------------------------------------------------------------------
    if extend_mode:
        if not existing_workflow_dir:
            return ActionResult(
                status="REJECTED",
                remark="EXISTING_WORKFLOW_DIR artifact required for extend mode.",
                artifacts={},
                reject_code="MISSING_EXISTING_WORKFLOW",
            )

        existing_dir = Path(existing_workflow_dir)
        if not existing_dir.exists():
            return ActionResult(
                status="REJECTED",
                remark=f"Existing workflow directory not found: {existing_dir}",
                artifacts={},
                reject_code="EXISTING_WORKFLOW_NOT_FOUND",
            )

        # Copy existing workflow.toml and append new implementation declarations
        existing_toml = existing_dir / "workflow.toml"
        if not existing_toml.exists():
            return ActionResult(
                status="REJECTED",
                remark=f"Existing workflow.toml not found: {existing_toml}",
                artifacts={},
                reject_code="EXISTING_TOML_NOT_FOUND",
            )

        # Read existing TOML content
        toml_content = existing_toml.read_text(encoding="utf-8")

        # Append new implementation declarations
        for impl in implementations:
            toml_content += "\n[[workflow.implementation]]\n"
            toml_content += f'name = "{_toml_str(impl["name"])}"\n'
            toml_content += f'description = "{_toml_str(impl.get("description", ""))}"\n'
            if impl.get("label"):
                toml_content += f'label = "{_toml_str(impl["label"])}"\n'

        manifest_path = out_dir / "workflow.toml"
        manifest_path.write_text(toml_content, encoding="utf-8")
        produced["WORKFLOW_MANIFEST_FILE"] = str(manifest_path)

        # Copy existing context_extensions.py
        existing_ext = existing_dir / "context_extensions.py"
        if existing_ext.exists():
            shutil.copy2(existing_ext, out_dir / "context_extensions.py")
            produced["WORKFLOW_EXTENSIONS_FILE"] = str(out_dir / "context_extensions.py")

        # Copy existing actions.py if not provided (extend mode may not regenerate it)
        if not actions_path or not Path(actions_path).exists():
            existing_actions = existing_dir / "actions.py"
            if existing_actions.exists():
                shutil.copy2(existing_actions, out_dir / "actions.py")
                produced["WORKFLOW_ACTIONS_FILE"] = str(out_dir / "actions.py")

        # Copy existing prompts/ if not provided
        existing_prompts_src = existing_dir / "prompts"
        out_prompts = out_dir / "prompts"
        if not out_prompts.exists() and existing_prompts_src.exists():
            shutil.copytree(existing_prompts_src, out_prompts)
            produced["WORKFLOW_PROMPTS_DIR"] = str(out_prompts)

        # Copy existing impls/ directory if present
        existing_impls = existing_dir / "impls"
        out_impls = out_dir / "impls"
        if existing_impls.exists():
            if out_impls.exists():
                shutil.rmtree(out_impls)
            shutil.copytree(existing_impls, out_impls)

        # Generate impl.yaml for NEW implementations only
        for impl in implementations:
            impl_dir = out_impls / impl["name"]
            impl_dir.mkdir(parents=True, exist_ok=True)

            overrides = impl.get("overrides", {})
            yaml_lines = []
            yaml_lines.append(f'name: {impl["name"]}')
            desc = impl.get("description", "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            yaml_lines.append(f'description: "{desc}"')
            yaml_lines.append("")
            yaml_lines.append("overrides:")
            for step_name, step_overrides in overrides.items():
                yaml_lines.append(f"  {step_name}:")
                if "prompt" in step_overrides:
                    yaml_lines.append(f'    prompt: "{step_overrides["prompt"]}"')
                if "action" in step_overrides:
                    yaml_lines.append(f'    action: "{step_overrides["action"]}"')
            yaml_lines.append("")

            impl_yaml_path = impl_dir / "impl.yaml"
            impl_yaml_path.write_text("\n".join(yaml_lines), encoding="utf-8")

        produced["IMPL_OVERRIDE_FILES"] = str(out_impls) if out_impls.exists() else ""

        remark = (
            f"Extended workflow '{identity['name']}' with {len(implementations)} new implementation(s). "
            f"Copied existing workflow files and added new impl declarations."
        )
        print(f"[assemble_package] {remark}", flush=True)

        return ActionResult(
            status="APPROVED",
            remark=remark,
            artifacts=produced,
        )

    # -------------------------------------------------------------------------
    # NEW WORKFLOW MODE: Generate all files from scratch
    # -------------------------------------------------------------------------
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

    # Implementation declarations
    for impl in implementations:
        toml_lines.append("[[workflow.implementation]]")
        toml_lines.append(f'name = "{_toml_str(impl["name"])}"')
        toml_lines.append(f'description = "{_toml_str(impl.get("description", ""))}"')
        if impl.get("label"):
            toml_lines.append(f'label = "{_toml_str(impl["label"])}"')
        toml_lines.append("")

    # Step definitions
    for i, step in enumerate(domain_steps):
        toml_lines.append("[[step]]")
        toml_lines.append(f'name = "{_toml_str(step["name"])}"')

        if step["type"] == "action":
            toml_lines.append(f'action = "{_toml_str(step["action_name"])}"')
        else:
            toml_lines.append(f'prompt = "prompts/{_toml_str(step["prompt_file"])}"')

        toml_lines.append("enable_notifications = false")
        toml_lines.append("requires_human_approval_after = false")

        # onsuccess: chain to next step, or terminal
        if i < len(domain_steps) - 1:
            toml_lines.append(f'onsuccess = "{domain_steps[i + 1]["name"]}"')
        else:
            toml_lines.append('onsuccess = "step_completion"')

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

    # Terminal step
    toml_lines.append("[[step]]")
    toml_lines.append('name = "step_completion"')
    toml_lines.append('action = "step_completion"')
    toml_lines.append("")

    manifest_path = out_dir / "workflow.toml"
    manifest_path.write_text("\n".join(toml_lines), encoding="utf-8")
    produced["WORKFLOW_MANIFEST_FILE"] = str(manifest_path)

    # -------------------------------------------------------------------------
    # 2. Generate context_extensions.py (two-dict pattern)
    # -------------------------------------------------------------------------
    class_name = _to_pascal_case(identity["name"]) + "Extensions"

    # Split artifact_keys into INPUT_ARTIFACTS and OUTPUT_ARTIFACTS
    # Inputs: keys ending with _FILE or _DIR from "inputs" category
    # Outputs: everything from "outputs" + "intermediate" categories
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

    all_keys = {**input_keys, **output_keys}

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

    # INPUT_ARTIFACTS dict
    ext_lines.append("    # -- Input artifacts: resolved to {workspace_root}/input/ --")
    ext_lines.append("    INPUT_ARTIFACTS: dict[str, str] = {")
    for key, filename in input_keys.items():
        ext_lines.append(f'        "{key}": "{filename}",')
    ext_lines.append("    }")
    ext_lines.append("")

    # OUTPUT_ARTIFACTS dict
    ext_lines.append("    # -- Output artifacts: resolved to {workspace_root}/output/{job_id}/ --")
    ext_lines.append("    OUTPUT_ARTIFACTS: dict[str, str] = {")
    for key, filename in output_keys.items():
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
    ext_lines.append("            get_governance_runtime_root() / \"BASE_COMPOSITION_STANDARD_v1.0.md\"")
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
    produced["WORKFLOW_EXTENSIONS_FILE"] = str(extensions_path)

    # -------------------------------------------------------------------------
    # 3. Generate impl.yaml files
    # -------------------------------------------------------------------------
    impl_paths = []
    for impl in implementations:
        impl_dir = out_dir / "impls" / impl["name"]
        impl_dir.mkdir(parents=True, exist_ok=True)

        overrides = impl.get("overrides", {})
        yaml_lines = []
        yaml_lines.append(f'name: {impl["name"]}')
        desc = impl.get("description", "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        yaml_lines.append(f'description: "{desc}"')
        yaml_lines.append("")
        yaml_lines.append("overrides:")
        for step_name, step_overrides in overrides.items():
            yaml_lines.append(f"  {step_name}:")
            if "prompt" in step_overrides:
                yaml_lines.append(f'    prompt: "{step_overrides["prompt"]}"')
            if "action" in step_overrides:
                yaml_lines.append(f'    action: "{step_overrides["action"]}"')
        yaml_lines.append("")

        impl_yaml_path = impl_dir / "impl.yaml"
        impl_yaml_path.write_text("\n".join(yaml_lines), encoding="utf-8")
        impl_paths.append(str(impl_yaml_path))

    produced["IMPL_OVERRIDE_FILES"] = str(out_dir / "impls") if impl_paths else ""

    remark = (
        f"Assembled workflow package for '{identity['name']}': "
        f"workflow.toml ({len(domain_steps)} steps + terminal), "
        f"context_extensions.py ({len(all_keys)} artifact keys), "
        f"{len(implementations)} implementation(s)"
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
        impl_section += "| default | Default implementation (workflow.toml) |\n"
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
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
    impls/          (if alternative implementations exist)
    README.md
```
"""


@action("validate_structure")
def validate_structure(*, context, state, step_cfg, project_root):
    """Run deterministic structural validation on the generated package.

    Uses workflow_package_validator.validate_package() to check:
    - TOML parse and structure
    - Python syntax
    - Artifact key bindings
    - Action implementations
    - Prompt file existence
    - Placeholder consistency

    Writes findings to {VALIDATION_FINDINGS_FILE}.
    """
    from agent_runner_v2.workflow_package_validator import (
        validate_package,
        render_report,
    )

    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    extensions_path = artifacts.get("WORKFLOW_EXTENSIONS_FILE", "")
    actions_path = artifacts.get("WORKFLOW_ACTIONS_FILE", "")

    result = validate_package(
        manifest_path=Path(manifest_path),
        extensions_path=Path(extensions_path) if extensions_path else None,
        actions_path=Path(actions_path) if actions_path else None,
    )

    # Use context-resolved path for the validation findings report
    job_id = str(state.get("job_id", "unknown"))
    report_path_str = context.get("VALIDATION_FINDINGS_FILE", "")
    if not report_path_str:
        report_path_str = artifacts.get("VALIDATION_FINDINGS_FILE", "")
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
            artifacts={"VALIDATION_FINDINGS_FILE": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Structural validation passed. {render_report(result)}",
        artifacts={"VALIDATION_FINDINGS_FILE": str(report_path)},
    )


