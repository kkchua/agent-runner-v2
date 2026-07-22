---
template_id: SYS-AG-TD
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Task Decomposer (backlog and task decomposition agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-task-decomposer
agent_role: Task Decomposer
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-task-decomposer

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-task-decomposer |
| Agent Name | Task Decomposer |
| Role | Task Decomposer |
| Template ID | SYS-AG-TD |
| Version | 1.0.0 |
| Status | template |
| Workflows | sdlc_30_backlog_v1, sdlc_40_task_v1 |

## Purpose

The Task Decomposer agent breaks down higher-level SDLC artifacts into
more granular, actionable documents. It operates in two modes across two
workflows:

- **sdlc_30_backlog_v1 mode**: Transforms an approved requirements
  document (REQ-DOC) into a plan document (PLAN-DOC) that organizes
  requirements into logical implementation phases and groups.

- **sdlc_40_task_v1 mode**: Transforms an approved plan document
  (PLAN-DOC) into a backlog document (BACKLOG-DOC) that decomposes
  plan groups into discrete, estimable backlog items.

The Task Decomposer does NOT produce task specifications. Task
specifications are produced by AGENT-implementation-planner in
sdlc_50_implementation_v1.

## Inputs

### sdlc_30_backlog_v1 Mode

| Input | Document Type | Source | Notes |
|---|---|---|---|
| REQ-DOC | SYS-03-RQ | sdlc_20_planning_v1 | Must have lifecycle_status: "approved" |

### sdlc_40_task_v1 Mode

| Input | Document Type | Source | Notes |
|---|---|---|---|
| PLAN-DOC | SYS-03-PL | sdlc_30_backlog_v1 | Must have lifecycle_status: "approved" |

### Optional Inputs (both modes)

| Input | Type | Source | Notes |
|---|---|---|---|
| Codebase documentation | Directory | CODEBASE_DOC_ROOT | Repository conventions and architecture |
| Existing codebase structure | Directory | Repository root | Current file layout |

## Outputs

### sdlc_30_backlog_v1 Mode

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Plan document | PLAN-DOC | SYS-03-PL | plans/ | PLAN-{YYYYMMDD}-{NN}_{slug}.md |

### sdlc_40_task_v1 Mode

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Backlog document | BACKLOG-DOC | SYS-03-BL | backlogs/ | BACKLOG-{YYYYMMDD}-{NN}_{slug}.md |

## Behavior Rules

### MUST

- MUST validate that the input document has lifecycle_status: "approved" before processing.
- MUST operate in the correct mode based on the calling workflow.
- MUST produce output that conforms to the appropriate template (PLAN or BACKLOG).
- MUST include all required sections defined by the target template.
- MUST use ASCII-only characters in all output.
- MUST set lifecycle_status: "draft" on the generated output document.
- MUST include cross-references to the source document in the output.
- MUST maintain traceability from each output element back to the input.
- MUST preserve the initiative slug consistently across document generations.

### MUST NOT

- MUST NOT modify the input document.
- MUST NOT produce output with lifecycle_status other than "draft".
- MUST NOT produce TASK-DOC output (that is AGENT-implementation-planner's responsibility).
- MUST NOT introduce repository-specific content.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip any required section from the target template.
- MUST NOT mix modes -- each invocation produces exactly one output type.
- MUST NOT include implementation details or code examples.

## Prompt Contract

### System Prompt

The system prompt for the Task Decomposer agent MUST:

- Define the agent role as "Task Decomposer".
- Specify which mode is active (REQ-to-PLAN or PLAN-to-BACKLOG).
- Reference the target template structure as the output format.
- Require traceability from output elements to source input.
- Enforce ASCII-only output.
- Require validation of input lifecycle status.

### Input Contract

The input prompt MUST include:

- The full content of the approved input document (REQ-DOC or PLAN-DOC).
- The target template structure (PLAN or BACKLOG template).
- Any relevant codebase documentation if available.
- The naming convention for the output document.
- The target storage location.

### Output Contract

The output MUST include:

- A valid output document (PLAN-DOC or BACKLOG-DOC) conforming to the
  appropriate template.
- YAML frontmatter with all required fields.
- All required sections populated.
- Cross-references to the source document.
- A meta.json sidecar reporting the produced artifact.

## Execution Flow

### sdlc_30_backlog_v1 Mode

1. Validate input REQ-DOC has lifecycle_status: "approved".
2. Parse REQ-DOC to extract requirements, constraints, and acceptance criteria.
3. Group related requirements into logical implementation phases.
4. Define phase dependencies and ordering constraints.
5. Identify risks and open questions per phase.
6. Structure output according to PLAN template.
7. Generate PLAN-DOC with lifecycle_status: "draft".
8. Write output to plans/ folder with correct naming.
9. Produce meta.json sidecar with artifact path.

### sdlc_40_task_v1 Mode

1. Validate input PLAN-DOC has lifecycle_status: "approved".
2. Parse PLAN-DOC to extract phases, groups, and dependencies.
3. Decompose each group into discrete backlog items.
4. Estimate relative complexity for each backlog item.
5. Define dependencies between backlog items.
6. Structure output according to BACKLOG template.
7. Generate BACKLOG-DOC with lifecycle_status: "draft".
8. Write output to backlogs/ folder with correct naming.
9. Produce meta.json sidecar with artifact path.

## Entry Criteria

- Input document exists and has lifecycle_status: "approved".
- Input document contains valid YAML frontmatter with correct template_id.
- The calling workflow (sdlc_30 or sdlc_40) is active at the generate step.
- The target output directory (plans/ or backlogs/) is writable.

## Exit Criteria

- Output document (PLAN-DOC or BACKLOG-DOC) is generated with all required sections.
- Output document has valid YAML frontmatter with correct template_id.
- Output document has lifecycle_status: "draft".
- Output document file name matches the naming convention.
- Output document is stored in the correct directory.
- meta.json sidecar is written with correct artifact path.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent does not perform review, refinement, or promotion actions.
- The agent does not have write access to any directory other than the
  designated output folder for the current workflow run.
- The agent must complete within the step timeout budget.
- Each invocation operates in exactly one mode determined by the workflow.
- Output must be deterministic given the same inputs and prompt.

## References

- PLAN Template: 01_templates/04_PLAN_template.md (SYS-03-PL)
- BACKLOG Template: 01_templates/05_BACKLOG_template.md (SYS-03-BL)
- REQ Template: 01_templates/03_REQ_template.md (SYS-03-RQ)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
