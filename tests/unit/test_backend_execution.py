from __future__ import annotations

from pathlib import Path

from agent_runner_v2.backend_execution import build_execution_state
from agent_runner_v2.backend_execution import build_group_cfg_from_execution_spec
from agent_runner_v2.execution_request import ExecutionRequest


class _BackendHooksStub:
    CURRENT_SCHEMA_VERSION = 6
    JOBS_ROOT = Path("C:/Users/test/.ukbe-runner/jobs")

    @staticmethod
    def get_workflow_module():
        class _Bundle:
            ARTIFACT_KEYS = ("CODEBASE_SCAN_SNAPSHOT", "PROJECT_ANALYSIS")

        return _Bundle()

    @staticmethod
    def default_task_execution_binding():
        return {
            "task_graph_id": None,
            "task_graph_file": None,
            "task_graph_checksum": None,
            "plan_id": None,
            "plan_file": None,
            "task_node_id": None,
            "task_title": None,
            "task_node_snapshot": None,
            "bound_at": None,
        }

    @staticmethod
    def default_usage_summary():
        return {
            "steps_with_usage": 0,
            "steps_without_usage": 0,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "cost": None,
            "duration_ms": 0,
        }

    @staticmethod
    def default_review_state():
        return {}

    @staticmethod
    def _now_iso():
        return "2026-07-17T00:00:00"


def test_build_group_cfg_from_execution_spec_restores_workflow_bundle_for_package_actions():
    prompt_file = str(
        Path("D:/MyProjectSpace/01_Workflows/agent-runner-v2/agent_runner_v2/bootstrap/workflows/default/00_core_governance_bootstrap_v1/prompts/01_generate_core_governance_docs.txt").resolve()
    )
    spec = {
        "prompt_file": prompt_file,
        "action_name": "validate_core_governance_docs",
        "raw_config": {
            "action": "validate_core_governance_docs",
        },
    }

    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        spec,
        "00_core_governance_bootstrap_v1",
        "validate_core_governance_docs",
    )

    bundle = step_cfg.get("_workflow_bundle")
    assert bundle is not None
    assert "validate_core_governance_docs" in (bundle.custom_actions or {})
    assert group_cfg.get("_workflow_bundle") is bundle


def test_build_execution_state_persists_run_roots_for_backend_sync():
    request = ExecutionRequest(
        workflow_name="default",
        template_group="00_repo_master_docs_bootstrap_v1",
        job_id="00RMD-20260717-test",
        step_name="00_scan_repo_codebase",
        project_root="D:/repo-target",
        target_project_root="D:/repo-target",
        workspace_root="D:/repo-target",
        input_artifacts={"CODEBASE_SCAN_SNAPSHOT": "docs/repo/codebase/snapshot.json"},
        context_payload={},
    )
    group_cfg = {"job_init_step": "00_scan_repo_codebase", "steps": ["00_scan_repo_codebase"]}

    state = build_execution_state(request=request, group_cfg=group_cfg, hooks=_BackendHooksStub())

    assert state["project_root"] == "D:/repo-target"
    assert state["workspace_path"] == "D:/repo-target"
    assert state["target_project_root"] == "D:/repo-target"


def test_build_group_cfg_from_execution_spec_without_prompt_file_skips_bundle_restore():
    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        {"raw_config": {}},
        "wf",
        "step",
    )
    assert "_workflow_bundle" not in step_cfg
    assert "_workflow_bundle" not in group_cfg


def test_build_group_cfg_from_execution_spec_restores_bundle_for_relative_prompt_file():
    spec = {
        "prompt_file": "00_core_governance_bootstrap_v1/prompts/01_generate_core_governance_docs.txt",
        "action_name": "validate_core_governance_docs",
        "raw_config": {
            "action": "validate_core_governance_docs",
        },
    }

    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        spec,
        "00_core_governance_bootstrap_v1",
        "validate_core_governance_docs",
    )

    bundle = step_cfg.get("_workflow_bundle")
    assert bundle is not None
    assert "validate_core_governance_docs" in (bundle.custom_actions or {})
    assert group_cfg.get("_workflow_bundle") is bundle
