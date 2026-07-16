"""Unit tests for the workflow package context extension system.

Tests that context_extensions.py produces the correct path aliases
and integrates properly with the step_runner hook.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.workflow_packages.base import WorkflowBundle
from agent_runner_v2.workflow_packages.loader import load_workflow_package


class TestContextExtensionsLoader:
    """Verify that the remaining workflow context_extensions module loads."""

    def test_layer1_module_exists_and_imports(self, project_root):
        ext_path = (
            project_root
            / "workflows"
            / "00_layer1_governance_bootstrap_v1"
            / "context_extensions.py"
        )
        assert ext_path.is_file(), f"context_extensions.py not found at {ext_path}"

        import importlib.util

        spec = importlib.util.spec_from_file_location("test_ctx_ext", ext_path)
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert hasattr(mod, "build_context_extensions")
        assert callable(mod.build_context_extensions)

    def test_layer1_build_context_extensions_returns_dict(self, project_root):
        ext_path = (
            project_root
            / "workflows"
            / "00_layer1_governance_bootstrap_v1"
            / "context_extensions.py"
        )
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_ctx_ext2", ext_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.build_context_extensions(
            state={"job_id": "00L1-TEST-001", "template_group": "00_layer1_governance_bootstrap_v1"},
            step="review_layer1_governance_docs",
            step_cfg={"mode": "bootstrap"},
            ctx={},
            project_root=project_root,
        )
        assert isinstance(result, dict)
        assert "SYSTEM_DOCS_INDEX" in result
        assert "SYSTEM_DOCS_INDEX_PATH" in result
        assert "SYSTEM_DOCS_INDEX_METAJSON" in result
        assert "REVIEW_FILE_SUGGESTED" in result


class TestContextHookIntegration:
    """Verify that _apply_workflow_package_context_hooks integrates correctly."""

    def test_hook_skips_when_no_bundle(self):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        ctx = {"EXISTING": "value"}
        _apply_workflow_package_context_hooks(
            ctx=ctx,
            state={},
            step="test",
            step_cfg=None,
        )
        assert ctx == {"EXISTING": "value"}  # unchanged

    def test_hook_skips_when_bundle_has_no_extension(self, project_root):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        bundle = WorkflowBundle(
            name="no_ext",
            version="1",
            label="No Extension",
            job_prefix="NOEXT",
            manifest_path=project_root / "fake.toml",
            bundle_root=project_root,
            steps={},
            step_order=[],
            init_step="",
            init_inputs=[],
            context_extensions_path=None,
        )
        step_cfg = {"_workflow_bundle": bundle}
        ctx = {"EXISTING": "value"}
        _apply_workflow_package_context_hooks(
            ctx=ctx,
            state={},
            step="test",
            step_cfg=step_cfg,
        )
        assert ctx == {"EXISTING": "value"}  # unchanged

    def test_hook_injects_layer1_absolute_paths(self, project_root):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        pkg_dir = project_root / "workflows" / "00_layer1_governance_bootstrap_v1"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        assert bundle.context_extensions_path is not None

        step_cfg = {"_workflow_bundle": bundle}
        ctx: dict[str, str] = {}
        _apply_workflow_package_context_hooks(
            ctx=ctx,
            state={
                "job_id": "00L1-TEST-001",
                "template_group": "00_layer1_governance_bootstrap_v1",
            },
            step="review_layer1_governance_docs",
            step_cfg=step_cfg,
            project_root=project_root,
        )

        assert ctx["SYSTEM_DOCS_INDEX"] == str(
            project_root / "docs" / "system" / "00_governance" / "bootstrap" / "README.md"
        )
        assert ctx["SYSTEM_DOC_STANDARD"].endswith("DOCUMENTATION_STANDARD.md")
        assert ctx["BUNDLE_TAXONOMY"].endswith("BUNDLE_TAXONOMY.md")
        assert ctx["RUNTIME_GOVERNANCE"].endswith("RUNTIME_GOVERNANCE.md")
        assert ctx["REVIEW_FILE_SUGGESTED"] == str(
            project_root / "docs" / "system" / "00_governance" / "bootstrap" / "00L1-TEST-001-layer1-governance-review.md"
        )
        assert "/docs/repo/governance/" not in ctx["SYSTEM_DOCS_INDEX"].replace("\\", "/")

    def test_hook_injects_layer1_review_and_audit_paths(self, project_root):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        pkg_dir = project_root / "workflows" / "00_layer1_governance_bootstrap_v1"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)

        review_ctx: dict[str, str] = {}
        _apply_workflow_package_context_hooks(
            ctx=review_ctx,
            state={
                "job_id": "00L1-TEST-002",
                "template_group": "00_layer1_governance_bootstrap_v1",
            },
            step="review_layer1_governance_docs",
            step_cfg={"_workflow_bundle": bundle},
            project_root=project_root,
        )
        assert review_ctx["REVIEW_FILE_SUGGESTED"].endswith("00L1-TEST-002-layer1-governance-review.md")
        assert review_ctx["SYSTEM_DOCS_VALIDATION"].endswith("00L1-TEST-002-layer1-governance-validation.md")

        audit_ctx: dict[str, str] = {}
        _apply_workflow_package_context_hooks(
            ctx=audit_ctx,
            state={
                "job_id": "00L1-TEST-003",
                "template_group": "00_layer1_governance_bootstrap_v1",
            },
            step="audit_layer1_governance_accuracy",
            step_cfg={"_workflow_bundle": bundle},
            project_root=project_root,
        )
        assert audit_ctx["REVIEW_FILE_SUGGESTED"].endswith("00L1-TEST-003-layer1-governance-audit.md")

    def test_hook_injects_master_docs_review_path_under_repo_governance(self, project_root):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        pkg_dir = project_root / "workflows" / "00_repo_master_docs_bootstrap_v1"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)

        ctx: dict[str, str] = {}
        _apply_workflow_package_context_hooks(
            ctx=ctx,
            state={
                "job_id": "00RMD-TEST-001",
                "template_group": "00_repo_master_docs_bootstrap_v1",
            },
            step="05_review_master_system_docs",
            step_cfg={"_workflow_bundle": bundle, "mode": "bootstrap"},
            project_root=project_root,
        )

        assert ctx["REVIEW_FILE_SUGGESTED"].replace("\\", "/") == str(
            (project_root / "docs" / "repo" / "governance" / "00RMD-TEST-001-master-system-docs-review.md").resolve()
        ).replace("\\", "/")
        assert ctx["EXISTING_REPO_WORKFLOW_SOP"].replace("\\", "/") == str(
            (project_root / "docs" / "repo" / "governance" / "EXISTING_REPO_WORKFLOW_SOP.md").resolve()
        ).replace("\\", "/")


def test_render_prompt_appends_bundle_governance_for_opted_in_bundle(project_root):
    from agent_runner_v2.step_runner import render_prompt

    pkg_dir = project_root / "workflows" / "00_core_governance_bootstrap_v1"
    if not pkg_dir.is_dir():
        pytest.skip("workflow package directory not found")

    bundle = load_workflow_package(pkg_dir)
    rendered = render_prompt(
        "Base prompt.",
        {
            "STEP_NAME": "generate_core_governance_docs",
            "TOOLS_DIR": "",
        },
        step_cfg={"_workflow_bundle": bundle},
    )

    assert "## Bundle Governance" in rendered
    assert "Core Governance Bundle Contract" in rendered
    assert "SYSTEM_DOCS_INDEX" in rendered


def test_render_prompt_normalizes_windows_paths_for_coder_output_contract() -> None:
    from agent_runner_v2.step_runner import render_prompt

    rendered = render_prompt(
        "Write review to {REVIEW_FILE_SUGGESTED}",
        {
            "STEP_NAME": "audit_layer1_governance_accuracy",
            "TOOLS_DIR": r"D:\tools",
            "REVIEW_FILE_SUGGESTED": r"D:\MyProjectSpace\01_Workflows\agent-runner-v2\docs\system\00_governance\bootstrap\JOB-audit.md",
            "REVIEW_FILE_SUGGESTED_METAJSON": r"D:\MyProjectSpace\01_Workflows\agent-runner-v2\docs\system\00_governance\bootstrap\JOB-audit.meta.json",
        },
        step_cfg={"result_meta_key_from_context": "REVIEW_FILE_SUGGESTED_METAJSON"},
    )

    assert r"D:\MyProjectSpace\01_Workflows\agent-runner-v2\docs\system\00_governance\bootstrap\JOB-audit.md" not in rendered
    assert r"D:\MyProjectSpace\01_Workflows\agent-runner-v2\docs\system\00_governance\bootstrap\JOB-audit.meta.json" not in rendered
    assert "D:/MyProjectSpace/01_Workflows/agent-runner-v2/docs/system/00_governance/bootstrap/JOB-audit.md" in rendered
    assert "D:/MyProjectSpace/01_Workflows/agent-runner-v2/docs/system/00_governance/bootstrap/JOB-audit.meta.json" in rendered
    assert "use forward slashes in JSON strings" in rendered
    assert '"status": "APPROVED"' in rendered
