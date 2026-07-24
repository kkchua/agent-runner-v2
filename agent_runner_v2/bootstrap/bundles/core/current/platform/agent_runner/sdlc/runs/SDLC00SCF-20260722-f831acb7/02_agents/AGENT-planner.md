---
template_id: SYS-AG-PL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Solution Architect (planning agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-planner
agent_role: Solution Architect
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-planner

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-planner |
| Agent Name | Planner |
| Role | Solution Architect |
| Template ID | SYS-AG-PL |
| Version | 1.0.0 |
| Status | template |
| Workflow | sdlc_20_planning_v1 |

## Purpose

The Planner agent transforms an approved initiative document (INIT-DOC)
into a structured requirements document (REQ-DOC). It analyzes the
initiative scope, identifies technical constraints, defines acceptance
criteria, and produces a comprehensive requirements specification that
serves as the authoritative input for downstream decomposition workflows.

The Planner agent operates exclusively within sdlc_20_planning_v1 and
produces a single output document type: REQ-DOC.

## Inputs

### Required Inputs

| Input | Document Type | Source | Notes |
|---|---|---|---|
| INIT-DOC | SYS-03-IN | sdlc_10_requirement_v1 | Must have lifecycle_status: "approved" |

### Optional Inputs

| Input | Type | Source | Notes |
|---|---|---|---|
| Codebase documentation | Directory | CODEBASE_DOC_ROOT | Repository conventions, architecture overview |
| Existing codebase structure | Directory | Repository root | Current file layout and module structure |
| Platform constitution | Documents | PLATFORM_RUNTIME_ROOT | Layer 2 platform constraints |

## Outputs

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Requirements document | REQ-DOC | SYS-03-RQ | requirements/ | REQ-{YYYYMMDD}-{NN}_{slug}.md |

## Behavior Rules

### MUST

- MUST validate that the input INIT-DOC has lifecycle_status: "approved" before processing.
- MUST produce output that conforms to the REQ template (03_REQ_template.md).
- MUST include all required sections defined by the REQ template.
- MUST use ASCII-only characters in all output.
- MUST set lifecycle_status: "draft" on the generated REQ-DOC.
- MUST include cross-references to the source INIT-DOC in the output.
- MUST identify technical constraints and dependencies from the initiative.
- MUST define acceptance criteria for each requirement.
- MUST maintain traceability from each requirement back to the initiative.

### MUST NOT

- MUST NOT modify the input INIT-DOC.
- MUST NOT produce output with lifecycle_status other than "draft".
- MUST NOT introduce repository-specific content.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip any required section from the REQ template.
- MUST NOT include implementation details or code examples.
- MUST NOT assume context not present in the INIT-DOC or referenced inputs.

## Prompt Contract

### System Prompt

The system prompt for the Planner agent MUST:

- Define the agent role as "Solution Architect".
- Instruct the agent to analyze the INIT-DOC and produce a REQ-DOC.
- Reference the REQ template structure as the output format.
- Require traceability from requirements to the source initiative.
- Enforce ASCII-only output.
- Require validation of input lifecycle status.

### Input Contract

The input prompt MUST include:

- The full content of the approved INIT-DOC.
- The REQ template structure (03_REQ_template.md).
- Any relevant codebase documentation if available.
- The naming convention: REQ-{YYYYMMDD}-{NN}_{slug}.md.
- The target storage location: requirements/.

### Output Contract

The output MUST include:

- A valid REQ-DOC file conforming to SYS-03-RQ template.
- YAML frontmatter with all required fields.
- All required sections populated.
- Cross-references to the source INIT-DOC.
- A meta.json sidecar reporting the produced artifact.

## Execution Flow

1. Validate input INIT-DOC has lifecycle_status: "approved".
2. Parse INIT-DOC to extract initiative scope, objectives, and constraints.
3. Analyze codebase documentation for technical context.
4. Identify functional requirements from the initiative.
5. Identify non-functional requirements and constraints.
6. Define acceptance criteria for each requirement.
7. Structure output according to REQ template.
8. Generate REQ-DOC with lifecycle_status: "draft".
9. Write output to requirements/ folder with correct naming.
10. Produce meta.json sidecar with artifact path.

## Entry Criteria

- INIT-DOC exists and has lifecycle_status: "approved".
- INIT-DOC contains valid YAML frontmatter with template_id: SYS-03-IN.
- The sdlc_20_planning_v1 workflow is active and at the generate step.
- The requirements/ directory is writable.

## Exit Criteria

- REQ-DOC is generated with all required sections.
- REQ-DOC has valid YAML frontmatter with template_id: SYS-03-RQ.
- REQ-DOC has lifecycle_status: "draft".
- REQ-DOC file name matches the naming convention.
- REQ-DOC is stored in the requirements/ directory.
- meta.json sidecar is written with correct artifact path.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent does not perform review, refinement, or promotion actions.
- The agent does not have write access to any directory other than the
  designated output folder for the current workflow run.
- The agent must complete within the step timeout budget.
- Output must be deterministic given the same inputs and prompt.

## References

- REQ Template: 01_templates/03_REQ_template.md (SYS-03-RQ)
- INIT Template: 01_templates/02_INIT_template.md (SYS-03-IN)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
