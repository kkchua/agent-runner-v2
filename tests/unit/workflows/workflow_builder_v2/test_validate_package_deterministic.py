"""Tests for validate_package_deterministic action.

Verifies the static analysis catches the runtime defects that LLM gatekeepers
frequently miss: TYPE_CHECKING imports, artifact binding inconsistencies,
syntax errors, missing files, and action implementation gaps.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from workflows.workflow_builder_v2.actions import (
    _check_action_implementations,
    _check_artifact_bindings,
    _check_python_syntax,
    _check_type_checking_imports,
)


# ---------------------------------------------------------------------------
# TYPE_CHECKING import detection
# ---------------------------------------------------------------------------


class TestTypeCheckingImports:
    """Detect imports inside TYPE_CHECKING blocks that are used at runtime."""

    def test_detects_function_call_inside_type_checking(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                from agent_runner_v2.codebase_docs import build_snapshot

            @action("my_action")
            def my_action(*, context, state, step_cfg, project_root):
                snapshot = build_snapshot(project_root)
                return ActionResult(status="APPROVED", remark="ok", artifacts={})
        """))
        findings: list[dict[str, str]] = []
        _check_type_checking_imports(actions_file, findings)
        assert len(findings) == 1
        assert findings[0]["code"] == "TYPE_CHECKING_RUNTIME_IMPORT"
        assert "build_snapshot" in findings[0]["message"]

    def test_passes_when_import_at_top_level(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from agent_runner_v2.codebase_docs import build_snapshot

            @action("my_action")
            def my_action(*, context, state, step_cfg, project_root):
                snapshot = build_snapshot(project_root)
                return ActionResult(status="APPROVED", remark="ok", artifacts={})
        """))
        findings: list[dict[str, str]] = []
        _check_type_checking_imports(actions_file, findings)
        assert len(findings) == 0

    def test_passes_when_type_checking_only_for_annotations(self, tmp_path: Path):
        """TYPE_CHECKING imports used ONLY in type annotations are fine."""
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                from agent_runner_v2.codebase_docs import SnapshotType

            def format_snapshot(snap: "SnapshotType") -> str:
                return str(snap)
        """))
        findings: list[dict[str, str]] = []
        _check_type_checking_imports(actions_file, findings)
        # No function calls to TYPE_CHECKING names — only type annotations
        assert len(findings) == 0

    def test_detects_multiple_runtime_imports(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                from module_a import func_a
                from module_b import func_b

            def do_work():
                func_a()
                func_b()
        """))
        findings: list[dict[str, str]] = []
        _check_type_checking_imports(actions_file, findings)
        assert len(findings) == 2
        codes = [f["message"] for f in findings]
        assert any("func_a" in m for m in codes)
        assert any("func_b" in m for m in codes)


# ---------------------------------------------------------------------------
# Artifact binding consistency
# ---------------------------------------------------------------------------


class TestArtifactBindings:
    """Detect self-referential and unresolvable artifact bindings."""

    def test_detects_self_referential_binding(self):
        manifest = {
            "step": [
                {
                    "name": "commit_updates",
                    "artifacts": {
                        "required_inputs": ["UPDATED_MANIFEST_FILE"],
                        "produces": ["UPDATED_MANIFEST_FILE"],
                    },
                }
            ]
        }
        findings: list[dict[str, str]] = []
        _check_artifact_bindings(manifest, findings)
        self_ref = [f for f in findings if f["code"] == "SELF_REFERENTIAL_ARTIFACT"]
        assert len(self_ref) == 1
        assert "UPDATED_MANIFEST_FILE" in self_ref[0]["message"]

    def test_allows_self_referential_binding_on_refine_step(self):
        """Refine steps legitimately read and rewrite the same artifact."""
        manifest = {
            "step": [
                {
                    "name": "generate_output",
                    "artifacts": {
                        "produces": ["OUTPUT_FILE"],
                    },
                },
                {
                    "name": "review_output",
                    "artifacts": {
                        "required_inputs": ["OUTPUT_FILE"],
                        "produces": ["REVIEW_FILE"],
                    },
                    "on_reject_refine": {
                        "step": "refine_output",
                        "artifact": "REVIEW_FILE",
                    },
                },
                {
                    "name": "refine_output",
                    "artifacts": {
                        "required_inputs": ["REVIEW_FILE", "OUTPUT_FILE"],
                        "produces": ["OUTPUT_FILE"],
                    },
                },
            ]
        }
        findings: list[dict[str, str]] = []
        _check_artifact_bindings(manifest, findings)
        self_ref = [f for f in findings if f["code"] == "SELF_REFERENTIAL_ARTIFACT"]
        assert len(self_ref) == 0

    def test_passes_clean_bindings(self):
        manifest = {
            "step": [
                {
                    "name": "detect_changes",
                    "artifacts": {
                        "produces": ["DETECTED_CHANGES_FILE"],
                    },
                },
                {
                    "name": "commit_updates",
                    "artifacts": {
                        "required_inputs": ["DETECTED_CHANGES_FILE"],
                        "produces": ["UPDATED_MANIFEST_FILE"],
                    },
                },
            ]
        }
        findings: list[dict[str, str]] = []
        _check_artifact_bindings(manifest, findings)
        errors = [f for f in findings if f["level"] == "error"]
        assert len(errors) == 0

    def test_warns_on_unresolvable_input(self):
        manifest = {
            "step": [
                {
                    "name": "my_step",
                    "artifacts": {
                        "required_inputs": ["NONEXISTENT_KEY"],
                        "produces": ["OUTPUT_KEY"],
                    },
                }
            ]
        }
        findings: list[dict[str, str]] = []
        _check_artifact_bindings(manifest, findings)
        warnings = [f for f in findings if f["code"] == "UNRESOLVABLE_INPUT_ARTIFACT"]
        assert len(warnings) == 1
        assert "NONEXISTENT_KEY" in warnings[0]["message"]

    def test_does_not_warn_for_spec_input(self):
        """WORKFLOW_SPEC_FILE is a well-known input artifact — no warning."""
        manifest = {
            "step": [
                {
                    "name": "analyze_spec",
                    "artifacts": {
                        "required_inputs": ["WORKFLOW_SPEC_FILE"],
                        "produces": ["REQUIREMENTS_FILE"],
                    },
                }
            ]
        }
        findings: list[dict[str, str]] = []
        _check_artifact_bindings(manifest, findings)
        warnings = [f for f in findings if f["code"] == "UNRESOLVABLE_INPUT_ARTIFACT"]
        assert len(warnings) == 0


# ---------------------------------------------------------------------------
# Python syntax validation
# ---------------------------------------------------------------------------


class TestPythonSyntax:
    """Detect syntax errors in generated Python files."""

    def test_detects_syntax_error(self, tmp_path: Path):
        bad_file = tmp_path / "actions.py"
        bad_file.write_text("def foo(\n")  # incomplete syntax
        findings: list[dict[str, str]] = []
        _check_python_syntax(bad_file, "actions.py", findings)
        assert len(findings) == 1
        assert findings[0]["code"] == "PYTHON_SYNTAX_ERROR"

    def test_passes_valid_python(self, tmp_path: Path):
        good_file = tmp_path / "actions.py"
        good_file.write_text("def foo():\n    return 42\n")
        findings: list[dict[str, str]] = []
        _check_python_syntax(good_file, "actions.py", findings)
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# Action implementation completeness
# ---------------------------------------------------------------------------


class TestActionImplementations:
    """Detect missing @action implementations for declared action steps."""

    def test_detects_missing_action(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from agent_runner_v2.workflow_packages.actions import action

            @action("detect_changes")
            def detect_changes(*, context, state, step_cfg, project_root):
                pass
        """))
        manifest = {
            "step": [
                {"name": "detect_changes", "action": "detect_changes"},
                {"name": "commit_updates", "action": "commit_updates"},
            ]
        }
        findings: list[dict[str, str]] = []
        _check_action_implementations(manifest, actions_file, findings)
        assert len(findings) == 1
        assert findings[0]["code"] == "MISSING_ACTION_IMPLEMENT"
        assert "commit_updates" in findings[0]["message"]

    def test_passes_when_all_actions_present(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text(textwrap.dedent("""\
            from agent_runner_v2.workflow_packages.actions import action

            @action("detect_changes")
            def detect_changes(*, context, state, step_cfg, project_root):
                pass

            @action("commit_updates")
            def commit_updates(*, context, state, step_cfg, project_root):
                pass
        """))
        manifest = {
            "step": [
                {"name": "detect_changes", "action": "detect_changes"},
                {"name": "commit_updates", "action": "commit_updates"},
            ]
        }
        findings: list[dict[str, str]] = []
        _check_action_implementations(manifest, actions_file, findings)
        assert len(findings) == 0

    def test_skips_builtin_actions(self, tmp_path: Path):
        actions_file = tmp_path / "actions.py"
        actions_file.write_text("# no custom actions\n")
        manifest = {
            "step": [
                {"name": "promote", "action": "promote_workflow_package"},
                {"name": "done", "action": "step_completion"},
                {"name": "promote_final", "action": "promote_artifact"},
                {"name": "copy_output", "action": "copy_artifact"},
                {"name": "archive", "action": "archive_inputs"},
            ]
        }
        findings: list[dict[str, str]] = []
        _check_action_implementations(manifest, actions_file, findings)
        assert len(findings) == 0
