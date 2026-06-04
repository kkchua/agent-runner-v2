# PRE-INIT: Agent Runner Daemon Mode with DB Job Management

## 1. Initiative Title

**Enhance Agent Runner into Daemon Mode with Database-backed Job Management**

## 2. Initiative ID

`PRE-INIT-20260602-AGENT-RUNNER-DAEMON-DB`

## 3. Background

The current Agent Runner CLI is able to execute predefined workflows by triggering coder tools such as Claude Code, Codex, Qwen Code, or other supported coding agents. It works well when the runner owns the workflow directly.

However, when OpenClaw is used as the assistant/orchestrator and asked to run Agent Runner as a background process, the OpenClaw session can still become blocked or occupied by polling, monitoring, and interpreting the long-running job. Using OpenClaw subagents also creates excessive LLM calls because subagents may independently reason, monitor, and invoke additional model calls.

The next architectural step is to separate human-facing orchestration from workflow execution:

- OpenClaw should act as a thin control-plane assistant.
- Agent Runner should own execution, workflow state, validation, retries, and coder calls.
- Long-running workflows should run inside a daemon/worker process.
- Jobs should be submitted into a persistent database-backed job table.
- OpenClaw should only submit jobs, check status, inspect logs/artifacts, approve/retry/cancel jobs, and summarize results.

This prevents OpenClaw from blocking while a workflow is running and prepares the system for future integration with a Control Plane UI, API service, and UKBE artifact pipeline.

## 4. Problem Statement

Agent Runner currently behaves primarily like a direct CLI execution tool. This makes it difficult to safely integrate with OpenClaw as an external orchestration assistant because:

1. Long-running commands block the OpenClaw session.
2. Background process handling inside OpenClaw is unreliable or still session-bound.
3. Subagent-based monitoring causes too many unnecessary LLM calls.
4. Job state is not cleanly persisted outside the execution process.
5. Human approval gates and failure recovery are harder to manage if state only exists in the active process.
6. The system needs a stable command contract that allows any controller, including OpenClaw or a future UI, to manage jobs without owning execution.

## 5. Goal

Implement a daemon/worker mode for Agent Runner using database-backed job management so that Agent Runner can accept submitted jobs, execute them asynchronously, persist job state, expose status/log/artifact inspection commands, and support approval/retry/cancel workflows.

## 6. Non-Goals

This initiative should **not** attempt to rebuild the entire Agent Runner workflow engine.

Out of scope for this first daemon milestone:

- Building the full Control Plane UI.
- Replacing the existing workflow step logic.
- Implementing distributed multi-worker scaling unless the current code already supports it easily.
- Adding complex scheduling logic.
- Implementing advanced observability dashboards.
- Rewriting coder provider integrations.
- Adding OpenClaw subagent orchestration.
- Moving all UKBE artifact features into this initiative.

The first version should be practical, local-first, and stable.

## 7. Target Architecture

```text
User
 ↓
OpenClaw Assistant / CLI / Future UI
 ↓
agent-runner submit/status/logs/approve/retry/cancel
 ↓
Database Job Store
 ↓
agent-runner worker daemon
 ↓
Existing Agent Runner workflow engine
 ↓
Coder providers: Claude / Codex / Qwen / OpenClaw CLI if needed
 ↓
Artifacts, logs, status, review gates
```

## 8. Core Design Principle

OpenClaw should never directly run the full long-running workflow.

Instead:

```bash
agent-runner submit --initiative INIT-xxx
```

should return quickly with a job ID.

Then the daemon process handles execution:

```bash
agent-runner worker
```

OpenClaw or any external controller can later call:

```bash
agent-runner status --job-id <job_id>
agent-runner logs --job-id <job_id>
agent-runner approve --job-id <job_id>
agent-runner retry --job-id <job_id>
agent-runner cancel --job-id <job_id>
```

## 9. Proposed CLI Contract

### 9.1 Submit Job

```bash
agent-runner submit --initiative <initiative_id_or_file>
```

Expected behavior:

- Creates a new job record in DB.
- Stores initiative reference and initial metadata.
- Sets status to `QUEUED`.
- Returns immediately.

Example output:

```json
{
  "job_id": "job_20260602_0001",
  "status": "QUEUED",
  "initiative": "INIT-20260602-01"
}
```

### 9.2 Run Worker

```bash
agent-runner worker
```

Expected behavior:

- Starts a long-running daemon process.
- Polls or listens for queued jobs.
- Claims one job safely.
- Executes workflow steps using existing Agent Runner logic.
- Persists step state, logs, artifacts, and errors.
- Stops job execution at approval/intervention gates.
- Continues processing available jobs until stopped.

Optional arguments:

```bash
agent-runner worker --once
agent-runner worker --poll-interval 5
agent-runner worker --provider qwen
agent-runner worker --max-jobs 1
```

### 9.3 Check Status

```bash
agent-runner status --job-id <job_id>
agent-runner status --latest
```

Expected output:

```json
{
  "job_id": "job_20260602_0001",
  "status": "RUNNING",
  "current_step": "review_impl",
  "review_state": "PENDING",
  "provider": "qwen",
  "created_at": "2026-06-02T10:30:00+08:00",
  "updated_at": "2026-06-02T10:45:00+08:00"
}
```

### 9.4 View Logs

```bash
agent-runner logs --job-id <job_id> --lines 100
agent-runner logs --latest --lines 100
```

Expected behavior:

- Shows recent job logs.
- Does not trigger LLM calls.
- Does not continue execution.
- Read-only operation.

### 9.5 View Artifacts

```bash
agent-runner artifact --job-id <job_id> --step latest
agent-runner artifact --job-id <job_id> --step impl
```

Expected behavior:

- Returns artifact path, metadata, and optionally content preview.
- Does not modify job state.

### 9.6 Approve Job Gate

```bash
agent-runner approve --job-id <job_id>
```

Expected behavior:

- Valid only when job is waiting for human approval.
- Records approval event.
- Moves job back to `QUEUED` or `READY_TO_RESUME`.
- Worker resumes on next pickup.

### 9.7 Reject / Request Changes

```bash
agent-runner reject --job-id <job_id> --reason "Implementation is too broad. Keep scope to daemon mode only."
```

Expected behavior:

- Records human rejection reason.
- Moves job to a retry or intervention state depending on workflow policy.

### 9.8 Retry

```bash
agent-runner retry --job-id <job_id>
agent-runner retry --job-id <job_id> --step <step_name>
```

Expected behavior:

- Requeues a failed or waiting job.
- Optionally retries from a specific allowed step.
- Records retry event.

### 9.9 Cancel

```bash
agent-runner cancel --job-id <job_id>
```

Expected behavior:

- Marks job as `CANCEL_REQUESTED` or `CANCELLED`.
- Worker should stop safely at the next checkpoint.
- Current running child process should be handled according to existing provider execution safety rules.

## 10. Proposed Job Status Model

Minimum recommended statuses:

```text
QUEUED
CLAIMED
RUNNING
WAITING_FOR_HUMAN_APPROVAL
WAITING_FOR_HUMAN_INTERVENTION
READY_TO_RESUME
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
```

Optional future statuses:

```text
PAUSED
BLOCKED
RETRY_SCHEDULED
STALE
ORPHANED
```

## 11. Proposed Database Tables

### 11.1 `agent_runner_jobs`

Purpose: stores the primary job lifecycle.

Suggested fields:

```sql
id UUID PRIMARY KEY,
job_code TEXT UNIQUE NOT NULL,
initiative_id TEXT NULL,
initiative_ref TEXT NULL,
status TEXT NOT NULL,
current_step TEXT NULL,
review_state TEXT NULL,
provider TEXT NULL,
workflow_name TEXT NULL,
workspace_path TEXT NULL,
input_json JSONB NOT NULL DEFAULT '{}'::jsonb,
result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
error_message TEXT NULL,
failure_count INTEGER NOT NULL DEFAULT 0,
claimed_by TEXT NULL,
claimed_at TIMESTAMPTZ NULL,
started_at TIMESTAMPTZ NULL,
completed_at TIMESTAMPTZ NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 11.2 `agent_runner_job_events`

Purpose: append-only audit trail.

Suggested fields:

```sql
id UUID PRIMARY KEY,
job_id UUID NOT NULL REFERENCES agent_runner_jobs(id),
event_type TEXT NOT NULL,
step_name TEXT NULL,
message TEXT NULL,
payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Example event types:

```text
JOB_SUBMITTED
JOB_CLAIMED
JOB_STARTED
STEP_STARTED
STEP_COMPLETED
STEP_FAILED
HUMAN_APPROVAL_REQUIRED
HUMAN_APPROVED
HUMAN_REJECTED
JOB_RETRIED
JOB_CANCEL_REQUESTED
JOB_CANCELLED
JOB_COMPLETED
JOB_FAILED
```

### 11.3 `agent_runner_job_artifacts`

Purpose: tracks generated files and important workflow outputs.

Suggested fields:

```sql
id UUID PRIMARY KEY,
job_id UUID NOT NULL REFERENCES agent_runner_jobs(id),
step_name TEXT NULL,
artifact_type TEXT NOT NULL,
artifact_path TEXT NOT NULL,
artifact_meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
checksum TEXT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 11.4 Optional: `agent_runner_job_locks`

This may not be needed if PostgreSQL row locking is used.

Recommended first version: use PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED` to safely claim jobs.

## 12. Worker Claiming Strategy

Use DB transaction-based claiming to prevent multiple workers from running the same job.

Recommended PostgreSQL pattern:

```sql
SELECT id
FROM agent_runner_jobs
WHERE status IN ('QUEUED', 'READY_TO_RESUME')
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

Then update the selected row:

```sql
UPDATE agent_runner_jobs
SET status = 'CLAIMED',
    claimed_by = :worker_id,
    claimed_at = now(),
    updated_at = now()
WHERE id = :job_id;
```

After claim:

```text
CLAIMED → RUNNING → COMPLETED
                  → FAILED
                  → WAITING_FOR_HUMAN_APPROVAL
                  → WAITING_FOR_HUMAN_INTERVENTION
                  → CANCELLED
```

## 13. Execution Checkpoints

The worker should persist state at clear checkpoints:

1. Before job starts.
2. Before each workflow step.
3. After each workflow step.
4. When validation fails.
5. When retry is scheduled.
6. When human approval is required.
7. When job completes.
8. When job fails.
9. When cancellation is requested or completed.

This allows safe recovery if the worker process crashes.

## 14. Resume Behavior

For the first version, resume behavior can be conservative.

Recommended v1 rule:

- If a worker crashes while a job is `RUNNING` or `CLAIMED`, mark the job as `FAILED` or `STALE` through a recovery command/manual operation.
- Do not automatically resume partially running coder steps unless the existing runner has deterministic checkpoints.
- Resume should happen only from the latest completed workflow step or explicit retry step.

Future enhancement:

```bash
agent-runner recover-stale --older-than-minutes 30
```

## 15. Integration with Existing Agent Runner Workflow

The daemon mode should wrap the existing execution flow instead of replacing it.

Existing direct execution can remain available:

```bash
agent-runner run --initiative INIT-xxx
```

New daemon path:

```bash
agent-runner submit --initiative INIT-xxx
agent-runner worker
```

Internally, worker should call the same workflow execution service used by `run`, but with a job context object that provides:

- job ID
- workspace path
- current step
- logging sink
- artifact registry
- cancellation checker
- approval gate handler
- status updater

## 16. OpenClaw Usage Rules

OpenClaw should be instructed as follows:

```text
Do not run long-running Agent Runner workflows directly.
Use `agent-runner submit` to create jobs.
Return the job ID to the user.
Use `agent-runner status`, `agent-runner logs`, and `agent-runner artifact` only when asked to inspect progress.
Do not continuously poll jobs.
Do not spawn subagents to monitor Agent Runner jobs.
Do not call coder tools directly unless the user explicitly asks.
Use `agent-runner approve`, `reject`, `retry`, or `cancel` only when the user requests the action.
```

## 17. Implementation Slices

### Slice 1: DB Schema and Repository Layer

Deliverables:

- Migration for `agent_runner_jobs`.
- Migration for `agent_runner_job_events`.
- Migration for `agent_runner_job_artifacts`.
- Repository/service methods:
  - create job
  - get job
  - get latest job
  - claim next job
  - update status
  - append event
  - register artifact

Acceptance:

- Tests can create, fetch, update, and claim jobs.
- Claim logic prevents duplicate claiming.
- Events are append-only.

### Slice 2: CLI Commands

Deliverables:

- `submit`
- `status`
- `logs`
- `artifact`
- `approve`
- `reject`
- `retry`
- `cancel`

Acceptance:

- Each command returns deterministic JSON or readable text.
- Submit returns quickly.
- Read-only commands do not trigger workflow execution or LLM calls.
- State-changing commands append job events.

### Slice 3: Worker Loop

Deliverables:

- `agent-runner worker`
- `--once` mode for testing
- `--poll-interval` option
- worker ID generation
- job claim loop
- status transitions

Acceptance:

- Worker can pick up a queued job.
- Worker does not pick up the same job twice.
- Worker exits after one job with `--once`.
- Worker handles no-job case cleanly.

### Slice 4: Existing Workflow Integration

Deliverables:

- Worker calls existing workflow execution engine.
- Job context passed into workflow execution.
- Current step persisted.
- Workflow outputs registered as artifacts.
- Failures persisted to job status and event log.

Acceptance:

- A submitted job can run through at least one existing workflow path.
- Current step is visible from `status`.
- Logs/events are visible after execution.
- Failed workflow does not leave job in ambiguous running state.

### Slice 5: Human Gate Support

Deliverables:

- Worker can set job to `WAITING_FOR_HUMAN_APPROVAL`.
- `approve` command moves job to `READY_TO_RESUME`.
- `reject` command records reason and moves job to appropriate retry/intervention state.

Acceptance:

- Job pauses at human approval gate.
- Worker does not continue until approval is recorded.
- After approval, job can resume.

### Slice 6: Cancellation and Retry

Deliverables:

- `cancel` command.
- cancellation checker inside worker step boundaries.
- `retry` command.
- retry event tracking.

Acceptance:

- Queued job can be cancelled before execution.
- Running job can be marked cancel requested.
- Worker respects cancellation at checkpoints.
- Failed job can be retried safely.

### Slice 7: OpenClaw Command Guide

Deliverables:

- Short instruction document for OpenClaw.
- Allowed command list.
- Forbidden behaviors.
- Example usage.

Acceptance:

- OpenClaw can submit and inspect jobs without blocking.
- No subagent monitoring is required.

## 18. Testing Strategy

### Unit Tests

Cover:

- job creation
- job status transitions
- job claiming
- event appending
- artifact registration
- approval transition
- retry transition
- cancellation transition

### Integration Tests

Cover:

1. Submit job → worker once → completed or expected waiting state.
2. Submit job → status returns queued.
3. Worker claims job → status shows running/current step.
4. Worker failure → job failed with error event.
5. Human approval gate → approve → resume.
6. Cancel queued job → cancelled.
7. Retry failed job → queued or ready to resume.

### No-LLM Tests

Where possible, use fake coder providers or mock workflow steps so tests do not call external LLMs.

## 19. Acceptance Criteria

This PRE-INIT is complete when the implementation can demonstrate:

1. `agent-runner submit` creates a DB-backed queued job and returns immediately.
2. `agent-runner worker --once` can claim and execute a queued job.
3. Job status can be inspected without triggering execution.
4. Logs/events can be inspected without triggering LLM calls.
5. Artifacts can be registered and listed by job.
6. Failed jobs persist error details.
7. Approval-gated jobs pause and can resume after approval.
8. Cancel and retry commands exist with safe state transitions.
9. OpenClaw can safely use the CLI as a control interface without running long workflows directly.

## 20. Suggested First Implementation Prompt for Existing Agent Runner

Use the following instruction for the current Agent Runner to start implementation planning:

```text
We need to enhance Agent Runner with daemon mode and database-backed job management.

Please create an implementation PLAN based on this PRE-INIT. The implementation must preserve the existing direct workflow execution path and add a new asynchronous path:

- agent-runner submit
- agent-runner worker
- agent-runner status
- agent-runner logs
- agent-runner artifact
- agent-runner approve
- agent-runner reject
- agent-runner retry
- agent-runner cancel

Use PostgreSQL for job management if the existing project already uses PostgreSQL. Otherwise propose the smallest compatible DB abstraction.

Prioritize a practical first milestone:
1. DB schema and repository layer
2. submit/status commands
3. worker --once mode
4. integration with one existing workflow path
5. event log and artifact registration

Do not build the Control Plane UI in this initiative.
Do not use OpenClaw subagents for monitoring.
Do not rewrite the existing workflow engine unless absolutely necessary.

The PLAN should include implementation slices, files likely to change, tests, acceptance criteria, and rollback considerations.
```

## 21. Recommended Naming

Suggested initiative name:

```text
Agent Runner Daemon Mode and DB Job Management
```

Suggested branch name:

```text
feature/agent-runner-daemon-db-jobs
```

Suggested first milestone:

```text
M1: DB-backed submit/status/worker-once loop
```

## 22. Final Notes

This initiative is the correct foundation before asking OpenClaw to orchestrate full workflows.

The desired operating model is:

```text
OpenClaw = cockpit / command assistant
Agent Runner daemon = workflow executor
Database = job state and audit trail
Coder tools = implementation engines
Artifacts = reviewable outputs
```

This should reduce blocking, reduce unnecessary LLM calls, improve recovery, and prepare the system for both OpenClaw control and future UI-based control.
