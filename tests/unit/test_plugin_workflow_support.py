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
            "template_group": "sdlc_00_delivery_scaffold_v1",
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

    def test_reference_files_from_constants(self):
        """REFERENCE_FILES should come from constants.py, not workflow module."""
        from agent_runner_v2.constants import REFERENCE_FILES

        # Verify REFERENCE_FILES exists and has content
        assert isinstance(REFERENCE_FILES, dict)
        assert len(REFERENCE_FILES) > 0

