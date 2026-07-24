---
template_id: SYS-AG-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Memory Manager (knowledge persistence agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-memory-manager
agent_role: Memory Manager
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-memory-manager

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-memory-manager |
| Agent Name | Memory Manager |
| Role | Memory Manager |
| Template ID | SYS-AG-MM |
| Version | 1.0.0 |
| Status | template |
| Workflow | sdlc_80_review_v1 |

## Purpose

The Memory Manager agent persists stable, reusable delivery knowledge
after an SDLC workflow completes. It operates exclusively within
sdlc_80_review_v1 (running after or alongside the Reviewer agent in
the same workflow) and produces two output documents:

- **MEM-DOC**: A memory document that captures reusable knowledge,
  patterns, lessons learned, and decisions made during the delivery.
  This knowledge is intended to improve future deliveries by providing
  context and reference material.

- **CLOSE-DOC**: A closure document that formally records the
  completion of the delivery initiative, summarizes outcomes, and
  marks the initiative as closed.

The Memory Manager does not review or validate. It extracts and
persists knowledge from approved artifacts and delivery summaries.

## Inputs

### Required Inputs

| Input | Document Type | Source | Notes |
|---|---|---|---|
| VALID-DOC | SYS-03-VL | sdlc_70_validation_v1 | Must have lifecycle_status: "approved" |
| REV-DOC | SYS-03-RV | sdlc_80_review_v1 (Reviewer) | Must have lifecycle_status: "approved" |

### Optional Inputs

| Input | Document Type | Source | Notes |
|---|---|---|---|
| Full delivery artifact chain | Documents | Delivery folders | Complete audit trail for knowledge extraction |
| Previous MEM-DOC documents | Documents | reviews/ | Historical knowledge for context |
| Codebase documentation | Directory | CODEBASE_DOC_ROOT | Repository conventions |

## Outputs

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Memory document | MEM-DOC | SYS-03-MM | reviews/ | MEM-{YYYYMMDD}-{NN}_{slug}.md |
| Closure document | CLOSE-DOC | SYS-03-CL | reviews/ | CLOSE-{YYYYMMDD}-{NN}_{slug}.md |

## Behavior Rules

### MUST

- MUST validate that both input documents (VALID-DOC and REV-DOC) have lifecycle_status: "approved" before processing.
- MUST produce both MEM-DOC and CLOSE-DOC outputs.
- MUST conform MEM-DOC to the MEM template (10_MEM_template.md).
- MUST conform CLOSE-DOC to the CLOSE template (11_CLOSE_template.md).
- MUST include all required sections in both output documents.
- MUST use ASCII-only characters in all output.
- MUST set lifecycle_status: "draft" on both generated documents.
- MUST include cross-references to all source documents in both outputs.
- MUST extract reusable patterns and lessons learned from the delivery.
- MUST record initiative outcomes and closure details in CLOSE-DOC.
- MUST maintain the initiative slug consistently across all output documents.

### MUST NOT

- MUST NOT modify any input documents.
- MUST NOT produce output with lifecycle_status other than "draft".
- MUST NOT perform review or validation (that is AGENT-reviewer's responsibility).
- MUST NOT introduce repository-specific content beyond what exists in the delivery artifacts.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip any required section from the MEM or CLOSE templates.
- MUST NOT duplicate verbatim content from input documents (extract and summarize).
- MUST NOT make subjective quality judgments (report facts only).

## Prompt Contract

### System Prompt

The system prompt for the Memory Manager agent MUST:

- Define the agent role as "Memory Manager".
- Instruct the agent to extract knowledge and produce MEM-DOC and CLOSE-DOC.
- Reference both the MEM and CLOSE template structures as output formats.
- Require extraction of reusable patterns and lessons learned.
- Enforce ASCII-only output.
- Require validation of input lifecycle status.
- Instruct the agent to summarize rather than duplicate input content.

### Input Contract

The input prompt MUST include:

- The full content of the approved VALID-DOC.
- The full content of the approved REV-DOC.
- The MEM template structure (10_MEM_template.md).
- The CLOSE template structure (11_CLOSE_template.md).
- The full delivery artifact chain if available.
- The naming conventions for both output documents.
- The target storage location: reviews/.

### Output Contract

The output MUST include:

- A valid MEM-DOC file conforming to SYS-03-MM template.
- A valid CLOSE-DOC file conforming to SYS-03-CL template.
- YAML frontmatter on both documents with all required fields.
- All required sections populated in both documents.
- Cross-references to all source documents.
- A meta.json sidecar reporting both produced artifact paths.

## Execution Flow

1. Validate input VALID-DOC has lifecycle_status: "approved".
2. Validate input REV-DOC has lifecycle_status: "approved".
3. Load the full delivery artifact chain for context.
4. Parse all approved documents to extract key decisions and patterns.
5. Identify reusable knowledge, lessons learned, and patterns.
6. Identify areas for improvement and recommendations.
7. Structure MEM-DOC according to MEM template.
8. Generate MEM-DOC with lifecycle_status: "draft".
9. Summarize initiative outcomes and closure details.
10. Structure CLOSE-DOC according to CLOSE template.
11. Generate CLOSE-DOC with lifecycle_status: "draft".
12. Write both documents to reviews/ folder with correct naming.
13. Produce meta.json sidecar with both artifact paths.

## Entry Criteria

- VALID-DOC exists and has lifecycle_status: "approved".
- REV-DOC exists and has lifecycle_status: "approved".
- Both documents contain valid YAML frontmatter.
- The sdlc_80_review_v1 workflow is active at the memory management step.
- The reviews/ directory is writable.

## Exit Criteria

- MEM-DOC is generated with all required sections.
- CLOSE-DOC is generated with all required sections.
- Both documents have valid YAML frontmatter with correct template_ids.
- Both documents have lifecycle_status: "draft".
- Both documents file names match the naming convention.
- Both documents are stored in the reviews/ directory.
- meta.json sidecar is written with both artifact paths.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent does not perform review, validation, or promotion actions.
- The agent does not have write access to any directory other than the
  designated output folder for the current workflow run.
- The agent must complete within the step timeout budget.
- The agent produces two documents per invocation (MEM-DOC and CLOSE-DOC).
- Output must be deterministic given the same inputs and prompt.
- Knowledge extraction must summarize, not duplicate, source content.

## References

- MEM Template: 01_templates/10_MEM_template.md (SYS-03-MM)
- CLOSE Template: 01_templates/11_CLOSE_template.md (SYS-03-CL)
- VALID Template: 01_templates/08_VALID_template.md (SYS-03-VL)
- REV Template: 01_templates/09_REV_template.md (SYS-03-RV)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
