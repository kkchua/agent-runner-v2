"""Deterministic workflow package validator.

Reusable static analysis for any workflow package. Catches runtime defects
that LLM reviewers frequently miss:
- Python syntax errors in actions.py / context_extensions.py
- TYPE_CHECKING imports used at runtime (NameError)
- Artifact binding inconsistencies (self-referential, missing producers)
- TOML parse failures in workflow.toml
- Missing prompt files declared in workflow.toml
- Action steps without corresponding @action implementations
- Prompt placeholder vs required_inputs mismatches
- context_extensions.py artifact key coverage gaps

Extracted from workflow_builder_v2/actions.py so any workflow (AGB, SDLC,
custom builders) can call it as a validation gate.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationFinding:
    """A single validation finding."""
    level: str  # "error" or "warning"
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass
class ValidationResult:
    """Aggregate result of a package validation run."""
    findings: list[ValidationFinding] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.level == "warning"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        n_err = len(self.errors)
        n_warn = len(self.warnings)
        if self.passed:
            return f"Validation passed. {n_warn} warning(s), 0 errors."
        return f"Validation failed. {n_err} error(s), {n_warn} warning(s)."


def validate_package(
    *,
    manifest_path: Path,
    extensions_path: Path | None = None,
    actions_path: Path | None = None,
) -> ValidationResult:
    """Run all static checks on a workflow package.

    Args:
        manifest_path: Path to workflow.toml (required).
        extensions_path: Path to context_extensions.py (optional).
        actions_path: Path to actions.py (optional).

    Returns:
        ValidationResult with findings.
    """
    result = ValidationResult()

    if not manifest_path.is_file():
        result.findings.append(ValidationFinding(
            "error", "MISSING_MANIFEST", "workflow.toml not found or not a file",
        ))
        return result

    bundle_root = manifest_path.parent

    # 1. TOML validity
    manifest_data = _parse_toml(manifest_path, result)
    if manifest_data is None:
        return result

    # 2. Python syntax
    for label, path in [("context_extensions.py", extensions_path), ("actions.py", actions_path)]:
        if path and path.is_file():
            _check_python_syntax(path, label, result)

    # 3. TYPE_CHECKING import detection
    if actions_path and actions_path.is_file():
        _check_type_checking_imports(actions_path, result)

    # 4. Artifact binding consistency
    _check_artifact_bindings(manifest_data, result)

    # 5. Action step completeness
    if actions_path and actions_path.is_file():
        _check_action_implementations(manifest_data, actions_path, result)

    # 6. Prompt file existence
    _check_prompt_files(manifest_data, bundle_root, result)

    # 7. Prompt placeholder vs required_inputs consistency
    _check_prompt_input_consistency(manifest_data, bundle_root, result)

    # 8. context_extensions.py artifact key coverage
    if extensions_path and extensions_path.is_file():
        _check_extension_key_coverage(manifest_data, extensions_path, result)

    # 9. Implementation override validity
    _check_implementation_overrides(manifest_data, bundle_root, result)

    return result


def render_report(result: ValidationResult, job_id: str = "") -> str:
    """Render validation result as Markdown report."""
    lines = [
        "---",
        'doc_type: "deterministic_validation"',
        f'lifecycle_status: "final"',
    ]
    if job_id:
        lines.append(f'job_id: "{job_id}"')
    lines += [
        "---",
        "",
        "# Deterministic Package Validation Report",
        "",
        f"- **Valid:** {'YES' if result.passed else 'NO'}",
        f"- **Errors:** {len(result.errors)}",
        f"- **Warnings:** {len(result.warnings)}",
        "",
    ]

    if result.findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| Level | Code | Message |")
        lines.append("|---|---|---|")
        for f in result.findings:
            lines.append(f"| {f.level} | {f.code} | {f.message} |")
    else:
        lines.append("No findings. Package passed all deterministic checks.")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Internal check implementations
# ---------------------------------------------------------------------------

def _parse_toml(path: Path, result: ValidationResult) -> dict | None:
    """Parse workflow.toml, return data or None on failure."""
    try:
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as exc:
        result.findings.append(ValidationFinding(
            "error", "TOML_PARSE_ERROR", f"workflow.toml is not valid TOML: {exc}",
        ))
        return None


def _check_python_syntax(path: Path, label: str, result: ValidationResult) -> None:
    """Check that a Python file parses without syntax errors."""
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        result.findings.append(ValidationFinding(
            "error", "PYTHON_SYNTAX_ERROR",
            f"{label} has syntax error at line {exc.lineno}: {exc.msg}",
        ))


def _check_type_checking_imports(path: Path, result: ValidationResult) -> None:
    """Detect imports inside TYPE_CHECKING blocks that are used at runtime."""
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return

    type_checking_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_type_checking = (
                (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING")
                or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
            )
            if is_type_checking:
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        for alias in child.names:
                            name = alias.asname or alias.name
                            type_checking_names.add(name)

    if not type_checking_names:
        return

    actually_used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in type_checking_names:
                actually_used.add(node.func.id)

    for name in sorted(actually_used):
        result.findings.append(ValidationFinding(
            "error", "TYPE_CHECKING_RUNTIME_IMPORT",
            f"'{name}' is imported inside TYPE_CHECKING block but called at runtime. "
            f"This will cause NameError. Move the import to top-level.",
        ))


def _check_artifact_bindings(manifest_data: dict, result: ValidationResult) -> None:
    """Check artifact binding consistency in workflow.toml."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

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

    refine_steps: set[str] = set()
    for step in steps:
        on_reject = step.get("on_reject_refine") or {}
        target = on_reject.get("step")
        if target:
            refine_steps.add(target)

    for name in step_produces:
        if name in refine_steps:
            continue
        self_ref = step_produces[name] & step_inputs[name]
        for artifact in sorted(self_ref):
            result.findings.append(ValidationFinding(
                "error", "SELF_REFERENTIAL_ARTIFACT",
                f"Step '{name}' has '{artifact}' in both required_inputs and produces. "
                f"This is a self-referential binding that will fail at runtime.",
            ))

    step_order = [s.get("name", "") for s in steps]
    produced_so_far: set[str] = set()

    for name in step_order:
        inputs = step_inputs.get(name, set())
        unresolvable = inputs - produced_so_far
        for artifact in sorted(unresolvable):
            if artifact in ("WORKFLOW_SPEC_FILE",):
                continue
            result.findings.append(ValidationFinding(
                "warning", "UNRESOLVABLE_INPUT_ARTIFACT",
                f"Step '{name}' requires '{artifact}' but no prior step produces it. "
                f"It may be an input artifact or a binding error.",
            ))
        produced_so_far |= step_produces.get(name, set())


def _check_action_implementations(
    manifest_data: dict, actions_path: Path, result: ValidationResult,
) -> None:
    """Check that all action-driven steps have @action implementations."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    builtin_actions = {
        "step_completion", "promote_workflow_package", "validate_workflow_bundle",
        "promote_artifact", "copy_artifact", "archive_inputs", "promote_init",
        "validate_package_deterministic", "promote_workflow_package",
    }

    try:
        actions_source = actions_path.read_text(encoding="utf-8")
    except Exception:
        return

    for step in steps:
        action_name = step.get("action", "")
        if not action_name or action_name in builtin_actions:
            continue

        decorator = f'@action("{action_name}")'
        if decorator not in actions_source:
            result.findings.append(ValidationFinding(
                "error", "MISSING_ACTION_IMPLEMENT",
                f"Step '{step.get('name', '')}' references action '{action_name}' "
                f"but {decorator} not found in actions.py",
            ))


def _check_prompt_files(
    manifest_data: dict, bundle_root: Path, result: ValidationResult,
) -> None:
    """Check that prompt files referenced in workflow.toml exist."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    for step in steps:
        prompt_file = step.get("prompt", "")
        if not prompt_file:
            continue
        prompt_path = bundle_root / prompt_file
        if not prompt_path.is_file():
            result.findings.append(ValidationFinding(
                "error", "MISSING_PROMPT_FILE",
                f"Step '{step.get('name', '')}' references prompt '{prompt_file}' "
                f"but file does not exist at {prompt_path}",
            ))


def _check_prompt_input_consistency(
    manifest_data: dict, bundle_root: Path, result: ValidationResult,
) -> None:
    """Check that artifact placeholders in prompts are declared in workflow.toml."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    for step in steps:
        prompt_file = step.get("prompt", "")
        if not prompt_file:
            continue

        prompt_path = bundle_root / prompt_file
        if not prompt_path.is_file():
            continue

        artifacts_section = step.get("artifacts", {})
        declared_keys = (
            set(artifacts_section.get("required_inputs", []))
            | set(artifacts_section.get("optional_inputs", []))
            | set(artifacts_section.get("produces", []))
            | set(artifacts_section.get("optional_produces", []))
        )

        content = prompt_path.read_text(encoding="utf-8")
        placeholders = set(re.findall(r"\{([A-Z][A-Z0-9_]+)\}", content))

        non_artifact = {
            "ARTIFACT_KEY", "SOME_KEY", "job_id", "seq", "UNRESOLVED",
            "PLACEHOLDER", "OUTPUT_FILE",
        }
        placeholders -= non_artifact

        undeclared = placeholders - declared_keys
        for key in sorted(undeclared):
            result.findings.append(ValidationFinding(
                "error", "PROMPT_INPUT_MISMATCH",
                f"Prompt '{prompt_file}' for step '{step.get('name', '')}' "
                f"references {{{key}}} but it is not declared in the step's "
                f"required_inputs or produces in workflow.toml. "
                f"The runner will not provide this artifact at runtime.",
            ))


def _check_extension_key_coverage(
    manifest_data: dict, extensions_path: Path, result: ValidationResult,
) -> None:
    """Check that context_extensions.py registers all artifact keys used in TOML."""
    steps = manifest_data.get("step", [])
    if not isinstance(steps, list):
        return

    all_keys: set[str] = set()
    for step in steps:
        artifacts_section = step.get("artifacts", {})
        for key_list in ["produces", "optional_produces", "required_inputs", "optional_inputs"]:
            all_keys.update(artifacts_section.get(key_list, []))

    try:
        ext_source = extensions_path.read_text(encoding="utf-8")
    except Exception:
        return

    missing_keys: list[str] = []
    for key in sorted(all_keys):
        if f'"{key}"' not in ext_source and f"'{key}'" not in ext_source:
            missing_keys.append(key)

    if missing_keys:
        result.findings.append(ValidationFinding(
            "warning", "UNREGISTERED_ARTIFACT_KEYS",
            f"Artifact keys used in workflow.toml but not registered in "
            f"context_extensions.py: {', '.join(missing_keys[:10])}",
        ))


def _check_implementation_overrides(
    manifest_data: dict, bundle_root: Path, result: ValidationResult,
) -> None:
    """Check that impl.yaml overrides reference valid steps and files."""
    implementations = manifest_data.get("workflow", {}).get("implementation", [])
    if not isinstance(implementations, list):
        return

    step_names = {
        s.get("name", "") for s in manifest_data.get("step", [])
        if isinstance(s, dict)
    }

    for impl in implementations:
        impl_name = impl.get("name", "")
        if not impl_name:
            continue

        impl_dir = bundle_root / "impls" / impl_name
        if not impl_dir.is_dir():
            result.findings.append(ValidationFinding(
                "error", "MISSING_IMPL_DIR",
                f"[[workflow.implementation]] declares '{impl_name}' but "
                f"impls/{impl_name}/ directory does not exist",
            ))
            continue

        impl_yaml = impl_dir / "impl.yaml"
        if not impl_yaml.is_file():
            result.findings.append(ValidationFinding(
                "error", "MISSING_IMPL_YAML",
                f"impls/{impl_name}/ exists but impl.yaml is missing",
            ))
            continue

        try:
            import yaml
            with open(impl_yaml, "r", encoding="utf-8") as f:
                impl_data = yaml.safe_load(f)
        except Exception:
            try:
                import tomllib
                impl_data = {}
            except Exception:
                continue

        if not isinstance(impl_data, dict):
            continue

        overrides = impl_data.get("overrides", {})
        if not isinstance(overrides, dict):
            continue

        for step_name, override in overrides.items():
            if step_name not in step_names:
                result.findings.append(ValidationFinding(
                    "error", "INVALID_OVERRIDE_STEP",
                    f"impls/{impl_name}/impl.yaml overrides step '{step_name}' "
                    f"which does not exist in workflow.toml",
                ))
                continue

            if isinstance(override, dict):
                prompt_override = override.get("prompt", "")
                if prompt_override:
                    prompt_path = bundle_root / prompt_override
                    if not prompt_path.is_file():
                        result.findings.append(ValidationFinding(
                            "error", "MISSING_OVERRIDE_PROMPT",
                            f"impls/{impl_name}/impl.yaml overrides prompt to "
                            f"'{prompt_override}' but file does not exist",
                        ))
