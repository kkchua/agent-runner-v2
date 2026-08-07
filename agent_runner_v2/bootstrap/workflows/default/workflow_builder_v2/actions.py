"""Custom actions for workflow_builder_v2 — Composition System Builder.

Provides:
- validate_package_deterministic: Static analysis of generated package files
  to catch runtime defects before LLM gatekeeper review.
- promote_workflow_package: Deploy generated package to workflows/ directory.
"""
from __future__ import annotations

import ast
import re
import shutil
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Deterministic package validation
# ---------------------------------------------------------------------------

@action("validate_package_deterministic")
def validate_package_deterministic(
    *, context: dict[str, str], state: dict[str, Any], step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Run static analysis on generated package files to catch runtime defects.

    Catches issues that LLM gatekeepers frequently miss:
    - TYPE_CHECKING imports used at runtime (NameError)
    - Artifact binding inconsistencies (self-referential, missing producers)
    - Python syntax errors in actions.py / context_extensions.py
    - TOML parse failures in workflow.toml
    - Missing files declared in workflow.toml
    - Action steps without corresponding @action implementations

    This runs BEFORE gatekeep_package so the LLM reviewer gets a clean
    report instead of rediscovering these issues at high token cost.
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})
    findings: list[dict[str, str]] = []

    # --- 1. Locate core files ---
    manifest_path_str = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    extensions_path_str = artifacts.get("WORKFLOW_EXTENSIONS_FILE", "")
    actions_path_str = artifacts.get("WORKFLOW_ACTIONS_FILE", "")

    manifest_path = Path(manifest_path_str) if manifest_path_str else None
    extensions_path = Path(extensions_path_str) if extensions_path_str else None
    actions_path = Path(actions_path_str) if actions_path_str else None

    bundle_root = manifest_path.parent if manifest_path and manifest_path.is_file() else None

    if not manifest_path or not manifest_path.is_file():
        findings.append(_finding("error", "MISSING_MANIFEST", "workflow.toml not found or not a file"))
        return _result(findings, state, project_root)

    # --- 2. TOML validity ---
    manifest_data = None
    try:
        import tomllib
        with open(manifest_path, "rb") as f:
            manifest_data = tomllib.load(f)
    except Exception as exc:
        findings.append(_finding("error", "TOML_PARSE_ERROR", f"workflow.toml is not valid TOML: {exc}"))
        return _result(findings, state, project_root)

    # --- 3. Python syntax validation ---
    for label, path in [("context_extensions.py", extensions_path), ("actions.py", actions_path)]:
        if path and path.is_file():
            _check_python_syntax(path, label, findings)

    # --- 4. TYPE_CHECKING import detection ---
    if actions_path and actions_path.is_file():
        _check_type_checking_imports(actions_path, findings)

    # --- 5. Artifact binding consistency ---
    if manifest_data:
        _check_artifact_bindings(manifest_data, findings)

    # --- 6. Action step completeness ---
    if manifest_data and actions_path and actions_path.is_file():
        _check_action_implementations(manifest_data, actions_path, findings)

    # --- 7. File existence for declared prompts ---
    if manifest_data and bundle_root:
        _check_prompt_files(manifest_data, bundle_root, findings)

    # --- 8. context_extensions.py artifact key coverage ---
    if manifest_data and extensions_path and extensions_path.is_file():
        _check_extension_key_coverage(manifest_data, extensions_path, findings)

    return _result(findings, state, project_root)


def _finding(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def _result(findings: list[dict[str, str]], state: dict[str, Any], project_root: Path) -> ActionResult:
    """Write validation report and return ActionResult."""
    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]

    # Write report
    job_id = str(state.get("job_id", "unknown"))
    run_root = project_root / "docs" / "repo" / "workflow_builder" / "runs" / job_id
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / f"VALIDATION-{datetime.now().strftime('%Y%m%d')}-001_deterministic.md"
    report_path.write_text(_render_report(findings, job_id), encoding="utf-8")

    if errors:
        error_summary = "\n".join(f"  - [{e['code']}] {e['message']}" for e in errors[:10])
        return ActionResult(
            status="REJECTED",
            remark=f"Deterministic validation found {len(errors)} error(s), {len(warnings)} warning(s):\n{error_summary}",
            artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
            reject_code="DETERMINISTIC_VALIDATION_FAILED",
        )

    remark = f"Deterministic validation passed. {len(warnings)} warning(s), 0 errors."
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
    )


def _check_python_syntax(path: Path, label: str, findings: list[dict[str, str]]) -> None:
    """Check that a Python file parses without syntax errors."""
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        findings.append(_finding(
            "error", "PYTHON_SYNTAX_ERROR",
            f"{label} has syntax error at line {exc.lineno}: {exc.msg}",
        ))


def _check_type_checking_imports(path: Path, findings: list[dict[str, str]]) -> None:
    """Detect imports inside TYPE_CHECKING blocks that are used at runtime.

    This is the #1 cause of NameError in LLM-generated action code.
    The LLM puts imports inside `if TYPE_CHECKING:` for type hints,
    but those names are then used in function bodies at runtime.
    """
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return  # syntax error already reported

    # Collect names imported inside TYPE_CHECKING blocks
    type_checking_names: set[str] = set()
    # Collect names used in function bodies (runtime usage)
    runtime_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check if this is `if TYPE_CHECKING:`
            test = node.test
            is_type_checking = False
            if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                is_type_checking = True
            elif isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
                is_type_checking = True

            if is_type_checking:
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        for alias in child.names:
                            name = alias.asname or alias.name
                            # For `from module import a, b, c` each name is separate
                            type_checking_names.add(name)

    # Now find all Name references outside TYPE_CHECKING blocks
    # that match the TYPE_CHECKING-imported names
    if not type_checking_names:
        return

    # Simple heuristic: scan for function calls using TYPE_CHECKING names
    # outside of TYPE_CHECKING blocks and type annotations
    in_type_checking = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_tc = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or \
                    (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
            if is_tc:
                continue  # skip the TYPE_CHECKING block itself

        # Look for function calls and attribute access using TYPE_CHECKING names
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in type_checking_names:
                runtime_names.add(node.func.id)
        elif isinstance(node, ast.Name) and node.id in type_checking_names:
            # Check if this is in a function body (not annotation)
            # Simple check: if it's used as a call target or in an expression
            runtime_names.add(node.id)

    # Filter: only report if the name is actually called/used (not just in annotations)
    # Re-scan for actual function call usage
    actually_used_at_runtime: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in type_checking_names:
                actually_used_at_runtime.add(node.func.id)

    for name in sorted(actually_used_at_runtime):
        findings.append(_finding(
            "error", "TYPE_CHECKING_RUNTIME_IMPORT",
            f"'{name}' is imported inside TYPE_CHECKING block but called at runtime. "
            f"This will cause NameError. Move the import to top-level.",
        ))


def _check_artifact_bindings(manifest_data: dict, findings: list[dict[str, str]]) -> None:
    """Check artifact binding consistency in workflow.toml.

    Detects:
    - Self-referential bindings (artifact in both required_inputs and produces)
    - required_inputs referencing artifacts not produced by any prior step
    """
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    # Build a map of step_name -> (produces, required_inputs)
    step_produces: dict[str, set[str]] = {}
    step_inputs: dict[str, set[str]] = {}

    for step in steps:
        name = step.get("name", "")
        artifacts_section = step.get("artifacts", {})
        produces = set(artifacts_section.get("produces", []))
        optional_produces = set(artifacts_section.get("optional_produces", []))
        required_inputs = set(artifacts_section.get("required_inputs", []))
        optional_inputs = set(artifacts_section.get("optional_inputs", []))

        step_produces[name] = produces | optional_produces
        step_inputs[name] = required_inputs | optional_inputs

    # Build set of refine step names (targets of on_reject_refine)
    refine_steps: set[str] = set()
    for step in steps:
        on_reject = step.get("on_reject_refine") or {}
        target = on_reject.get("step")
        if target:
            refine_steps.add(target)

    # Check 1: Self-referential bindings
    # Refine steps legitimately read and rewrite the same artifact — skip them.
    for name in step_produces:
        if name in refine_steps:
            continue
        self_ref = step_produces[name] & step_inputs[name]
        for artifact in sorted(self_ref):
            findings.append(_finding(
                "error", "SELF_REFERENTIAL_ARTIFACT",
                f"Step '{name}' has '{artifact}' in both required_inputs and produces. "
                f"This is a self-referential binding that will fail at runtime.",
            ))

    # Check 2: required_inputs referencing artifacts not produced by any prior step
    # Build cumulative set of produced artifacts up to each step
    step_order = [s.get("name", "") for s in steps]
    produced_so_far: set[str] = set()

    for name in step_order:
        inputs = step_inputs.get(name, set())
        unresolvable = inputs - produced_so_far
        for artifact in sorted(unresolvable):
            # Skip well-known built-in artifacts
            if artifact in ("WORKFLOW_SPEC_FILE",):
                continue
            findings.append(_finding(
                "warning", "UNRESOLVABLE_INPUT_ARTIFACT",
                f"Step '{name}' requires '{artifact}' but no prior step produces it. "
                f"It may be an input artifact or a binding error.",
            ))
        produced_so_far |= step_produces.get(name, set())


def _check_action_implementations(
    manifest_data: dict, actions_path: Path, findings: list[dict[str, str]],
) -> None:
    """Check that all action-driven steps have corresponding @action implementations."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    # Built-in actions that don't need implementation in this file
    builtin_actions = {"step_completion", "promote_workflow_package", "validate_workflow_bundle"}

    actions_source = actions_path.read_text(encoding="utf-8")

    for step in steps:
        action_name = step.get("action", "")
        if not action_name or action_name in builtin_actions:
            continue

        decorator = f'@action("{action_name}")'
        if decorator not in actions_source:
            findings.append(_finding(
                "error", "MISSING_ACTION_IMPLEMENT",
                f"Step '{step.get('name', '')}' references action '{action_name}' "
                f"but {decorator} not found in actions.py",
            ))


def _check_prompt_files(
    manifest_data: dict, bundle_root: Path, findings: list[dict[str, str]],
) -> None:
    """Check that prompt files referenced in workflow.toml actually exist."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    for step in steps:
        prompt_file = step.get("prompt", "")
        if not prompt_file:
            continue
        prompt_path = bundle_root / prompt_file
        if not prompt_path.is_file():
            findings.append(_finding(
                "error", "MISSING_PROMPT_FILE",
                f"Step '{step.get('name', '')}' references prompt '{prompt_file}' "
                f"but file does not exist at {prompt_path}",
            ))


def _check_extension_key_coverage(
    manifest_data: dict, extensions_path: Path, findings: list[dict[str, str]],
) -> None:
    """Check that context_extensions.py registers all artifact keys used in workflow.toml."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    # Collect all artifact keys used in workflow.toml
    all_keys: set[str] = set()
    for step in steps:
        artifacts_section = step.get("artifacts", {})
        for key_list in ["produces", "optional_produces", "required_inputs", "optional_inputs"]:
            all_keys.update(artifacts_section.get(key_list, []))

    # Read context_extensions.py and check for key registrations
    ext_source = extensions_path.read_text(encoding="utf-8")

    missing_keys: list[str] = []
    for key in sorted(all_keys):
        # Check if the key appears as a string literal in register_artifact_keys
        if f'"{key}"' not in ext_source and f"'{key}'" not in ext_source:
            missing_keys.append(key)

    if missing_keys:
        findings.append(_finding(
            "warning", "UNREGISTERED_ARTIFACT_KEYS",
            f"Artifact keys used in workflow.toml but not registered in "
            f"context_extensions.py: {', '.join(missing_keys[:10])}",
        ))


def _render_report(findings: list[dict[str, str]], job_id: str) -> str:
    """Render deterministic validation report as Markdown."""
    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]
    valid = len(errors) == 0

    lines = [
        "---",
        f'doc_type: "deterministic_validation"',
        f'lifecycle_status: "final"',
        f'job_id: "{job_id}"',
        "---",
        "",
        "# Deterministic Package Validation Report",
        "",
        f"- **Valid:** {'YES' if valid else 'NO'}",
        f"- **Errors:** {len(errors)}",
        f"- **Warnings:** {len(warnings)}",
        "",
    ]

    if findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| Level | Code | Message |")
        lines.append("|---|---|---|")
        for f in findings:
            lines.append(f"| {f['level']} | {f['code']} | {f['message']} |")
    else:
        lines.append("No findings. Package passed all deterministic checks.")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Promote workflow package (reused from v1 pattern)
# ---------------------------------------------------------------------------

@action("promote_workflow_package")
def promote_workflow_package(
    *, context: dict[str, str], state: dict[str, Any], step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Promote the generated workflow package to the repo workflows directory.

    Copies deployable files from the run directory to workflows/{slug}/.
    The slug is derived from the WORKFLOW_SPEC_FILE artifact path.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    slug_source_key = step_cfg.get("slug_source_artifact", "WORKFLOW_SPEC_FILE")
    spec_path = artifacts.get(slug_source_key, "")
    if not spec_path:
        return ActionResult(
            status="REJECTED",
            remark=f"{slug_source_key} artifact not found in state.",
            artifacts={},
            reject_code="MISSING_SPEC",
        )
    slug = Path(spec_path).stem
    if not slug:
        return ActionResult(
            status="REJECTED",
            remark=f"Could not derive slug from {slug_source_key}: {spec_path}",
            artifacts={},
            reject_code="SLUG_EXTRACTION_FAILED",
        )

    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )
    source_dir = Path(manifest_path).parent
    target_dir = project_root / "workflows" / slug

    # Backup existing target
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = project_root / "workflows" / f"{slug}_bak_{timestamp}"
        shutil.copytree(target_dir, backup_dir)
        print(f"[promote_workflow_package] backed up {target_dir} -> {backup_dir}", flush=True)

    target_dir.mkdir(parents=True, exist_ok=True)

    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
    copy_dirs = ["prompts"]

    copied: list[str] = []

    for filename in always_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for filename in conditional_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for dirname in copy_dirs:
        src = source_dir / dirname
        if src.is_dir():
            dst = target_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(f"{dirname}/")

    if not copied:
        return ActionResult(
            status="REJECTED",
            remark=f"No files found to promote in {source_dir}",
            artifacts={},
            reject_code="NOTHING_TO_PROMOTE",
        )

    remark = f"Promoted to {target_dir}: {', '.join(copied)}"
    print(f"[promote_workflow_package] {remark}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"WORKFLOW_PACKAGE_DIR_FILE": str(target_dir)},
    )
