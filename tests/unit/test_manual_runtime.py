from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent_runner_v2 import manual_runtime


def test_initialize_state_from_backend_flat_run_response_uses_workflow_name():
    """Flat RunResponse (get_run shape) must resolve group_name from workflow_name.

    Regression test: daemon writes get_run()'s flat RunResponse to
    backend_state.json (no nested 'run' key). Previously the reader only
    looked for backend_state['run'], yielding an empty dict and creating
    the job under JOBS_ROOT directly with an empty template_group.
    """
    captured: dict[str, object] = {}

    def fake_create_job(*, group_name, group_cfg, seed_artifacts, mode, job_no):
        captured["group_name"] = group_name
        captured["job_no"] = job_no
        return {
            "job_id": job_no,
            "template_group": group_name,
            "artifacts": {},
            "job_status": "IN_PROGRESS",
            "current_step": group_cfg.get("job_init_step"),
        }

    hooks = SimpleNamespace(create_job=fake_create_job)
    backend_state = {
        "run_id": "0323ea15-0609-4d12-b80d-dfd4b34a4721",
        "run_code": "AMGEN-3p68wei8",
        "workflow_name": "agnes_media_gen_v1",
        "run_status": "IN_PROGRESS",
        "current_step": "extract_descriptions",
        "current_step_run_id": "1f41d2f3-5e20-4961-88b6-c175e9ab0ffe",
    }
    group_cfg = {
        "steps": ["extract_descriptions"],
        "step_configs": {},
        "job_init_step": "extract_descriptions",
    }

    state = manual_runtime._initialize_state_from_backend(
        backend_state=backend_state,
        group_cfg=group_cfg,
        seed_artifacts={},
        mode="daemon",
        job_no="AMGEN-3p68wei8",
        hooks=hooks,
    )

    assert captured["group_name"] == "agnes_media_gen_v1"
    assert captured["job_no"] == "AMGEN-3p68wei8"
    assert state["template_group"] == "agnes_media_gen_v1"
    assert state["workflow_run_id"] == "0323ea15-0609-4d12-b80d-dfd4b34a4721"
    assert state["workflow_step_run_id"] == "1f41d2f3-5e20-4961-88b6-c175e9ab0ffe"


def test_initialize_state_from_backend_nested_claim_shape_still_works():
    """Backward compat: nested claim shape ({"run": {...}}) keeps working."""
    captured: dict[str, object] = {}

    def fake_create_job(*, group_name, group_cfg, seed_artifacts, mode, job_no):
        captured["group_name"] = group_name
        return {
            "job_id": job_no,
            "template_group": group_name,
            "artifacts": {},
            "job_status": "IN_PROGRESS",
            "current_step": group_cfg.get("job_init_step"),
        }

    hooks = SimpleNamespace(create_job=fake_create_job)
    backend_state = {
        "run": {
            "id": "abc-123",
            "run_code": "JOB-9",
            "workflow_name": "sdlc_10_requirement_v1",
            "current_step_run_id": "step-9",
        }
    }
    group_cfg = {
        "steps": ["init"],
        "step_configs": {},
        "job_init_step": "init",
    }

    state = manual_runtime._initialize_state_from_backend(
        backend_state=backend_state,
        group_cfg=group_cfg,
        seed_artifacts={},
        mode="daemon",
        job_no="JOB-9",
        hooks=hooks,
    )

    assert captured["group_name"] == "sdlc_10_requirement_v1"
    assert state["workflow_run_id"] == "abc-123"


def test_sync_local_from_backend_pending_clears_stale_approval():
    """After approval, backend advances to PENDING + next step.

    Regression test: the V2 backend state machine uses PENDING (not
    IN_PROGRESS) once an approved run moves to the next step. The local
    job.json still has pending_human_approval_for set — the sync must
    clear it or the CLI rejects the claimed step with
    WAITING_FOR_HUMAN_APPROVAL.
    """
    state = {
        "job_id": "AMGEN-988yaqof",
        "job_status": "WAITING_FOR_HUMAN_APPROVAL",
        "current_step": "generate_images",
        "pending_human_approval_for": "generate_images",
        "workflow_step_run_id": "old-step-id",
        "artifacts": {},
    }
    backend_state = {
        "run_id": "fd20f5eb-f0fc-425c-bad9-c63c0a814431",
        "run_code": "AMGEN-988yaqof",
        "workflow_name": "agnes_media_gen_v1",
        "run_status": "PENDING",
        "current_step": "archive_step_02",
        "current_step_run_id": None,
    }

    changed = manual_runtime.sync_local_from_backend(state, backend_state)

    assert changed is True
    assert state["job_status"] == "IN_PROGRESS"
    assert state["current_step"] == "archive_step_02"
    assert state["pending_human_approval_for"] is None


def test_sync_local_from_backend_flat_run_response_maps_fields():
    """Flat RunResponse must map run_status and current_step into local state."""
    state = {
        "job_id": "AMGEN-3p68wei8",
        "job_status": "WAITING_FOR_HUMAN_APPROVAL",
        "current_step": "generate_images",
        "pending_human_approval_for": "generate_images",
        "workflow_step_run_id": "old-step-id",
        "artifacts": {},
    }
    backend_state = {
        "run_id": "0323ea15-0609-4d12-b80d-dfd4b34a4721",
        "run_code": "AMGEN-3p68wei8",
        "workflow_name": "agnes_media_gen_v1",
        "run_status": "RUNNING",
        "current_step": "archive_step_02",
        "current_step_run_id": "new-step-id",
    }

    changed = manual_runtime.sync_local_from_backend(state, backend_state)

    assert changed is True
    assert state["job_status"] == "IN_PROGRESS"
    assert state["current_step"] == "archive_step_02"
    assert state["workflow_step_run_id"] == "new-step-id"
    assert state["pending_human_approval_for"] is None


def test_sync_local_from_backend_keeps_approval_while_backend_still_gated():
    """Backend still in WAITING_FOR_HUMAN_APPROVAL for the same step → keep flag."""
    state = {
        "job_id": "AMGEN-3p68wei8",
        "job_status": "WAITING_FOR_HUMAN_APPROVAL",
        "current_step": "generate_images",
        "pending_human_approval_for": "generate_images",
        "artifacts": {},
    }
    backend_state = {
        "run_id": "r1",
        "run_code": "AMGEN-3p68wei8",
        "workflow_name": "agnes_media_gen_v1",
        "run_status": "WAITING_FOR_HUMAN_APPROVAL",
        "current_step": "generate_images",
    }

    changed = manual_runtime.sync_local_from_backend(state, backend_state)

    assert changed is False
    assert state["pending_human_approval_for"] == "generate_images"


def test_resolve_manual_run_rejects_daemon_claimed_step_mismatch():
    args = SimpleNamespace(
        job_id='JOB-123',
        job='review_core_governance_docs',
        new_job=False,
        set=[],
        template_group='00_core_governance_bootstrap_v1',
        task_graph_id='',
        task_node_id='',
        job_no='JOB-123',
    )
    group_cfg = {
        'steps': ['generate_core_governance_docs', 'review_core_governance_docs'],
        'step_configs': {},
        'job_init_step': 'generate_core_governance_docs',
        'job_init_inputs': [],
        'default_max_rejects': 2,
    }
    state = {
        'job_id': 'JOB-123',
        'current_step': 'validate_core_governance_docs',
        'pending_human_approval_for': None,
    }
    hooks = SimpleNamespace(
        load_job=lambda *args, **kwargs: dict(state),
        ensure_backward_compatible_state=lambda payload: payload,
        migrate_job_state=lambda payload: payload,
        recover_exhausted_planning_job=lambda payload, cfg: payload,
        reconcile_job_state=lambda payload, cfg: payload,
        prepare_state_for_retry=lambda **kwargs: kwargs['state'],
        get_job_status=lambda payload: payload.get('job_status', 'IN_PROGRESS'),
        _step_progress_label=lambda *args, **kwargs: 'step 1 of 1',
        _format_job_status_summary=lambda *args, **kwargs: 'summary',
    )

    with pytest.raises(ValueError, match="Daemon claimed step 'review_core_governance_docs' but job JOB-123 is currently at 'validate_core_governance_docs'"):
        manual_runtime.resolve_manual_run(args=args, group_cfg=group_cfg, hooks=hooks, mode='daemon')
