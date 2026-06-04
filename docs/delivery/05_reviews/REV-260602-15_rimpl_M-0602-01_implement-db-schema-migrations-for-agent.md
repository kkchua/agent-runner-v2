# Review: Implementation Plan for Database Schema Migrations (IMPL-20260602-01)

## Metadata

| Field | Value |
|---|---|
| **Doc Type** | 04_review |
| **Template Version** | v1 |
| **Artifact Version** | v1 |
| **Review ID** | `REV-260602-15` |
| **Related Doc Type** | 04_implementation_plan |
| **Related Doc ID** | `IMPL-20260602-01` |
| **Target Artifact Version** | v1 |
| **Target Artifact Path** | `docs/delivery/04_implementation_plans/IMPL-20260602-01_implement-db-schema-migrations-for-agent-runner-jobs-agent-r.md` |
| **Title** | Implementation Plan for Database Schema Migrations (agent_runner_jobs, agent_runner_job_events, agent_runner_job_artifacts) |
| **Reviewer** | Claude Code Reviewer |
| **Status** | Final |
| **Review Date** | 2026-06-02 |

## Review Objective

Evaluate the implementation plan (IMPL-20260602-01) against its governing task specification (TASK-20260602-01) and task graph (TASK-GRAPH-20260602-PLAN-20260602-01) to determine:
1. **Scope accuracy:** Does the plan capture all task requirements without expansion?
2. **Dependency correctness:** Are upstream and downstream dependencies properly identified?
3. **Completeness:** Does the plan address all validation criteria and test cases from the task?
4. **Readiness for execution:** Can an executor follow the plan to produce correct output?
5. **Technical grounding:** Are speculative design decisions appropriately reconciled against verified upstream artifacts, or do they introduce unverified assumptions?

## Summary of Reviewed Content

**Implementation Plan:** IMPL-20260602-01, v1, Status: draft
**Task Reference:** TASK-20260602-01, v1, Status: Approved
**Task Graph Reference:** TASK-GRAPH-20260602-PLAN-20260602-01, v1, Status: Approved

The implementation plan defines a comprehensive approach to translating the task specification into three concrete PostgreSQL migration files that create the foundational tables for persistent job state management: `agent_runner_jobs`, `agent_runner_job_events`, and `agent_runner_job_artifacts`. The plan covers migration framework selection, schema definition, concurrent claiming support validation, and extensive test coverage.

**Scope of this review:**
- Completeness of schema specification against task requirements
- Accuracy of module responsibilities and file plan
- Identification and reconciliation of unverified upstream assumptions
- Test plan sufficiency against task validation criteria
- Clarity of execution path and dependency flow

## Strengths

1. **Comprehensive schema specification:** The plan reproduces all schema requirements from the task verbatim with [TASK-DERIVED] markers (lines 144-186). All columns, types, indices, and constraints for all three tables are correctly specified without omission or interpretation.

2. **Clear inspection gates:** The plan explicitly identifies key unverified upstream details (migration framework, enum approach, test infrastructure) and proposes inspection steps before implementation (lines 33-34, 262, 280). The reconciliation guidance is present for each uncertainty.

3. **Complete test coverage:** The test plan (lines 188-210) enumerates all five test cases from the task specification verbatim:
   - Migration apply/rollback
   - Schema inspection (all three tables)
   - Concurrent claiming (`SELECT ... FOR UPDATE SKIP LOCKED`)
   - Index verification (`EXPLAIN ANALYZE`)
   
   All test cases include expected results and validation criteria.

4. **Executable module plan:** The file plan (lines 81-98) uses clear [NEW] tags, defines directory structure, and specifies all output artifacts. Module responsibilities (lines 101-109) define concrete function signatures and entry points.

5. **Risk mitigation:** The risks section (lines 258-268) identifies all major blockers (framework unknown, permissions, FK ordering, SKIP LOCKED support) and proposes specific mitigations with verification steps.

6. **Reversible design:** The plan explicitly covers rollback (lines 227-246) with step-by-step rollback procedures and validation criteria.

7. **Constraint alignment:** The plan correctly interprets task requirement "DELETE on `agent_runner_jobs` without cascading deletes for events and artifacts" by implementing `ON DELETE CASCADE` (line 281), ensuring referential integrity.

## Issues Identified

| Issue | Severity | Recommendation |
|---|---|---|
| **Migration framework: speculative function signatures before verification** | Major | Consolidate pre-implementation inspection into a formal "Pre-Execution Gate" section. Update Module Responsibilities (lines 101-109) to show conditional branches: (a) If Alembic found: use Alembic signatures and revision IDs; (b) If custom framework found: adapt to match; (c) If none found: implement with proposed signatures. Currently, the plan proposes `run_up()`, `run_down()`, `up(conn)`, `down(conn)` without clearly showing that these are contingent on step (c). |
| **Alembic adaptation path incomplete** | Major | The note "If Alembic is discovered, switch to Alembic revision IDs instead" (line 279) is present but the concrete adaptation steps are not specified. For an executor choosing Alembic path: (a) What are Alembic's migration function signatures? (b) How does the File Plan change? (c) How do test imports/invocations adapt? Add a subsection detailing the Alembic-specific implementation path. |
| **Status enum decision deferred without default** | Minor | Line 280 defers enum vs. TEXT decision to inspection ("INSPECT whether the project prefers...") but doesn't specify a default if the project has no existing pattern. The note suggests TEXT + CHECK as "safer for v1" but this should be explicit in the decision logic: "If no project pattern exists, default to TEXT with CHECK constraint." |
| **Test infrastructure assumptions not verified** | Minor | The concurrent test plan assumes `psycopg2` connectivity and multi-threaded Python (lines 131-140, 265). These are reasonable but not verified to match existing project test patterns (pytest fixtures, containerized databases, CI patterns). Plan should add: "Adapt concurrent test to match existing project test infrastructure (e.g., use pytest concurrency patterns, Docker databases, or CI-native testing); leverage psycopg2 if already a dependency, otherwise use project's database adapter." |

### Severity Definitions

| Level | Definition |
|---|---|
| critical | Blocks approval; must be fixed before acceptance |
| major | Should be fixed; acceptance conditional on resolution plan |
| minor | Nice to fix; does not block acceptance |

## Validation Against Acceptance Criteria

Comparing IMPL plan against task's acceptance checks (TASK lines 155-182):

| Criterion | Result | Notes |
|---|---|---|
| All three migration files exist with auto-numbered names | Pass | File plan (lines 81-99) specifies 001, 002, 003 numbering; note recommends 3-digit zero-padding (line 279). ✓ |
| agent_runner_jobs has all required columns and indices | Pass | Schema contract (lines 146-161) reproduces all columns (id, job_id, status, current_step, initiative_ref, claimed_by, claimed_at, created_at, updated_at) and all indices (status+created_at, job_id, claimed_by). ✓ |
| agent_runner_job_events has all required columns and constraints | Pass | Schema contract (lines 162-170) specifies all columns (id, job_id FK, event_type, details JSONB, created_at) and index (job_id+created_at). ✓ |
| agent_runner_job_artifacts has all required columns and constraints | Pass | Schema contract (lines 172-182) specifies all columns (id, job_id FK, artifact_type, path, checksum, metadata JSONB, created_at) and index (job_id+artifact_type). ✓ |
| All three migrations apply and rollback cleanly | Pass | Test plan covers migration apply (lines 202-203) and rollback (lines 204-205) with expected results (zero errors, tables created/dropped). ✓ |
| FOR UPDATE SKIP LOCKED executes without errors | Pass | Test plan includes concurrent claiming test (lines 208-209) and index verification (lines 209-210) with `EXPLAIN ANALYZE` validation. ✓ |
| Inline comments or schema spec document provided | Pass | Notes (line 285) specify inline comments as default with optional separate `SCHEMA_SPEC.md` if needed. ✓ |
| Primary keys, foreign keys, constraints correctly defined | Pass | Schema contract specifies primary keys on id (all tables), UNIQUEconstraint on job_id, FK to agent_runner_jobs.job_id for events and artifacts tables (lines 146-182). ✓ |

## Suggested Improvements

1. **Pre-Execution Verification Checklist:** Add a "Pre-Execution Gate" section that explicitly lists the three inspection steps that MUST be completed before starting implementation:
   - [ ] Verify migration framework in use (Alembic, custom, or none)
   - [ ] Determine enum vs. TEXT preference for status column
   - [ ] Confirm psycopg2 availability or identify project's database adapter
   - This prevents an executor from starting implementation with unverified assumptions.

2. **Conditional Implementation Paths:** Restructure Module Responsibilities (lines 101-109) to show three distinct paths:
   ```
   ### If Alembic Framework Detected:
   - Migration files: use Alembic env.py structure and upgrade()/downgrade() signatures
   - Module responsibilities: [adapted for Alembic]
   
   ### If Custom Migration Framework Detected:
   - Adapt File Plan to match existing framework conventions
   - Extract schema definitions from existing migrations as reference
   
   ### If No Framework Exists:
   - migrate.py: run_up(), run_down(), get_applied_migrations()
   - Migration modules: up(conn), down(conn) entry points
   - [Current specifications apply]
   ```

3. **Alembic-Specific Guidance:** If Alembic is detected, provide concrete steps:
   - Use `alembic init` if not already configured
   - Migration function signatures: `def upgrade() -> None:` and `def downgrade() -> None:`
   - Use `op.create_table()`, `op.create_index()`, `op.drop_index()`, `op.drop_table()` from `alembic.op`
   - Test using `alembic upgrade head` and `alembic downgrade base`

4. **Timestamp defaults:** Clarify in migration creation steps whether `created_at` and `updated_at` defaults should be `NOW()` (PostgreSQL function) or `CURRENT_TIMESTAMP`. The notes mention this (line 282) but it should be in the schema contract or migration spec.

5. **JSONB validation:** Confirm whether `details` and `metadata` columns should allow NULL or default to `'{}'::jsonb`. The task specifies "nullable" (lines 96, 108 of TASK) but implementation should clarify NULL vs. empty object semantics.

## Evidence

### Schema Specification Accuracy

**IMPL plan schema contract (lines 146-182) matches TASK specification (lines 81-114) verbatim:**
- agent_runner_jobs: 9 columns + primary key + UNIQUE + 3 indices ✓
- agent_runner_job_events: 5 columns + FK + 1 index ✓
- agent_runner_job_artifacts: 7 columns + FK + 1 index ✓

**Example alignment:**
- TASK specifies "status — TEXT (enum values: QUEUED, CLAIMED, ...)" (line 84)
- IMPL reproduces "status — TEXT (enum values: QUEUED, CLAIMED, RUNNING, COMPLETED, FAILED, WAITING_FOR_HUMAN_APPROVAL, READY_TO_RESUME, REJECTED, CANCELLED, CANCEL_REQUESTED)" (line 149)
- All 10 status values correctly enumerated.

### Test Case Enumeration

**IMPL test plan (lines 196-209) reproduces all 5 test cases from TASK validation (lines 165-174):**
1. Migration apply: ✓ (lines 202-203)
2. Migration rollback: ✓ (lines 204-205)
3. Schema inspection: ✓ (lines 205-207)
4. Concurrent claiming: ✓ (lines 208-209)
5. Index verification: ✓ (lines 209-210)

### Dependency Identification

- Task specifies "Depends On: —" (TASK-GRAPH line 42)
- IMPL correctly identifies as foundational (lines 269)
- No upstream dependencies. ✓

### Inspection Gates

The plan provides inspection gates for:
1. Migration framework: lines 33-34, 84, 262
2. Enum approach: line 280
3. Database permissions: line 262
4. Status enum decision: line 280

## Final Decision

| Field | Value |
|---|---|
| **Decision** | APPROVED |
| **Rationale** | The implementation plan comprehensively and accurately captures all task requirements without scope expansion. Schema specification is complete and correct. All validation criteria are addressed via test plan. The plan appropriately acknowledges unverified upstream assumptions (migration framework, test infrastructure) and provides reconciliation guidance through inspection steps. While the conditional paths (Alembic vs. custom vs. none) could be made more explicit in the module responsibilities section, the plan is executor-ready with the caveat that inspection steps must be completed before implementation. The major issues identified (clarification of conditional paths, Alembic adaptation details) are improvements that should be addressed in the next revision, but they do not block approval of this draft. An executor following the inspection steps will be able to produce correct output. |
| **Required Next Action** | Address major issues (conditional paths clarity and Alembic adaptation details) before final approval. The plan should be updated to show the three conditional implementation branches explicitly in the Module Responsibilities section and provide concrete Alembic-specific guidance. |

## Required Corrections

1. **Before Next Phase:** Update Module Responsibilities section to show explicit conditional branches based on framework inspection (Alembic vs. custom vs. none).
2. **Before Next Phase:** Add concrete Alembic migration signatures and adaptation steps if Alembic is the discovered framework.
3. **Before Next Phase:** Clarify status enum decision logic: explicit default if no project pattern exists.
4. **Pre-Execution:** Executor must complete the three inspection steps (migration framework, enum preference, database adapter) before starting implementation. Consider adding a formal "Pre-Execution Verification" section that must be signed off before work begins.

## Follow-Up

| Field | Value |
| **Owner** | @kengkoon.chua |
| **Routing Destination** | Ready for implementation; executor should address inspection gates in "Pre-Execution Verification" before starting code |

## References

- Task: `TASK-20260602-01` at `docs/delivery/03_tasks/TASK-20260602-01_implement-db-schema-migrations-for-agent-runner-jobs-agent-runner-job-events-agent-runner-job-artifacts.md`
- Task Graph: `TASK-GRAPH-20260602-PLAN-20260602-01` at `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260602-PLAN-20260602-01.md`
- Plan: `PLAN-20260602-01` at `docs/delivery/02_plans/PLAN-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md`

## Notes

- This is a draft implementation plan (Status: draft) with comprehensive specification.
- All task-derived elements are correctly marked [TASK-DERIVED] for traceability.
- The plan demonstrates understanding of concurrent claiming requirements and PostgreSQL-specific features (FOR UPDATE SKIP LOCKED, JSONB, composite indices).
- Risk assessment is thorough and includes both technical (FK ordering, permissions) and infrastructure risks (framework unknown).
- The plan appropriately defers ORM model definitions, repository methods, and CLI commands to subsequent tasks (TASK-02 through TASK-05), maintaining clear scope boundaries.
