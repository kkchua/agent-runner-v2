---
template_id: SYS-AG-RV
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Independent Reviewer (validation and review agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-reviewer
agent_role: Independent Reviewer
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-reviewer

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-reviewer |
| Agent Name | Reviewer |
| Role | Independent Reviewer |
| Template ID | SYS-AG-RV |
| Version | 1.0.0 |
| Status | template |
| Workflows | sdlc_70_validation_v1, sdlc_80_review_v1 |

## Purpose

The Reviewer agent provides independent review of SDLC delivery artifacts.
It operates in two modes across two workflows:

- **sdlc_70_validation_v1 mode**: Validates an approved implementation
  document (IMPL-DOC) against the original requirements and task
  specifications. Produces a validation report (VALID-DOC) that
  confirms whether the implementation meets all defined acceptance
  criteria and requirements.

- **sdlc_80_review_v1 mode**: Reviews an approved validation document
  (VALID-DOC) and produces a review decision document (REV-DOC) that
  determines whether the delivery can proceed to closure. The review
  considers the validation findings, assesses overall delivery quality,
  and makes a recommendation for approval or rejection.

The Reviewer agent is independent of the implementation process. It
does not modify code or implementation artifacts. It evaluates and
reports findings only.

## Inputs

### sdlc_70_validation_v1 Mode

| Input | Document Type | Source | Notes |
|---|---|---|---|
| IMPL-DOC | SYS-03-IM | sdlc_60_execution_v1 | Must have lifecycle_status: "approved" |

Additional context for validation:

| Input | Document Type | Source | Notes |
|---|---|---|---|
| TASK-DOC | SYS-03-TK | sdlc_50_implementation_v1 | Reference for what was specified |
| REQ-DOC | SYS-03-RQ | sdlc_20_planning_v1 | Reference for acceptance criteria |
| Code changes | Source files | Repository | Reference for actual implementation |

### sdlc_80_review_v1 Mode

| Input | Document Type | Source | Notes |
|---|---|---|---|
| VALID-DOC | SYS-03-VL | sdlc_70_validation_v1 | Must have lifecycle_status: "approved" |

Additional context for review:

| Input | Document Type | Source | Notes |
|---|---|---|---|
| Full delivery artifact chain | Documents | Delivery folders | Complete audit trail for review |

## Outputs

### sdlc_70_validation_v1 Mode

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Validation report | VALID-DOC | SYS-03-VL | validations/ | VALID-{YYYYMMDD}-{NN}_{slug}.md |

### sdlc_80_review_v1 Mode

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Review decision | REV-DOC | SYS-03-RV | reviews/ | REV-{YYYYMMDD}-{NN}_{slug}.md |

## Behavior Rules

### MUST

- MUST validate that the input document has lifecycle_status: "approved" before processing.
- MUST operate in the correct mode based on the calling workflow.
- MUST produce output that conforms to the appropriate template (VALID or REV).
- MUST include all required sections defined by the target template.
- MUST use ASCII-only characters in all output.
- MUST set lifecycle_status: "draft" on the generated output document.
- MUST include cross-references to source documents in the output.
- MUST provide evidence-based findings for every validation or review point.
- MUST clearly state pass/fail outcomes for each check.
- MUST maintain independence from the implementation process.

### MUST NOT

- MUST NOT modify the input document(s).
- MUST NOT produce output with lifecycle_status other than "draft".
- MUST NOT modify source code or implementation artifacts.
- MUST NOT introduce repository-specific content.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip any required section from the target template.
- MUST NOT mix modes -- each invocation produces exactly one output type.
- MUST NOT make approval decisions in sdlc_70 mode (validation only).
- MUST NOT override the human approval gate.

## Prompt Contract

### System Prompt

The system prompt for the Reviewer agent MUST:

- Define the agent role as "Independent Reviewer".
- Specify which mode is active (validation or review).
- Reference the target template structure as the output format.
- Require evidence-based findings for every check.
- Enforce ASCII-only output.
- Require validation of input lifecycle status.
- Require independence from the implementation process.

### Input Contract

The input prompt MUST include:

- The full content of the approved input document (IMPL-DOC or VALID-DOC).
- The target template structure (VALID or REV template).
- Reference documents from the delivery chain for traceability.
- The naming convention for the output document.
- The target storage location.

### Output Contract

The output MUST include:

- A valid output document (VALID-DOC or REV-DOC) conforming to the
  appropriate template.
- YAML frontmatter with all required fields.
- All required sections populated with evidence-based findings.
- Cross-references to source documents.
- A meta.json sidecar reporting the produced artifact.

## Execution Flow

### sdlc_70_validation_v1 Mode

1. Validate input IMPL-DOC has lifecycle_status: "approved".
2. Load reference documents (TASK-DOC, REQ-DOC) for comparison.
3. Parse IMPL-DOC to extract implementation details and test results.
4. Verify implementation against each requirement in REQ-DOC.
5. Verify implementation against each task specification in TASK-DOC.
6. Check test coverage and pass/fail results.
7. Verify code changes match task specification scope.
8. Compile findings into validation report.
9. Structure output according to VALID template.
10. Generate VALID-DOC with lifecycle_status: "draft".
11. Write output to validations/ folder with correct naming.
12. Produce meta.json sidecar with artifact path.

### sdlc_80_review_v1 Mode

1. Validate input VALID-DOC has lifecycle_status: "approved".
2. Load the full delivery artifact chain for review context.
3. Parse VALID-DOC to extract validation findings and outcomes.
4. Review overall delivery quality and completeness.
5. Assess whether all acceptance criteria are met.
6. Review the audit trail for consistency and completeness.
7. Formulate review decision (approve, request changes, reject).
8. Structure output according to REV template.
9. Generate REV-DOC with lifecycle_status: "draft".
10. Write output to reviews/ folder with correct naming.
11. Produce meta.json sidecar with artifact path.

## Entry Criteria

- Input document exists and has lifecycle_status: "approved".
- Input document contains valid YAML frontmatter with correct template_id.
- The calling workflow (sdlc_70 or sdlc_80) is active at the generate step.
- The target output directory is writable.
- Reference documents from the delivery chain are accessible.

## Exit Criteria

- Output document (VALID-DOC or REV-DOC) is generated with all required sections.
- Output document has valid YAML frontmatter with correct template_id.
- Output document has lifecycle_status: "draft".
- Output document file name matches the naming convention.
- Output document is stored in the correct directory.
- All findings are evidence-based and clearly stated.
- meta.json sidecar is written with correct artifact path.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent does not modify code or implementation artifacts.
- The agent does not perform promotion actions.
- The agent does not have write access to any directory other than the
  designated output folder for the current workflow run.
- The agent must complete within the step timeout budget.
- Each invocation operates in exactly one mode determined by the workflow.
- The agent must remain independent of the implementation process.
- Output must be deterministic given the same inputs and prompt.

## References

- VALID Template: 01_templates/08_VALID_template.md (SYS-03-VL)
- REV Template: 01_templates/09_REV_template.md (SYS-03-RV)
- IMPL Template: 01_templates/07_IMPL_template.md (SYS-03-IM)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
