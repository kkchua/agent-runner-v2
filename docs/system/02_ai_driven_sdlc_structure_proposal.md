# 02 AI-Driven SDLC Structure Proposal

## Purpose

This document proposes a repo-level SDLC file structure and workflow split for
an AI-driven development lifecycle in `agent-runner-v2`.

The proposal is designed to:

- keep AI as a first-class execution engine
- preserve human approval on critical decisions
- persist SDLC context as repo artifacts
- split the lifecycle into multiple specialized workflows
- use artifact-semantic folders instead of workflow-step folders

This proposal assumes the Layer 2 repo baseline defined in:

- `docs/system/01_layer2_repo_master_docs_solution_proposal.md`

That means the initial repo-level SDLC governance package under
`docs/repo/sdlc/00_governance/` is owned by
`00_master_docs_bootstrap_v2`, not by a separate first-pass SDLC workflow.

## External Reference Model

This proposal aligns to the recent AI-DLC direction described by AWS:

- AI creates plans, asks clarifying questions, and implements only after human
  validation
- context is persisted in repo artifacts across lifecycle phases
- the lifecycle is organized into Inception, Construction, and Operations
- work is broken into shorter, faster cycles with strong traceability

Reference sources:

- AWS DevOps blog: AI-Driven Development Life Cycle
- AWS Builder content: AI-driven product development lifecycle
- Medium critique: AI-DLC as promising but requiring stronger conceptual clarity

## Core Design Decision

The current `docs/repo/delivery/` structure is too workflow-centric.

It groups artifacts by execution stage such as `01_init` and `02_plans`, which
causes distinct SDLC artifacts like `DRAFT_PRE_INIT`, `PRE_INIT`, `INIT`,
`PLAN`, and `TASK_GRAPH` to be forced into the same folder even though they are
semantically different.

The new structure should group by artifact meaning, not by the historical step
that created it.

## Naming Direction

Use `docs/repo/sdlc/` as the canonical root.

Reasons:

- `sdlc` better matches the domain than `delivery`
- it supports multiple workflows without implying one specific execution style
- it is easier to map to AI-driven phases and product-engineering language

Keep `docs/repo/delivery/` only as a legacy compatibility alias during
migration.

## Proposed SDLC Root Structure

```text
docs/repo/sdlc/
  00_governance/
    README.md
    SDLC_WORKFLOW_SOP.md
    SDLC_STATUS_RULES.md
    SDLC_FOLDER_MAP.md

  01_requirements/
    DRAFT_PRE_INIT.md
    PRE_INIT.md
    INITIATIVE.md
    REQUIREMENTS.md
    ACCEPTANCE_CRITERIA.md

  02_planning/
    PLAN.md
    PLAN_REVIEW.md
    PLAN_APPROVAL.md
    CONTEXT_PACK.md

  03_backlog/
    TASK_GRAPH.md
    BACKLOG.md
    STORY_MAP.md
    STORY_INDEX.md

  04_tasks/
    TASK-001.md
    TASK-002.md
    TASK-003.md

  05_implementation/
    IMPL-001.md
    IMPL-002.md
    CHANGESET_SUMMARY.md

  06_review/
    REVIEW-001.md
    REVIEW-002.md
    DEFECT_LOG.md

  07_execution/
    EXECUTION_LOG.md
    RUN_STATUS.md
    DECISIONS.md

  08_validation/
    VALIDATION-001.md
    VALIDATION-002.md
    REGRESSION_REPORT.md

  09_memory/
    MEMORY.md
    LESSONS_LEARNED.md
    REUSABLE_PATTERNS.md

  10_archive/
```

## AI-Driven Phase Mapping

The folder model should map to three AI-driven macro phases.

### Inception

Owns:

- `01_requirements/`
- `02_planning/`
- `03_backlog/`

Primary behavior:

- AI expands business intent into structured requirements
- AI proposes planning decomposition
- humans approve scope, intent, and priority

### Construction

Owns:

- `04_tasks/`
- `05_implementation/`
- `06_review/`
- `08_validation/`

Primary behavior:

- AI executes implementation work from approved context
- AI proposes code and tests
- humans make critical architecture and acceptance decisions

### Operations

Owns:

- `07_execution/`
- `09_memory/`
- selected records in `10_archive/`

Primary behavior:

- AI maintains run logs and execution context
- AI records reusable memory and lessons learned
- humans govern promotion, rollout, and exception handling

## Workflow Split

The SDLC should be implemented as a workflow family, not one giant workflow.

Recommended workflow bundles:

### 10_requirement_intake_v1

Owns:

- `DRAFT_PRE_INIT.md`
- `PRE_INIT.md`
- `INITIATIVE.md`
- `REQUIREMENTS.md`
- `ACCEPTANCE_CRITERIA.md`

Purpose:

- transform rough intent into approved requirement artifacts

### 20_planning_v1

Owns:

- `PLAN.md`
- `PLAN_REVIEW.md`
- `PLAN_APPROVAL.md`
- `CONTEXT_PACK.md`

Purpose:

- create execution strategy from approved requirements

### 30_backlog_design_v1

Owns:

- `TASK_GRAPH.md`
- `BACKLOG.md`
- `STORY_MAP.md`
- `STORY_INDEX.md`

Purpose:

- decompose plan into sequenced backlog and story structure

### 40_task_preparation_v1

Owns:

- task records under `04_tasks/`

Purpose:

- turn approved backlog items into executable task units

### 50_task_execution_v1

Owns:

- implementation records under `05_implementation/`
- execution records under `07_execution/`

Purpose:

- perform the actual task implementation cycle

### 60_review_v1

Owns:

- review records under `06_review/`

Purpose:

- perform structured review against implementation and requirement intent

### 70_validation_v1

Owns:

- validation artifacts under `08_validation/`

Purpose:

- verify correctness, regression posture, and completion status

### 80_memory_capture_v1

Owns:

- memory artifacts under `09_memory/`

Purpose:

- persist reusable project intelligence for future AI and human runs

## Recommended Artifact Renaming

Current internal artifact keys can remain stable initially, but file semantics
should shift toward SDLC naming.

Recommended mapping:

| Current Key | Proposed Canonical File |
|-------------|--------------------------|
| `DRAFT_INIT_FILE` | `01_requirements/DRAFT_PRE_INIT.md` |
| `PRE_INIT_FILE` | `01_requirements/PRE_INIT.md` |
| `INIT_FILE` | `01_requirements/INITIATIVE.md` |
| `PLAN_FILE` | `02_planning/PLAN.md` |
| `TASK_GRAPH_FILE` | `03_backlog/TASK_GRAPH.md` |
| `TASK_FILE` | `04_tasks/TASK-xxx.md` |
| `IMPL_FILE` | `05_implementation/IMPL-xxx.md` |
| `REVIEW_FILE` | `06_review/REVIEW-xxx.md` |
| `VALIDATION_FILE` | `08_validation/VALIDATION-xxx.md` |
| `CONTEXT_PACK_FILE` | `02_planning/CONTEXT_PACK.md` |

## Folder Naming Rules

### Required rules

- Folder names must describe artifact semantics, not workflow step order.
- Workflow names and folder names must not be tightly coupled.
- AI-generated records must be traceable to one governing workflow family.
- Cross-workflow handoff must occur through approved artifacts, not hidden state.

### Avoid

- `01_init/`
- `02_plan_task/`
- `03_step_execution/`
- any folder named after an internal runner step

### Prefer

- `01_requirements/`
- `02_planning/`
- `03_backlog/`
- `04_tasks/`
- `05_implementation/`

## SDLC Governance Files

`00_governance/` should hold the repo-level SDLC operating contract.

This governance package should be created by the Layer 2 repo master-doc
bootstrap described in
`docs/system/01_layer2_repo_master_docs_solution_proposal.md`.

Recommended files:

- `README.md`
  - explains the repo SDLC model and workflow family overview
- `SDLC_WORKFLOW_SOP.md`
  - defines the standard operating pattern for AI-driven repo delivery
- `SDLC_STATUS_RULES.md`
  - defines allowed states, transitions, approvals, and completion rules
- `SDLC_FOLDER_MAP.md`
  - maps artifact keys, filenames, owners, and producing workflows

## Human Oversight Model

Human approval should be explicit at these boundaries:

- requirements approval
- plan approval
- backlog approval
- architecture-significant task approval
- release or validation sign-off

AI should drive:

- decomposition
- artifact drafting
- implementation planning
- execution support
- review preparation
- validation evidence generation

## Migration Strategy

### Phase 1

- restore and complete `00_master_docs_bootstrap_v2` as the live Layer 2
  bootstrap workflow
- generate the repo master-doc baseline
- generate the initial `docs/repo/sdlc/00_governance/` package
- keep current artifact keys

### Phase 2

- introduce `docs/repo/sdlc/`
- add path aliases from legacy `docs/repo/delivery/`
- rename workflow families around requirements, planning, backlog, tasks,
  implementation, review, validation, and memory
- update constants and validators to treat `sdlc/` as canonical

### Phase 3

- remove `delivery/` as the canonical root
- keep only read-only legacy compatibility if still needed

## Recommendation

Adopt this canonical root:

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
```

This structure best fits:

- AI-driven persistent context
- multiple specialized workflows
- human-gated approvals
- SDLC-style naming
- long-term repo governance

## Next Follow-Up

The next implementation step should be a path-and-artifact migration plan for:

- `agent_runner_v2/constants.py`
- SDLC workflow artifact ownership
- legacy `docs/repo/delivery/` compatibility
- workflow family renaming and split sequencing

That migration should be read after:

1. `docs/system/01_layer2_repo_master_docs_solution_proposal.md`
2. this document
