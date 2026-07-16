# 01 Layer 2 Repo Master Docs Solution Proposal

## Purpose

This document defines the missing Layer 2 solution for `agent-runner-v2`.

It answers the question:

- what should `00_master_docs_bootstrap_v2` actually establish before the
  downstream SDLC workflow family is introduced

This is not a Layer 1 governance document and not a Layer 3 workflow-family
plan. It is the repo-level master-doc proposal that sits between them.

## Problem

The repository now has Layer 1 governance under
`docs/system/00_governance/bootstrap/`, but it does not yet have an active
Layer 2 master-doc bootstrap package under `workflows/00_master_docs_bootstrap_v2/`.

At the same time, the SDLC planning docs already assume a repo-level operating
model and SDLC governance structure that would normally be created by Layer 2.

That leaves a structural gap:

- Layer 1 exists
- Layer 3 direction is being designed
- Layer 2 repo master docs are not yet established as a live workflow-owned
  baseline

## Proposed Role of Layer 2

`00_master_docs_bootstrap_v2` should be the canonical Layer 2 repo master-doc
bootstrap for this repository.

Its job is to translate generic Layer 1 governance into concrete
repository-specific operating structure.

Layer 2 should establish:

- what this repository is
- how the repository is structured
- how the runtime and workflow families fit together
- where canonical repo-level documentation lives
- how repo-level SDLC artifacts are organized
- how humans and AI agents navigate the repository

Layer 2 should not establish:

- ecosystem-wide governance rules that belong to Layer 1
- run-local execution artifacts that belong to Layer 3
- workflow-family-specific detailed SOPs for every downstream bundle

## Target Outcome

The output of `00_master_docs_bootstrap_v2` should be a coherent repo master
documentation baseline with two connected surfaces:

1. repository system/master docs under `docs/system/`
2. repo-level SDLC operating docs under `docs/repo/sdlc/00_governance/`

The first surface explains the repository as a system.

The second surface explains the repository's operating contract for AI-driven
SDLC workflows.

These two surfaces should be generated together because they describe the same
Layer 2 operating model from different angles.

## Proposed Layer 2 Document Set

### A. Repository System / Master Docs

These documents describe the repository as a software and workflow system.

Proposed outputs:

- `PROJECT_ANALYSIS`
- `SYSTEM_DOCS_INDEX`
- `SYSTEM_DOC_STANDARD`
- `BUNDLE_TAXONOMY`
- `SYSTEM_OVERVIEW`
- `BUSINESS_CAPABILITIES`
- `FUNCTIONAL_SPEC`
- `NON_FUNCTIONAL_REQUIREMENTS`
- `SYSTEM_CONTEXT`
- `COMPONENT_ARCHITECTURE`
- `DECISION_LOG`
- `SYSTEM_FILE_STRUCTURE`
- `DEVELOPER_GUIDE`
- `RUNBOOK`
- `INTEGRATION_MAP`
- `FAILURE_MODES`
- `ARCHITECTURE_FLOW`
- `SYSTEM_DOCS_VALIDATION`
- `BOOTSTRAP_SUMMARY`

These already align with the archived `00_master_docs_bootstrap_v2` workflow
shape and should remain the core Layer 2 repo-master-doc set.

### B. Repo-Level SDLC Governance Package

These documents establish the repo-specific SDLC operating contract that
downstream workflow families consume.

Proposed outputs under `docs/repo/sdlc/00_governance/`:

- `README.md`
- `SDLC_WORKFLOW_SOP.md`
- `SDLC_STATUS_RULES.md`
- `SDLC_FOLDER_MAP.md`

These should not be created by a separate first-pass SDLC workflow. They
should be emitted by `00_master_docs_bootstrap_v2` as part of the Layer 2
bootstrap baseline.

## Ownership Model

`00_master_docs_bootstrap_v2` should own the initial creation and refresh of:

- repo master docs under `docs/system/`
- repo SDLC governance docs under `docs/repo/sdlc/00_governance/`

Downstream workflow families should then own only their domain artifacts:

- requirements workflows own `01_requirements/`
- planning workflows own `02_planning/`
- backlog workflows own `03_backlog/`
- task workflows own `04_tasks/`
- implementation workflows own `05_implementation/`
- review workflows own `06_review/`
- execution workflows own `07_execution/`
- validation workflows own `08_validation/`
- memory workflows own `09_memory/`

This means Layer 2 owns the repo contract, while Layer 3 owns the repo usage.

## Proposed Directory Contract

The Layer 2 solution should standardize these roots:

### `docs/system/`

Use for repository master/system understanding.

This root should contain:

- system overview and architecture views
- developer/operator guidance
- integration and failure analysis
- master-doc indexes and validation outputs
- planning/design documents about repo evolution

### `docs/repo/sdlc/00_governance/`

Use for repo-specific SDLC operating rules.

This root should define:

- the repo SDLC model
- workflow-family handoff expectations
- approval boundaries
- allowed artifact states and transitions
- canonical artifact/folder ownership

### `docs/repo/sdlc/01_*` onward

Use for downstream execution artifacts created by specialized workflow
families after Layer 2 is in place.

## Proposed Workflow Scope for `00_master_docs_bootstrap_v2`

The workflow should have four responsibilities.

### 1. Scan and analyze the repository

This includes:

- codebase inventory
- change-impact baseline
- runtime and integration understanding
- current workflow and artifact structure analysis

### 2. Generate repo master/system docs

This includes:

- the existing archived output family already defined in the workflow

### 3. Generate the repo SDLC governance baseline

This includes:

- `docs/repo/sdlc/00_governance/README.md`
- `docs/repo/sdlc/00_governance/SDLC_WORKFLOW_SOP.md`
- `docs/repo/sdlc/00_governance/SDLC_STATUS_RULES.md`
- `docs/repo/sdlc/00_governance/SDLC_FOLDER_MAP.md`

### 4. Validate repo master-doc coherence

Validation should ensure:

- Layer 1 and Layer 2 boundaries are respected
- repo-specific assumptions are documented only in Layer 2
- SDLC governance docs align with system docs
- downstream workflow ownership is clearly partitioned

## Proposed Content of the Repo SDLC Governance Package

### `README.md`

Should explain:

- the repo's AI-driven SDLC model
- the workflow-family overview
- the relationship between `docs/system/` and `docs/repo/sdlc/`
- the handoff from Layer 2 governance to Layer 3 execution

### `SDLC_WORKFLOW_SOP.md`

Should define:

- the standard repo operating pattern for AI-assisted work
- required approval points
- artifact progression across requirements, planning, execution, review, and
  validation
- the expected interaction between humans, coders, and runtime actions

### `SDLC_STATUS_RULES.md`

Should define:

- allowed artifact states
- required transitions
- rejection/refinement rules
- approval gates
- completion rules for workflow phases

### `SDLC_FOLDER_MAP.md`

Should define:

- canonical folder ownership
- artifact-key to file-path mapping
- producing workflow family
- consuming workflow family
- legacy compatibility notes for `docs/repo/delivery/`

## Sequencing Recommendation

The correct dependency order should be:

1. complete Layer 1 governance bootstrap
2. restore and finish `00_master_docs_bootstrap_v2` as a live workflow package
3. run Layer 2 bootstrap to generate repo master docs and SDLC governance docs
4. migrate runtime path constants toward `docs/repo/sdlc/`
5. introduce specialized SDLC workflow families

This means the first concrete prerequisite to the SDLC migration proposal is
not a new SDLC workflow bundle. It is the restoration and completion of
`00_master_docs_bootstrap_v2`.

## Implementation Direction

The archived `00_master_docs_bootstrap_v2` package should be used as the base.

Recommended implementation direction:

- restore it under `workflows/00_master_docs_bootstrap_v2/`
- complete its role-routing migration
- extend its prompt/output contract to include the repo SDLC governance package
- keep it as the canonical Layer 2 bootstrap owner

Do not create a separate first-pass workflow just to generate
`docs/repo/sdlc/00_governance/`.

That would split one Layer 2 responsibility across multiple bootstrap owners
too early and weaken the repo contract.

## Acceptance Criteria

The Layer 2 solution is complete when:

- `00_repo_master_docs_bootstrap_v1` exists as a live workflow package in
  `workflows/`
- the workflow generates repo master docs under `docs/repo/governance/`
- the ownership split between Layer 2 and downstream SDLC workflow families is
  explicit
- the SDLC migration docs can reference Layer 2 as an existing prerequisite,
  not an implied future gap
- validators and prompts can rely on a real repo-level governance contract

## Recommendation

Adopt `00_repo_master_docs_bootstrap_v1` as the single canonical Layer 2 repo
master-doc bootstrap.

Use it to establish:

- the repository master/system documentation baseline under `docs/repo/governance/`

Then treat all later SDLC workflows as specialized Layer 3 families operating
inside that Layer 2 contract.

## Status (Updated 2026-07-16)

Migration completed:
- Workflow migrated from `archive/workflows/00_master_docs_bootstrap_v2/` to `workflows/00_repo_master_docs_bootstrap_v1/`
- Output path changed from `docs/system/00_governance/bootstrap/` to `docs/repo/governance/`
- Legacy coder_roles.json deleted, using role-based routing
- Batch file created: `run-00_repo_master_docs_bootstrap_v1.bat`
