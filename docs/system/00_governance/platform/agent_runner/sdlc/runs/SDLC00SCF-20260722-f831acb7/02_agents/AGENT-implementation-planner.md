---
template_id: SYS-AG-IP
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Implementation Planner (task specification agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-implementation-planner
agent_role: Implementation Planner
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-implementation-planner

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-implementation-planner |
| Agent Name | Implementation Planner |
| Role | Implementation Planner |
| Template ID | SYS-AG-IP |
| Version | 1.0.0 |
| Status | template |
| Workflow | sdlc_50_implementation_v1 |

## Purpose

The Implementation Planner agent transforms an approved backlog document
(BACKLOG-DOC) into a detailed task specification document (TASK-DOC).
It analyzes the backlog items, maps them to specific codebase locations,
defines implementation steps, identifies affected files and modules, and
produces a comprehensive task specification that the executor agent can
follow to implement the changes.

The Implementation Planner operates exclusively within
sdlc_50_implementation_v1 and produces a single output document type:
TASK-DOC.

## Inputs

### Required Inputs

| Input | Document Type | Source | Notes |
|---|---|---|---|
| BACKLOG-DOC | SYS-03-BL | sdlc_40_task_v1 | Must have lifecycle_status: "approved" |

### Optional Inputs

| Input | Type | Source | Notes |
|---|---|---|---|
| Codebase documentation | Directory | CODEBASE_DOC_ROOT | Repository conventions, architecture, module map |
| Existing codebase structure | Directory | Repository root | Current file layout and source code |
| Platform constitution | Documents | PLATFORM_RUNTIME_ROOT | Layer 2 platform constraints |

## Outputs

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Task specification | TASK-DOC | SYS-03-TK | tasks/ | TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md |

## Behavior Rules

### MUST

- MUST validate that the input BACKLOG-DOC has lifecycle_status: "approved" before processing.
- MUST produce output that conforms to the TASK template (06_TASK_template.md).
- MUST include all required sections defined by the TASK template.
- MUST use ASCII-only characters in all output.
- MUST set lifecycle_status: "draft" on the generated TASK-DOC.
- MUST include cross-references to the source BACKLOG-DOC in the output.
- MUST identify specific files and modules affected by each task.
- MUST define step-by-step implementation instructions.
- MUST maintain traceability from each task back to the backlog items.
- MUST include test requirements and verification steps.

### MUST NOT

- MUST NOT modify the input BACKLOG-DOC.
- MUST NOT produce output with lifecycle_status other than "draft".
- MUST NOT introduce repository-specific content beyond what is in the backlog and codebase.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip any required section from the TASK template.
- MUST NOT write or modify source code (that is AGENT-executor's responsibility).
- MUST NOT include actual code implementations (only specifications).

## Prompt Contract

### System Prompt

The system prompt for the Implementation Planner agent MUST:

- Define the agent role as "Implementation Planner".
- Instruct the agent to analyze the BACKLOG-DOC and produce a TASK-DOC.
- Reference the TASK template structure as the output format.
- Require traceability from tasks to backlog items.
- Enforce ASCII-only output.
- Require validation of input lifecycle status.
- Instruct the agent to map tasks to specific codebase locations.

### Input Contract

The input prompt MUST include:

- The full content of the approved BACKLOG-DOC.
- The TASK template structure (06_TASK_template.md).
- Codebase documentation and structure if available.
- The naming convention: TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md.
- The target storage location: tasks/.

### Output Contract

The output MUST include:

- A valid TASK-DOC file conforming to SYS-03-TK template.
- YAML frontmatter with all required fields.
- All required sections populated.
- Cross-references to the source BACKLOG-DOC.
- A meta.json sidecar reporting the produced artifact.

## Execution Flow

1. Validate input BACKLOG-DOC has lifecycle_status: "approved".
2. Parse BACKLOG-DOC to extract backlog items, dependencies, and priorities.
3. Analyze codebase documentation for module structure and conventions.
4. Map each backlog item to specific codebase locations.
5. Define step-by-step implementation instructions for each task.
6. Identify affected files and modules per task.
7. Define test requirements and verification steps.
8. Structure output according to TASK template.
9. Generate TASK-DOC with lifecycle_status: "draft".
10. Write output to tasks/ folder with correct naming.
11. Produce meta.json sidecar with artifact path.

## Entry Criteria

- BACKLOG-DOC exists and has lifecycle_status: "approved".
- BACKLOG-DOC contains valid YAML frontmatter with template_id: SYS-03-BL.
- The sdlc_50_implementation_v1 workflow is active and at the generate step.
- The tasks/ directory is writable.

## Exit Criteria

- TASK-DOC is generated with all required sections.
- TASK-DOC has valid YAML frontmatter with template_id: SYS-03-TK.
- TASK-DOC has lifecycle_status: "draft".
- TASK-DOC file name matches the naming convention.
- TASK-DOC is stored in the tasks/ directory.
- meta.json sidecar is written with correct artifact path.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent does not perform review, refinement, or promotion actions.
- The agent does not have write access to any directory other than the
  designated output folder for the current workflow run.
- The agent must complete within the step timeout budget.
- Output must be deterministic given the same inputs and prompt.
- The agent produces specifications only, not implementations.

## References

- TASK Template: 01_templates/06_TASK_template.md (SYS-03-TK)
- BACKLOG Template: 01_templates/05_BACKLOG_template.md (SYS-03-BL)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
