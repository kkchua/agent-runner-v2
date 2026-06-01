"""Shared fixtures for agent-runner-v2 tests.

All fixtures use real temporary directories — no mocks for filesystem state.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixture: real temporary workspace
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a real temporary workspace with a .ukbe-runner/ structure.

    Returns a SimpleNamespace with:
      - workspace_root: the tmp_path
      - runner_home: workspace_root/.ukbe-runner
      - workflow_root: runner_home/workflows/default
      - jobs_root: runner_home/jobs
    """
    runner_home = tmp_path / ".ukbe-runner"
    workflow_root = runner_home / "workflows" / "default"
    jobs_root = runner_home / "jobs"

    runner_home.mkdir(parents=True)
    workflow_root.mkdir(parents=True)
    jobs_root.mkdir(parents=True)

    return SimpleNamespace(
        workspace_root=tmp_path,
        runner_home=runner_home,
        workflow_root=workflow_root,
        jobs_root=jobs_root,
    )


# ---------------------------------------------------------------------------
# Fixture: minimal workflow module
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_workflow(tmp_workspace):
    """Create a minimal workflow module (template_groups.py) in the workflow root."""
    module_path = tmp_workspace.workflow_root / "template_groups.py"
    module_path.write_text("""
REFERENCE_FILES = {
    "README": "README.md",
    "ARCHITECTURE": "docs/architecture.md",
}

ARTIFACT_KEYS = [
    "INIT_FILE", "PLAN_FILE", "TASK_GRAPH_FILE", "TASK_FILE",
    "REVIEW_FILE", "IMPL_FILE", "ARCHIVED_IMAGES",
]

TEMPLATE_GROUPS = {
    "delivery_planning_v1": {
        "steps": [
            "project_analysis", "generate_sop", "review_sop",
            "generate_plan", "review_plan",
            "generate_task_graph", "review_task_graph",
            "task", "review_task", "refine_task", "replan_task",
        ],
        "job_init_step": "project_analysis",
        "step_configs": {
            "project_analysis": {"coder": "qwen"},
            "generate_sop": {"coder": "qwen", "loop_returns_to": "review_sop"},
            "review_sop": {"requires_human_approval_after": True},
            "generate_plan": {"coder": "qwen", "replan_returns_to": "review_plan"},
            "review_plan": {"requires_human_approval_after": True},
            "generate_task_graph": {"coder": "qwen"},
            "review_task_graph": {"requires_human_approval_after": True},
            "task": {"coder": "qwen", "loop_returns_to": "review_task"},
            "review_task": {},
            "refine_task": {"loop_returns_to": "review_task", "target_artifact": "TASK_FILE"},
            "replan_task": {"replan_returns_to": "review_task", "target_artifact": "TASK_GRAPH_FILE"},
        },
        "job_prefix": "DEL",
    },
    "task_execution_v1": {
        "steps": ["task", "review_task", "refine_task"],
        "job_init_step": "task",
        "step_configs": {
            "task": {"coder": "qwen"},
            "review_task": {"requires_human_approval_after": True},
            "refine_task": {"loop_returns_to": "review_task", "target_artifact": "IMPL_FILE"},
        },
        "job_prefix": "TASK",
    },
}
""")
    return module_path


# ---------------------------------------------------------------------------
# Fixture: real job.json on disk
# ---------------------------------------------------------------------------

SAMPLE_JOB_STATE = {
    "job_id": "DEL-GEN-20260601-001",
    "template_group": "delivery_planning_v1",
    "runner_version": "v2",
    "job_init_step": "project_analysis",
    "job_status": "IN_PROGRESS",
    "status": "IN_PROGRESS",
    "current_step": "project_analysis",
    "completed_steps": [],
    "failed_steps": [],
    "reject_counts": {},
    "step_coders": {},
    "step_usage": {},
    "usage_summary": {
        "steps_with_usage": 0, "steps_without_usage": 0,
        "input_tokens": None, "output_tokens": None,
        "total_tokens": None, "cost": None, "duration_ms": None,
    },
    "pending_human_approval_for": None,
    "human_approvals": {},
    "model_approved_steps": [],
    "review_state": {
        "artifact_type": None, "artifact_key": None, "artifact_path": None,
        "reviewer_step": None, "review_iteration": 0, "review_decision": "PENDING",
        "review_decided_at": None, "coder_used": None, "human_decision": "PENDING",
        "human_decided_at": None, "human_actor": None,
        "final_decision": None, "final_decision_source": None,
    },
    "last_model_output": None,
    "retry_history": [],
    "pending_intervention_for": None,
    "last_failure_class": None,
    "last_failure_code": None,
    "last_failure_reason": None,
    "last_failure_source": None,
    "auto_retry_count_by_step": {},
    "human_retry_count_by_step": {},
    "failure_history": [],
    "seed_artifact_type": None,
    "seed_artifact_path": None,
    "created_at": "2026-06-01T00:00:00",
    "updated_at": "2026-06-01T00:00:00",
    "artifacts": {
        "INIT_FILE": None, "PLAN_FILE": None, "TASK_GRAPH_FILE": None,
        "TASK_FILE": None, "REVIEW_FILE": None, "IMPL_FILE": None, "ARCHIVED_IMAGES": None,
    },
    "loop_context": {
        "active": False, "loop_step": None, "refine_step": None,
        "loop_target_artifact": None, "loop_source_review": None,
        "loop_iteration": 0, "pre_refine_checksum": None,
    },
    "loop_history": [],
    "replan_context": {
        "active": False, "source_review_step": None, "replan_step": None,
        "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
        "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
        "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
    },
    "replan_history": [],
    "planning_attempt_count": 0,
    "recovered_from_invalid_result": False,
    "recovery_code": None,
    "recovery_source": None,
    "task_generation_state_version": 1,
    "task_generation_state": None,
    "task_execution_binding": {
        "task_graph_id": None, "task_graph_file": None, "task_graph_checksum": None,
        "plan_id": None, "plan_file": None, "task_node_id": None,
        "task_title": None, "task_node_snapshot": None, "bound_at": None,
    },
    "state_schema_version": 6,
    "repair_history": [],
    "reconciled_from_failure": None,
}


@pytest.fixture
def real_job_on_disk(tmp_workspace):
    """Write a real job.json to disk under jobs_root/delivery_planning_v1/<job_id>/."""
    group_name = "delivery_planning_v1"
    job_id = "DEL-GEN-20260601-001"
    job_dir = tmp_workspace.jobs_root / group_name / job_id
    job_dir.mkdir(parents=True)
    job_path = job_dir / "job.json"
    job_path.write_text(json.dumps(SAMPLE_JOB_STATE, indent=2), encoding="utf-8")
    return SimpleNamespace(
        group_name=group_name,
        job_id=job_id,
        job_dir=job_dir,
        job_path=job_path,
    )


# ---------------------------------------------------------------------------
# Fixture: set runtime context for job_state tests
# ---------------------------------------------------------------------------

@pytest.fixture
def set_context(tmp_workspace, fake_workflow):
    """Set the runtime context to point at our temporary workspace."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "template_groups", str(fake_workflow)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    from agent_runner_v2.runtime_context import set_context as _set_ctx
    _set_ctx(
        workspace_root=tmp_workspace.workspace_root,
        workflow_name="default",
        workflow_root=tmp_workspace.workflow_root,
        workflow_module=module,
        delivery_root=tmp_workspace.workspace_root,
    )

    yield

    # Reset context after test
    from agent_runner_v2.runtime_context import PACKAGE_ROOT, DEFAULT_RUNNER_HOME, set_context as _set_ctx, RuntimeContext
    from types import ModuleType
    _set_ctx(
        workspace_root=Path.cwd().resolve(),
        workflow_name="default",
        workflow_root=PACKAGE_ROOT,
        workflow_module=None,
        delivery_root=None,
    )
