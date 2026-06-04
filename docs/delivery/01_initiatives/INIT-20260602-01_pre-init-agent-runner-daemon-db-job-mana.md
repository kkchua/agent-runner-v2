# Enhance Agent Runner into Daemon Mode with Database-backed Job Management

## Metadata

| Field | Value |
|---|---|
| **Doc Type** | pre-init (promotion candidate) |
| **Template Version** | v1 |
| **Artifact Version** | v1 |
| **Source Pre-Init ID** | `PRE-INIT-20260602-AGENT-RUNNER-DAEMON-DB` |
| **Proposed Initiative ID** | `INIT-20260602-01` |
| **Title** | Enhance Agent Runner into Daemon Mode with Database-backed Job Management |
| **Status** | under review |
| **Supersedes** | None |
| **Owner** | @kengkoon.chua |
| **Workflow Governance In Scope** | Job lifecycle management, execution control, approval gates, artifact tracking |
| **Enforced Budget** | Milestone-based (M1: DB schema + submit/status/worker-once loop) |
| **Snapshot Reference** | None |
| **Created At** | 2026-06-02 |
| **Approved At** | Pending |
| **Traceability** | Source: `docs/delivery/01_initiatives/draft/PRE_INIT_agent_runner_daemon_db_job_management.md` → This pre-init promotion artifact (consolidated and self-contained) |

## Objective

Enhance Agent Runner to support daemon/worker mode with persistent database-backed job management, allowing long-running workflows to execute asynchronously without blocking OpenClaw or other orchestration clients. This decouples human-facing job submission and inspection from workflow execution, reducing LLM calls and improving system stability for both direct CLI usage and OpenClaw integration.

## Problem Statement

The current Agent Runner CLI works well when the runner owns the workflow directly. However, when OpenClaw is used as an external orchestrator:

1. Long-running commands block the OpenClaw session.
2. Background process handling inside OpenClaw is unreliable or session-bound.
3. Subagent-based monitoring causes excessive unnecessary LLM calls.
4. Job state is not cleanly persisted outside the active execution process.
5. Human approval gates and failure recovery are harder to manage if state only exists in the active process.
6. The system needs a stable command contract allowing any controller (OpenClaw or future UI) to manage jobs without owning execution.

## Expected Outcomes

### Business

- Reduced blocking of OpenClaw sessions during long-running workflows
- Preparation for Control Plane UI and API service integration
- Clearer separation between orchestration and execution responsibilities
- Foundation for future enterprise integration and audit compliance

### Technical

- Persistent, queryable job state in a database
- Non-blocking submit/status/inspect operations
- Safe concurrent job claiming and execution using DB transactions
- Clear approval/retry/cancel workflow support
- Artifact and event audit trails for all jobs
- Reduced LLM call overhead by eliminating subagent monitoring

### User

- OpenClaw users can submit jobs and inspect progress without session blocking
- Clear job IDs and status feedback for long-running workflows
- Ability to approve, reject, retry, or cancel jobs with recorded audit trails
- Direct CLI users retain existing execution path while gaining access to async options

## Scope

### Included

- Database schema for job lifecycle, events, and artifacts
- CLI commands: `submit`, `status`, `logs`, `artifact`, `approve`, `reject`, `retry`, `cancel`
- Worker daemon loop with job claiming and execution
- Integration with existing Agent Runner workflow execution engine
- Status model with defined transitions (QUEUED, CLAIMED, RUNNING, WAITING_FOR_HUMAN_APPROVAL, WAITING_FOR_HUMAN_INTERVENTION, READY_TO_RESUME, COMPLETED, FAILED, CANCEL_REQUESTED, CANCELLED)
- Human approval gates and state-changing operations
- Artifact registration and event appending
- OpenClaw usage guidelines and instruction document

### Excluded

- Full Control Plane UI rebuild
- Replacement of existing workflow step logic
- Distributed multi-worker scaling (unless current code supports it easily)
- Complex scheduling logic beyond FIFO job queue
- Advanced observability dashboards
- Rewriting coder provider integrations
- OpenClaw subagent orchestration
- Moving all UKBE artifact features into this initiative
- Automatic recovery of crashed workers (initial version uses conservative resume strategy)

## Constraints

- First version should be practical, local-first, and stable
- Resume behavior conservative for v1: manual recovery or explicit retry required after worker crash
- Database must support PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED` pattern for job claiming
- Must preserve existing direct execution path (`agent-runner run`)
- Existing workflow execution engine should not be rewritten; daemon must wrap it

## Dependencies

| Dependency | Owner | Status | Notes |
|---|---|---|---|
| PostgreSQL or compatible DB | Existing project DB | Assumed available | Used for job state and audit trail |
| Existing Agent Runner workflow engine | Current codebase | In use | Daemon wraps, does not replace |
| Initiative schema/structure | UKBE delivery framework | Defined | Pre-init follows template |

## Success Criteria

1. `agent-runner submit --initiative INIT-xxx` creates a DB-backed queued job and returns immediately with a job ID
2. `agent-runner worker --once` can claim and execute a queued job through at least one existing workflow path
3. Job status can be inspected via `agent-runner status --job-id <id>` without triggering execution
4. Logs and events can be inspected via `agent-runner logs --job-id <id>` without triggering LLM calls
5. Artifacts can be registered and listed by job via `agent-runner artifact --job-id <id>`
6. Failed jobs persist error details in job status and event log
7. Approval-gated jobs pause at `WAITING_FOR_HUMAN_APPROVAL` and resume after `agent-runner approve`
8. Cancel and retry commands exist with safe state transitions
9. OpenClaw can safely use the CLI as a control interface without running long workflows directly
10. Job claiming prevents duplicate execution using database transaction locking

## CLI Contract

The daemon mode exposes the following command interface:

### submit
```bash
agent-runner submit --initiative <initiative_id_or_file>
```
Creates a new job record in DB, stores initiative reference, sets status to `QUEUED`, returns immediately with job ID.

Example output:
```json
{
  "job_id": "job_20260602_0001",
  "status": "QUEUED",
  "initiative": "INIT-20260602-01"
}
```

### worker
```bash
agent-runner worker [--once] [--poll-interval N] [--provider <provider>] [--max-jobs N]
```
Starts a daemon that polls for queued jobs, claims one safely using DB transactions, executes workflow steps, persists state/logs/artifacts, and stops job execution at approval gates. `--once` mode claims and executes exactly one job then exits.

### status
```bash
agent-runner status --job-id <job_id>
agent-runner status --latest
```
Inspects job status without triggering execution or LLM calls.

Example output:
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

### logs
```bash
agent-runner logs --job-id <job_id> [--lines N]
agent-runner logs --latest [--lines N]
```
Shows recent job logs. Read-only, does not trigger LLM calls or execution.

### artifact
```bash
agent-runner artifact --job-id <job_id> [--step <step_name>]
agent-runner artifact --job-id <job_id> --step latest
```
Returns artifact path, metadata, and optionally content preview. Does not modify job state.

### approve
```bash
agent-runner approve --job-id <job_id>
```
Valid only when job is waiting for human approval. Records approval event, moves job to `READY_TO_RESUME`, worker resumes on next pickup.

### reject
```bash
agent-runner reject --job-id <job_id> --reason "<reason>"
```
Records human rejection reason, moves job to retry or intervention state depending on workflow policy.

### retry
```bash
agent-runner retry --job-id <job_id> [--step <step_name>]
```
Requeues a failed or waiting job, optionally retrying from a specific allowed step. Records retry event.

### cancel
```bash
agent-runner cancel --job-id <job_id>
```
Marks job as `CANCEL_REQUESTED` or `CANCELLED`. Worker stops safely at the next checkpoint.

## Job Status Model

The following status transitions define the job lifecycle:

**Core Statuses:**
- `QUEUED` - Job submitted, waiting for worker to claim
- `CLAIMED` - Worker claimed job, preparing to run
- `RUNNING` - Workflow steps in progress
- `WAITING_FOR_HUMAN_APPROVAL` - Job paused at approval gate, requires human decision
- `WAITING_FOR_HUMAN_INTERVENTION` - Job paused for human input (e.g., rejection/scope changes)
- `READY_TO_RESUME` - Job approved, ready for worker to continue
- `COMPLETED` - Job finished successfully
- `FAILED` - Job failed with error; error details persisted in job status and event log
- `CANCEL_REQUESTED` - Cancellation requested by user or system
- `CANCELLED` - Cancellation completed

**Optional Future Statuses:**
- `PAUSED` - Temporarily suspended (not scheduled in v1)
- `BLOCKED` - Waiting for external dependency
- `RETRY_SCHEDULED` - Retry scheduled for later execution
- `STALE` - Job abandoned after worker crash without recovery
- `ORPHANED` - No assigned worker

**Status Transition Rules:**
```
QUEUED → CLAIMED → RUNNING → COMPLETED
                           → FAILED
                           → WAITING_FOR_HUMAN_APPROVAL
                           → WAITING_FOR_HUMAN_INTERVENTION
                           → CANCEL_REQUESTED

WAITING_FOR_HUMAN_APPROVAL → READY_TO_RESUME → RUNNING
WAITING_FOR_HUMAN_INTERVENTION → READY_TO_RESUME → RUNNING

READY_TO_RESUME → RUNNING → (same as above)

*_REQUESTED → CANCELLED (at safe checkpoint)
```

## Database Schema

### Table: `agent_runner_jobs`
Primary job lifecycle table.

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
```

### Table: `agent_runner_job_events`
Append-only audit trail for all job state changes and human actions.

```sql
id UUID PRIMARY KEY,
job_id UUID NOT NULL REFERENCES agent_runner_jobs(id),
event_type TEXT NOT NULL,
step_name TEXT NULL,
message TEXT NULL,
payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

**Event Types:**
- `JOB_SUBMITTED` - Job created
- `JOB_CLAIMED` - Worker claimed job
- `JOB_STARTED` - Workflow execution started
- `STEP_STARTED` - Specific workflow step began
- `STEP_COMPLETED` - Workflow step finished
- `STEP_FAILED` - Workflow step failed
- `HUMAN_APPROVAL_REQUIRED` - Job paused for approval
- `HUMAN_APPROVED` - Human approved job
- `HUMAN_REJECTED` - Human rejected job
- `JOB_RETRIED` - Job requeued for retry
- `JOB_CANCEL_REQUESTED` - Cancellation initiated
- `JOB_CANCELLED` - Cancellation completed
- `JOB_COMPLETED` - Job finished successfully
- `JOB_FAILED` - Job terminated with error

### Table: `agent_runner_job_artifacts`
Tracks generated files and important workflow outputs.

```sql
id UUID PRIMARY KEY,
job_id UUID NOT NULL REFERENCES agent_runner_jobs(id),
step_name TEXT NULL,
artifact_type TEXT NOT NULL,
artifact_path TEXT NOT NULL,
artifact_meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
checksum TEXT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

## Worker Claiming Strategy

Job claiming uses PostgreSQL transaction-based locking to prevent multiple workers from executing the same job:

```sql
SELECT id
FROM agent_runner_jobs
WHERE status IN ('QUEUED', 'READY_TO_RESUME')
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

Then immediately update:

```sql
UPDATE agent_runner_jobs
SET status = 'CLAIMED',
    claimed_by = :worker_id,
    claimed_at = now(),
    updated_at = now()
WHERE id = :job_id;
```

This FIFO claiming pattern ensures no duplicate execution and allows safe concurrent workers.

## Testing Strategy

### Unit Tests
- Job creation and metadata
- Status transition validation
- Job claiming logic (no duplicates)
- Event appending (append-only)
- Artifact registration
- Approval, retry, and cancellation transitions

### Integration Tests
1. `submit` → `worker --once` → successful completion
2. `submit` → `status` shows QUEUED before execution
3. Worker claims → `status` shows RUNNING/current step
4. Worker failure → job marked FAILED with error event
5. Human approval gate → `approve` → job resumes
6. `cancel` on QUEUED job → job marked CANCELLED
7. `retry` on FAILED job → job requeued

### No-LLM Tests
Use fake coder providers or mock workflow steps to test job management without external LLM calls.

### Acceptance Tests
- `submit` returns JSON job ID immediately
- `worker --once` claims and executes a queued job through at least one existing workflow path
- Current step is visible in `status` output
- Logs and events are visible after execution
- Failed workflow does not leave job in ambiguous running state

## Implementation Slices

**Slice 1: DB Schema and Repository Layer**
- Migrations for `agent_runner_jobs`, `agent_runner_job_events`, `agent_runner_job_artifacts`
- Repository methods: create job, get job, claim next job, update status, append event, register artifact
- Tests verify create, fetch, update, claiming, and append-only events

**Slice 2: CLI Commands**
- Implement: `submit`, `status`, `logs`, `artifact`, `approve`, `reject`, `retry`, `cancel`
- Each command returns deterministic JSON or readable text
- Submit returns immediately; read-only commands do not trigger execution

**Slice 3: Worker Loop**
- `agent-runner worker` with `--once`, `--poll-interval`, `--provider`, `--max-jobs` options
- Worker ID generation (hostname + PID or UUID)
- Job claim loop with FIFO ordering and safe transaction handling
- Graceful handling of no-available-jobs case

**Slice 4: Existing Workflow Integration**
- Worker calls existing workflow execution engine with job context
- Current step persisted during execution
- Workflow outputs registered as artifacts
- Failures persisted to job status and event log

**Slice 5: Human Gate Support**
- Worker can set job to `WAITING_FOR_HUMAN_APPROVAL`
- `approve` command moves job to `READY_TO_RESUME`
- `reject` command records reason and transitions appropriately

**Slice 6: Cancellation and Retry**
- `cancel` command implementation
- Cancellation checker at worker checkpoints
- `retry` command with event tracking

**Slice 7: OpenClaw Command Guide**
- Short instruction document for OpenClaw with allowed/forbidden behaviors
- Example usage patterns

## References

- Source draft: `docs/delivery/01_initiatives/draft/PRE_INIT_agent_runner_daemon_db_job_management.md`

## Notes

- **Assumed initiative structure**: Workflow uses existing Agent Runner steps (plan, init, implementation, review, validation, etc.)
- **Job ID format**: `job_YYYYMMDD_NNNN` with FIFO claiming via PostgreSQL `ORDER BY created_at ASC FOR UPDATE SKIP LOCKED`
- **Worker ID**: Generated at daemon startup (hostname + PID or UUID)
- **Provider support**: Worker accepts `--provider` flag to route jobs to specific coder tools (Claude, Codex, Qwen, etc.)
- **Event audit trail**: All state changes and human actions recorded in `agent_runner_job_events` for compliance and debugging
- **Artifact registry**: Generated files and workflow outputs registered in `agent_runner_job_artifacts` with checksum and metadata
- **OpenClaw instruction**: OpenClaw should be explicitly instructed to use `submit` instead of running long workflows directly; forbidden behaviors include continuous polling, subagent monitoring, and direct coder tool invocation for long-running flows
- **Resume strategy for v1**: Conservative approach—do not automatically resume partially running coder steps unless deterministic checkpoints exist; resume only from latest completed step or explicit retry step
- **Source draft file**: `docs/delivery/01_initiatives/draft/PRE_INIT_agent_runner_daemon_db_job_management.md`
- **Generated by**: `pre_init`
- **Generated at**: `2026-06-02T00:00:00Z`

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Sponsor | | | Pending |
| Technical Lead | | | Pending |
