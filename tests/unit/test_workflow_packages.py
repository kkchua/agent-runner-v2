"""Unit tests for the workflow packages plugin framework.

Tests cover:
- WorkflowBundle and StepConfig dataclass construction
- workflow.toml parsing (valid and invalid manifests)
- Edge cases: missing files, validation errors

Note: Legacy workflow-specific tests (TestWorkflowTOMLParsing, TestBundleAdapter)
have been removed. New workflow tests should be added in
tests/unit/workflows/<workflow_name>/ directories.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.workflow_packages.base import StepConfig, WorkflowBundle
from agent_runner_v2.workflow_packages.loader import load_workflow_package


class TestStepConfig:
    """StepConfig construction and field defaults."""

    def test_minimal_step_config(self):
        sc = StepConfig(name="test_step")
        assert sc.name == "test_step"
        assert sc.prompt_file is None
        assert sc.action is None
        assert sc.produces == []
        assert sc.required_inputs == []
        assert sc.coder_default is None
        assert sc.extra == {}

    def test_full_step_config(self):
        sc = StepConfig(
            name="generate_docs",
            prompt_file="prompts/gen.txt",
            action="validate",
            mode="bootstrap",
            produces=["OUTPUT_DOC"],
            required_inputs=["INPUT_SEED"],
            result_meta_key="OUTPUT_DOC",
            coder_default="qwen-architect",
            coder_allowed=["claude", "qwen-architect"],
            coder_role_policy="architect_standard",
            coder_default_role="architect_primary",
            coder_allowed_roles=["architect_primary", "architect_secondary"],
            enable_notifications=True,
            on_reject_refine={"step": "refine", "max_iterations": 2},
        )
        assert sc.name == "generate_docs"
        assert sc.prompt_file == "prompts/gen.txt"
        assert sc.action == "validate"
        assert sc.produces == ["OUTPUT_DOC"]
        assert sc.coder_default == "qwen-architect"
        assert sc.coder_role_policy == "architect_standard"
        assert sc.coder_default_role == "architect_primary"
        assert sc.on_reject_refine == {"step": "refine", "max_iterations": 2}

    def test_extra_fields_preserved(self):
        sc = StepConfig(name="test", extra={"custom_flag": True, "tags": ["a", "b"]})
        assert sc.extra["custom_flag"] is True
        assert sc.extra["tags"] == ["a", "b"]


class TestWorkflowBundle:
    """WorkflowBundle construction and helper methods."""

    def test_minimal_bundle(self):
        step = StepConfig(name="init")
        bundle = WorkflowBundle(
            name="test_wf",
            version="1",
            label="Test",
            job_prefix="TEST",
            manifest_path=Path("/fake/manifest.toml"),
            bundle_root=Path("/fake"),
            steps={"init": step},
            step_order=["init"],
            init_step="init",
            init_inputs=[],
        )
        assert bundle.name == "test_wf"
        assert bundle.get_step("init") == step
        assert bundle.next_step("init") is None

    def test_next_step_returns_correct_order(self):
        steps = {
            "a": StepConfig(name="a"),
            "b": StepConfig(name="b"),
            "c": StepConfig(name="c"),
        }
        bundle = WorkflowBundle(
            name="ordered",
            version="1",
            label="Ordered",
            job_prefix="ORD",
            manifest_path=Path("/m.toml"),
            bundle_root=Path("/"),
            steps=steps,
            step_order=["a", "b", "c"],
            init_step="a",
            init_inputs=[],
        )
        assert bundle.next_step("a") == "b"
        assert bundle.next_step("b") == "c"
        assert bundle.next_step("c") is None

    def test_next_step_unknown_returns_none(self):
        bundle = WorkflowBundle(
            name="empty",
            version="1",
            label="Empty",
            job_prefix="EMP",
            manifest_path=Path("/m.toml"),
            bundle_root=Path("/"),
            steps={},
            step_order=[],
            init_step="",
            init_inputs=[],
        )
        assert bundle.next_step("nonexistent") is None

    def test_manifest_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="workflow.toml"):
            load_workflow_package(tmp_path / "nonexistent")


# ---------------------------------------------------------------------------
# Repo-wide workflow TOML validation
# ---------------------------------------------------------------------------

_WORKFLOWS_ROOT = Path("workflows")


def _all_workflow_toml_paths() -> list[Path]:
    return sorted(_WORKFLOWS_ROOT.glob("*/workflow.toml"))


class TestAllWorkflowTOMLsLoadable:
    """Every workflow.toml in workflows/ must parse and load cleanly.

    This catches silent TOML traps — e.g. ``onsuccess`` placed after a
    ``[step.artifacts]`` header gets absorbed into the artifacts sub-dict,
    breaking routing with no visible error.
    """

    def test_all_workflow_tomls_load_without_error(self):
        paths = _all_workflow_toml_paths()
        assert paths, "No workflow.toml files found under workflows/"
        failures: list[str] = []
        for p in paths:
            try:
                bundle = load_workflow_package(p.parent)
            except Exception as exc:
                failures.append(f"{p}: {exc}")
        assert failures == [], (
            f"{len(failures)} workflow(s) failed to load:\n"
            + "\n".join(failures)
        )

    def test_all_steps_have_onsuccess_at_step_level(self):
        """Verify onsuccess is not trapped inside artifacts/coder sub-tables."""
        import tomllib

        paths = _all_workflow_toml_paths()
        assert paths, "No workflow.toml files found under workflows/"
        misplaced: list[str] = []
        for p in paths:
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            for step in data.get("step", []):
                name = step.get("name", "?")
                for sub in ("artifacts", "coder"):
                    sub_dict = step.get(sub) or {}
                    if "onsuccess" in sub_dict:
                        misplaced.append(
                            f"{p}: step '{name}' has onsuccess "
                            f"inside [step.{sub}]"
                        )
        assert misplaced == [], (
            f"{len(misplaced)} step(s) have misplaced onsuccess:\n"
            + "\n".join(misplaced)
            + "\n\nFix: move onsuccess BEFORE any [step.*] sub-table header."
        )

    def test_all_steps_with_onsuccess_have_valid_target(self):
        """Every onsuccess value must name a step that exists in the workflow."""
        import tomllib

        paths = _all_workflow_toml_paths()
        bad: list[str] = []
        for p in paths:
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            steps = data.get("step", [])
            step_names = {s.get("name") for s in steps}
            for step in steps:
                name = step.get("name", "?")
                target = step.get("onsuccess")
                if target and target not in step_names and target != "stepCompletion":
                    bad.append(
                        f"{p}: step '{name}' onsuccess='{target}' "
                        f"not found in steps {sorted(step_names)}"
                    )
        assert bad == [], (
            f"{len(bad)} step(s) have invalid onsuccess targets:\n"
            + "\n".join(bad)
        )