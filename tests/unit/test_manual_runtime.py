from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent_runner_v2 import manual_runtime


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
