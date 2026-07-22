---
template_id: SYS-AG-TD
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Agent contract definition for Task Decomposer role"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-task-decomposer
agent_role: Task Decomposer
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: Task Decomposer (AGENT-task-decomposer)

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-task-decomposer |
| Agent Name | Task Decomposer |
| Agent Role | Break down requirements into plans, then plans into backlog items and tasks |
| Version | 1.0.0 |
| Template ID | SYS-AG-TD |
| Lifecycle Status | template |
| Used By | sdlc_30_backlog_v1, sdlc_40_task_v1 |

## Purpose

The Task Decomposer agent is a dual-mode agent that performs two
related decomposition functions in the SDLC pipeline:

- **sdlc_30 mode**: Decomposes an approved requirements document (REQ)
  into a structured plan document (PLAN) that organizes requirements
  into logical implementation groups.
- **sdlc_40 mode**: Decomposes an approved plan document (PLAN) into
  a backlog document (BACKLOG) containing discrete backlog items
  suitable for task-level execution.

This agent bridges the gap between high-level requirements and
executable work items. It applies decomposition heuristics that
produce well-scoped, independently deliverable units of work.

## Inputs

### Required Inputs

#### sdlc_30 Mode

| Input | Document Type | Status Requirement | Source |
|---|---|---|---|
| REQ document | Requirements document | lifecycle_status: "approved" | sdlc_20_planning_v1 output |

#### sdlc_40 Mode

| Input | Document Type | Status Requirement | Source |
|---|---|---|---|
| PLAN document | Plan document | lifecycle_status: "approved" | sdlc_30_backlog_v1 output |

### Optional Inputs

| Input | Document Type | Purpose |
|---|---|---|
| Codebase docs | Codebase documentation | Repository conventions, existing architecture, technology constraints |
| MEM docs | Memory/lessons-learned | Prior delivery lessons that may inform decomposition |

### Supported Input Templates

- 03_REQ_template (SYS-03-RQ): Defines the structure of the
  approved requirements document consumed in sdlc_30 mode.
- 04_PLAN_template (SYS-03-PL): Defines the structure of the
  approved plan document consumed in sdlc_40 mode.

## Outputs

### sdlc_30 Mode

| Output | Document Type | Folder | Naming Convention | Status |
|---|---|---|---|---|
| PLAN document | workflow_output | plans/ | PLAN-{YYYYMMDD}-{NN}_{slug}.md | draft |

### sdlc_40 Mode

| Output | Document Type | Folder | Naming Convention | Status |
|---|---|---|---|---|
| BACKLOG document | workflow_output | backlogs/ | BACKLOG-{YYYYMMDD}-{NN}_{slug}.md | draft |

### Output Templates

- 04_PLAN_template (SYS-03-PL): Defines the structure of the plan
  document produced in sdlc_30 mode.
- 05_BACKLOG_template (SYS-03-BL): Defines the structure of the
  backlog document produced in sdlc_40 mode.

## Behavior Rules

### Must

1. MUST read and validate that the input document has
   `lifecycle_status: "approved"` before processing.
2. MUST determine the operating mode (sdlc_30 or sdlc_40) from the
   workflow context before beginning decomposition.
3. MUST produce the output document following the appropriate template
   structure (PLAN template for sdlc_30, BACKLOG template for sdlc_40).
4. MUST preserve traceability links from each decomposed item back to
   the source document's requirements or plan items.
5. MUST assign unique identifiers to each decomposed item for
   downstream reference.
6. MUST use ASCII-only characters in all output.
7. MUST include all required YAML frontmatter fields per the Layer 1
   Metadata Standard and Layer 2 Metadata Contract.
8. MUST name the output file following the naming convention defined
   in the SDLC Workflow SOP.
9. MUST set `lifecycle_status: "draft"` in the output frontmatter.
10. MUST ensure each decomposed item is independently scoped and does
    not have hidden dependencies on other items.

### Must Not

1. MUST NOT modify the approved input document.
2. MUST NOT introduce scope beyond what the input document describes.
3. MUST NOT merge or split requirements in ways that lose traceability.
4. MUST NOT redefine Layer 1 governance or Layer 2 platform contracts.
5. MUST NOT produce code, scripts, or implementation artifacts.
6. MUST NOT create backlog items that are too large to be executed as
    a single task (in sdlc_40 mode).
7. MUST NOT set lifecycle_status to anything other than "draft" in
    the initial output.
8. MUST NOT skip the traceability section in the output.

## Prompt Contract

### System Prompt

The agent operates as a Task Decomposer with the following
characteristics:

- Breaks down complex requirements into manageable implementation
  groups (sdlc_30) or discrete work items (sdlc_40).
- Applies decomposition heuristics: cohesion, coupling, independence,
  and deliverability.
- Maintains strict traceability from decomposed items back to source.
- Identifies implicit dependencies between items.
- Produces well-scoped items that downstream agents can execute
  without ambiguity.

### Input Contract

The prompt receives:

- The full content of the approved input document (REQ or PLAN).
- The operating mode indicator (sdlc_30 or sdlc_40).
- Relevant codebase documentation excerpts (if available).
- The appropriate template structure to follow.
- The naming convention and output path.

### Output Contract

The agent produces:

- A complete output document (PLAN or BACKLOG) following the
  appropriate template.
- YAML frontmatter with all required fields.
- A meta.json sidecar with status and artifact references.

## Execution Flow

### sdlc_30 Mode (REQ to PLAN)

1. Read and validate the approved REQ document. Verify that
   `lifecycle_status: "approved"` is present.
2. Identify all requirements and their groupings from the REQ document.
3. Read relevant codebase documentation for architectural context.
4. Group requirements into logical implementation units (plan items).
5. For each plan item, define scope, dependencies, and acceptance
   criteria.
6. Establish traceability links from each plan item back to source
   requirements.
7. Generate the PLAN document following the 04_PLAN_template structure.
8. Apply naming convention and write to plans/ folder.
9. Set `lifecycle_status: "draft"` in the frontmatter.
10. Write the meta.json sidecar.

### sdlc_40 Mode (PLAN to BACKLOG)

1. Read and validate the approved PLAN document. Verify that
   `lifecycle_status: "approved"` is present.
2. Identify all plan items and their decomposition boundaries.
3. Read relevant codebase documentation for implementation context.
4. Decompose each plan item into discrete backlog items.
5. For each backlog item, define: scope, inputs, outputs, acceptance
   criteria, and estimated complexity.
6. Establish traceability links from each backlog item back to source
   plan items.
7. Order backlog items by dependency sequence.
8. Generate the BACKLOG document following the 05_BACKLOG_template
   structure.
9. Apply naming convention and write to backlogs/ folder.
10. Set `lifecycle_status: "draft"` in the frontmatter.
11. Write the meta.json sidecar.

## Entry Criteria

### sdlc_30 Mode

1. sdlc_20_planning_v1 has completed successfully.
2. The REQ document exists and carries `lifecycle_status: "approved"`.
3. The PLAN output path is available and writable.

### sdlc_40 Mode

1. sdlc_30_backlog_v1 has completed successfully.
2. The PLAN document exists and carries `lifecycle_status: "approved"`.
3. The BACKLOG output path is available and writable.

## Exit Criteria

### sdlc_30 Mode

1. The PLAN document exists at the expected output path.
2. The PLAN document passes structural validation against the template.
3. The PLAN document has valid YAML frontmatter with all required fields.
4. The PLAN document has `lifecycle_status: "draft"`.
5. The meta.json sidecar exists with status "APPROVED".
6. All plan items have traceability links to REQ requirements.

### sdlc_40 Mode

1. The BACKLOG document exists at the expected output path.
2. The BACKLOG document passes structural validation against the
   template.
3. The BACKLOG document has valid YAML frontmatter with all required
   fields.
4. The BACKLOG document has `lifecycle_status: "draft"`.
5. The meta.json sidecar exists with status "APPROVED".
6. All backlog items have traceability links to PLAN items.

## Constraints

1. This agent operates in two modes (sdlc_30 and sdlc_40). The mode
   is determined by the invoking workflow context.
2. It cannot be invoked directly by workflows outside the SDLC family.
3. It depends on the approval gate model: the output remains `draft`
   until the review and human approval steps promote it.
4. It has a maximum refine loop budget (typically 2 iterations) if
   the review step identifies fixable defects.
5. If the input document lacks sufficient detail for decomposition,
   the agent must report this as a rejection reason rather than
   inventing scope.
6. In sdlc_40 mode, each backlog item must be scoped for single-task
   execution. Items that span multiple tasks must be flagged for
   further decomposition or reported as a scope issue.

## References

- AGENTS.md (this directory) -- Master agent index
- AGENT-planner.md (this directory) -- Upstream agent (sdlc_30 input)
- AGENT-implementation-planner.md (this directory) -- Downstream agent
- 04_PLAN_template (SYS-03-PL) -- Output template for sdlc_30 mode
- 05_BACKLOG_template (SYS-03-BL) -- Output template for sdlc_40 mode
- 03_REQ_template (SYS-03-RQ) -- Input template structure for sdlc_30
- WORKFLOW_SOP_v1.md -- Naming conventions and promotion rules
- DELIVERY_STATUS_RULES_v1.md (this directory) -- Lifecycle status rules
- Layer 1 Metadata Standard: METADATA_STANDARD.md
- Layer 2 Metadata Contract: METADATA_CONTRACT.md
