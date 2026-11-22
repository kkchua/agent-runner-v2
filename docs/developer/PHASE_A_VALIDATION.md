# Phase A validation

Phase A covers local `plan_first_review_v1` attempt preparation, result eligibility,
recovery, durable outcomes and duplicate replay. Baseline transactions and approval
binding have separate milestone scopes.

`tests/unit/test_phase_a_final_closure.py` uses the actual workflow manifest and
production job save/load under temporary paths. Only coder execution, notifications
and intentional failure boundaries are intercepted. Its scenarios verify:

- Generation, current model-review rejection, persisted recovery context and actual
  refinement preparation/execution, with changed and unchanged output.
- Persisted MD5 before coder entry, exact no-op recovery reason, revision advancement
  once on change, and no false completion on no-op.
- Relative and absolute review declarations with a stale generic review alias.
- Applied and failed writer/save/reload/replay with equivalent path representations
  in both directions, whole-state/disk equality and no additional effects.
- Invalid state preparation through the real wrapper, without saving or coder entry.
- Mandatory exact positive record baselines through actual first-outcome routing.
- Invalid-ID and foreign-owner failure saves with pre-replacement exceptions,
  unchanged caller/disk state and no notification.

`test_phase_a_r24_regression.py` retains focused baseline, declaration and non-file
observation tests. Its job-path fixture isolates imported save aliases as well as
direct job-state calls. Omitted current review declarations fail even when an old
canonical review exists; a generic model-rejection failure is not sufficient evidence.

Run both focused files with the repository interpreter:

```bash
.venv/bin/python -m pytest tests/unit/test_phase_a_final_closure.py tests/unit/test_phase_a_r24_regression.py -q
```

For milestone regression validation, also retain `test_plan_first_review_v1.py`,
`test_baseline_transactions.py`, `test_attempt_tracking.py`,
`test_phase_a_acceptance.py`, `test_phase_a_corrections.py`,
`test_phase_a_integration.py`, `test_phase_a_f1_corrections.py`,
`test_phase_a_f3_corrections.py`, `test_job_state_review_completion.py`,
`test_workflow_router_notifications.py` and `test_run_agent_hook_surface.py`.
Required broader validation is `.venv/bin/python -m pytest tests/unit/ -q`.

Some older tests outside the focused fixtures still use default runner-home paths.
The workspace validation harness redirects `Path.home` to temporary storage before
test imports. Record this isolation when reporting results. Compare exact broader
failure IDs with the documented baseline; do not treat an unexpected failure as a
baseline failure merely because the total count is unchanged.
