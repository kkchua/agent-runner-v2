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

