# Daemon Job State Sync Plan

## Objective

Eliminate the backend's `resolve_transition()` execution logic. The daemon (via
`run_agent.py run`) becomes the sole owner of workflow execution and step
routing. The backend becomes a pure persistence layer — it accepts the job
state from `job.json` and saves it as-is.

## Architecture Change

**Before:**

```
daemon → _submit_worker_result → backend.complete_step_run() → resolve_transition() → recomputes next_step
```

**After:**

```
daemon → reads job.json → maps state → backend.sync_job_state() → persists as-is (no routing logic)
```

## Phase 1: Backend — New API Endpoint

### 1a. Schema (`agent_runner_backend/api/schemas.py`)

Add `JobSyncItem`:

```python
class JobSyncItem(BaseModel):
    step_status: str                        # "completed", "failed", "approved"
    step_outcome: Optional[str] = None      # "approved", "rejected"
    step_coder: Optional[str] = None
    step_duration_seconds: Optional[int] = None
    run_status: str                         # "pending", "failed", "awaiting_human", "completed"
    next_step_name: Optional[str] = None    # null = terminal
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    review: Optional[dict[str, Any]] = None
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    events: list[dict[str, Any]] = Field(default_factory=list)
```

### 1b. Service (`agent_runner_backend/services/execution_service.py`)

New function `synchronize_job_state(db, step_run_id, body)`:

- Update `step_run.status`, `step_run.completed_at`, `step_run.outcome`,
  `step_run.coder`, `step_run.duration_seconds`, `step_run.error_message`
- Update `run.status = body.run_status`
- Merge `body.output_payload` into `run.context_payload`
- If `body.next_step_name` is set: create
  `WorkflowStepRun(step_name=next_step_name, status="pending")`, set
  `run.current_step_name = next_step_name`
- If `body.next_step_name` is None: set `run.completed_at = utcnow()`
- Create `WorkflowArtifact` from each item in `body.artifacts`
- Create `WorkflowEvent` from each item in `body.events`
- Create `WorkflowReview` if `body.review` provided
- **No `resolve_transition()`. No outcome routing. No status computation.**

### 1c. Route (`agent_runner_backend/api/run_routes.py`)

```python
@router.post("/step-runs/{step_run_id}/job-sync")
async def sync_job_state(step_run_id: str, body: JobSyncItem, db: Session = Depends(get_db)):
    result = execution_service.synchronize_job_state(db, step_run_id=step_run_id, body=body)
    return result
```

### 1d. BackendClient method (`agent_runner_backend/workers/backend_client.py`)

```python
def sync_job_state(self, *, step_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return self._request('POST', f'/api/step-runs/{step_run_id}/job-sync', payload)
```

## Phase 2: agent-runner-v2 — Daemon reads `job.json`, maps to sync payload

### 2a. New payload builder (`agent_runner_v2/daemon_runtime.py`)

`build_job_sync_payload(job: dict, step_result: dict) -> dict`:

**Status mapping:**

| `job.json` field | API field |
|---|---|
| `job_status == "IN_PROGRESS"` | `run_status = "pending"` |
| `job_status == "COMPLETED"` | `run_status = "completed"`, `next_step_name = None` |
| `job_status == "FAILED"` | `run_status = "failed"` |
| `job_status == "WAITING_FOR_HUMAN_INTERVENTION"` | `run_status = "awaiting_human"` |
| `current_step` (if set + IN_PROGRESS) | `next_step_name = current_step` |
| `last_failure_reason` | `error_message` |
| `artifacts` dict | `artifacts` list of `{artifact_key, file_path}` |

### 2b. Modify daemon result handling (`agent_runner_v2/daemon.py`)

In `_run_supervisor()`, replace:

```python
completion = _submit_worker_result(client, run, step_run, result)
completion_info = _finalize_worker_completion(client, run, step_run, completion, ...)
```

With:

```python
job_path = job_dir(template_group, backend_run_code) / "job.json"
if job_path.exists():
    job_state = json.loads(job_path.read_text(encoding="utf-8"))
    sync_payload = build_job_sync_payload(job_state, result)
    client.sync_job_state(step_run_id=sync_payload)
```

Also add `_read_job_state()` helper that reads `job.json` from
`JOBS_ROOT/template_group/run_code/job.json`.

### 2c. Remove deprecated code

- `daemon_runtime.py`: Remove `submit_worker_result()`,
  `finalize_worker_completion()`, `write_backend_job_json()`
- `run_agent.py`: Remove `_submit_worker_result()` and
  `_finalize_worker_completion()` delegation functions
- `backend_client.py` in v2: No change needed (reuses existing `BackendClient`)

## Phase 3: Cleanup

- Keep existing `complete_step_run` endpoint for backward compatibility with any
  non-daemon callers
- Keep `resolve_transition()` as dead code for now (can be removed in a
  follow-up after confirming no regression)

## Files Changed

| Repo | File | Change |
|---|---|---|
| backend | `api/schemas.py` | Add `JobSyncItem` |
| backend | `api/run_routes.py` | Add `POST /api/step-runs/{id}/job-sync` |
| backend | `services/execution_service.py` | Add `synchronize_job_state()` |
| backend | `workers/backend_client.py` | Add `sync_job_state()` |
| v2 | `daemon_runtime.py` | Add `build_job_sync_payload()`, remove old functions |
| v2 | `daemon.py` | Replace old submission calls with job-sync |

## Verification

### Unit tests (backend)

- `synchronize_job_state` with `next_step_name` set → creates
  `WorkflowStepRun(status="pending")`
- `synchronize_job_state` with `next_step_name = None` → terminal,
  `run.status = "completed"`
- `synchronize_job_state` with `run_status = "failed"` → terminal with error
- `synchronize_job_state` with `run_status = "awaiting_human"` → paused

### Unit tests (v2)

- `build_job_sync_payload` mapping for all status transitions

### Integration

1. Daemon claims step → spawns subprocess → subprocess completes step, writes
   `job.json`
2. Daemon reads `job.json`, builds sync payload
3. Daemon calls `POST /api/step-runs/{id}/job-sync`
4. Backend creates next `WorkflowStepRun(status="pending")`
5. Daemon polls, claims the newly created step run
