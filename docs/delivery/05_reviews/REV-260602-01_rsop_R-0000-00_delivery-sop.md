# Delivery SOP Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-01_rsop_R-0000-00 |
| Review Type | SOP Review |
| Decision | REJECTED |
| Reviewer Role | SOP Reviewer |

## Targets
- `docs/delivery/00_templates/delivery_sop.json`
- `docs/delivery/00_templates/delivery_status_rules.json`

## Governing Reference
- `delivery_scaffold_v1/SCAFFOLD-GEN-20260602-003/00_project_analysis/project_analysis.json`

## Findings

### F-001: JSON deliverables are not machine-readable JSON
Severity: High

Both review targets use `.json` filenames but contain Markdown documents. Parsing either target with `python -m json.tool` fails at line 1 column 1. This conflicts with the project analysis requirement that machine-readable JSON comes first and prevents deterministic schema validation of the SOP and status rules.

Required correction: Generate valid JSON documents or place narrative Markdown in correctly named companion files while retaining valid JSON as the authoritative artifacts.

### F-002: Task approval lifecycle is not reconciled with the SOP state machine
Severity: High

The status rules define the task lifecycle as `Pending -> In Progress -> Implemented -> Approved` and require `Task Implemented -> Approved` after implementation review and required validation. The SOP workflow moves from `EXECUTION_IN_PROGRESS` to `IMPLEMENTATION_REVIEWED`, then to `VALIDATION_IN_PROGRESS`, `VALIDATED`, and `COMPLETED`, but does not define when the task becomes `Implemented` or `Approved`. The relationship between per-task approval and workflow-level validation is therefore ambiguous.

Required correction: Define the runner-enforced task transitions and their ordering relative to implementation review, validation, and completion. Ensure both documents describe the same lifecycle.

### F-003: Rejection routing is not explicit enough for deterministic runner transitions
Severity: Medium

The SOP states that rejection routes to an owning prior phase and that validation failure returns work to the appropriate owning phase. The state table routes both implementation review rejection and validation rejection to `IMPLEMENTATION_PLANNED`, while the status rules allow refinement, replanning, or explicit failure handling without a transition map. The documents do not specify how the runner selects a destination when a defect belongs to initiative scope, plan, task graph, task, implementation plan, or execution.

Required correction: Add an explicit rejection-routing table keyed by gate and failure category, including allowed destination states and supersession behavior.

### F-004: Sidecar requirements are not mapped to workflow phases
Severity: Medium

The documents correctly state that meta.json sidecars are authoritative and define the sidecar result fields. However, they do not enumerate which generated artifacts and gate decisions require sidecars at each phase. The document-first rule qualifies the requirement with "where the runner contract requires one," leaving the mandatory sidecar contract incomplete inside the SOP and status rules.

Required correction: Define the required sidecar for each generated artifact, review, validation, and gate decision, including basename rules and runner acceptance behavior.

## Coverage Summary
The SOP includes the major delivery phases identified in the project analysis: initiative intake, planning, task decomposition, implementation planning, execution, review, validation, memory management, parallel execution, budgets, deterministic hashing, snapshots, and sidecar-only communication. Approval gates are present, but the findings above prevent complete and deterministic alignment.

## Decision
REJECTED
