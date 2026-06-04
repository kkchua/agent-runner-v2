# Implement DB schema migrations for agent_runner_jobs, agent_runner_job_events, agent_runner_job_artifacts

## Metadata

| Field | Value |
|---|---|
| **Doc Type** | 04_implementation_plan |
| **Template Version** | v1 |
| **Artifact Version** | v1 |
| **Implementation Plan ID** | `IMPL-20260602-01` |
| **Plan ID** | `PLAN-20260602-01` |
| **Plan Path** | `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |
| **Plan Version** | v1 |
| **Task Graph ID** | `TASK-GRAPH-20260602-PLAN-20260602-01` |
| **Task Graph Path** | `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260602-PLAN-20260602-01.md` |
| **Task Graph Version** | v1 |
| **Task ID** | `TASK-20260602-01` |
| **Task Path** | `docs/delivery/03_tasks/TASK-20260602-01_implement-db-schema-migrations-for-agent-runner-jobs-agent-runner-job-events-agent-runner-job-artifacts.md` |
| **Task Version** | v1 |
| **Title** | Implement DB schema migrations for agent_runner_jobs, agent_runner_job_events, agent_runner_job_artifacts |
| **Status** | draft |
| **Supersedes** | — |
| **Snapshot Reference** | — |
| **Contract Reference** | — |
| **Created At** | 2026-06-02 |
| **Author** | @kengkoon.chua |
| **Review File Path** | `docs/delivery/04_reviews/REVIEW-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |

## Objective

Translate the task document's schema requirements into three concrete PostgreSQL migration files with reversible up/down scripts, inline documentation, and validation evidence. The approach covers:

1. **Migration framework selection**: Inspect the project to confirm whether Alembic, a custom migration runner, or raw SQL migrations are in use. If no framework exists, create a lightweight Python-based migration runner in `agent_runner_v2/db/migrate.py` that executes numbered migration modules with `up()` and `down()` entry points.
2. **Schema definition**: Define all three tables with exact columns, types, constraints, and indices as specified in the task document — no field omissions, no type changes.
3. **Concurrent claiming support**: Ensure the `agent_runner_jobs` schema and indices support `SELECT ... FOR UPDATE SKIP LOCKED` with index-backed execution.
4. **Validation evidence**: Produce `psql \d` output, migration apply/rollback logs, and a concurrent claiming test script as completion evidence.

## Inputs

| Type | Reference |
|---|---|
| Task spec | `docs/delivery/03_tasks/TASK-20260602-01_implement-db-schema-migrations-for-agent-runner-jobs-agent-runner-job-events-agent-runner-job-artifacts.md` |
| Design docs | `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` (status model, job ID format) |
| Existing code | `agent_runner_v2/` — inspect for existing `db/` directory, migration framework, SQLAlchemy models |
| External APIs | PostgreSQL database (confirmed target per task); database connection string via environment variable |

## Outputs

| Artifact | Path | Description |
|---|---|---|
| Migration: agent_runner_jobs | `agent_runner_v2/db/migrations/001_create_agent_runner_jobs.py` | Migration creating the `agent_runner_jobs` table with all required columns, constraints, and indices |
| Migration: agent_runner_job_events | `agent_runner_v2/db/migrations/002_create_agent_runner_job_events.py` | Migration creating the `agent_runner_job_events` append-only audit trail table |
| Migration: agent_runner_job_artifacts | `agent_runner_v2/db/migrations/003_create_agent_runner_job_artifacts.py` | Migration creating the `agent_runner_job_artifacts` table with FK to agent_runner_jobs |
| Migration runner (if needed) | `agent_runner_v2/db/migrate.py` | Lightweight migration runner executing numbered `up()`/`down()` modules |
| Schema spec (optional) | `agent_runner_v2/db/SCHEMA_SPEC.md` | Column purposes, constraint rationale, transaction semantics — only if inline comments are insufficient |

## Scope Clarification

### Included

- Three migration files creating `agent_runner_jobs`, `agent_runner_job_events`, `agent_runner_job_artifacts` tables
- All columns, types, constraints, and indices exactly as specified in the task document
- Reversible up/down scripts for each migration
- Inline comments documenting column purposes, constraint rationale, and `FOR UPDATE SKIP LOCKED` support
- Migration apply/rollback validation against a fresh PostgreSQL database
- Concurrent claiming test script demonstrating `SELECT ... FOR UPDATE SKIP LOCKED` with zero race conditions
- Migration runner infrastructure if no framework exists

### Excluded

- Repository layer methods (`create_job`, `claim_next_job`, etc.) — deferred to TASK-20260602-02
- CLI commands (`submit`, `status`, etc.) — deferred to TASK-20260602-03 through TASK-20260602-05
- Worker daemon loop — deferred to TASK-20260602-06
- ORM model definitions (SQLAlchemy or similar) — schema-only at this stage; ORM layer deferred to TASK-20260602-02
- Automatic worker crash recovery — excluded per plan (v1 conservative approach)
- Database connection pool configuration — beyond schema scope

## File Plan

```
agent_runner_v2/
├── db/
│   ├── [NEW] __init__.py                    # Package init for db module
│   ├── [NEW] migrate.py                     # Lightweight migration runner (only if no framework exists — inspect first)
│   └── migrations/
│       ├── [NEW] __init__.py                # Package init for migrations
│       ├── [NEW] 001_create_agent_runner_jobs.py        # Migration: agent_runner_jobs table
│       ├── [NEW] 002_create_agent_runner_job_events.py  # Migration: agent_runner_job_events table
│       └── [NEW] 003_create_agent_runner_job_artifacts.py # Migration: agent_runner_job_artifacts table

tests/
├── [NEW] test_migrations.py                 # Migration apply/rollback validation
└── [NEW] test_concurrent_claiming.py        # Concurrent FOR UPDATE SKIP LOCKED test

docs/delivery/
└── 04_implementation_plans/
    └── [NEW] IMPL-20260602-01_...md         # This implementation plan
```

## Module Responsibilities

| Module | Responsibility | Key Functions/Classes |
|---|---|---|
| `agent_runner_v2/db/migrate.py` | Migration runner: discovers numbered migrations, executes `up()` or `down()` in order, tracks applied migrations | `run_up()`, `run_down()`, `get_applied_migrations()` |
| `agent_runner_v2/db/migrations/001_create_agent_runner_jobs.py` | Creates `agent_runner_jobs` table with all columns, constraints, indices; documents FIFO claiming support | `up(conn)`, `down(conn)` |
| `agent_runner_v2/db/migrations/002_create_agent_runner_job_events.py` | Creates `agent_runner_job_events` table with FK to `agent_runner_jobs`, append-only documentation | `up(conn)`, `down(conn)` |
| `agent_runner_v2/db/migrations/003_create_agent_runner_job_artifacts.py` | Creates `agent_runner_job_artifacts` table with FK to `agent_runner_jobs`, artifact lookup index | `up(conn)`, `down(conn)` |
| `tests/test_migrations.py` | Validates migrations apply/rollback cleanly, schema matches specification via `psql \d` | `test_migrations_apply()`, `test_migrations_rollback()`, `test_schema_inspection()` |
| `tests/test_concurrent_claiming.py` | Validates `FOR UPDATE SKIP LOCKED` with concurrent workers claiming distinct rows | `test_concurrent_skip_locked()` |

## Reuse Strategy

| Existing Component | How It's Reused | Adaptation Needed |
|---|---|---|
| PostgreSQL database | Confirmed target database per task document; connection string via environment variable | None — verify connectivity before running migrations |
| Existing Python environment | Migrations written as Python modules with `up()`/`down()` entry points | Inspect whether `psycopg2` or `asyncpg` is available; install if needed |
| `pyproject.toml` | Add `psycopg2-binary` as dependency for migration execution | Add to `[project.dependencies]` or as optional dev dependency for test execution |

## Data Flow

### Migration Execution Flow

```
Migration runner invoked → Connect to PostgreSQL (via DATABASE_URL env var) → 
  Discover numbered migrations in `agent_runner_v2/db/migrations/` → 
  Filter to unapplied migrations → 
  Execute each migration's up(conn) in ascending order within a transaction → 
  Commit → Record applied migration → Exit
```

### Concurrent Claiming Verification Flow

```
Two concurrent transactions open → 
  Transaction A: SELECT * FROM agent_runner_jobs WHERE status = 'QUEUED' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED → 
  Transaction B: SELECT * FROM agent_runner_jobs WHERE status = 'QUEUED' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED → 
  Verify: each transaction claims distinct rows (no overlap) → 
  Verify: no blocking or deadlocks → 
  Verify: EXPLAIN ANALYZE shows index scan on (status, created_at) composite index
```

### Schema Contract for Downstream Tasks

[TASK-DERIVED] The following schema contract is derived directly from the task document and must be preserved verbatim for TASK-20260602-02 (repository layer):

**`agent_runner_jobs` columns:**
- `id` — SERIAL (primary key, auto-increment)
- `job_id` — TEXT (UNIQUE, format: `job_YYYYMMDD_NNNN` per plan)
- `status` — TEXT (enum values: QUEUED, CLAIMED, RUNNING, COMPLETED, FAILED, WAITING_FOR_HUMAN_APPROVAL, READY_TO_RESUME, REJECTED, CANCELLED, CANCEL_REQUESTED)
- `current_step` — TEXT (nullable — tracks which workflow step is executing)
- `initiative_ref` — TEXT (which initiative spawned this job)
- `claimed_by` — TEXT (nullable — worker ID that claimed this job)
- `claimed_at` — TIMESTAMP WITH TIME ZONE (nullable — when the job was claimed)
- `created_at` — TIMESTAMP WITH TIME ZONE
- `updated_at` — TIMESTAMP WITH TIME ZONE

[TASK-DERIVED] **`agent_runner_jobs` indices:**
- `(status, created_at)` — composite index for FIFO claiming: `ORDER BY created_at ASC FOR UPDATE SKIP LOCKED`
- `(job_id)` — unique index for lookups (enforced via UNIQUE constraint)
- `(claimed_by)` — index for worker introspection

[TASK-DERIVED] **`agent_runner_job_events` columns:**
- `id` — SERIAL (primary key, auto-increment)
- `job_id` — TEXT (foreign key → `agent_runner_jobs.job_id`, indexed)
- `event_type` — TEXT (e.g., CREATED, CLAIMED, STATUS_CHANGED, HUMAN_APPROVED, HUMAN_REJECTED, CANCELLED, ERROR)
- `details` — JSONB (nullable — structured event payload)
- `created_at` — TIMESTAMP WITH TIME ZONE

[TASK-DERIVED] **`agent_runner_job_events` indices:**
- `(job_id, created_at)` — composite index for chronological event retrieval per job

[TASK-DERIVED] **`agent_runner_job_artifacts` columns:**
- `id` — SERIAL (primary key, auto-increment)
- `job_id` — TEXT (foreign key → `agent_runner_jobs.job_id`, indexed)
- `artifact_type` — TEXT (e.g., PLAN_FILE, TASK_GRAPH_FILE, REVIEW_FILE, etc.)
- `path` — TEXT (filesystem path relative to project root)
- `checksum` — TEXT (nullable — file hash for integrity verification)
- `metadata` — JSONB (nullable — additional artifact metadata)
- `created_at` — TIMESTAMP WITH TIME ZONE

[TASK-DERIVED] **`agent_runner_job_artifacts` indices:**
- `(job_id, artifact_type)` — composite index for artifact lookup by type

[TASK-DERIVED] **Allowed/Forbidden operations at schema level:**
- ALLOWED: INSERT, SELECT on all tables; UPDATE on `agent_runner_jobs` (status transitions); UPDATE on `agent_runner_job_artifacts` (checksum updates after artifact finalization)
- FORBIDDEN: UPDATE or DELETE on `agent_runner_job_events` (append-only audit trail); DELETE on `agent_runner_jobs` without cascading deletes for events and artifacts (referential integrity must be preserved or cascade explicitly)

## Test Plan

### Test Files

| Test File | Covers |
|---|---|
| `tests/test_migrations.py` | Migration apply, rollback, schema inspection |
| `tests/test_concurrent_claiming.py` | Concurrent `FOR UPDATE SKIP LOCKED` behavior, index verification |

### Test Cases

[TASK-DERIVED] Every test case from the task document's Validation Criteria must be covered:

| Case | Input | Expected |
|---|---|---|
| Migration apply | Run migration runner `up` against fresh test DB | Zero errors; all three tables created (`agent_runner_jobs`, `agent_runner_job_events`, `agent_runner_job_artifacts`) |
| Migration rollback | Run migration runner `down` | Zero errors; all three tables dropped; no orphaned objects |
| Schema inspection — agent_runner_jobs | `psql \d agent_runner_jobs` | All columns present (id, job_id, status, current_step, initiative_ref, claimed_by, claimed_at, created_at, updated_at); primary key on `id`; UNIQUE constraint on `job_id`; indices on `(status, created_at)`, `(job_id)`, `(claimed_by)` |
| Schema inspection — agent_runner_job_events | `psql \d agent_runner_job_events` | All columns present (id, job_id, event_type, details, created_at); foreign key to `agent_runner_jobs.job_id`; index on `(job_id, created_at)` |
| Schema inspection — agent_runner_job_artifacts | `psql \d agent_runner_job_artifacts` | All columns present (id, job_id, artifact_type, path, checksum, metadata, created_at); foreign key to `agent_runner_jobs.job_id`; index on `(job_id, artifact_type)` |
| Concurrent claiming | Two concurrent transactions execute `SELECT ... FOR UPDATE SKIP LOCKED` against sample QUEUED rows | Each transaction claims distinct rows; no blocking or deadlocks; zero race conditions |
| Index verification | `EXPLAIN ANALYZE SELECT * FROM agent_runner_jobs WHERE status = 'QUEUED' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED` | Query plan shows index scan on `(status, created_at)` composite index |

### Test Constraints

- Requires a running PostgreSQL database accessible via `DATABASE_URL` environment variable
- Test database should be isolated (use a dedicated test database or transaction-wrapped tests)
- `psycopg2-binary` must be installed for Python-to-PostgreSQL connectivity
- No existing tables should conflict — tests run against a fresh database or with DROP TABLE IF EXISTS in down scripts

## Implementation Evidence

- Migration apply log: capture stdout/stderr from `python -m agent_runner_v2.db.migrate up` against fresh DB
- Migration rollback log: capture stdout/stderr from `python -m agent_runner_v2.db.migrate down`
- `psql \d` output for all three tables saved as reference artifact
- `EXPLAIN ANALYZE` output showing index scan on `(status, created_at)` saved as reference
- Concurrent test script output showing distinct row claims per transaction

## Rollback Plan

### Trigger Conditions

- Migration fails to apply against production or staging database
- Schema inspection reveals missing columns, incorrect types, or absent indices
- Concurrent claiming test demonstrates race conditions or deadlocks
- Downstream repository layer (TASK-02) finds schema incompatible with repository method signatures

### Rollback Steps

1. Run migration runner `down` to reverse all three migrations in reverse order (003 → 002 → 001)
2. Verify all three tables are dropped via `psql \d` — no orphaned tables, indices, or constraints
3. If down script fails, manually execute `DROP TABLE IF EXISTS agent_runner_job_artifacts, agent_runner_job_events, agent_runner_jobs CASCADE;`
4. Confirm rollback with `psql \d` showing no remaining tables

### Rollback Validation

- `psql \d` returns no tables matching `agent_runner_job*`
- No orphaned indices or constraints remain
- Migration runner reports zero applied migrations after rollback

## Constraints

[TASK-DERIVED] PostgreSQL is the target database — all migrations use PostgreSQL-specific features (e.g., `FOR UPDATE SKIP LOCKED`, JSONB)
[TASK-DERIVED] Migration framework must support auto-numbered migrations with reversible up/down scripts
[TASK-DERIVED] `agent_runner_jobs` must support FIFO claiming pattern: `ORDER BY created_at ASC FOR UPDATE SKIP LOCKED`
[TASK-DERIVED] `agent_runner_job_events` is append-only — no UPDATE or DELETE operations expected
[TASK-DERIVED] Job ID format: `job_YYYYMMDD_NNNN` with auto-increment (enforced at application layer, not schema — schema enforces UNIQUE constraint only)
[TASK-DERIVED] All state-changing operations in the repository layer (TASK-02) will be wrapped in transactions — schema must support this
[TASK-DERIVED] v1 conservative approach: no automatic resume after worker crash — manual recovery or explicit retry required

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Migration framework unknown or incompatible with project | Medium | High | Inspect `agent_runner_v2/` for existing `db/` directory, Alembic config, or custom migration runner before starting; adapt migration files to match existing framework if found; create lightweight runner only if none exists |
| Database permissions insufficient for table creation | Low | Medium | Ensure test database user has CREATE TABLE, CREATE INDEX permissions; verify with a simple `CREATE TABLE` test before running full migrations |
| `psycopg2` or `asyncpg` not installed in project environment | Medium | Low | Add `psycopg2-binary` to `pyproject.toml` dependencies; install before migration execution |
| FK constraint failure if migrations applied out of order | Low | Medium | Migration runner must apply migrations in ascending numeric order; 001 (jobs) before 002/003 (events/artifacts with FKs) |
| `FOR UPDATE SKIP LOCKED` not supported (non-PostgreSQL) | Low | High | Confirm PostgreSQL is the target database; this pattern is PostgreSQL-specific — task document confirms PostgreSQL |
| Composite index `(status, created_at)` not used by query planner | Low | Medium | Verify with `EXPLAIN ANALYZE`; if index scan not used, check that `status` is the leading column in the WHERE clause and `created_at` is used in ORDER BY |

## Dependencies

| Dependency | Version / Source | Purpose |
|---|---|---|
| PostgreSQL | Confirmed target per task | Database for all three tables |
| `psycopg2` or `psycopg2-binary` | Install via pip | Python-to-PostgreSQL connectivity for migration runner |
| Python 3.11+ | Project requirement per `pyproject.toml` | Migration modules written in Python |

## Notes

- **Migration numbering**: Use 3-digit zero-padded numbers (001, 002, 003) for consistent ordering. If Alembic is discovered, switch to Alembic revision IDs instead.
- **Status enum**: Task document lists 10 status values. Consider PostgreSQL `CREATE TYPE` for strict enum enforcement, OR use TEXT with CHECK constraint for flexibility. INSPECT whether the project prefers native PostgreSQL enums or TEXT-based status columns before deciding. If unsure, TEXT with CHECK constraint is safer for v1 — it allows adding status values without ALTER TYPE migrations.
- **Foreign key cascade**: The task document states "DELETE on `agent_runner_jobs` without cascading deletes for events and artifacts (referential integrity must be preserved or cascade explicitly)." Implement FK constraints with `ON DELETE CASCADE` on both `agent_runner_job_events.job_id` and `agent_runner_job_artifacts.job_id` to ensure referential integrity when a job is deleted.
- **Timestamps**: Use `TIMESTAMP WITH TIME ZONE` (PostgreSQL `timestamptz`) for all timestamp columns to ensure timezone safety. Set `created_at` and `updated_at` defaults to `NOW()` in the migration.
- **JSONB columns**: `details` (events) and `metadata` (artifacts) are JSONB — this is PostgreSQL-specific and enables structured querying. Ensure the migration uses `JSONB` type, not `JSON` (which lacks indexing support).
- **Inline comments**: Each migration file must include inline comments explaining: (a) column purpose, (b) constraint rationale, (c) transaction semantics for concurrent claiming (for 001), (d) append-only semantics (for 002).
- **Schema spec document**: Create `agent_runner_v2/db/SCHEMA_SPEC.md` only if inline comments become too verbose. Prefer inline comments for v1.

## Ready for Execution Checklist

- [x] File plan is complete with [NEW]/[MODIFY] tags
- [x] Module responsibilities defined
- [x] Test plan covers all acceptance criteria from task spec (migration apply, rollback, schema inspection, concurrent claiming, index verification)
- [x] Dependencies identified (PostgreSQL, psycopg2, Python 3.11+)
- [x] Reuse strategy documented (existing PostgreSQL, Python environment)
- [x] Risks assessed and mitigations planned (framework unknown, permissions, FK ordering, SKIP LOCKED support)
- [x] Scope boundaries clear (schema-only; repository, CLI, worker deferred to subsequent tasks)
- [x] All task-derived constraints marked [TASK-DERIVED] for traceability
- [x] All 5 test cases from task document enumerated verbatim in test plan
- [x] All schema columns, types, and indices from task document reproduced without omission or paraphrasing
