# Plan: Enhance Agent Runner into Daemon Mode with Database-backed Job Management

## Metadata

| Field | Value |
|---|---|
| **Plan ID** | PLAN-20260602-01 |
| **Initiative ID** | INIT-20260602-01 |
| **Title** | Enhance Agent Runner into Daemon Mode with Database-backed Job Management |
| **Status** | Approved |
| **Owner** | @kengkoon.chua |
| **Created At** | 2026-06-02 |
| **Review File Path** | `docs/delivery/04_reviews/REVIEW-20260602-01_pre-init-agent-runner-daemon-db-job-mana.md` |

## Executive Summary

This plan translates the approved initiative to enhance Agent Runner with persistent database-backed daemon/worker mode into seven implementation slices. The core goal is to decouple job submission and inspection from execution, enabling long-running workflows to proceed asynchronously without blocking OpenClaw or client sessions. The plan prioritizes foundational infrastructure (database schema, repository layer, CLI commands) before integration with existing workflows, followed by optional enhancements like human approval gates and OpenClaw guidance.

## 🎯 Objectives

**Technical Objectives:**
- Establish persistent, queryable job state in a database with transactional safety
- Implement non-blocking submit/status/inspect operations decoupled from execution
- Enable safe concurrent job claiming using PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED`
- Integrate daemon worker loop with existing Agent Runner workflow execution engine
- Support defined job status transitions and human approval/rejection gates
- Maintain append-only audit trail of all job state changes and human actions
- Register and track workflow-generated artifacts with checksums and metadata

**User-Facing Objectives:**
- OpenClaw can submit jobs and inspect progress without session blocking
- Clear job IDs and status feedback for long-running workflows
- Ability to approve, reject, retry, or cancel jobs with recorded audit trails
- Direct CLI users retain existing execution path while gaining async options

**Business Objectives:**
- Reduce blocking of orchestration clients during long-running workflows
- Foundation for future Control Plane UI and API service integration
- Clearer separation of orchestration and execution responsibilities

## 📅 Execution Phases

### Phase 1: Foundation (Slices 1–2)
Database schema, repository layer, and CLI command structure. Establishes the data model and command interface, enabling job submission and status inspection without execution.

**Target outcome:** `submit` returns job ID immediately; `status` reads DB without triggering execution.

### Phase 2: Worker & Integration (Slices 3–4)
Worker daemon loop with job claiming, execution integration, and workflow output registration. Connects job management to existing workflow steps.

**Target outcome:** `worker --once` claims and executes a queued job through at least one existing workflow path.

### Phase 3: Advanced Operations (Slices 5–6)
Human approval gates, rejection, retry, and cancellation logic with safe state transitions.

**Target outcome:** Jobs can pause for human decision; resume after approval; failed jobs can be retried.

### Phase 4: External Guidance (Slice 7)
OpenClaw integration documentation and usage guidelines.

**Target outcome:** OpenClaw team has clear instructions on allowed/forbidden behaviors.

## 📋 Task Breakdown

| Task ID | Description | Slice | Phase | Acceptance Criteria |
|---|---|---|---|---|
| TASK-20260602-01 | Implement DB schema migrations for `agent_runner_jobs`, `agent_runner_job_events`, `agent_runner_job_artifacts` | 1 | 1 | All three tables created with correct columns, indices, and constraints; migrations reversible; schema supports PostgreSQL `FOR UPDATE SKIP LOCKED` |
| TASK-20260602-02 | Implement repository layer: create job, fetch job, claim next job, update status, append event, register artifact | 1 | 1 | All six repository methods implemented; unit tests pass; no N+1 queries; transaction safety verified |
| TASK-20260602-03 | Implement CLI command `submit --initiative`: creates queued job, returns job ID immediately | 2 | 1 | Command accepts initiative ID or file path; returns JSON with job_id and status=QUEUED; does not trigger execution |
| TASK-20260602-04 | Implement CLI command `status --job-id` and `--latest`: reads job state without triggering execution | 2 | 1 | Command returns JSON with job_id, status, current_step, created_at, updated_at; does not call LLM or trigger execution |
| TASK-20260602-05 | Implement CLI commands `logs --job-id` and `artifact --job-id`: read-only inspection of logs and workflow outputs | 2 | 1 | Both commands return artifact metadata and optionally content preview; read-only, no execution triggered |
| TASK-20260602-06 | Implement worker loop `worker --once`: claim job, execute workflow, persist state and logs | 3 | 2 | Worker claims exactly one QUEUED job; executes through at least one workflow path; transitions job to COMPLETED or FAILED; persists logs and status |
| TASK-20260602-07 | Integrate worker execution with existing Agent Runner workflow engine; persist current_step and workflow outputs as artifacts | 4 | 2 | Worker calls existing workflow steps; current_step updated during execution; workflow artifacts registered with artifact path and metadata; error details persisted on failure |
| TASK-20260602-08 | Implement human approval gate support: detect approval gates, pause job at `WAITING_FOR_HUMAN_APPROVAL`, allow resume after `approve` command | 5 | 3 | Worker can identify approval-gated steps; job transitions to WAITING_FOR_HUMAN_APPROVAL; `approve` command moves job to READY_TO_RESUME; worker resumes on next pickup |
| TASK-20260602-09 | Implement CLI commands `approve --job-id`, `reject --job-id --reason`, `retry --job-id`: state-changing operations with event tracking | 5 | 3 | All three commands validate preconditions; record events; transition job state safely; reject and retry support safe state transitions per status model |
| TASK-20260602-10 | Implement CLI command `cancel --job-id`: safe cancellation with checkpoint support | 6 | 3 | Command marks job CANCEL_REQUESTED; worker checks cancellation at safe checkpoints; job transitions to CANCELLED; event recorded |
| TASK-20260602-11 | Create comprehensive integration and acceptance tests: submit → worker → completion flow; failure handling; approval gates; cancellation | 1–6 | 1–3 | All core flows tested with no LLM calls (mocked providers); test coverage includes success, failure, approval, rejection, retry, cancellation; tests pass without external dependencies |
| TASK-20260602-12 | Create OpenClaw integration guide: usage patterns, allowed/forbidden behaviors, command examples | 7 | 4 | Document created at specified path; includes examples of submit/status/approve patterns; clearly lists forbidden behaviors (direct workflow invocation, continuous polling); suitable for external team handoff |

## 🎬 Implementation Strategy

### Database Foundation (Early)
Migrations and repository layer establish the persistent data model before any CLI commands or workers are built. This enables testing and validation of transaction safety and claiming logic without depending on workflow integration.

### Non-Blocking CLI (Immediate)
`submit`, `status`, `logs`, `artifact` commands are read-only or write-only operations that do not trigger execution. These validate the data model and command interface before workers are introduced.

### Worker Integration (Sequential)
Worker daemon loop depends on stable job schema and repository layer. Single-job execution (`--once` mode) is the primary validation point before supporting continuous polling or multi-job workers.

### Advanced Features (Layered)
Approval gates, retry, and cancellation are built on top of stable worker execution. Testing can use simplified approval logic initially before full workflow integration.

### OpenClaw Guidance (Late)
External documentation is written once the command interface and worker behavior are finalized, ensuring guidance reflects actual implementation.

### Testing Throughout
Each slice includes unit, integration, or acceptance tests. No LLM calls in tests; mocked providers or fixture-based workflows used.

## ⚠️ Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Job claiming race conditions with multiple workers | High | Use PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED` within transaction; validate with concurrent worker tests |
| Workflow integration complexity; existing engine has undocumented assumptions | Medium | Early integration testing with minimal workflow steps; isolate assumptions via adapter layer; fallback to wrapping existing CLI |
| Database transaction deadlocks under concurrent approval/rejection | Medium | Keep transactions short; order lock acquisitions consistently; monitor deadlock rate in integration tests |
| Large audit trail growth; event table unbounded | Low | Add retention policy in later version; use indices on job_id and created_at; optimize query patterns early |
| Worker crash recovery and resumption | Medium | v1 conservative approach: no automatic resume; manual retry or explicit restart required; document clearly; investigate automatic recovery in v2 |
| Status model complexity and edge cases in transitions | Medium | Document all valid transitions explicitly; test each transition path; validate in state-machine unit tests |

## 📦 Deliverables

All deliverables follow UKBE delivery structure and naming conventions.

### Infrastructure Deliverables
1. **Database Migrations**
   - Path: `agent_runner_v2/db/migrations/` (auto-numbered by framework)
   - Files: Three migration files for jobs, events, artifacts tables
   - Acceptance: Tables exist in DB; schema matches specification; indices created; migrations reversible

2. **Repository Layer Module**
   - Path: `agent_runner_v2/db/job_repository.py`
   - Implements: create_job, fetch_job, claim_next_job, update_job_status, append_event, register_artifact
   - Acceptance: All methods implemented; no N+1 queries; transaction-safe claiming

### CLI Command Deliverables
3. **CLI Commands Module**
   - Path: `agent_runner_v2/cli/daemon_commands.py` (or structured submodules)
   - Implements: submit, status, logs, artifact, approve, reject, retry, cancel
   - Acceptance: All commands implemented; return JSON or readable output; no execution triggered by read-only commands

### Worker & Integration Deliverables
4. **Worker Loop Module**
   - Path: `agent_runner_v2/worker/daemon_loop.py`
   - Implements: Worker ID generation, job claiming, FIFO ordering, safe transaction handling
   - Acceptance: `--once` mode claims and executes one job; graceful handling of empty queue

5. **Workflow Integration Adapter**
   - Path: `agent_runner_v2/worker/workflow_adapter.py`
   - Integrates daemon job context with existing workflow execution engine
   - Acceptance: current_step persisted; workflow outputs registered as artifacts; errors recorded

### Advanced Features Deliverables
6. **Human Gate & State Transitions Module**
   - Path: `agent_runner_v2/worker/approval_gates.py`
   - Implements: approval gate detection, job pause/resume, rejection, retry logic
   - Acceptance: Jobs pause at approval gates; approve/reject/retry transition state correctly

### External Documentation Deliverables
7. **OpenClaw Integration Guide**
   - Path: `docs/delivery/guides/OPENCLAW_INTEGRATION_GUIDE.md`
   - Content: Usage patterns, allowed/forbidden behaviors, command examples, error handling
   - Acceptance: Document suitable for external team; clear recommendations for safe usage

### Test Deliverables
8. **Comprehensive Test Suite**
   - Path: `agent_runner_v2/tests/` (distributed across test modules for each component)
   - Coverage: Unit tests (repo, claiming logic, transitions), integration tests (submit → worker → completion, approval gates, cancellation)
   - Acceptance: All tests pass; no LLM calls; test coverage meets thresholds for all components

## 🔗 Dependencies

| Dependency | Owner | Status | Notes |
|---|---|---|---|
| PostgreSQL database | Existing project DB | Assumed available | Used for job state, events, artifacts |
| Existing Agent Runner workflow engine | Current codebase | In use | Daemon wraps, does not replace |
| UKBE delivery structure | Framework | Defined | Initiative, plan, task, review templates |
| Python environment and CLI framework | Current codebase | In use | Agent Runner CLI already uses Click or Argparse |

## ✅ Acceptance Criteria

**Phase 1 (Foundation):**
- [ ] `submit --initiative INIT-xxx` creates queued job and returns immediately with job ID
- [ ] `status --job-id <id>` reads job state from DB without triggering execution
- [ ] Job schema validated; no N+1 queries; transactions support concurrent claiming

**Phase 2 (Worker & Integration):**
- [ ] `worker --once` claims and executes one queued job through at least one existing workflow path
- [ ] Job status transitions from QUEUED → CLAIMED → RUNNING → COMPLETED (or FAILED)
- [ ] Workflow outputs registered as artifacts; logs persisted; errors recorded in job status

**Phase 3 (Advanced Operations):**
- [ ] Approval-gated jobs pause at WAITING_FOR_HUMAN_APPROVAL; `approve` resumes execution
- [ ] `reject` and `retry` commands work safely with event recording
- [ ] `cancel` command marks job CANCELLED with safe checkpoint support

**Phase 4 (External Guidance):**
- [ ] OpenClaw integration guide is complete, reviewed, and approved for external handoff
- [ ] Guide includes clear examples and forbidden behaviors

**Overall Acceptance:**
- [ ] All seven implementation slices completed
- [ ] Test suite comprehensive; all tests pass
- [ ] No breaking changes to existing `agent-runner run` execution path
- [ ] Job claiming prevents duplicate execution across concurrent workers
- [ ] Audit trail captures all state changes and human actions

## 🧭 Scope Mapping

- TASK-20260602-01 -> Included Scope: Database schema; Slice 1
- TASK-20260602-02 -> Included Scope: Database schema and Repository Layer; Slice 1; Success Criteria 10
- TASK-20260602-03 -> Included Scope: CLI command submit; Success Criteria 1
- TASK-20260602-04 -> Included Scope: CLI command status; Success Criteria 3; CLI Contract
- TASK-20260602-05 -> Included Scope: CLI commands logs and artifact; Success Criteria 4, 5; CLI Contract
- TASK-20260602-06 -> Included Scope: Worker daemon loop; Success Criteria 2; Slice 3
- TASK-20260602-07 -> Included Scope: Workflow integration, artifact registration; Success Criteria 5; Slice 4
- TASK-20260602-08 -> Included Scope: Human approval gates; Success Criteria 7; Slice 5
- TASK-20260602-09 -> Included Scope: CLI commands approve, reject, retry; Success Criteria 7, 8; Slice 5
- TASK-20260602-10 -> Included Scope: CLI command cancel; Success Criteria 8; Slice 6
- TASK-20260602-11 -> Included Scope: Testing strategy; Integration, Unit, Acceptance tests; Success Criteria 2, 3, 4, 6
- TASK-20260602-12 -> Included Scope: OpenClaw usage guidelines; Success Criteria 9; Slice 7

## 🚫 Explicitly Excluded / Not Planned

- Full Control Plane UI rebuild: excluded (future enhancement)
- Replacement of existing workflow step logic: excluded (daemon wraps, does not replace)
- Distributed multi-worker scaling beyond FIFO claiming: excluded (v1 focuses on local stability)
- Complex scheduling logic beyond FIFO job queue: excluded (FIFO sufficient for v1)
- Advanced observability dashboards: excluded (basic logs/status queries sufficient)
- Rewriting coder provider integrations: excluded (daemon uses existing providers)
- OpenClaw subagent orchestration: excluded (outside daemon scope)
- Moving all UKBE artifact features into this initiative: excluded (daemon registers, UKBE integration separate)
- Automatic recovery of crashed workers: excluded (v1 uses conservative manual recovery; future enhancement)
- Distributed database replication: excluded (local PostgreSQL sufficient; future enhancement)
- Job scheduling by priority or SLA: excluded (FIFO priority sufficient; future enhancement)
- WebSocket or streaming job notifications: excluded (polling via status command sufficient; future enhancement)

## 📝 Notes

- **Job ID format:** `job_YYYYMMDD_NNNN` with auto-increment; FIFO claiming via PostgreSQL `ORDER BY created_at ASC FOR UPDATE SKIP LOCKED`
- **Worker ID:** Generated at daemon startup (hostname + PID or UUID)
- **Provider support:** Worker accepts `--provider` flag to route jobs to specific coder tools
- **Event audit trail:** All state changes and human actions recorded in `agent_runner_job_events` for compliance and debugging
- **Resume strategy for v1:** Conservative—do not auto-resume partial coder steps; manual recovery or explicit retry required after worker crash
- **Database transactions:** All state-changing operations wrapped in transactions; claiming uses SKIP LOCKED to avoid blocking
- **Backward compatibility:** Existing `agent-runner run` path unchanged; async features are additions
- **Testing approach:** Comprehensive unit, integration, and acceptance tests; no LLM calls in tests (mocked providers)

---

**Document generated:** 2026-06-02
