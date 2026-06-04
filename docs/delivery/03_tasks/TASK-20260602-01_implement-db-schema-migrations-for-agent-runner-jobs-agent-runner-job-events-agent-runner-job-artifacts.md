# Implement DB schema migrations for agent_runner_jobs, agent_runner_job_events, agent_runner_job_artifacts

## Metadata

| Field | Value |
|---|---|
| **Doc Type** | 03_task |
| **Template Version** | v1 |
| **Artifact Version** | v1 |
| **Task ID** | `TASK-20260602-01` |
| **Task Graph ID** | `TASK-GRAPH-20260602-PLAN-20260602-01` |
| **Task Graph Path** | `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260602-PLAN-20260602-01.md` |
| **Task Graph Version** | v1 |
| **Plan ID** | `PLAN-20260602-01` |
| **Plan Path** | `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |
| **Plan Version** | v1 |
| **Initiative ID** | `INIT-20260602-01` |
| **Initiative Path** | `docs/delivery/01_initiatives/INIT-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |
| **Initiative Version** | v1 |
| **Title** | Implement DB schema migrations for agent_runner_jobs, agent_runner_job_events, agent_runner_job_artifacts |
| **Status** | Approved |
| **Supersedes** | — |
| **Snapshot Reference** | — |
| **Contract Reference** | — |
| **Priority** | P0 |
| **Assigned To** | @kengkoon.chua |
| **Created At** | 2026-06-02 |
| **Due At** | — |
| **Source Task Graph ID** | `TASK-GRAPH-20260602-PLAN-20260602-01` |
| **Source Task Node ID** | `TASK-20260602-01` |
| **Review File Path** | `docs/delivery/04_reviews/REVIEW-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |

## Objective

Design and implement three PostgreSQL migration files that create the foundational tables for persistent job state management: `agent_runner_jobs`, `agent_runner_job_events`, and `agent_runner_job_artifacts`. All tables must include appropriate columns, indices, and constraints — including support for PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED` concurrent claiming. Migrations must be fully reversible (up and down scripts). Transaction safety and concurrent claiming semantics must be validated at the schema level.

## Inputs

| Type | Reference |
|---|---|
| Source plan | `PLAN-20260602-01` at `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |
| Source task graph | `TASK-GRAPH-20260602-PLAN-20260602-01` at `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260602-PLAN-20260602-01.md` |
| Dependencies | None (foundational task — no dependent task docs to read) |
| Required data/APIs | Existing project PostgreSQL database; database migration framework in use (e.g., Alembic or custom migration runner) |

## Outputs

| Artifact | Path | Description |
|---|---|---|
| Migration file: agent_runner_jobs | `agent_runner_v2/db/migrations/<auto-numbered>_create_agent_runner_jobs.py` | Migration creating the `agent_runner_jobs` table with columns for job metadata, status, current_step, created_at, updated_at, claimed_by, and constraints/indices for concurrent claiming |
| Migration file: agent_runner_job_events | `agent_runner_v2/db/migrations/<auto-numbered>_create_agent_runner_job_events.py` | Migration creating the `agent_runner_job_events` append-only audit trail table with columns for job_id (FK), event_type, details, created_at, and appropriate indices |
| Migration file: agent_runner_job_artifacts | `agent_runner_v2/db/migrations/<auto-numbered>_create_agent_runner_job_artifacts.py` | Migration creating the `agent_runner_job_artifacts` table with columns for job_id (FK), artifact_type, path, checksum, metadata, created_at, and appropriate indices |
| Schema specification | Inline migration comments or separate spec document | Documentation clarifying column purposes, constraint rationale, and transaction semantics for concurrent claiming support |

### Completion Evidence

- All three migrations apply cleanly against a fresh PostgreSQL database
- All three migrations rollback cleanly without errors
- `psql \d` output shows all three tables with expected columns, primary keys, foreign keys, unique constraints, and indices
- A concurrent test script using `SELECT ... FOR UPDATE SKIP LOCKED` against `agent_runner_jobs` demonstrates zero race conditions with multiple workers
- Schema specification (inline comments or separate doc) explains column purposes and `FOR UPDATE SKIP LOCKED` support

## Implementation Details

### Technical Notes

- PostgreSQL is the target database for all migrations
- Migration framework must support auto-numbered migrations with reversible up/down scripts
- `agent_runner_jobs` is the primary table — it must support the FIFO claiming pattern: `ORDER BY created_at ASC FOR UPDATE SKIP LOCKED`
- `agent_runner_job_events` is append-only — no UPDATE or DELETE operations expected on this table
- `agent_runner_job_artifacts` registers workflow outputs with checksums and metadata for later inspection

### API/Contract Notes

- This task defines the database schema contract that `TASK-20260602-02` (repository layer) will depend on
- The repository layer will implement: `create_job`, `fetch_job`, `claim_next_job`, `update_job_status`, `append_event`, `register_artifact` — all mapped to these three tables
- Job ID format per plan: `job_YYYYMMDD_NNNN` with auto-increment

### Data/Schema Notes

**`agent_runner_jobs` required columns and constraints:**
- `id` (primary key, auto-increment or serial)
- `job_id` (unique, format: `job_YYYYMMDD_NNNN`)
- `status` (enum or text: QUEUED, CLAIMED, RUNNING, COMPLETED, FAILED, WAITING_FOR_HUMAN_APPROVAL, READY_TO_RESUME, REJECTED, CANCELLED, CANCEL_REQUESTED)
- `current_step` (nullable text — tracks which workflow step is executing)
- `initiative_id` or `initiative_ref` (text — which initiative spawned this job)
- `claimed_by` (nullable text — worker ID that claimed this job)
- `claimed_at` (nullable timestamp — when the job was claimed)
- `created_at` (timestamp with time zone)
- `updated_at` (timestamp with time zone)
- Indices: `(status, created_at)` for FIFO claiming; `(job_id)` for lookups; `(claimed_by)` for worker introspection
- Constraint: `job_id` must be unique

**`agent_runner_job_events` required columns and constraints:**
- `id` (primary key, auto-increment)
- `job_id` (foreign key → `agent_runner_jobs.job_id`, indexed)
- `event_type` (text — e.g., CREATED, CLAIMED, STATUS_CHANGED, HUMAN_APPROVED, HUMAN_REJECTED, CANCELLED, ERROR)
- `details` (JSONB — structured event payload, nullable)
- `created_at` (timestamp with time zone)
- Indices: `(job_id, created_at)` for chronological event retrieval per job

**`agent_runner_job_artifacts` required columns and constraints:**
- `id` (primary key, auto-increment)
- `job_id` (foreign key → `agent_runner_jobs.job_id`, indexed)
- `artifact_type` (text — e.g., PLAN_FILE, TASK_GRAPH_FILE, REVIEW_FILE, etc.)
- `path` (text — filesystem path relative to project root)
- `checksum` (nullable text — file hash for integrity verification)
- `metadata` (JSONB — additional artifact metadata, nullable)
- `created_at` (timestamp with time zone)
- Indices: `(job_id, artifact_type)` for artifact lookup by type

**Allowed/Forbidden operations at schema level:**
- ALLOWED: INSERT, SELECT on all tables; UPDATE on `agent_runner_jobs` (status transitions); UPDATE on `agent_runner_job_artifacts` (checksum updates after artifact finalization)
- FORBIDDEN: UPDATE or DELETE on `agent_runner_job_events` (append-only audit trail); DELETE on `agent_runner_jobs` without cascading deletes for events and artifacts (referential integrity must be preserved or cascade explicitly)

## Execution Steps

1. **Create migration for `agent_runner_jobs` table**
   - Define all required columns (id, job_id, status, current_step, initiative_ref, claimed_by, claimed_at, created_at, updated_at)
   - Add primary key on `id`, unique constraint on `job_id`
   - Create indices: `(status, created_at)` for FIFO claiming, `(job_id)` for lookups, `(claimed_by)` for worker introspection
   - Write reversible down script that drops the table and all indices
   - Add inline comments documenting column purposes and `FOR UPDATE SKIP LOCKED` support

2. **Create migration for `agent_runner_job_events` table**
   - Define all required columns (id, job_id FK, event_type, details JSONB, created_at)
   - Add foreign key constraint to `agent_runner_jobs.job_id`
   - Create index `(job_id, created_at)` for chronological event retrieval
   - Write reversible down script that drops the table and indices
   - Add inline comments documenting append-only semantics

3. **Create migration for `agent_runner_job_artifacts` table**
   - Define all required columns (id, job_id FK, artifact_type, path, checksum, metadata JSONB, created_at)
   - Add foreign key constraint to `agent_runner_jobs.job_id`
   - Create index `(job_id, artifact_type)` for artifact lookup by type
   - Write reversible down script that drops the table and indices

4. **Validate migrations apply and rollback cleanly**
   - Run all three migrations up against a fresh test database
   - Verify all three tables exist with correct columns, constraints, and indices
   - Run all three migrations down — verify no errors and all tables dropped
   - Re-run migrations up to confirm idempotent behavior

5. **Verify concurrent claiming support**
   - Execute a test query: `SELECT * FROM agent_runner_jobs WHERE status = 'QUEUED' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED` against sample data
   - Confirm the query executes without errors and returns expected rows
   - Confirm indices support the query pattern (use `EXPLAIN ANALYZE` to verify index scan)

6. **Document schema specification**
   - Ensure inline comments in all three migration files explain column purposes, constraint rationale, and transaction semantics
   - Alternatively, create a separate schema spec document at `agent_runner_v2/db/SCHEMA_SPEC.md` if inline comments are insufficient

## Validation Criteria

### Acceptance Checks

1. All three migration files exist in `agent_runner_v2/db/migrations/` with auto-numbered filenames
2. `agent_runner_jobs` table has all required columns, primary key, unique constraint on `job_id`, and indices on `(status, created_at)`, `(job_id)`, `(claimed_by)`
3. `agent_runner_job_events` table has all required columns, foreign key to `agent_runner_jobs.job_id`, and index on `(job_id, created_at)`
4. `agent_runner_job_artifacts` table has all required columns, foreign key to `agent_runner_jobs.job_id`, and index on `(job_id, artifact_type)`
5. All three migrations apply cleanly and rollback cleanly without errors
6. `FOR UPDATE SKIP LOCKED` query executes successfully against `agent_runner_jobs` with appropriate index usage confirmed via `EXPLAIN ANALYZE`
7. Inline comments or schema spec document explains column purposes and transaction semantics for concurrent claiming

### Test Cases

| Test | Command / Method | Expected Result |
|---|---|---|
| Migration apply | Run migration runner up against fresh test DB | Zero errors; all three tables created |
| Migration rollback | Run migration runner down | Zero errors; all three tables dropped |
| Schema inspection | `psql \d agent_runner_jobs`, `\d agent_runner_job_events`, `\d agent_runner_job_artifacts` | Columns, constraints, and indices match specification |
| Concurrent claiming | Two concurrent transactions execute `SELECT ... FOR UPDATE SKIP LOCKED` | Each transaction claims distinct rows; no blocking or deadlocks |
| Index verification | `EXPLAIN ANALYZE SELECT ... WHERE status = 'QUEUED' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED` | Query plan shows index scan on `(status, created_at)` |

### Review Requirements

- [ ] All three migration files present with correct auto-numbered filenames
- [ ] Primary keys, foreign keys, and unique constraints correctly defined
- [ ] Indices created for claimed query patterns (job_id, status, created_at, claimed_by)
- [ ] Migrations are reversible (up and down scripts tested)
- [ ] Schema supports `FOR UPDATE SKIP LOCKED` without errors
- [ ] Inline comments or schema spec document clarifies column purposes and transaction semantics

## Risks / Blockers

| Risk/Blocker | Impact | Mitigation |
|---|---|---|
| Migration framework unknown or incompatible | Cannot create auto-numbered reversible migrations | Confirm existing migration framework (Alembic, custom) before starting; adapt migration files accordingly |
| Database permissions insufficient for table creation | Migrations fail to apply | Ensure test database user has CREATE TABLE, CREATE INDEX permissions |
| `FOR UPDATE SKIP LOCKED` not supported (non-PostgreSQL) | Concurrent claiming pattern fails | Confirm PostgreSQL is the target database; this pattern is PostgreSQL-specific |

## References

- Task Graph: `TASK-GRAPH-20260602-PLAN-20260602-01` at `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260602-PLAN-20260602-01.md`
- Plan: `PLAN-20260602-01` at `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md`
- Initiative: `INIT-20260602-01`
- Review: `docs/delivery/04_reviews/REVIEW-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md`
- PostgreSQL `SKIP LOCKED` documentation: https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE

## Notes

- This is the foundational task — no dependent task docs exist to read
- Job ID format per plan: `job_YYYYMMDD_NNNN` with auto-increment
- Worker ID format: hostname + PID or UUID (generated at daemon startup)
- All state-changing operations in the repository layer (TASK-02) will be wrapped in transactions — schema must support this
- v1 conservative approach: no automatic resume after worker crash — manual recovery or explicit retry required
- Status model for `agent_runner_jobs.status`: QUEUED, CLAIMED, RUNNING, WAITING_FOR_HUMAN_APPROVAL, READY_TO_RESUME, COMPLETED, FAILED, REJECTED, CANCELLED, CANCEL_REQUESTED
- `agent_runner_job_events` is append-only — do not add UPDATE or DELETE operations at the repository layer
