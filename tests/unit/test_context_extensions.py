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
    """Verify that the context_extensions module can be dynamically loaded."""

    def test_module_exists_and_imports(self, project_root):
        ext_path = (
            project_root
            / "workflows"
            / "00_master_docs_bootstrap_v2"
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

    def test_build_context_extensions_returns_dict(self, project_root):
        ext_path = (
            project_root
            / "workflows"
            / "00_master_docs_bootstrap_v2"
            / "context_extensions.py"
        )
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_ctx_ext2", ext_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.build_context_extensions(
            state={"job_id": "00DOC-TEST-001", "template_group": "00_master_docs_bootstrap_v2"},
            step="02_generate_project_analysis",
            step_cfg={"mode": "bootstrap"},
            ctx={},
        )
        assert isinstance(result, dict)
        # Should at least have PROJECT_ANALYSIS and PROJECT_ANALYSIS_METAJSON
        assert "PROJECT_ANALYSIS" in result
        assert "PROJECT_ANALYSIS_PATH" in result
        assert "PROJECT_ANALYSIS_METAJSON" in result

    def test_output_paths_match_expected_pattern(self, project_root):
        ext_path = (
            project_root
            / "workflows"
            / "00_master_docs_bootstrap_v2"
            / "context_extensions.py"
        )
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_ctx_ext3", ext_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.build_context_extensions(
            state={"job_id": "00DOC-TEST-001", "template_group": "00_master_docs_bootstrap_v2"},
            step="04_generate_architecture_docs",
            step_cfg={"mode": "bootstrap"},
            ctx={},
        )
        # Static paths should resolve to docs/system/00_governance/bootstrap/
        assert "docs/system/00_governance/bootstrap/" in result.get("PROJECT_ANALYSIS", "")


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

    def test_hook_injects_master_docs_paths(self, project_root):
        from agent_runner_v2.step_runner import _apply_workflow_package_context_hooks

        # Load the real _v2 package
        pkg_dir = project_root / "workflows" / "00_master_docs_bootstrap_v2"
        if not pkg_dir.is_dir():
            pytest.skip("workflow package directory not found")
        bundle = load_workflow_package(pkg_dir)
        assert bundle.context_extensions_path is not None

        step_cfg = {"_workflow_bundle": bundle}
        ctx = {
            "SYSTEM_DOC_ROOT": "docs/system/00_governance/bootstrap",
            "DOCS_ROOT": "docs",
        }
        _apply_workflow_package_context_hooks(
            ctx=ctx,
            state={
                "job_id": "00DOC-TEST-002",
                "template_group": "00_master_docs_bootstrap_v2",
            },
            step="02_generate_project_analysis",
            step_cfg=step_cfg,
        )

        # Should have master docs path aliases injected
        assert "PROJECT_ANALYSIS" in ctx
        assert "PROJECT_ANALYSIS_PATH" in ctx
        assert "SYSTEM_DOCS_INDEX" in ctx
        assert "BUNDLE_TAXONOMY" in ctx
        assert ctx["PROJECT_ANALYSIS"].endswith("PROJECT_ANALYSIS.md")


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
