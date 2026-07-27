# Job Definition Dictionary

**Version:** 1.0 | **Date:** 2026-07-27 | **Schema Version:** 6

Reference document for the agent-runner-v2 job state model — covering local job.json fields, backend run/step_run fields, status values, transitions, and the mapping between them.

---

## 1. Architecture Overview

```
job.json (local)  ←→  CLI (run_agent.py)  ←→  Backend Database (runs/step_runs)
                                              ↑
                         Daemon syncs via build_job_sync_payload()
                         (Phase 2: CLI syncs directly)
```

- **job.json**: Local file at `~/.ukbe-runner/jobs/{template_group}/{job_id}/job.json`
- **Backend runs table**: Database record for the overall workflow run
- **Backend step_runs table**: Database record for each step execution

---

## 2. Job Statuses (job.json)

### Non-Terminal Statuses

| Status | Meaning | What Happens Next |
|--------|---------|-------------------|
| `IN_PROGRESS` | Step is executing or ready to execute | Daemon claims and runs the step |
| `WAITING_FOR_AUTO_RETRY` | Transient failure, will auto-retry | Daemon re-runs after brief delay |
| `WAITING_FOR_HUMAN_APPROVAL` | Review gate — coder approved, needs human sign-off | Console user approves/rejects |
| `WAITING_FOR_HUMAN_INTERVENTION` | Error encountered — validator failure, coder crash, config issue | Console user resumes/retries |
| `WAITING_FOR_HUMAN_MAXRETRIED` | Refine loop exhausted (reviewer rejected N times) | Console user resumes/retries |

### Terminal Statuses

| Status | Meaning |
|--------|---------|
| `COMPLETED` | All steps finished successfully |
| `FAILED` | Unrecoverable failure |
| `STOPPED` | Cancelled by operator |

---

## 3. Backend Run Statuses

| Backend `run_status` | Mapped From (job_status) | Description |
|----------------------|--------------------------|-------------|
| `pending` | `IN_PROGRESS`, `WAITING_FOR_AUTO_RETRY` | Step is queued or retrying |
| `completed` | `COMPLETED` | Workflow finished |
| `failed` | `FAILED` | Workflow failed |
| `awaiting_human` | `WAITING_FOR_HUMAN_APPROVAL`, `WAITING_FOR_HUMAN_INTERVENTION`, `WAITING_FOR_HUMAN_MAXRETRIED` | Needs human action |
| `stopped` | `STOPPED` | Cancelled by operator |

**Mapping function:** `_map_job_status_to_run_status()` in `daemon_runtime.py`

---

## 4. job.json Field Dictionary

### Identity Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `job_id` | string | Unique job identifier (run_code from backend) | `"01PC-GEN-20260727-001"` |
| `template_group` | string | Workflow name | `"agnes_media_gen_v1"` |
| `runner_version` | string | Runner version marker | `"v2"` |
| `state_schema_version` | int | Schema version for migration | `6` |

### Path Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `project_root` | string | Workspace root path | `"D:/MyProjectSpace/..."` |
| `workspace_path` | string | Same as project_root (alias) | `"D:/MyProjectSpace/..."` |
| `target_project_root` | string | Delivery target path | `"D:/MyProjectSpace/..."` |

### Status & Routing Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `job_status` | string | Current job status (see Section 2) | `"IN_PROGRESS"` |
| `status` | string | Mirror of job_status (dual-field compat) | `"IN_PROGRESS"` |
| `current_step` | string | Current/next step to execute | `"generate_prompts"` |
| `completed_steps` | list[string] | Steps that completed successfully | `["extract_descriptions"]` |
| `failed_steps` | list[string] | Steps that failed | `[]` |
| `job_init_step` | string/null | Initial step override from workflow config | `null` |

### Backend Linkage Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `workflow_run_id` | string | Backend run UUID | `"abc-123-def"` |
| `workflow_step_run_id` | string | Backend step_run UUID | `"step-run-xyz"` |
| `backend_url` | string | Backend base URL | `"http://127.0.0.1:8100"` |
| `backend_context_payload` | dict | Original context from backend claim | `{"start_step": "..."}` |
| `backend_artifact_rules` | dict | Artifact publish rules from backend | `{}` |
| `backend_step_order` | int | Step order from backend spec | `2` |
| `backend_step_sequence` | int | Step sequence number | `2` |
| `backend_step_dir_rel` | string | Relative step dir path | `"jobs/agnes.../02_generate_prompts"` |

### Coder & Usage Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `step_coders` | dict | Coder used per step | `{"extract_descriptions": "opencode"}` |
| `step_usage` | dict | Token usage per step | `{}` |
| `usage_summary` | dict | Aggregated token usage | `{"input_tokens": 5000, ...}` |

### Approval & Review Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pending_human_approval_for` | string/null | Step awaiting human approval | `"generate_prompts"` |
| `human_approvals` | dict | Human approval decisions per step | `{}` |
| `model_approved_steps` | list[string] | Steps approved by model | `["extract_descriptions"]` |
| `review_state` | dict | Current review state | `{"review_decision": "PENDING", ...}` |
| `last_model_output` | string/null | Last coder output | `null` |

### Failure & Retry Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `reject_counts` | dict | Rejection count per step | `{"extract_descriptions": 1}` |
| `retry_history` | list | History of retry attempts | `[]` |
| `pending_intervention_for` | string/null | Step needing human intervention | `null` |
| `last_failure_class` | string/null | Failure classification | `"HUMAN_RETRY_REQUIRED"` |
| `last_failure_code` | string/null | Specific failure code | `"IMAGE_GEN_PARTIAL_FAILURE"` |
| `last_failure_reason` | string/null | Human-readable failure reason | `"API timeout on variant 3"` |
| `last_failure_source` | string/null | Where failure originated | `"validator"`, `"runner"`, `"model"`, `"adapter"` |
| `auto_retry_count_by_step` | dict | Auto-retry count per step | `{}` |
| `human_retry_count_by_step` | dict | Human-retry count per step | `{}` |
| `failure_history` | list | Full failure history | `[]` |

### Refine Loop & Replan Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `loop_context` | dict | Active refine loop state | `{"active": false, ...}` |
| `loop_history` | list | Past refine loop records | `[]` |
| `replan_context` | dict | Active replan state | `{"active": false, ...}` |
| `replan_history` | list | Past replan records | `[]` |
| `planning_attempt_count` | int | Number of replan attempts | `0` |

### Artifact Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `artifacts` | dict | All artifact key→path mappings | `{"IMAGE_DESCRIPTIONS": "step_01/index.json", ...}` |
| `seed_artifact_type` | string/null | Input artifact type | `null` |
| `seed_artifact_path` | string/null | Input artifact path | `null` |

### Recovery & Repair Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `recovered_from_invalid_result` | bool | Whether last result was recovered | `false` |
| `recovery_code` | string/null | Recovery code if recovered | `null` |
| `recovery_source` | string/null | Recovery source | `null` |
| `repair_history` | list | State repair history | `[]` |
| `reconciled_from_failure` | string/null | Failure reconciliation info | `null` |

### Task Execution Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `task_generation_state_version` | int | Task gen state version | `1` |
| `task_generation_state` | dict/null | Task generation state | `null` |
| `task_execution_binding` | dict | Task graph binding | `{"task_node_id": null, ...}` |

### Timestamp Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `created_at` | string | Job creation timestamp (ISO-8601) | `"2026-07-27T10:30:00"` |
| `updated_at` | string | Last update timestamp (ISO-8601) | `"2026-07-27T10:35:00"` |

---

## 5. Status Transition Diagram

```
                          ┌──────────────────────────────────────────┐
                          │                                          │
    ┌──────────┐     ┌────▼─────┐     ┌──────────────────┐     ┌───┴────┐
    │ PENDING   │────►│IN_PROGRESS│────►│ WAITING_FOR_AUTO │────►│IN_PROGRESS│
    │(backend)  │     │          │     │ _RETRY           │     │(retry)  │
    └──────────┘     └────┬─────┘     └──────────────────┘     └────────┘
                          │
              ┌───────────┼───────────┬──────────────────┐
              │           │           │                  │
         ┌────▼────┐ ┌───▼─────┐ ┌───▼──────────┐ ┌────▼─────┐
         │COMPLETED│ │ FAILED  │ │WAITING_FOR   │ │ STOPPED  │
         │(final)  │ │(final)  │ │_HUMAN_*      │ │(cancel)  │
         └─────────┘ └─────────┘ └───┬──────────┘ └──────────┘
                                      │
                              ┌───────┼───────┐
                              │       │       │
                         APPROVE  RESUME   RETRY
                              │       │       │
                              ▼       ▼       ▼
                         IN_PROGRESS  IN_PROGRESS  IN_PROGRESS
                         (next step)  (same step)  (same step,
                                                    reset counts)
```

### Transition Triggers

| From | To | Trigger | Source |
|------|----|---------|--------|
| IN_PROGRESS | IN_PROGRESS | Step approved, advance to next | `route_after_step()` |
| IN_PROGRESS | COMPLETED | Last step completed | `advance_to_next_step()` |
| IN_PROGRESS | WAITING_FOR_HUMAN_APPROVAL | Review step needs sign-off | `mark_review_waiting_for_human()` |
| IN_PROGRESS | WAITING_FOR_HUMAN_INTERVENTION | Validator failure, coder crash | `route_after_failure()` |
| IN_PROGRESS | WAITING_FOR_AUTO_RETRY | Transient error (API timeout, 429) | `_classify_model_rejection()` |
| IN_PROGRESS | FAILED | Max retries exhausted, FATAL error | `route_after_failure()` |
| WAITING_FOR_AUTO_RETRY | IN_PROGRESS | Auto-retry triggers | Daemon re-execution |
| WAITING_FOR_HUMAN_APPROVAL | IN_PROGRESS | Human approves | `--approve-step` |
| WAITING_FOR_HUMAN_INTERVENTION | IN_PROGRESS | Human resumes | `--resume-step` |
| WAITING_FOR_HUMAN_MAXRETRIED | IN_PROGRESS | Human resumes | `--resume-step` |
| * | STOPPED | Operator cancels | `stop <run_id>` |

---

## 6. Backend Data Model (PostgreSQL via SQLAlchemy)

### workflow_runs Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | String(36) PK | UUID |
| `run_code` | String(80) UNIQUE | Human-readable job ID (e.g., `"01PC-GEN-20260727-001"`) |
| `workflow_definition_id` | String(36) FK | Links to workflow_definitions |
| `status` | String(40) | Current status (see Section 3). Default: `"pending"` |
| `current_step_name` | String(120) | Currently executing step |
| `current_step_run_id` | String(36) | **Active step_run UUID** (used by stop_commands.py) |
| `awaiting_human_step` | String(120) | Step awaiting human approval |
| `target_worker_id` | String(80) | Pinned worker ID |
| `claimed_by_worker` | String(80) | Worker that claimed this run |
| `worker_label` | String(40) | Queue label (`"live"` or `"dev"`) |
| `project_root` | Text | Workspace root path |
| `workspace_path` | Text | Workspace path |
| `env_overrides` | JSONB | Environment variable overrides |
| `input_payload` | JSONB | Input artifacts dict |
| `context_payload` | JSONB | Context dict (includes `__run_control.stop_requested`) |
| `result_payload` | JSONB | Result data |
| `error_message` | Text | Error message if failed |
| `submitted_at` | DateTime | Submission timestamp |
| `started_at` | DateTime | Execution start timestamp |
| `completed_at` | DateTime | Completion timestamp |
| `created_at` / `updated_at` | DateTime | Record timestamps |

**Run status values:** `"pending"`, `"running"`, `"claimed"`, `"awaiting_human"`, `"completed"`, `"failed"`, `"stopped"`

**Non-terminal group:** `["pending", "running", "claimed", "awaiting_human"]`
**Terminal group:** `["completed", "failed", "stopped"]`

### workflow_step_runs Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | String(36) PK | UUID |
| `workflow_run_id` | String(36) FK | CASCADE delete to workflow_runs |
| `step_definition_id` | String(36) FK | Links to step definition |
| `step_name` | String(120) | Step name |
| `sequence_no` | Integer | Step order (1-based) |
| `attempt_no` | Integer | Attempt number (default 1) |
| `iteration_no` | Integer | Iteration number (default 1) |
| `status` | String(40) | `"pending"`, `"claimed"`, `"running"`, `"completed"`, `"failed"`, `"cancelled"` |
| `outcome` | String(50) | `"success"`, `"approved"`, `"rejected"`, `"rejected_exhausted"`, `"failed"`, `"preflight_blocked"` |
| `coder` | String(50) | Coder name used |
| `assigned_worker_id` | String(80) | Worker assigned to this step |
| `input_snapshot` | JSONB | Input snapshot at execution time |
| `output_payload` | JSONB | Output artifacts |
| `usage_summary` | JSONB | Token/cost usage |
| `error_message` | Text | Error if failed |
| `started_at` / `completed_at` | DateTime | Execution timestamps |

### worker_registry Table

| Field | Type | Description |
|-------|------|-------------|
| `worker_id` | String(80) PK | Worker identifier |
| `host_name` | String(120) | Host machine name |
| `capabilities` | JSONB | Worker capabilities |
| `status` | String(30) | `"active"`, `"busy"`, `"idle"` |
| `worker_label` | String(40) | Queue label |
| `current_step_run_id` | String(36) | Currently executing step_run |
| `last_heartbeat` | DateTime | Last heartbeat timestamp |

### Claim Endpoint Logic

```
POST /api/workers/claim?worker_id={worker_id}
```

Filters:
1. `step_run.status == "pending"` only
2. `run.worker_label` must match worker's label
3. `run.target_worker_id` must match worker_id or be NULL
4. Ordered by oldest run first, then lowest sequence_no

**⚠️ Does NOT filter by `run.status`** — stopped runs with pending step_runs can still be claimed.

### Stop Endpoint Logic

```
POST /api/runs/{run_id}/stop
```

**⚠️ Does NOT change `run.status`** — only sets `context_payload.__run_control.stop_requested = True`. The actual status transition to `"stopped"` must be done by the CLI via `sync_job_state`.

---

## 7. CLI Commands Reference

### Backend API Wrapper Commands (no job.json needed)

| Command | Backend Endpoint | Description |
|---------|-----------------|-------------|
| `ukbe-run-agent list-runs [--worker-id X] [--status-group Y]` | `GET /api/runs` | List workflow runs |
| `ukbe-run-agent show-run <run_id>` | `GET /api/runs/{id}` | Show run details |
| `ukbe-run-agent submit --workflow-name X` | `POST /api/runs` | Submit new run |
| `ukbe-run-agent stop <run_id>` | `GET /api/runs/{id}` + `POST /api/step-runs/{id}/job-sync` + `POST /api/runs/{id}/stop` | Comprehensive cancel |
| `ukbe-run-agent approve <run_id> [--reject] [--resume] [--retry]` | `POST /api/runs/{id}/approve` | Approve/reject/resume/retry |
| `ukbe-run-agent reset-step <run_id> <step_name>` | `POST /api/runs/{id}/reset-step` | Reset current step |

### Execution Commands (requires job.json)

| Command | Description |
|---------|-------------|
| `ukbe-run-agent run --template-group X --mode daemon --job-id Y --job Z` | Execute a step (daemon mode) |
| `ukbe-run-agent run --template-group X --job-id Y --approve-step Z` | Approve step (local) |
| `ukbe-run-agent run --template-group X --job-id Y --reject-step Z` | Reject step (local) |
| `ukbe-run-agent run --template-group X --job-id Y --cancel-run` | Cancel run (local) |
| `ukbe-run-agent run --template-group X --job-id Y --resume-step Z` | Resume step (local) |
| `ukbe-run-agent run --template-group X --job-id Y --retry-step Z` | Retry step (local) |
| `ukbe-run-agent run --template-group X --job-id Y --override-step Z` | Override step (local) |

---

## 8. Daemon ↔ Backend ↔ CLI Flow

### Normal Execution Flow

```
1. Daemon → Backend: claim_step(worker_id)
2. Backend → Daemon: {run, step_run, step_execution_spec}
3. Daemon → CLI: spawn subprocess (run --mode daemon)
4. CLI: execute step, write job.json, write result.json
5. CLI → Backend: sync_job_state(step_run_id, payload)  [Phase 1+]
6. Daemon: monitor child process
7. Daemon: child exits → log → cleanup  [Phase 2: no more sync]
```

### Cancel Flow

```
1. Console → CLI: stop <run_id>
2. CLI → Backend: get_run(run_id) → get active_step_run_id
3. CLI → Backend: sync_job_state(step_run_id, {stopped, cancelled})
4. CLI → Backend: stop_run(run_id) → set run_status=stopped
5. Daemon: claim_step → backend returns nothing (stopped filtered)
   OR: Daemon claims → _is_stop_requested() → skip
```

---

## 9. Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| `CURRENT_SCHEMA_VERSION` | `6` | `job_state.py` |
| `NON_TERMINAL_JOB_STATUSES` | `{IN_PROGRESS, WAITING_FOR_AUTO_RETRY, WAITING_FOR_HUMAN_INTERVENTION, WAITING_FOR_HUMAN_APPROVAL, WAITING_FOR_HUMAN_MAXRETRIED}` | `job_state.py` |
| `REVIEW_DECISIONS` | `{PENDING, APPROVED, REJECTED}` | `job_state.py` |
| `HUMAN_DECISIONS` | `{PENDING, APPROVED, REJECTED, NOT_REQUIRED}` | `job_state.py` |
| `CONTROL_CLASSES` | `{AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL}` | `job_state.py` |
| `FAILURE_SOURCES` | `{runner, adapter, model, validator}` | `job_state.py` |
