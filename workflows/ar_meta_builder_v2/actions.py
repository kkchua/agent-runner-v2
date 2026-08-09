"""Custom actions for AR Meta Builder v2.

Provides:
- validate_input_spec: Pre-flight check on the runtime spec.
- validate_design_artifact: Phase-parameterized deterministic validation.
- validate_package: Full package validation before review.
- promote_workflow_package: Deploy generated package to workflows/.
"""
from __future__ import annotations

import ast
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _finding(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def _read_spec_identity(spec_path: Path) -> dict[str, str]:
    """Extract identity fields from a runtime spec's YAML frontmatter."""
    if not spec_path.is_file():
        return {}
    text = spec_path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = text[3:end]
    identity: dict[str, str] = {}
    for key in (
        "workflow_name",
        "standard_name",
        "standard_version",
        "standard_filename",
        "output_type",
    ):
        m = re.search(rf'^{key}\s*:\s*["\']?([^"\n]+?)["\']?\s*$', fm, re.M)
        if m:
            identity[key] = m.group(1).strip()
    return identity


def _write_report(
    findings: list[dict[str, str]],
    job_id: str,
    project_root: Path,
    report_name: str = "VALIDATION",
) -> Path:
    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]
    valid = len(errors) == 0

    run_root = (
        project_root / "docs" / "repo" / "ar_meta_builder_v2" / "runs" / job_id
    )
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = (
        run_root
        / f"{report_name}-{datetime.now().strftime('%Y%m%d')}-001.md"
    )

    lines = [
        "---",
        f'doc_type: "{report_name.lower()}"',
        'lifecycle_status: "final"',
        f'job_id: "{job_id}"',
        "---",
        "",
        f"# {report_name} Report",
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
        lines.append("No findings. All checks passed.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# 1. validate_input_spec
# ---------------------------------------------------------------------------


@action("validate_input_spec")
def validate_input_spec(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Pre-flight validation of the runtime spec.

    Checks:
    - Spec file exists and is readable
    - YAML frontmatter present with identity fields
    - standard_name, standard_version, standard_filename declared
    - output_type declared (documented_versioned or direct)
    - Domain overview section present
    - At least one component or domain concept described
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})
    spec_path_str = artifacts.get("WORKFLOW_SPEC_FILE", "")
    spec_path = Path(spec_path_str) if spec_path_str else None
    findings: list[dict[str, str]] = []

    if not spec_path or not spec_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"WORKFLOW_SPEC_FILE not found: {spec_path_str}",
            artifacts={},
            reject_code="SPEC_NOT_FOUND",
        )

    text = spec_path.read_text(encoding="utf-8", errors="replace")

    # Check YAML frontmatter
    if not text.startswith("---"):
        findings.append(_finding(
            "error", "NO_FRONTMATTER",
            "Spec file does not start with YAML frontmatter (---)",
        ))
    else:
        identity = _read_spec_identity(spec_path)

        for field in ("standard_name", "standard_version", "standard_filename"):
            if field not in identity:
                findings.append(_finding(
                    "error", "MISSING_IDENTITY_FIELD",
                    f"Frontmatter missing required field: {field}",
                ))

        if "output_type" not in identity:
            findings.append(_finding(
                "error", "MISSING_OUTPUT_TYPE",
                "Frontmatter missing output_type declaration",
            ))
        elif identity["output_type"] not in (
            "documented_versioned", "direct",
        ):
            findings.append(_finding(
                "error", "INVALID_OUTPUT_TYPE",
                f"output_type must be 'documented_versioned' or 'direct', "
                f"got '{identity['output_type']}'",
            ))

    # Check domain overview section
    if not re.search(r"^#+ .*domain", text, re.I | re.M):
        findings.append(_finding(
            "warning", "NO_DOMAIN_SECTION",
            "No section heading containing 'domain' found",
        ))

    # Check for at least one component or concept
    if not re.search(
        r"(component|type|phase|binding|artifact)", text, re.I,
    ):
        findings.append(_finding(
            "warning", "NO_COMPONENT_CONCEPT",
            "Spec does not appear to describe any components or domain concepts",
        ))

    job_id = str(state.get("job_id", "unknown"))
    report_path = _write_report(findings, job_id, project_root, "VALIDATION_INPUT_SPEC")

    errors = [f for f in findings if f["level"] == "error"]
    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Input spec validation failed: {len(errors)} error(s)",
            artifacts={"VALIDATION_INPUT_SPEC_FILE": str(report_path)},
            reject_code="INPUT_SPEC_VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark="Input spec validation passed.",
        artifacts={"VALIDATION_INPUT_SPEC_FILE": str(report_path)},
    )


# ---------------------------------------------------------------------------
# 2. validate_design_artifact (parameterized by phase)
# ---------------------------------------------------------------------------

# Phase -> (artifact key, expected sections/patterns)
_PHASE_CHECKS: dict[str, dict[str, Any]] = {
    "domain_analysis": {
        "required_patterns": [
            (r"target_identity|identity", "identity section"),
            (r"output_type", "output_type declaration"),
            (r"meta_test_criteria|meta.test", "meta-test-criteria"),
        ],
    },
    "component_schema": {
        "required_patterns": [
            (r"component.?type", "component type definitions"),
            (r"common.?propert|validation.?rule|VR-", "properties or rules"),
        ],
    },
    "composition_format": {
        "required_patterns": [
            (r"binding.?rule|binding", "binding rules"),
            (r"override|placeholder", "override or placeholder mechanism"),
        ],
    },
    "output_format": {
        "required_patterns": [
            (r"output.?struct|resolution.?rule|quality.?req",
             "output structure or rules"),
        ],
    },
    "artifact_contract": {
        "required_patterns": [
            (r"artifact.?key|key.*pattern", "artifact key definitions"),
        ],
    },
    "step_sequence": {
        "required_patterns": [
            (r"step|routing|onsuccess|on_reject", "step definitions or routing"),
        ],
    },
    "runtime_standard": {
        "required_patterns": [
            (r"standard_name|standard_version|consolidat",
             "standard identity or consolidation"),
        ],
    },
    "operational_workflow": {
        "required_patterns": [
            (r"workflow.?step|prompt.?file|action",
             "workflow steps or implementation details"),
        ],
    },
}


@action("validate_design_artifact")
def validate_design_artifact(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Phase-parameterized deterministic validation of design artifacts.

    Reads ``step_cfg["phase"]`` and ``step_cfg["artifact_key"]`` to
    determine which artifact to validate and what checks to apply.

    Common checks (all phases):
    - Artifact file exists and is non-empty
    - File contains ASCII-only content
    - Identity fields in the file match the spec (if detectable)

    Phase-specific checks:
    - Required content patterns are present
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})
    findings: list[dict[str, str]] = []

    phase = step_cfg.get("phase", "")
    artifact_key = step_cfg.get("artifact_key", "")

    if not phase or not artifact_key:
        findings.append(_finding(
            "error", "MISSING_CONFIG",
            "step_cfg must define 'phase' and 'artifact_key'",
        ))
        job_id = str(state.get("job_id", "unknown"))
        report_path = _write_report(
            findings, job_id, project_root, f"VALIDATE_{phase or 'unknown'}",
        )
        return ActionResult(
            status="REJECTED",
            remark="Missing step configuration for validate_design_artifact",
            artifacts={f"VALIDATE_{phase.upper()}_FILE": str(report_path)},
            reject_code="MISSING_VALIDATE_CONFIG",
        )

    artifact_path_str = artifacts.get(artifact_key, "")
    artifact_path = Path(artifact_path_str) if artifact_path_str else None

    # Check file exists
    if not artifact_path or not artifact_path.is_file():
        findings.append(_finding(
            "error", "ARTIFACT_NOT_FOUND",
            f"{artifact_key} not found at {artifact_path_str}",
        ))
        job_id = str(state.get("job_id", "unknown"))
        report_path = _write_report(
            findings, job_id, project_root, f"VALIDATE_{phase.upper()}",
        )
        return ActionResult(
            status="REJECTED",
            remark=f"{artifact_key} file not found",
            artifacts={f"VALIDATE_{phase.upper()}_FILE": str(report_path)},
            reject_code="ARTIFACT_NOT_FOUND",
        )

    text = artifact_path.read_text(encoding="utf-8", errors="replace")

    # Non-empty check
    if len(text.strip()) < 100:
        findings.append(_finding(
            "error", "ARTIFACT_TOO_SHORT",
            f"{artifact_key} has only {len(text.strip())} chars, expected more",
        ))

    # ASCII-only check
    non_ascii = [
        (i + 1, ch)
        for i, ch in enumerate(text)
        if ord(ch) > 127 and ch not in ("\n", "\r", "\t")
    ]
    if non_ascii:
        samples = non_ascii[:5]
        findings.append(_finding(
            "warning", "NON_ASCII_CONTENT",
            f"Found {len(non_ascii)} non-ASCII chars, e.g. line "
            f"{samples[0][0]}: {samples[0][1]!r}",
        ))

    # Identity leak check -- the artifact should NOT contain the
    # builder's identity as the target identity
    spec_identity = _read_spec_identity(
        Path(artifacts.get("WORKFLOW_SPEC_FILE", ""))
    )
    target_wf = spec_identity.get("workflow_name", "")
    if target_wf and target_wf != "ar_meta_builder_v2":
        # Check that the artifact uses the TARGET identity, not the builder's
        if "ar_meta_builder_v2" in text and target_wf not in text:
            findings.append(_finding(
                "error", "BUILDER_IDENTITY_LEAK",
                "Artifact contains builder identity 'ar_meta_builder_v2' "
                "but not the target identity",
            ))

    # Phase-specific pattern checks
    phase_info = _PHASE_CHECKS.get(phase, {})
    for pattern, description in phase_info.get("required_patterns", []):
        if not re.search(pattern, text, re.I):
            findings.append(_finding(
                "error", "MISSING_PHASE_CONTENT",
                f"Phase '{phase}' artifact missing: {description} "
                f"(pattern: {pattern})",
            ))

    # Phase 5 (artifact_contract): check for key uniqueness indicators
    if phase == "artifact_contract":
        if not re.search(r"unique|conflict|registry", text, re.I):
            findings.append(_finding(
                "warning", "NO_UNIQUENESS_CHECK",
                "Artifact contract does not mention key uniqueness or "
                "conflict checking",
            ))

    job_id = str(state.get("job_id", "unknown"))
    report_path = _write_report(
        findings, job_id, project_root, f"VALIDATE_{phase.upper()}",
    )

    errors = [f for f in findings if f["level"] == "error"]
    result_key = f"VALIDATE_{phase.upper()}_FILE"

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Validation of {phase} failed: {len(errors)} error(s), "
                f"see {report_path.name}"
            ),
            artifacts={result_key: str(report_path)},
            reject_code=f"VALIDATE_{phase.upper()}_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Validation of {phase} passed.",
        artifacts={result_key: str(report_path)},
    )


# ---------------------------------------------------------------------------
# 3. validate_package
# ---------------------------------------------------------------------------


@action("validate_package")
def validate_package(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Full package validation before review.

    Checks:
    1. TOML parse validity of workflow.toml
    2. Python syntax of context_extensions.py and actions.py
    3. TYPE_CHECKING runtime import detection
    4. Identity consistency -- workflow.toml name matches spec
    5. No builder identity leakage (QR-002)
    6. Prompt file existence
    7. Prompt placeholder vs required_inputs consistency
    8. context_extensions.py artifact key coverage
    9. Standards/ directory with composition standard
    10. Specs/ directory with embedded builder spec
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})
    findings: list[dict[str, str]] = []

    manifest_str = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    extensions_str = artifacts.get("WORKFLOW_EXTENSIONS_FILE", "")
    actions_str = artifacts.get("WORKFLOW_ACTIONS_FILE", "")

    manifest_path = Path(manifest_str) if manifest_str else None
    extensions_path = Path(extensions_str) if extensions_str else None
    actions_path = Path(actions_str) if actions_str else None

    bundle_root = (
        manifest_path.parent
        if manifest_path and manifest_path.is_file()
        else None
    )

    if not manifest_path or not manifest_path.is_file():
        findings.append(_finding(
            "error", "MISSING_MANIFEST",
            "workflow.toml not found",
        ))
        job_id = str(state.get("job_id", "unknown"))
        report_path = _write_report(findings, job_id, project_root, "VALIDATION")
        return ActionResult(
            status="REJECTED",
            remark="workflow.toml not found",
            artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
            reject_code="DETERMINISTIC_VALIDATION_FAILED",
        )

    # 1. TOML validity
    manifest_data = None
    try:
        import tomllib
        with open(manifest_path, "rb") as f:
            manifest_data = tomllib.load(f)
    except Exception as exc:
        findings.append(_finding(
            "error", "TOML_PARSE_ERROR",
            f"workflow.toml is not valid TOML: {exc}",
        ))
        job_id = str(state.get("job_id", "unknown"))
        report_path = _write_report(findings, job_id, project_root, "VALIDATION")
        return ActionResult(
            status="REJECTED",
            remark=f"TOML parse error: {exc}",
            artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
            reject_code="DETERMINISTIC_VALIDATION_FAILED",
        )

    # 2. Python syntax
    for label, path in [
        ("context_extensions.py", extensions_path),
        ("actions.py", actions_path),
    ]:
        if path and path.is_file():
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                findings.append(_finding(
                    "error", "PYTHON_SYNTAX_ERROR",
                    f"{label} syntax error at line {exc.lineno}: {exc.msg}",
                ))

    # 3. TYPE_CHECKING import detection
    if actions_path and actions_path.is_file():
        _check_type_checking_imports(actions_path, findings)

    # 4. Identity consistency
    spec_identity = _read_spec_identity(
        Path(artifacts.get("WORKFLOW_SPEC_FILE", ""))
    )
    target_name = spec_identity.get("workflow_name", "")
    toml_name = ""
    if manifest_data:
        toml_name = manifest_data.get("workflow", {}).get("name", "")

    if target_name and toml_name and toml_name != target_name:
        findings.append(_finding(
            "error", "IDENTITY_MISMATCH",
            f"workflow.toml name='{toml_name}' does not match "
            f"spec workflow_name='{target_name}'",
        ))

    # 5. Builder identity leakage (QR-002)
    if target_name and target_name != "ar_meta_builder_v2" and bundle_root:
        builder_names = {"ar_meta_builder_v2", "AMB_STANDARD", "AMB"}
        for py_file in bundle_root.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="replace")
            for bn in builder_names:
                if bn in content:
                    findings.append(_finding(
                        "error", "BUILDER_LEAKAGE",
                        f"{py_file.relative_to(bundle_root)} contains "
                        f"builder identity '{bn}'",
                    ))
        toml_text = manifest_path.read_text(encoding="utf-8", errors="replace")
        for bn in builder_names:
            if bn in toml_text:
                findings.append(_finding(
                    "error", "BUILDER_LEAKAGE",
                    f"workflow.toml contains builder identity '{bn}'",
                ))

    # 6. Prompt file existence
    if manifest_data and bundle_root:
        steps = manifest_data.get("step", [])
        if isinstance(steps, list):
            for step in steps:
                prompt_file = step.get("prompt", "")
                if prompt_file:
                    prompt_path = bundle_root / prompt_file
                    if not prompt_path.is_file():
                        findings.append(_finding(
                            "error", "MISSING_PROMPT_FILE",
                            f"Step '{step.get('name', '')}' references "
                            f"'{prompt_file}' but file does not exist",
                        ))

    # 7. Prompt placeholder vs required_inputs consistency
    if manifest_data and bundle_root:
        steps = manifest_data.get("step", [])
        if isinstance(steps, list):
            for step in steps:
                prompt_file = step.get("prompt", "")
                if not prompt_file:
                    continue
                prompt_path = bundle_root / prompt_file
                if not prompt_path.is_file():
                    continue
                arts = step.get("artifacts", {})
                declared = (
                    set(arts.get("required_inputs", []))
                    | set(arts.get("optional_inputs", []))
                    | set(arts.get("produces", []))
                    | set(arts.get("optional_produces", []))
                )
                content = prompt_path.read_text(encoding="utf-8")
                placeholders = set(
                    re.findall(r"\{([A-Z][A-Z0-9_]+)\}", content)
                )
                non_artifact = {"ARTIFACT_KEY", "job_id", "seq", "UNRESOLVED"}
                placeholders -= non_artifact
                undeclared = placeholders - declared
                for key in sorted(undeclared):
                    findings.append(_finding(
                        "error", "PROMPT_INPUT_MISMATCH",
                        f"Prompt '{prompt_file}' references {{{key}}} "
                        f"but it is not declared in step artifacts",
                    ))

    # 8. context_extensions.py artifact key coverage
    if manifest_data and extensions_path and extensions_path.is_file():
        steps = manifest_data.get("step", [])
        all_keys: set[str] = set()
        if isinstance(steps, list):
            for step in steps:
                arts = step.get("artifacts", {})
                for kl in [
                    "produces", "optional_produces",
                    "required_inputs", "optional_inputs",
                ]:
                    all_keys.update(arts.get(kl, []))
        ext_source = extensions_path.read_text(encoding="utf-8")
        missing = [
            k for k in sorted(all_keys)
            if f'"{k}"' not in ext_source and f"'{k}'" not in ext_source
        ]
        if missing:
            findings.append(_finding(
                "warning", "UNREGISTERED_ARTIFACT_KEYS",
                f"Keys in workflow.toml but not in context_extensions.py: "
                f"{', '.join(missing[:10])}",
            ))

    # 9. Standards/ directory
    if bundle_root:
        standards_dir = bundle_root / "Standards"
        if not standards_dir.is_dir():
            findings.append(_finding(
                "error", "MISSING_STANDARDS_DIR",
                "Standards/ directory not found in output package",
            ))
        else:
            md_files = list(standards_dir.glob("*.md"))
            if not md_files:
                findings.append(_finding(
                    "error", "EMPTY_STANDARDS_DIR",
                    "Standards/ directory has no .md files",
                ))

    # 10. Specs/ directory
    if bundle_root:
        specs_dir = bundle_root / "Specs"
        if not specs_dir.is_dir():
            findings.append(_finding(
                "warning", "MISSING_SPECS_DIR",
                "Specs/ directory not found (needed for self-bootstrap)",
            ))

    job_id = str(state.get("job_id", "unknown"))
    report_path = _write_report(findings, job_id, project_root, "VALIDATION")

    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]

    if errors:
        error_summary = "\n".join(
            f"  - [{e['code']}] {e['message']}" for e in errors[:10]
        )
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Package validation failed: {len(errors)} error(s), "
                f"{len(warnings)} warning(s):\n{error_summary}"
            ),
            artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
            reject_code="DETERMINISTIC_VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Package validation passed. {len(warnings)} warning(s), 0 errors.",
        artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
    )


def _check_type_checking_imports(
    path: Path, findings: list[dict[str, str]],
) -> None:
    """Detect imports inside TYPE_CHECKING blocks used at runtime."""
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return

    type_checking_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_tc = False
            if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                is_tc = True
            elif isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
                is_tc = True
            if is_tc:
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        for alias in child.names:
                            type_checking_names.add(alias.asname or alias.name)

    if not type_checking_names:
        return

    actually_used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in type_checking_names:
                actually_used.add(node.func.id)

    for name in sorted(actually_used):
        findings.append(_finding(
            "error", "TYPE_CHECKING_RUNTIME_IMPORT",
            f"'{name}' imported inside TYPE_CHECKING but called at runtime",
        ))


# ---------------------------------------------------------------------------
# 4. promote_workflow_package
# ---------------------------------------------------------------------------


@action("promote_workflow_package")
def promote_workflow_package(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Deploy the generated workflow package to workflows/ directory."""
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    slug_source_key = step_cfg.get(
        "slug_source_artifact", "WORKFLOW_SPEC_FILE",
    )
    spec_path = artifacts.get(slug_source_key, "")
    if not spec_path:
        return ActionResult(
            status="REJECTED",
            remark=f"{slug_source_key} artifact not found.",
            artifacts={},
            reject_code="MISSING_SPEC",
        )
    slug = Path(spec_path).stem
    if not slug:
        return ActionResult(
            status="REJECTED",
            remark=f"Could not derive slug from {spec_path}",
            artifacts={},
            reject_code="SLUG_EXTRACTION_FAILED",
        )

    manifest_path = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found.",
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

    target_dir.mkdir(parents=True, exist_ok=True)

    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
    copy_dirs = ["prompts", "Standards", "Specs"]

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
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"WORKFLOW_PACKAGE_DIR_FILE": str(target_dir)},
    )
