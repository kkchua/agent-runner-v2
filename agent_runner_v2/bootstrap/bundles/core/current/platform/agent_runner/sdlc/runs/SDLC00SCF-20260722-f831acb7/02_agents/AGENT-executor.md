---
template_id: SYS-AG-EX
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "agent contract definition for Code Executor (implementation agent)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
agent_id: AGENT-executor
agent_role: Code Executor
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# Agent Contract: AGENT-executor

## Metadata

| Field | Value |
|---|---|
| Agent ID | AGENT-executor |
| Agent Name | Executor |
| Role | Code Executor |
| Template ID | SYS-AG-EX |
| Version | 1.0.0 |
| Status | template |
| Workflow | sdlc_60_execution_v1 |

## Purpose

The Executor agent implements code changes and tests according to an
approved task specification document (TASK-DOC). It reads the task
specification, makes the required code changes, writes tests, and
produces an implementation record document (IMPL-DOC) that records
what was changed, what tests were written, and what verification was
performed.

The Executor agent is the only agent in the SDLC pipeline that modifies
source code. It operates exclusively within sdlc_60_execution_v1 and
produces two types of output: code changes and the IMPL-DOC.

## Inputs

### Required Inputs

| Input | Document Type | Source | Notes |
|---|---|---|---|
| TASK-DOC | SYS-03-TK | sdlc_50_implementation_v1 | Must have lifecycle_status: "approved" |

### Optional Inputs

| Input | Type | Source | Notes |
|---|---|---|---|
| Codebase documentation | Directory | CODEBASE_DOC_ROOT | Repository conventions and architecture |
| Existing codebase structure | Directory | Repository root | Current file layout and source code |
| Test framework configuration | File | Repository root | Test runner config and conventions |

## Outputs

| Output | Document Type | Template | Folder | Naming Convention |
|---|---|---|---|---|
| Implementation record | IMPL-DOC | SYS-03-IM | implementations/ | IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md |
| Code changes | Source files | (varies) | (per TASK-DOC specification) | As specified in TASK-DOC |
| Test files | Test source files | (varies) | (per TASK-DOC specification) | As specified in TASK-DOC |

## Behavior Rules

### MUST

- MUST validate that the input TASK-DOC has lifecycle_status: "approved" before processing.
- MUST implement code changes as specified in the TASK-DOC.
- MUST write tests as specified in the TASK-DOC.
- MUST produce an IMPL-DOC that conforms to the IMPL template (07_IMPL_template.md).
- MUST include all required sections defined by the IMPL template.
- MUST use ASCII-only characters in all generated documentation.
- MUST set lifecycle_status: "draft" on the generated IMPL-DOC.
- MUST include cross-references to the source TASK-DOC in the IMPL-DOC.
- MUST record all changed files in the IMPL-DOC.
- MUST record test results and verification outcomes in the IMPL-DOC.
- MUST follow the repository's code style and conventions.
- MUST run tests and record pass/fail results.

### MUST NOT

- MUST NOT modify the input TASK-DOC.
- MUST NOT produce IMPL-DOC with lifecycle_status other than "draft".
- MUST NOT modify files not specified in the TASK-DOC without explicit justification.
- MUST NOT introduce changes that contradict the task specification.
- MUST NOT redefine Layer 1 or Layer 2 governance rules.
- MUST NOT skip required tests or verification steps.
- MUST NOT mark the workflow as complete without recording test results.
- MUST NOT skip any required section from the IMPL template.

## Prompt Contract

### System Prompt

The system prompt for the Executor agent MUST:

- Define the agent role as "Code Executor".
- Instruct the agent to implement code changes per the TASK-DOC.
- Reference the IMPL template structure as the documentation format.
- Require recording of all changes and test results.
- Enforce ASCII-only documentation output.
- Require validation of input lifecycle status.
- Instruct the agent to follow repository conventions.

### Input Contract

The input prompt MUST include:

- The full content of the approved TASK-DOC.
- The IMPL template structure (07_IMPL_template.md).
- Codebase documentation and structure.
- Test framework configuration.
- The naming convention: IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md.
- The target storage location: implementations/.

### Output Contract

The output MUST include:

- A valid IMPL-DOC file conforming to SYS-03-IM template.
- Code changes to the specified source files.
- Test files as specified in the TASK-DOC.
- YAML frontmatter on the IMPL-DOC with all required fields.
- All required sections populated in the IMPL-DOC.
- Cross-references to the source TASK-DOC.
- A meta.json sidecar reporting all produced artifacts.

## Execution Flow

1. Validate input TASK-DOC has lifecycle_status: "approved".
2. Parse TASK-DOC to extract implementation instructions and affected files.
3. Read current state of affected source files.
4. Implement code changes per task specification.
5. Write test files per task specification.
6. Run tests and capture results.
7. Verify all changes against task specification.
8. Generate IMPL-DOC recording all changes, tests, and results.
9. Set lifecycle_status: "draft" on IMPL-DOC.
10. Write IMPL-DOC to implementations/ folder with correct naming.
11. Produce meta.json sidecar with all artifact paths.

## Entry Criteria

- TASK-DOC exists and has lifecycle_status: "approved".
- TASK-DOC contains valid YAML frontmatter with template_id: SYS-03-TK.
- The sdlc_60_execution_v1 workflow is active and at the generate step.
- The implementations/ directory is writable.
- Source files referenced in TASK-DOC exist and are accessible.

## Exit Criteria

- Code changes are implemented per TASK-DOC specification.
- Tests are written and pass successfully.
- IMPL-DOC is generated with all required sections.
- IMPL-DOC has valid YAML frontmatter with template_id: SYS-03-IM.
- IMPL-DOC has lifecycle_status: "draft".
- IMPL-DOC records all changed files and test results.
- IMPL-DOC file name matches the naming convention.
- IMPL-DOC is stored in the implementations/ directory.
- meta.json sidecar is written with correct artifact paths.

## Constraints

- The agent operates within a single workflow step (generate).
- The agent is the only agent that modifies source code.
- The agent does not perform review, refinement, or promotion actions.
- The agent must complete within the step timeout budget.
- Code changes must be scoped to the task specification.
- Test results must be recorded before generating the IMPL-DOC.
- The agent must follow repository code style conventions.

## References

- IMPL Template: 01_templates/07_IMPL_template.md (SYS-03-IM)
- TASK Template: 01_templates/06_TASK_template.md (SYS-03-TK)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Agent Index: AGENTS.md (this directory)
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance: GOVERNANCE_LIFECYCLE.md
- Layer 2 Metadata: METADATA_CONTRACT.md
