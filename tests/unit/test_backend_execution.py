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


def test_build_execution_state_persists_run_roots_for_backend_sync():
    request = ExecutionRequest(
        workflow_name="default",
        template_group="sdlc_00_delivery_scaffold_v1",
        job_id="SDLC-20260717-test",
        step_name="scaffold_delivery",
        project_root="D:/repo-target",
        target_project_root="D:/repo-target",
        workspace_root="D:/repo-target",
        input_artifacts={},
        context_payload={},
    )
    group_cfg = {"job_init_step": "scaffold_delivery", "steps": ["scaffold_delivery"]}

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


