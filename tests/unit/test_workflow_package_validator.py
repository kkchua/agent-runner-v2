"""Tests for the reusable workflow package validator.

Verifies that validate_package() catches real defects in workflow packages:
syntax errors, missing files, artifact binding issues, action mismatches,
prompt placeholder problems, and implementation override validity.
"""
from __future__ import annotations

from pathlib import Path

from agent_runner_v2.workflow_package_validator import (
    ValidationResult,
    validate_package,
    render_report,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


MINIMAL_TOML = """\
[workflow]
name = "test_pkg"
job_prefix = "TST"
init_step = "step_one"

[[step]]
name = "step_one"
prompt = "prompts/step_one.txt"
onsuccess = "step_two"

[step.artifacts]
produces = ["OUTPUT_A"]
result_meta_key = "OUTPUT_A"

[[step]]
name = "step_two"
action = "do_something"

[step.artifacts]
required_inputs = ["OUTPUT_A"]
produces = ["OUTPUT_B"]
result_meta_key = "OUTPUT_B"
"""


def _make_valid_package(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a minimal valid package, return (manifest, extensions, actions) paths."""
    _write(tmp_path / "workflow.toml", MINIMAL_TOML)
    _write(tmp_path / "prompts/step_one.txt", "Do step one with {OUTPUT_A}\n")
    _write(tmp_path / "context_extensions.py", 'ARTIFACT_KEY_OUTPUT_A = "OUTPUT_A"\nARTIFACT_KEY_OUTPUT_B = "OUTPUT_B"\n')
    _write(tmp_path / "actions.py", 'from agent_runner_v2.workflow_packages.actions import action\n\n@action("do_something")\ndef do_something(*, context, state, step_cfg, project_root):\n    pass\n')
    return (
        tmp_path / "workflow.toml",
        tmp_path / "context_extensions.py",
        tmp_path / "actions.py",
    )


# --- Passing cases ---

def test_valid_package_passes_all_checks(tmp_path: Path) -> None:
    manifest, ext, actions = _make_valid_package(tmp_path)
    result = validate_package(manifest_path=manifest, extensions_path=ext, actions_path=actions)
    assert result.passed is True
    assert len(result.errors) == 0


def test_valid_package_without_optional_files(tmp_path: Path) -> None:
    _write(tmp_path / "workflow.toml", MINIMAL_TOML)
    _write(tmp_path / "prompts/step_one.txt", "hello\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert result.passed is True


# --- TOML errors ---

def test_missing_manifest_returns_error(tmp_path: Path) -> None:
    result = validate_package(manifest_path=tmp_path / "nonexistent.toml")
    assert result.passed is False
    assert any(f.code == "MISSING_MANIFEST" for f in result.errors)


def test_invalid_toml_returns_error(tmp_path: Path) -> None:
    _write(tmp_path / "workflow.toml", "this is not [[[valid toml")
    result = validate_package(manifest_path=tmp_path / "workflow.toml")
    assert result.passed is False
    assert any(f.code == "TOML_PARSE_ERROR" for f in result.errors)


# --- Python syntax ---

def test_syntax_error_in_actions_py(tmp_path: Path) -> None:
    manifest, ext, actions = _make_valid_package(tmp_path)
    _write(actions, "def broken(\n")
    result = validate_package(manifest_path=manifest, extensions_path=ext, actions_path=actions)
    assert any(f.code == "PYTHON_SYNTAX_ERROR" and "actions.py" in f.message for f in result.errors)


def test_syntax_error_in_context_extensions(tmp_path: Path) -> None:
    manifest, ext, actions = _make_valid_package(tmp_path)
    _write(ext, "class Bad:\n  def oops(\n")
    result = validate_package(manifest_path=manifest, extensions_path=ext, actions_path=actions)
    assert any(f.code == "PYTHON_SYNTAX_ERROR" and "context_extensions" in f.message for f in result.errors)


# --- Missing prompt files ---

def test_missing_prompt_file_detected(tmp_path: Path) -> None:
    _write(tmp_path / "workflow.toml", MINIMAL_TOML)
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert any(f.code == "MISSING_PROMPT_FILE" for f in result.errors)


# --- Action implementation ---

def test_missing_action_decorator_detected(tmp_path: Path) -> None:
    manifest, ext, _actions = _make_valid_package(tmp_path)
    _write(_actions, "# no @action decorator here\ndef do_something():\n    pass\n")
    result = validate_package(manifest_path=manifest, extensions_path=ext, actions_path=_actions)
    assert any(f.code == "MISSING_ACTION_IMPLEMENT" for f in result.errors)


def test_builtin_action_not_flagged(tmp_path: Path) -> None:
    toml_content = """\
[workflow]
name = "test_pkg"
job_prefix = "TST"
init_step = "finish"

[[step]]
name = "finish"
action = "step_completion"
"""
    _write(tmp_path / "workflow.toml", toml_content)
    _write(tmp_path / "actions.py", "# empty\n")
    manifest = tmp_path / "workflow.toml"
    actions = tmp_path / "actions.py"
    result = validate_package(manifest_path=manifest, actions_path=actions)
    assert not any(f.code == "MISSING_ACTION_IMPLEMENT" for f in result.errors)


# --- Artifact bindings ---

def test_self_referential_artifact_detected(tmp_path: Path) -> None:
    toml_content = """\
[workflow]
name = "test_pkg"
job_prefix = "TST"
init_step = "step_one"

[[step]]
name = "step_one"
prompt = "prompts/step_one.txt"

[step.artifacts]
required_inputs = ["DATA"]
produces = ["DATA"]
result_meta_key = "DATA"
"""
    _write(tmp_path / "workflow.toml", toml_content)
    _write(tmp_path / "prompts/step_one.txt", "hello\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert any(f.code == "SELF_REFERENTIAL_ARTIFACT" for f in result.errors)


def test_unresolvable_input_artifact_warning(tmp_path: Path) -> None:
    toml_content = """\
[workflow]
name = "test_pkg"
job_prefix = "TST"
init_step = "step_one"

[[step]]
name = "step_one"
prompt = "prompts/step_one.txt"

[step.artifacts]
required_inputs = ["NEVER_PRODUCED"]
produces = ["OUTPUT"]
result_meta_key = "OUTPUT"
"""
    _write(tmp_path / "workflow.toml", toml_content)
    _write(tmp_path / "prompts/step_one.txt", "hello\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert any(f.code == "UNRESOLVABLE_INPUT_ARTIFACT" for f in result.warnings)


# --- Prompt placeholder consistency ---

def test_prompt_placeholder_not_in_artifacts_detected(tmp_path: Path) -> None:
    _write(tmp_path / "workflow.toml", MINIMAL_TOML)
    _write(tmp_path / "prompts/step_one.txt", "Use {MISSING_KEY} here\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert any(f.code == "PROMPT_INPUT_MISMATCH" and "MISSING_KEY" in f.message for f in result.errors)


# --- Extension key coverage ---

def test_unregistered_artifact_keys_warning(tmp_path: Path) -> None:
    manifest, _ext, actions = _make_valid_package(tmp_path)
    _write(_ext, '# no keys registered\n')
    result = validate_package(manifest_path=manifest, extensions_path=_ext, actions_path=actions)
    assert any(f.code == "UNREGISTERED_ARTIFACT_KEYS" for f in result.warnings)


# --- Implementation overrides ---

def test_missing_impl_dir_detected(tmp_path: Path) -> None:
    toml_content = MINIMAL_TOML + """
[[workflow.implementation]]
name = "variant_a"
description = "Variant A"
"""
    _write(tmp_path / "workflow.toml", toml_content)
    _write(tmp_path / "prompts/step_one.txt", "hello\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert any(f.code == "MISSING_IMPL_DIR" for f in result.errors)


def test_valid_impl_override_passes(tmp_path: Path) -> None:
    toml_content = MINIMAL_TOML + """
[[workflow.implementation]]
name = "variant_a"
description = "Variant A"
"""
    _write(tmp_path / "workflow.toml", toml_content)
    _write(tmp_path / "prompts/step_one.txt", "hello\n")
    _write(tmp_path / "impls/variant_a/impl.yaml", "name: variant_a\noverrides: {}\n")
    manifest = tmp_path / "workflow.toml"
    result = validate_package(manifest_path=manifest)
    assert not any(f.code == "MISSING_IMPL_DIR" for f in result.errors)


# --- Report rendering ---

def test_render_report_passing() -> None:
    result = ValidationResult()
    report = render_report(result, job_id="TEST-123")
    assert "YES" in report
    assert "**Errors:** 0" in report


def test_render_report_with_errors() -> None:
    from agent_runner_v2.workflow_package_validator import ValidationFinding
    result = ValidationResult()
    result.findings.append(ValidationFinding("error", "TEST_ERROR", "Something broke"))
    report = render_report(result, job_id="TEST-456")
    assert "NO" in report
    assert "TEST_ERROR" in report
    assert "Something broke" in report
