# Workflow Bundle Validation And Backend Sync Refactor Plan

## Purpose

This document defines the target refactor for workflow bundle validation and
backend sync.

The current behavior is unacceptable:

- `sync_workflows.py` attempts to POST workflow definitions directly to the
  backend
- the backend may reject or crash on definition changes that should be owned
  by `agent-runner-v2`
- this makes backend sync fragile and reduces its practical value

The target model is:

- `agent-runner-v2` owns workflow bundle validation
- backend stores already-validated workflow definitions as data
- sync performs local validation first and syncs only when validation passes

## Core Decision

Workflow bundle validation must live in `agent-runner-v2`, not in the backend.

The backend must not own semantic workflow validation such as:

- artifact vocabulary rules
- role policy semantics
- prompt governance expectations
- bundle governance completeness
- workflow-specific routing semantics

Those responsibilities belong to the local runner, which is the source of
truth for workflow execution knowledge.

## Target Flow

The intended steady-state sync flow is:

1. load workflow bundle locally
2. validate workflow bundle locally
3. if validation fails, stop locally and do not call backend
4. if validation passes, build normalized workflow definition payload
5. POST the validated payload to backend
6. backend stores it with only minimal persistence and transport checks

## CLI Requirement

`agent-runner-v2` should provide a first-class CLI command:

```text
ukbe-run-agent validate-workflow-bundle --workflow-name 00_core_governance_bootstrap_v1
```

Optional scope:

- validate a single workflow bundle
- validate multiple named bundles
- validate all bundles under the bootstrap workflow root

The command should return a non-zero exit code on failure and provide a clear,
structured report of findings.

## Validation Scope

The local validator should verify at least:

### Manifest and Structure

- `workflow.toml` exists
- workflow package loads successfully
- bundle name is non-empty
- step list is non-empty
- step names are unique
- `init_step` exists in the declared step order

### Step Contract Integrity

- every step has either a prompt or an action
- referenced prompt files exist
- `onsuccess` targets point to declared steps
- `loop_returns_to` targets point to declared steps
- `replan_returns_to` targets point to declared steps
- `on_reject_refine.step` targets point to declared steps
- produced/required artifact keys are non-empty strings

### Bundle Governance Integrity

- if `bundle_governance.toml` exists, it loads successfully
- canonical governance source exists
- extension source files exist
- artifact registry entries are structurally valid
- generated adapter targets are declared consistently

### Control Plane Integrity

- declared role policies are structurally valid at step level
- workflow bundle can be normalized into `TEMPLATE_GROUPS` shape
- normalized definition is JSON-serializable after runtime-only bundle refs are removed

## Sync Integration Requirement

`sync_workflows.py` must run the same validator before POSTing any workflow
definition.

This should happen in-process through shared validation functions, not by
duplicating validation logic.

The sync script should:

1. discover workflows
2. validate each selected workflow locally
3. print local validation failure details if any
4. skip backend POST for invalid workflows
5. POST only validated workflows

## Backend Responsibility After Refactor

After this refactor, backend sync should do only minimal checks:

- request body is parseable
- required top-level payload fields are present
- workflow definition can be stored

The backend should not re-own local bundle semantics.

## Phase Plan

### Phase 1

Add local validation infrastructure.

Deliverables:

- reusable workflow bundle validator module
- `validate-workflow-bundle` CLI command
- unit tests for validator behavior

### Phase 2

Integrate validation into `sync_workflows.py`.

Deliverables:

- sync preflight local validation
- sync failure reporting that distinguishes:
  - local validation failure
  - backend transport/storage failure

### Phase 3

Harden validator coverage.

Deliverables:

- richer bundle governance checks
- artifact registry consistency checks
- optional JSON report output for automation

### Phase 4

Simplify backend expectations.

Deliverables:

- document backend as persistence-only for synced workflow definitions
- remove duplicated validation assumptions over time

## Current Status

Completed:

- Phase 1
  - reusable workflow bundle validator module added
  - `validate-workflow-bundle` CLI command added
  - unit tests added for core validator behavior
- Phase 2
  - `sync_workflows.py` now runs local validation before POST
  - sync output now distinguishes:
    - local validation failure
    - backend transport/storage failure
- Phase 3
  - bundle governance prompt-target validation added
  - governance artifact registry consistency checks added
  - unit tests added for governance-drift failure modes

In progress:

- Phase 4
  - local documentation and tool messaging are being aligned so backend sync
    is explicitly treated as persistence-oriented and local validation remains
    authoritative

## Phase 4 Backend Cutover

The backend currently still owns too much workflow-definition interpretation.

Observed current behavior in `agent-runner-backend`:

- `services/workflow_registry.py` rebuilds artifact rules, transitions, coder
  policy rows, and nested step state from the incoming definition
- sync success still depends on backend-side interpretation matching the
  runner-owned normalized payload
- `api/serializers.py` builds `step_execution_spec` from persisted backend
  step/artifact/coder rows instead of treating `raw_definition` as the source
  of truth
- `services/execution_service.py` creates and routes runs from persisted step
  rows

That means local validation can pass while backend sync still fails or drifts.

### Phase 4A

Introduce a backend raw-definition view and make it the source of truth for
execution payload generation.

Implementation target:

- add helper functions in backend to read:
  - ordered step names from `workflow.raw_definition["steps"]`
  - step config from `workflow.raw_definition["step_configs"][step_name]`
  - artifact rule map from `workflow.raw_definition["artifact_rules"]`
- update backend `build_step_execution_spec(...)` so worker payloads are
  derived from `workflow.raw_definition`, not reconstructed from relational
  step bindings

Target modules:

- `agent_runner_backend/api/serializers.py`
- optionally extract helpers into a dedicated backend workflow-definition
  utility module if reuse grows

Expected result:

- worker step specs follow the runner-owned normalized payload exactly
- backend step-spec generation no longer depends on backend-only semantic
  reconstruction

### Phase 4B

Reduce backend sync to persistence plus mechanical denormalization.

Implementation target:

- keep storing top-level workflow fields needed for run creation:
  - `name`
  - `job_prefix`
  - `job_init_step`
  - `default_max_rejects`
  - `max_planning_attempts`
  - `job_init_inputs`
  - `reference_files`
  - `raw_definition`
  - `source_hash`
- keep denormalized step rows only as an execution index while
  `workflow_step_runs.step_definition_id` remains required
- remove backend special-case workflow semantics from sync:
  - no delivery/image workflow-specific artifact rule synthesis
  - no backend-specific nested equivalence gate beyond persistence integrity
  - no backend semantic ownership over role policy, routing rules, or prompt
    governance

Target modules:

- `agent_runner_backend/services/workflow_registry.py`

Expected result:

- backend sync no longer rejects valid runner definitions because of backend
  semantic drift
- backend keeps enough denormalized state for current execution tables without
  becoming the workflow-validation owner

### Phase 4C

Move backend run creation and default routing lookups onto the raw definition
view where practical.

Implementation target:

- update backend step lookup helpers so run creation and next-step routing are
  derived from `workflow.raw_definition`
- retained step rows remain compatibility data, not the primary workflow
  contract

Target modules:

- `agent_runner_backend/services/execution_service.py`

Expected result:

- run orchestration follows the same step order and step names as the synced
  normalized payload
- backend execution becomes resilient to future step-shape refactors

### Phase 4D

Return workflow details from the raw definition view for admin/read APIs.

Implementation target:

- update workflow detail serialization so `/api/workflows/...` exposes the
  synced normalized definition as authoritative
- relational step/artifact/coder rows should not be the canonical public
  contract

Target modules:

- `agent_runner_backend/api/workflow_routes.py`
- `agent_runner_backend/api/serializers.py`

Expected result:

- backend read APIs reflect the exact synced definition
- troubleshooting becomes easier because the stored source-of-truth payload is
  directly visible

### Phase 4E

Add backend tests that lock in persistence-oriented behavior.

Implementation target:

- add sync tests proving:
  - valid locally-normalized definitions can be stored without backend-specific
    workflow semantics
  - `step_execution_spec` is generated from `raw_definition`
  - workflow read APIs expose the authoritative normalized definition
- preserve existing execution-history safety checks

Suggested target tests:

- `tests/unit/test_workflow_registry.py`
- API route tests covering `/api/admin/workflows/sync`
- worker/run route tests covering `step_execution_spec`

### Constraints

This phase should avoid an immediate database migration.

Pragmatic transitional rule:

- relational step/artifact/coder rows may remain for now
- `raw_definition` becomes authoritative immediately
- denormalized rows become cache/index data generated mechanically from the
  authoritative raw definition

### Exit Criteria For Phase 4

Phase 4 is complete when:

1. backend accepts locally validated workflow definitions without re-owning
   runner semantics
2. worker `step_execution_spec` payloads are generated from
   `workflow.raw_definition`
3. backend read APIs present the synced normalized definition as authoritative
4. backend still preserves execution-history safety and current run/step tables
   without requiring a schema migration

## Acceptance Criteria

This refactor is complete when:

1. workflow bundle validation is available as a local CLI command
2. sync to backend refuses to POST invalid local workflow definitions
3. validation logic is owned in one place inside `agent-runner-v2`
4. backend sync failures are clearly separated into:
   - local validation failures
   - backend transport/storage failures
5. normal workflow-definition changes do not require backend code changes just
   to pass local validation and reach the sync endpoint
