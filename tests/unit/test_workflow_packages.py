"""Unit tests for the workflow packages plugin framework.

Tests cover:
- WorkflowBundle and StepConfig dataclass construction
- workflow.toml parsing (valid and invalid manifests)
- bundle_to_template_group_dict() adapter output
- Edge cases: missing files, validation errors
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.bundle_governance import generate_bundle_governance_adapters
from agent_runner_v2.workflow_packages.base import StepConfig, WorkflowBundle
from agent_runner_v2.workflow_packages.loader import (
    bundle_to_template_group_dict,
    load_workflow_package,
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


class TestWorkflowTOMLParsing:
    """Parse real workflow.toml files and validate their structure."""

    def test_load_real_master_docs_v2_package(self, project_root):
        """Verify the migrated 00_master_docs_bootstrap_v2 package loads."""
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")

        bundle = load_workflow_package(pkg_dir)
        assert bundle.name == "00_master_docs_bootstrap_v2"
        assert bundle.version == "2"
        assert bundle.job_prefix == "00DOC"
        assert len(bundle.step_order) == 14
        assert bundle.init_step == "00_scan_repo_codebase"

    def test_load_core_governance_package(self, project_root):
        pkg_dir = project_root / "workflows" / "00_core_governance_bootstrap_v1"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")

        bundle = load_workflow_package(pkg_dir)
        assert bundle.name == "00_core_governance_bootstrap_v1"
        assert bundle.version == "1"
        assert bundle.job_prefix == "00CORE"
        assert bundle.step_order == [
            "generate_core_governance_docs",
            "review_core_governance_docs",
            "refine_core_governance_docs",
            "validate_core_governance_docs",
            "audit_core_governance_accuracy",
            "stepCompletion",
        ]
        assert bundle.steps["generate_core_governance_docs"].coder_default_role == "architect_primary"
        assert bundle.steps["review_core_governance_docs"].coder_default_role == "reviewer_primary"
        assert bundle.steps["validate_core_governance_docs"].on_reject_refine == {
            "step": "refine_core_governance_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 2,
            "exhausted_failure_code": "CORE_GOVERNANCE_VALIDATION_EXHAUSTED",
            "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
        }
        assert bundle.governance is not None
        assert bundle.governance.include_in_prompts is True
        assert bundle.governance.adapter_targets == ["AGENTS.md", "QWEN.md", "CLAUDE.md"]
        assert len(bundle.governance.artifact_registry) == 6
        assert bundle.governance.canonical_source_path.name == "core_governance.md"

    def test_core_governance_prompt_package_copy_matches_source(self, project_root):
        prompt_names = [
            "01_generate_core_governance_docs.txt",
            "02_review_core_governance_docs.txt",
            "03_refine_core_governance_docs.txt",
            "04_audit_core_governance_accuracy.txt",
        ]
        source_dir = project_root / "workflows" / "00_core_governance_bootstrap_v1" / "prompts"
        packaged_dir = (
            project_root
            / "agent_runner_v2"
            / "bootstrap"
            / "workflows"
            / "default"
            / "00_core_governance_bootstrap_v1"
            / "prompts"
        )

        for prompt_name in prompt_names:
            assert _read_text(source_dir / prompt_name) == _read_text(packaged_dir / prompt_name)

    def test_core_governance_prompts_do_not_allow_repo_artifact_placeholders_in_layer1_docs(self, project_root):
        prompt_dir = project_root / "workflows" / "00_core_governance_bootstrap_v1" / "prompts"

        generate_text = _read_text(prompt_dir / "01_generate_core_governance_docs.txt")
        refine_text = _read_text(prompt_dir / "03_refine_core_governance_docs.txt")
        audit_text = _read_text(prompt_dir / "04_audit_core_governance_accuracy.txt")

        assert "direct artifact placeholders such as `{PROJECT_ANALYSIS}`" not in generate_text
        assert "replace it with direct artifact placeholder wording such as `{PROJECT_ANALYSIS}`" not in refine_text
        assert "uses direct artifact placeholders like `{PROJECT_ANALYSIS}`" not in audit_text
        assert "repo-derived filenames" in generate_text
        assert "repo-derived filenames" in refine_text
        assert "repo-derived filenames" in audit_text

    def test_core_governance_adapter_generation(self, project_root, tmp_path):
        pkg_dir = project_root / "workflows" / "00_core_governance_bootstrap_v1"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")

        bundle = load_workflow_package(pkg_dir)
        assert bundle.governance is not None

        generated_dir = tmp_path / "generated"
        governance = bundle.governance
        governance = type(governance)(
            manifest_path=governance.manifest_path,
            canonical_source_path=governance.canonical_source_path,
            generated_dir=generated_dir,
            adapter_targets=governance.adapter_targets,
            include_in_prompts=governance.include_in_prompts,
            prompt_targets=governance.prompt_targets,
            extensions=governance.extensions,
            artifact_registry=governance.artifact_registry,
        )

        written = generate_bundle_governance_adapters(
            governance,
            bundle_name=bundle.name,
            bundle_label=bundle.label,
        )

        assert sorted(written) == ["AGENTS.md", "CLAUDE.md", "QWEN.md"]
        agents_text = written["AGENTS.md"].read_text(encoding="utf-8")
        assert "Core Governance Bundle Contract" in agents_text
        assert "Artifact Registry" in agents_text
        assert "SYSTEM_DOCS_INDEX" in agents_text

    def test_all_steps_present(self, project_root):
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        expected_steps = [
            "00_scan_repo_codebase",
            "01_generate_codebase_baseline",
            "02_generate_project_analysis",
            "03_generate_system_overview_docs",
            "04_generate_architecture_docs",
            "04b_generate_integration_docs",
            "04c_generate_failure_docs",
            "04d_generate_architecture_flow_docs",
            "05_review_master_system_docs",
            "06_refine_master_system_docs",
            "07_validate_codebase_baseline",
            "08_validate_master_system_docs",
            "09_finalize_bootstrap",
            "stepCompletion",
        ]
        assert bundle.step_order == expected_steps

    def test_step_artifact_contracts(self, project_root):
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)

        # Action steps
        scan = bundle.steps["00_scan_repo_codebase"]
        assert scan.action == "scan_repo_codebase"
        assert scan.produces == ["CODEBASE_SCAN_SNAPSHOT"]

        # LLM steps
        analysis = bundle.steps["02_generate_project_analysis"]
        assert analysis.prompt_file == "prompts/02_generate_project_analysis.txt"
        assert "CODEBASE_CHANGE_IMPACT" in analysis.required_inputs
        assert analysis.produces == ["PROJECT_ANALYSIS"]
        assert analysis.coder_default_role == "architect_primary"

        # Review step with routing
        review = bundle.steps["05_review_master_system_docs"]
        assert review.coder_default_role == "reviewer_primary"
        assert review.on_reject_refine is not None
        assert review.on_reject_refine["step"] == "06_refine_master_system_docs"

        # Refine step with loop return
        refine = bundle.steps["06_refine_master_system_docs"]
        assert refine.loop_returns_to == "05_review_master_system_docs"
        assert "REVIEW_FILE_SUGGESTED" in refine.required_inputs

    def test_produces_chain_is_consistent(self, project_root):
        """Verify that required_inputs across steps are satisfied by earlier steps."""
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)

        cumulative: set[str] = set()
        for step_name in bundle.step_order:
            sc = bundle.steps[step_name]
            for req in sc.required_inputs:
                # REVIEW_FILE_SUGGESTED and VALIDATION_FILE are special
                # — they are produced by the runner mechanics, not a step config
                if req in ("REVIEW_FILE_SUGGESTED", "VALIDATION_FILE"):
                    continue
                assert req in cumulative or req in sc.produces, (
                    f"Step '{step_name}' requires '{req}' which is not "
                    f"produced by any previous step. Cumulative: {cumulative}"
                )
            cumulative.update(sc.produces)

    def test_all_prompt_files_exist(self, project_root):
        """Every step with a prompt_file points to an actual file on disk."""
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        for step_name in bundle.step_order:
            sc = bundle.steps[step_name]
            if sc.prompt_file:
                prompt_path = pkg_dir / sc.prompt_file
                assert prompt_path.is_file(), (
                    f"Step '{step_name}' references prompt '{sc.prompt_file}' "
                    f"but file does not exist at {prompt_path}"
                )

    def test_manifest_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="workflow.toml"):
            load_workflow_package(tmp_path / "nonexistent")


class TestBundleAdapter:
    """bundle_to_template_group_dict() output matches expected dict shape."""

    def test_adapter_basic_structure(self, project_root):
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        group = bundle_to_template_group_dict(bundle)

        assert group["job_prefix"] == "00DOC"
        assert group["job_init_step"] == "00_scan_repo_codebase"
        assert group["job_init_inputs"] == []
        assert group["default_max_rejects"] == 4
        assert group["steps"] == bundle.step_order
        assert "step_configs" in group
        assert "_workflow_bundle" not in group  # group-level, not stamped here

    def test_adapter_step_config_dict_shape(self, project_root):
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        group = bundle_to_template_group_dict(bundle)

        # Action step
        scan_cfg = group["step_configs"]["00_scan_repo_codebase"]
        assert scan_cfg["action"] == "scan_repo_codebase"
        assert scan_cfg["mode"] == "bootstrap"
        assert "_workflow_bundle" in scan_cfg

        # LLM step
        analysis_cfg = group["step_configs"]["02_generate_project_analysis"]
        assert "prompt_file" in analysis_cfg
        assert str(analysis_cfg["prompt_file"]).endswith("02_generate_project_analysis.txt")
        assert analysis_cfg["coder"]["default_role"] == "architect_primary"
        assert analysis_cfg["coder"]["allowed_roles"] == [
            "architect_primary",
            "architect_secondary",
            "architect_tertiary",
        ]

        # Review step with routing
        review_cfg = group["step_configs"]["05_review_master_system_docs"]
        assert "on_reject_refine" in review_cfg
        assert review_cfg["on_reject_refine"]["step"] == "06_refine_master_system_docs"

    def test_adapter_prompt_file_is_absolute(self, project_root):
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        group = bundle_to_template_group_dict(bundle)

        ref = group["step_configs"]["02_generate_project_analysis"]
        prompt_path = ref["prompt_file"]
        assert Path(prompt_path).is_absolute()
        assert prompt_path.replace("\\", "/").endswith(
            "workflows/00_master_docs_bootstrap_v2/prompts/02_generate_project_analysis.txt"
        )
