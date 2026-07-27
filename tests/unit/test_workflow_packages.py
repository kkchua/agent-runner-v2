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