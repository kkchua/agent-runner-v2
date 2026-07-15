"""Unit tests for plugin workflow support without workflow module.

Tests that core functions work without requiring template_groups.py workflow module.
"""
import pytest
from pathlib import Path


class TestPluginWorkflowSupport:
    """Test that functions work with plugin workflows (workflow.toml) instead of legacy modules."""

    def test_build_context_without_workflow_module(self):
        """build_context() should use centralized constants, not workflow module."""
        from agent_runner_v2.step_runner import build_context
        from agent_runner_v2.runtime_context import set_context, set_workflow_module
        
        # Set context WITHOUT workflow module (plugin workflow scenario)
        set_context(
            workspace_root=Path.cwd(),
            workflow_name="test_workflow",
            workflow_root=Path.cwd(),
            workflow_module=None,  # No workflow module!
        )
        set_workflow_module(None)
        
        # Create minimal state
        state = {
            "template_group": "00_core_governance_bootstrap_v1",
            "job_id": "TEST-001",
            "artifacts": {},
            "backend_step_dir_rel": "test/TEST-001/01_test_step",
        }
        
        step_cfg = {
            "result_meta_key": "SYSTEM_DOCS_INDEX",
        }
        
        # This should NOT raise "Workflow module is not loaded" error
        ctx = build_context(state, step="test_step", step_cfg=step_cfg)
        
        # Verify context was built successfully
        assert isinstance(ctx, dict)
        assert "SYSTEM_DOC_ROOT" in ctx
        assert "DOCS_ROOT" in ctx
        assert "CODEBASE_DOC_ROOT" in ctx
        assert "DELIVERY_DOC_ROOT" in ctx
        
        # Verify REFERENCE_FILES constants were injected
        # (should have keys like ARTIFACT_KEY_*, ARTIFACT_PATH_*)
        artifact_keys = [k for k in ctx.keys() if k.startswith("ARTIFACT_KEY_") or k.startswith("ARTIFACT_PATH_")]
        assert len(artifact_keys) > 0, "REFERENCE_FILES constants should be in context"

    def test_reference_files_from_constants(self):
        """REFERENCE_FILES should come from constants.py, not workflow module."""
        from agent_runner_v2.constants import REFERENCE_FILES
        
        # Verify REFERENCE_FILES exists and has content
        assert isinstance(REFERENCE_FILES, dict)
        assert len(REFERENCE_FILES) > 0
        
        # Should have both ARTIFACT_KEY_* and ARTIFACT_PATH_* entries
        key_entries = [k for k in REFERENCE_FILES.keys() if k.startswith("ARTIFACT_KEY_")]
        path_entries = [k for k in REFERENCE_FILES.keys() if k.startswith("ARTIFACT_PATH_")]
        
        assert len(key_entries) > 0, "Should have ARTIFACT_KEY_* entries"
        assert len(path_entries) > 0, "Should have ARTIFACT_PATH_* entries"

    def test_workflow_package_loading(self):
        """Should be able to load plugin workflow from global runner home."""
        from agent_runner_v2.runtime_context import GLOBAL_RUNNER_HOME
        from agent_runner_v2.workflow_packages.loader import load_workflow_package
        
        wf_name = "00_core_governance_bootstrap_v1"
        wf_root = GLOBAL_RUNNER_HOME / "workflows" / "default" / wf_name
        
        # Verify workflow exists
        assert wf_root.exists(), f"Workflow root should exist at {wf_root}"
        assert (wf_root / "workflow.toml").exists(), "workflow.toml should exist"
        
        # Load the workflow package
        bundle = load_workflow_package(wf_root)
        
        # Verify bundle loaded correctly
        assert bundle is not None
        assert bundle.name == wf_name
        assert hasattr(bundle, 'steps')
        assert len(bundle.steps) > 0
        
        # Verify steps are accessible
        step_names = list(bundle.steps.keys())
        assert "generate_core_governance_docs" in step_names

    def test_step_order_from_workflow_package(self):
        """Should extract step order from workflow package when needed."""
        from agent_runner_v2.runtime_context import GLOBAL_RUNNER_HOME
        from agent_runner_v2.workflow_packages.loader import load_workflow_package
        
        wf_name = "00_core_governance_bootstrap_v1"
        wf_root = GLOBAL_RUNNER_HOME / "workflows" / "default" / wf_name
        
        bundle = load_workflow_package(wf_root)
        
        # Get step order
        steps = list(bundle.steps.keys())
        
        # Verify expected step order
        assert steps[0] == "generate_core_governance_docs"
        assert steps[1] == "review_core_governance_docs"
        assert "validate_core_governance_docs" in steps
