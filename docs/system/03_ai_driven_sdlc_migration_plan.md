# 03 AI-Driven SDLC Migration Plan

## Purpose

This document translates the SDLC structure proposal into a concrete runtime
migration plan for `agent_runner_v2`.

It focuses on:

- `agent_runner_v2/constants.py`
- artifact-key to file-path ownership
- legacy `docs/repo/delivery/` compatibility
- workflow-family split sequencing
- validator and prompt impacts

This migration plan depends on:

- `docs/system/01_layer2_repo_master_docs_solution_proposal.md`
- `docs/system/02_ai_driven_sdlc_structure_proposal.md`

It assumes `00_master_docs_bootstrap_v2` is the Layer 2 owner that creates the
initial repo-level SDLC governance baseline under
`docs/repo/sdlc/00_governance/`.

## Current Runtime Baseline

As of `2026-07-16`, the runtime still treats the legacy delivery model as the
canonical SDLC structure.

Observed in `agent_runner_v2/constants.py`:

- artifact keys still use delivery-era semantics
  - `DRAFT_INIT_FILE`
  - `PRE_INIT_FILE`
  - `INIT_FILE`
  - `PLAN_FILE`
  - `TASK_GRAPH_FILE`
  - `TASK_FILE`
  - `IMPL_FILE`
  - `REVIEW_FILE`
  - `VALIDATION_FILE`
  - `CONTEXT_PACK_FILE`
- folder constants still point to `docs/repo/delivery/*`
- `delivery_scaffold_docs()` still exposes the delivery scaffold as a primary
  runtime registry
- `known_artifact_paths()` includes `delivery_scaffold_docs()` as canonical
  known paths
- `legacy_artifact_paths()` already exists and can be used as the migration
  compatibility layer

This means the runtime is not yet aligned to the proposed
`docs/repo/sdlc/` structure.

## Migration Goal

Make `docs/repo/sdlc/` the only canonical SDLC root for new workflows, while
keeping `docs/repo/delivery/` as a temporary read-only compatibility alias.

The runtime should become:

- semantic-folder based
- workflow-agnostic at the path layer
- compatible with multi-workflow SDLC orchestration
- explicit about which paths are canonical versus legacy

## Canonical SDLC Root

```text
docs/repo/sdlc/
  00_governance/
  01_requirements/
  02_planning/
  03_backlog/
  04_tasks/
  05_implementation/
  06_review/
  07_execution/
  08_validation/
  09_memory/
  10_archive/
```

## Artifact Mapping

Keep the existing artifact key literals during the first migration stage, but
change their canonical output paths.

| Current Artifact Key | Current Meaning | Canonical SDLC Path |
|---|---|---|
| `DRAFT_INIT_FILE` | draft pre-init intent | `docs/repo/sdlc/01_requirements/DRAFT_PRE_INIT.md` |
| `PRE_INIT_FILE` | structured pre-init | `docs/repo/sdlc/01_requirements/PRE_INIT.md` |
| `INIT_FILE` | approved initiative/init | `docs/repo/sdlc/01_requirements/INITIATIVE.md` |
| `PLAN_FILE` | execution plan | `docs/repo/sdlc/02_planning/PLAN.md` |
| `CONTEXT_PACK_FILE` | planning context pack | `docs/repo/sdlc/02_planning/CONTEXT_PACK.md` |
| `TASK_GRAPH_FILE` | backlog decomposition | `docs/repo/sdlc/03_backlog/TASK_GRAPH.md` |
| `TASK_FILE` | task unit | `docs/repo/sdlc/04_tasks/TASK-{id}.md` |
| `IMPL_FILE` | implementation record | `docs/repo/sdlc/05_implementation/IMPL-{id}.md` |
| `REVIEW_FILE` | review result | `docs/repo/sdlc/06_review/REVIEW-{id}.md` |
| `VALIDATION_FILE` | validation result | `docs/repo/sdlc/08_validation/VALIDATION-{id}.md` |

## New Constant Model

Replace the old delivery-centric folder constants with SDLC-centric constants.

### Add

- `FOLDER_KEY_SDLC_DOC_ROOT = "docs/repo/sdlc"`
- `FOLDER_KEY_SDLC_GOVERNANCE = "docs/repo/sdlc/00_governance"`
- `FOLDER_KEY_SDLC_REQUIREMENTS = "docs/repo/sdlc/01_requirements"`
- `FOLDER_KEY_SDLC_PLANNING = "docs/repo/sdlc/02_planning"`
- `FOLDER_KEY_SDLC_BACKLOG = "docs/repo/sdlc/03_backlog"`
- `FOLDER_KEY_SDLC_TASKS = "docs/repo/sdlc/04_tasks"`
- `FOLDER_KEY_SDLC_IMPLEMENTATION = "docs/repo/sdlc/05_implementation"`
- `FOLDER_KEY_SDLC_REVIEW = "docs/repo/sdlc/06_review"`
- `FOLDER_KEY_SDLC_EXECUTION = "docs/repo/sdlc/07_execution"`
- `FOLDER_KEY_SDLC_VALIDATION = "docs/repo/sdlc/08_validation"`
- `FOLDER_KEY_SDLC_MEMORY = "docs/repo/sdlc/09_memory"`
- `FOLDER_KEY_SDLC_ARCHIVE = "docs/repo/sdlc/10_archive"`

### Keep temporarily as compatibility aliases

- `FOLDER_KEY_DELIVERY_DOC_ROOT`
- `FOLDER_KEY_DELIVERY_STANDARDS`
- `FOLDER_KEY_DELIVERY_INITIATIVES`
- `FOLDER_KEY_DELIVERY_PLANS`
- `FOLDER_KEY_DELIVERY_TASKS`
- `FOLDER_KEY_DELIVERY_IMPLEMENTATIONS`
- `FOLDER_KEY_DELIVERY_REVIEWS`
- `FOLDER_KEY_DELIVERY_VALIDATIONS`
- `FOLDER_KEY_DELIVERY_MEMORY`
- `FOLDER_KEY_DELIVERY_AGENTS`

These legacy constants should be explicitly marked:

- read-only
- compatibility only
- not valid for new workflow output declarations

## Path Registry Refactor

`constants.py` should be split conceptually into three layers.

### Layer A: canonical path builders

These functions define the active repo contract:

- `sdlc_doc_rel(...)`
- `sdlc_governance_rel(...)`
- `sdlc_requirements_rel(...)`
- `sdlc_planning_rel(...)`
- `sdlc_backlog_rel(...)`
- `sdlc_tasks_rel(...)`
- `sdlc_implementation_rel(...)`
- `sdlc_review_rel(...)`
- `sdlc_execution_rel(...)`
- `sdlc_validation_rel(...)`
- `sdlc_memory_rel(...)`

### Layer B: canonical artifact registries

Replace delivery-centric registries with SDLC registries:

- `sdlc_governance_docs()`
- `sdlc_artifact_paths()`
- `known_artifact_paths()`

`known_artifact_paths()` should only expose canonical `docs/repo/sdlc/` paths
for active SDLC artifacts.

### Layer C: legacy compatibility registry

Keep legacy lookups isolated in:

- `legacy_artifact_paths()`

This function should be the only place that knows about
`docs/repo/delivery/*` after migration.

## Required Runtime Changes

### 1. Canonicalize SDLC path generation

Update any workflow or action that currently writes to:

- `docs/repo/delivery/*`

to instead write to:

- `docs/repo/sdlc/*`

### 2. Stop exposing delivery as canonical

Refactor:

- `delivery_scaffold_docs()`

Options:

1. rename it to `sdlc_scaffold_docs()` and point it to `docs/repo/sdlc/*`
2. keep the function name temporarily for compatibility, but its returned paths
   must become SDLC canonical

Recommended:

- rename to `sdlc_scaffold_docs()`
- add a thin deprecated alias only if needed by existing imports

### 3. Tighten artifact ownership

Each future workflow bundle should own only its artifact domain.

Example:

- `10_requirement_intake_v1`
  - only `01_requirements/*`
- `20_planning_v1`
  - only `02_planning/*`
- `30_backlog_design_v1`
  - only `03_backlog/*`
- `40_task_preparation_v1`
  - only `04_tasks/*`
- `50_task_execution_v1`
  - only `05_implementation/*` and selected `07_execution/*`
- `60_review_v1`
  - only `06_review/*`
- `70_validation_v1`
  - only `08_validation/*`
- `80_memory_capture_v1`
  - only `09_memory/*`

### 4. Tighten validators

Validators should reject:

- new workflow outputs under `docs/repo/delivery/*`
- prompts that instruct models to write to delivery-era folders
- cross-phase artifact leakage

Validators should allow:

- reading legacy delivery paths only during migration

### 5. Tighten prompt contracts

Prompt templates should stop using workflow-stage folder language such as:

- init folder
- plan folder
- implementation plan folder

Prompt language should instead use:

- requirements artifact
- planning artifact
- backlog artifact
- task artifact
- implementation artifact
- review artifact
- validation artifact

## Workflow Migration Sequence

### Phase 1: Layer 2 bootstrap prerequisite

Scope:

- restore `00_master_docs_bootstrap_v2` under `workflows/`
- complete its migration to the shared registry/runtime model
- generate repo master docs and the initial `docs/repo/sdlc/00_governance/`
  package

Exit criteria:

- the repo has a real Layer 2 owner and a canonical repo-level SDLC operating
  contract

### Phase 2: Runtime path foundation

Scope:

- add SDLC folder constants
- add SDLC path helpers
- add canonical SDLC artifact registry
- move delivery registry behind compatibility layer

Exit criteria:

- new code can resolve all SDLC paths without touching delivery constants

### Phase 3: Requirement and planning workflow split

Scope:

- introduce requirement workflow bundle
- introduce planning workflow bundle
- introduce backlog workflow bundle

Exit criteria:

- no new workflow depends on `docs/repo/delivery/*`

### Phase 4: Execution family migration

Scope:

- migrate task preparation
- migrate implementation execution
- migrate review
- migrate validation
- migrate memory capture

Exit criteria:

- all active SDLC workflows write only to `docs/repo/sdlc/*`

### Phase 5: Compatibility freeze

Scope:

- mark delivery paths as deprecated
- remove delivery paths from active prompt instructions
- keep read-only fallback resolution only in `legacy_artifact_paths()`

Exit criteria:

- `docs/repo/delivery/*` is no longer canonical anywhere in runtime logic

## Files To Change First

The initial implementation should start with:

1. restore `workflows/00_master_docs_bootstrap_v2`
2. `agent_runner_v2/constants.py`
3. any path resolver using `delivery_scaffold_docs()`
4. any validator that inspects repo output paths

## Do Not Do

- do not rename artifact key literals in the first pass
- do not mix canonical SDLC paths with new delivery outputs
- do not let prompts choose arbitrary folder names
- do not let workflow names define folder structure

## Recommended Immediate Next Steps

1. Add the SDLC folder constants and helper functions to `constants.py`.
2. Introduce `sdlc_scaffold_docs()` and make it the canonical registry.
3. Restrict `legacy_artifact_paths()` to compatibility-only lookup.
4. Extend `00_master_docs_bootstrap_v2` to emit the `00_governance/` baseline.
5. Migrate the first specialized workflow as `10_requirement_intake_v1`.

## Source Alignment

This plan implements the structure proposed in:

- `docs/system/02_ai_driven_sdlc_structure_proposal.md`
- `docs/system/01_layer2_repo_master_docs_solution_proposal.md`

It also reflects the current runtime baseline in:

- `agent_runner_v2/constants.py`

## Decision

Proceed with a staged runtime migration where:

- `docs/repo/sdlc/` becomes canonical
- `docs/repo/delivery/` becomes compatibility-only
- workflow bundles become domain-scoped by SDLC artifact ownership
