---
template_id: "SYS-03-PL"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved plan for console sdlc_10 support initiative, produced by sdlc_20_planning_v1"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "approved"
effective_version: "SDLC20PLN-20260723-5c08a3d0"
managed_by: "workflow-generated"
source_document: "REQ-20260723-001_console-sdlc10-support.md"
---

# Plan Overview

This plan addresses the approved requirement to add SDLC workflow input
handling to the operator console, a Flet-based desktop GUI for the
agent-runner-v2 platform. The current console supports generic job
submission but has no awareness of SDLC workflow input requirements. Users
must manually construct CLI commands with --input KEY=VALUE arguments to
submit SDLC workflows.

The solution introduces three coordinated capabilities into the console:

1. A file picker UI component that allows users to select draft initiative
   documents from the local filesystem.
2. Conditional visibility logic that shows the file picker only when an
   SDLC workflow is selected and the action is "submit job".
3. Input artifact forwarding through the existing submit flow, passing
   the selected file path as DRAFT_INIT_FILE to the backend.

This is Phase 1 of a planned multi-phase console SDLC support plan. The
architecture must be extensible to support additional input artifact keys
in future phases without structural changes to the file picker component.

The solution operates entirely within Layer 3 boundaries. It modifies the
console UI layer and the runner service layer, both of which are console-
side components. No changes to backend API, daemon behavior, or Layer 1
governance are required or permitted.


# Document Metadata

| Field | Value |
|---|---|
| Document ID | PLAN-20260723-001 |
| Source Requirement | REQ-20260723-001_console-sdlc10-support.md |
| Source Initiative | INIT-20260723-001_console-sdlc10-support.md |
| Date of Generation | 2026-07-23 |
| Producing Workflow | sdlc_20_planning_v1 |
| Producing Step | generate_plan |
| Template | SYS-03-PL |
| Plan Version | 1.0.0 (refined) |
| Review Reference | console-sdlc10-support-REV-20-plan.md |



# Requirement Traceability

This plan is derived from the approved requirement document
REQ-20260723-001_console-sdlc10-support.md. The requirement document
itself was derived from the approved initiative
INIT-20260723-001_console-sdlc10-support.md.

## Key Requirements Addressed

| Requirement | Summary | Plan Section |
|---|---|---|
| FR-001 | File picker UI component | Solution Architecture, Component Breakdown |
| FR-002 | Conditional visibility on SDLC workflow selection | Solution Architecture, Integration Points |
| FR-003 | Hidden on non-SDLC workflow deselection | Solution Architecture, Integration Points |
| FR-004 | Hidden on action change from submit job | Solution Architecture, Integration Points |
| FR-005 | File browsing and selection | Solution Architecture, Component Breakdown |
| FR-006 | Path display in text field | Solution Architecture, Component Breakdown |
| FR-007 | Input artifact submission | Data Flow, Integration Points |
| FR-008 | Runner service input artifact support | Component Breakdown, Integration Points |
| FR-009 | Generic submission preservation | Solution Architecture, Risk Assessment |
| FR-010 | Workflow dropdown integration | Solution Architecture |
| NFR-001 | Flet framework compliance | Solution Architecture |
| NFR-002 | Windows platform support | Risk Assessment |
| NFR-003 | No backend API changes | Solution Architecture, Constraints |
| NFR-006 | Extensibility | Solution Architecture, Component Breakdown |
| NFR-007 | Console startup stability | Risk Assessment |

## Traceability to Layer 1 and Layer 2

- The plan respects Layer 1 metadata standard (METADATA_STANDARD.md) by
  ensuring any generated or modified governed documents conform to the
  required metadata fields and allowed vocabularies.
- The plan respects Layer 2 platform constitution (RUNTIME_MODEL.md,
  METADATA_CONTRACT.md) by operating within the existing runtime model
  and metadata contract. No platform-level changes are introduced.
- The solution is scoped to Layer 3 (concrete delivery) and does not
  redefine or contradict Layer 1 governance or Layer 2 platform
  constitution (per NFR-005, DC-011).


# Solution Architecture

## High-Level Approach

The solution follows an additive architecture. Existing console components
remain in place and are extended with new UI controls and service
parameters. The approach minimizes structural changes to reduce regression
risk.

The architecture introduces three logical components:

1. File Picker UI Component - A new row of controls in the console layout
   consisting of a Flet FilePicker, a TextField for the file path, and a
   Browse button. This component is conditionally visible based on workflow
   and action selection state.

2. Conditional Visibility Controller - A logic layer embedded in the
   existing update_visibility() function that evaluates two conditions:
   (a) the selected workflow name starts with "sdlc_", and (b) the selected
   action is "submit job". When both conditions are true, the file picker
   row is shown; otherwise it is hidden.

3. Input Artifact Forwarding - An extension to the runner_service.submit_job()
   method that accepts an optional input_artifacts dictionary and forwards
   it as --input KEY=VALUE arguments to the submit_commands.main() entry
   point. The submit_commands module already supports --input arguments,
   so no CLI-level changes are needed.

## Architectural Decisions

### Decision 1: Additive Extension Over Restructuring

The console app.py already has a well-defined structure with dropdowns,
action handlers, and a dynamic section. The file picker is added as a new
row in the existing layout rather than restructuring the entire console.
This preserves backward compatibility (FR-009) and reduces the surface
area for regression (RA-002).

### Decision 2: Leverage Existing CLI Contract

The submit_commands.main() function already supports --input KEY=VALUE
arguments through its argparse configuration. The runner_service.submit_job()
method simply needs to accept and forward input artifact paths as
additional --input arguments. No changes to the CLI argument parser or
backend client are required.

### Decision 3: Artifact Key as Component Parameter

Although Phase 1 hardcodes DRAFT_INIT_FILE as the artifact key, the file
picker component is designed with an internal artifact_key property. This
satisfies the extensibility requirement (NFR-006) by allowing future phases
to change the artifact key without restructuring the component. The
parameterization is at the component level, not at the configuration level,
keeping the Phase 1 scope minimal.

### Decision 4: Conditional Visibility via Existing Mechanism

The console already has an update_visibility() function that controls which
UI elements are shown based on the selected action. The file picker
visibility is integrated into this existing mechanism by adding an SDLC
workflow check to the visibility logic. This avoids introducing a separate
visibility system.

## Scope Boundaries

- The solution does not modify the backend API, daemon, or BackendClient.
- The solution does not modify the sdlc_10_requirement_v1 workflow
  definition or any other workflow bundle.
- The solution does not introduce new dependencies beyond Flet, which is
  already a console dependency.
- The solution handles only one input artifact (DRAFT_INIT_FILE) in this
  phase.


# Component Breakdown

## Component 1: File Picker UI Controls

Location: operator_console/app.py (within the app() closure)

Responsibilities:
- Compose a Flet FilePicker, a TextField for file path display, and a
  Browse button into a single row.
- Handle the FilePicker on_result callback to populate the TextField
  with the selected file path.
- Maintain the selected file path as state accessible to the submit
  action handler.

Constraints:
- Must use Flet controls only (NFR-001).
- Must operate on the local filesystem only (NFR-009).
- Must work on Windows (NFR-002, DC-008).

## Component 2: Conditional Visibility Logic

Location: operator_console/app.py (update_visibility function and
on_workflow_changed handler)

Responsibilities:
- Evaluate whether the file picker row should be visible based on:
  (a) the current action selection (must be "submit job"), and
  (b) the current workflow selection (workflow name must start with
      "sdlc_").
- Show the file picker row when both conditions are met.
- Hide the file picker row when either condition is not met.
- Reset the file picker state (clear the selected path) when the row
  is hidden, to prevent stale data from being submitted.

Constraints:
- Must integrate with the existing update_visibility() flow.
- Must respond to both workflow dropdown changes and action dropdown
  changes.

## Component 3: Runner Service Input Artifact Support

Location: operator_console/services/runner_service.py (RunnerActionService.submit_job)

Responsibilities:
- Accept an optional input_artifacts parameter (dict of key-value pairs)
  in the submit_job() method.
- When input_artifacts is provided and non-empty, append --input KEY=VALUE
  arguments to the CLI argument list before invoking submit_commands.main().
- When input_artifacts is not provided or empty, do not add any --input
  arguments (preserving existing behavior).

Constraints:
- Must not break existing submit_job() callers that do not pass input
  artifacts (FR-009).
- The parameter should be optional with a sensible default (empty dict
  or None).

## Component 4: Submit Action Integration

Location: operator_console/app.py (execute_action function)

Responsibilities:
- When the "submit job" action is triggered and an SDLC workflow is
  selected with a file picked, construct the input_artifacts dictionary
  with the DRAFT_INIT_FILE key and the selected file path as the value.
- Pass the input_artifacts to runner_service.submit_job().
- When the "submit job" action is triggered for a non-SDLC workflow or
  no file is selected, call submit_job() without input_artifacts
  (preserving generic submission behavior).

Constraints:
- Must validate that the file path is non-empty before including it
  in input_artifacts.
- Must handle the case where the file picker is visible but no file
  has been selected (show an error or warning).


# Work Breakdown Structure

The work for this plan is organized into work packages aligned with the
four components defined in the Component Breakdown section. Each work
package corresponds to a coherent unit of delivery. Detailed task
decomposition into backlog items is performed by the downstream sdlc_40
workflow and is out of scope for this plan document.

## WP-1: File Picker UI Controls

Deliverable: A new row of Flet controls (FilePicker, TextField, Browse
button) integrated into the console layout.

Scope: Component 1 responsibilities as defined in the Component Breakdown
section.

Dependencies: None (foundational UI component).

## WP-2: Conditional Visibility Logic

Deliverable: Extended visibility logic that conditionally shows or hides
the file picker row based on workflow and action selection state.

Scope: Component 2 responsibilities as defined in the Component Breakdown
section.

Dependencies: WP-1 (requires the file picker row to exist).

## WP-3: Runner Service Input Artifact Forwarding

Deliverable: Extended submit_job() method that accepts and forwards input
artifacts as --input CLI arguments.

Scope: Component 3 responsibilities as defined in the Component Breakdown
section.

Dependencies: None (service layer change, independent of UI).

## WP-4: Submit Action Integration

Deliverable: Wiring between the file picker UI, the visibility logic, and
the runner service to enable end-to-end SDLC job submission with input
artifacts.

Scope: Component 4 responsibilities as defined in the Component Breakdown
section.

Dependencies: WP-1, WP-2, WP-3 (integrates all other work packages).


# Task Decomposition Strategy

Detailed task decomposition is the responsibility of the downstream
sdlc_40_task_v1 workflow, which consumes this plan document and produces
a backlog document (BACKLOG-DOC) with granular tasks.

This plan document provides the following guidance for task decomposition:

- Each work package (WP-1 through WP-4) should be decomposed into
  implementable tasks by the backlog workflow.
- Tasks should respect the dependency order: WP-1 and WP-3 can be worked
  in parallel; WP-2 depends on WP-1; WP-4 depends on WP-1, WP-2, and
  WP-3.
- Regression testing for generic submission (FR-009, AC-008) should be
  included as part of each work package that modifies existing behavior.
- The risk items RA-001 through RA-006 should inform task-level risk
  mitigation during implementation.

No specific task assignments, scheduling, or sprint planning are included
in this document, as those belong to the backlog phase.


# Technical Constraints

The following technical constraints apply to the implementation. These
are derived from the requirement document constraints and the Layer 2
platform contract.

## Platform Constraints

- TC-001: Must use the Flet UI framework exclusively for all console UI
  components. Flet is the existing console dependency (NFR-001, DC-006).
- TC-002: Must work on Windows, the primary development platform
  (NFR-002, DC-008).
- TC-003: Must integrate with the existing submit_commands.main() entry
  point and its argparse-based argument parsing (DC-007).
- TC-004: Must operate on the local filesystem only. No remote or network
  file sources (NFR-009).

## Boundary Constraints

- TC-005: No changes to the backend API, daemon, or BackendClient are
  permitted (NFR-003, DC-009).
- TC-006: No changes to the sdlc_10_requirement_v1 workflow definition
  or any other workflow bundle (SC-012).
- TC-007: No new dependencies beyond Flet may be introduced (NFR-001).
- TC-008: Must not redefine or contradict Layer 1 governance or Layer 2
  platform constitution (NFR-005, DC-011).

## Metadata Constraints

- TC-009: Any generated or modified governed documents must conform to
  the Layer 2 platform metadata contract METADATA_CONTRACT.md (NFR-004,
  DC-010).



# Integration Points

## Integration Point 1: File Picker to Conditional Visibility

The file picker row visibility property is controlled by the
update_visibility() function. When the action dropdown or workflow
dropdown changes, update_visibility() is called and evaluates the
SDLC workflow + submit job condition. The file picker row visible
attribute is set accordingly and page.update() is called to refresh
the display.

## Integration Point 2: Workflow Dropdown to File Picker

The existing on_workflow_changed() and on_repo_changed() handlers
trigger update_visibility(). No new event handlers are needed for
the workflow-to-file-picker connection; the existing event routing
already covers this case.

## Integration Point 3: File Picker to Submit Action

When the user clicks "Run Action" with "submit job" selected, the
execute_action() function reads the current file path from the file
picker text field. If the workflow is an SDLC workflow (starts with
"sdlc_"), the file path is packaged as DRAFT_INIT_FILE and passed to
runner_service.submit_job().

## Integration Point 4: Runner Service to Submit Commands

The runner_service.submit_job() method constructs a CLI argument list
and invokes submit_commands.main(). The --input arguments are appended
to this list when input_artifacts are present. The submit_commands
module parses these arguments via its existing argparse --input handler
and passes them to BackendClient.submit_run() as input_payload.

## Integration Point 5: Console to Backend (Unchanged)

The backend receives input_payload through the existing
BackendClient.submit_run() interface. No backend changes are required.
The backend passes the input_payload to the job state, where it becomes
available as artifact path inputs for workflow steps.


# Data Flow

## Phase 1 Data Flow: SDLC Job Submission with Input Artifact

1. User selects a repository from the repo dropdown.
2. User selects an SDLC workflow (e.g., sdlc_10_requirement_v1) from
   the workflow dropdown.
3. The update_visibility() function detects that:
   - The action is "submit job" (default).
   - The workflow name starts with "sdlc_".
4. The file picker row becomes visible.
5. User clicks "Browse" and selects a .md file from the local filesystem.
6. The FilePicker on_result callback populates the TextField with the
   full file path.
7. User clicks "Run Action".
8. The execute_action() function:
   a. Reads the file path from the text field.
   b. Constructs input_artifacts = {"DRAFT_INIT_FILE": "<file_path>"}.
   c. Calls runner_service.submit_job() with input_artifacts.
9. The runner_service.submit_job() method:
   a. Builds the CLI argument list with --workflow-name and other args.
   b. Appends --input DRAFT_INIT_FILE=<file_path> to the argument list.
   c. Invokes submit_commands.main(argv=args).
10. The submit_commands.main() function:
    a. Parses the --input arguments via argparse.
    b. Calls _parse_kv() to build input_payload dict.
    c. Calls BackendClient.submit_run() with input_payload.
11. The backend receives the run request with DRAFT_INIT_FILE in the
    input_payload and creates a job.
12. The daemon picks up the job and processes it through the sdlc_10
    workflow steps.

## Generic Submission Data Flow (Preserved)

For non-SDLC workflows or when the action is not "submit job" with an
SDLC workflow, the data flow remains unchanged:

1. User selects a non-SDLC workflow.
2. The file picker row is hidden.
3. User clicks "Run Action".
4. The execute_action() function calls runner_service.submit_job()
   without input_artifacts.
5. The runner_service.submit_job() builds the argument list without
   any --input arguments.
6. submit_commands.main() processes the submission normally.


# Risk Mitigation Plan

## Risk 1: Flet FilePicker Platform Compatibility (RA-001)

Severity: Medium
Likelihood: Low

The Flet FilePicker component may have behavioral differences on Windows.
Flet FilePicker is a well-established component in the Flet framework,
but path formats (backslashes, spaces, long paths) on Windows require
attention.

Mitigation: Test file selection with various Windows path formats during
implementation. Ensure the path string is properly handled when passed
as a CLI argument.

## Risk 2: Regression in Generic Job Submission (RA-002)

Severity: High
Likelihood: Medium

Changes to the submit flow could break existing generic job submission.
The submit_job() method is called for all workflow submissions, not
just SDLC ones.

Mitigation: The input_artifacts parameter is optional and defaults to
None/empty. When not provided, the argument list is identical to the
current behavior. The file picker visibility is strictly conditional
on SDLC workflow + submit job action. Existing tests for generic
submission should be preserved and extended to cover the new code paths.

## Risk 3: Tight Coupling to DRAFT_INIT_FILE (RA-003)

Severity: Low
Likelihood: Low

Hardcoding DRAFT_INIT_FILE could make future extension more difficult.

Mitigation: The file picker component uses an internal artifact_key
property. Although Phase 1 hardcodes DRAFT_INIT_FILE, the component
design allows parameterization without structural changes. Extension
points are documented but not implemented.

## Risk 4: Backend Workflow Unavailability (RA-004)

Severity: Medium
Likelihood: Low

The sdlc_10_requirement_v1 workflow may not be synced to the backend.

Mitigation: This is a prerequisite dependency (DC-003). The console
relies on existing backend error handling for unavailable workflows.
The _build_error_payload() function in submit_commands.py already
handles "workflow not found" errors gracefully.

## Risk 5: File Path Format Issues (RA-005)

Severity: Medium
Likelihood: Medium

Windows file paths with spaces or special characters may cause issues
when passed as CLI arguments.

Mitigation: The _invoke() method in runner_service.py uses direct
function invocation (func(argv)) rather than shell execution, so
shell quoting issues are avoided. The argparse module handles argument
parsing without shell interpretation.

## Risk 6: Scope Creep (RA-006)

Severity: Low
Likelihood: Medium

Knowledge of the multi-phase plan may lead to premature implementation
of features beyond Phase 1 scope.

Mitigation: Strictly enforce scope boundaries. Phase 1 handles only
DRAFT_INIT_FILE for sdlc_10_requirement_v1. Future artifact keys and
workflows are documented as extension points but not implemented.


# Dependencies

## External Dependencies

- DC-001: Console configuration must include at least one repository
  with sdlc_10_requirement_v1 in its workflow list.
- DC-002: Draft initiative documents must exist on the local filesystem
  for users to select via the file picker.
- DC-003: The sdlc_10_requirement_v1 workflow must be synced to the
  backend and operational for end-to-end validation.
- DC-004: The Flet FilePicker component must be available in the
  version of Flet used by the console application. Flet is already
  a dependency of the console.
- DC-005: The runner_service module must be accessible and modifiable
  within the console application codebase.

## Internal Dependencies

- The operator_console/app.py module is the primary UI entry point.
  Changes to its structure affect the file picker integration.
- The runner_service.py module is the service layer between the console
  UI and the CLI commands. Changes to submit_job() affect all callers.
- The submit_commands.py module already supports --input arguments.
  No changes to this module are required.
- The backend_client.py module already supports input_payload in
  submit_run(). No changes to this module are required.

## Prerequisites

- The Flet framework must be installed in the console environment.
- The console configuration file must be valid and loadable.
- The backend must be running and accessible at the configured URL.


# Acceptance Criteria Summary

This section consolidates the acceptance criteria from the source
requirement document REQ-20260723-001_console-sdlc10-support.md and
maps each criterion to the relevant plan components and work packages.

| AC ID | Summary | Verifies | Plan Section | Work Package |
|---|---|---|---|---|
| AC-001 | Console launches without errors with SDLC workflows in config | NFR-007 | Solution Architecture | WP-2 |
| AC-002 | File picker appears when SDLC workflow + submit job selected | FR-001, FR-002 | Component 1, Component 2, Integration Points | WP-1, WP-2 |
| AC-003 | File picker hidden on non-SDLC workflow selection | FR-003 | Component 2, Integration Points | WP-2 |
| AC-004 | File picker hidden on non-submit action | FR-004 | Component 2, Integration Points | WP-2 |
| AC-005 | File path populated in text field after selection | FR-005, FR-006 | Component 1 | WP-1 |
| AC-006 | Job submitted with DRAFT_INIT_FILE input artifact | FR-007, FR-008 | Component 3, Component 4, Data Flow | WP-3, WP-4 |
| AC-007 | Daemon processes job through sdlc_10 workflow | FR-007 (E2E) | Data Flow | WP-4 |
| AC-008 | Generic submission continues without regression | FR-009 | Solution Architecture, Risk Assessment | WP-3, WP-4 |
| AC-009 | File picker extensible to different artifact keys | NFR-006 | Component 1, Architectural Decision 3 | WP-1 |



# Open Questions

## OQ-001: File Type Filtering

The file picker should ideally filter for .md files only. The Flet
FilePicker dialog_type and allowed_extensions parameters should be
verified for Windows compatibility. If filtering is not supported,
the solution falls back to showing all files and relying on the
user to select the correct file type.

## OQ-002: File Path Validation

Should the console validate that the selected file exists and is
readable before submission? The backend will reject invalid paths,
but client-side validation could improve user experience. The scope
of validation (existence check, readability check, file size check)
needs clarification.

## OQ-003: Error Handling for Missing File

If the user clicks "Run Action" with the file picker visible but
no file selected, should the console show an error dialog or
silently proceed without the input artifact? The recommended approach
is to show an error, but this needs confirmation against user
experience expectations.

## OQ-004: Relative vs Absolute Paths

The Flet FilePicker may return relative or absolute paths depending
on the platform. The solution should normalize to absolute paths
before submission. The exact behavior of Flet FilePicker on Windows
needs verification.

## OQ-005: Future Extension Mechanism

Phase 1 hardcodes DRAFT_INIT_FILE. For future phases, the mechanism
for determining which artifact key to use for a given workflow needs
design. Options include: (a) a configuration mapping in the console
config, (b) a workflow metadata field, or (c) a hardcoded mapping in
the console code. This is deferred but should be considered during
implementation to ensure the component design accommodates future
needs.

# Source Reference

This plan is derived from the following source documents:

- Primary Source: REQ-20260723-001_console-sdlc10-support.md (approved
  requirement document produced by sdlc_10_requirement_v1)
- Originating Initiative: INIT-20260723-001_console-sdlc10-support.md
  (approved initiative document)
- Review Reference: console-sdlc10-support-REV-20-plan.md (plan review,
  iteration 1)

The requirement document contains 10 functional requirements (FR-001
through FR-010), 9 non-functional requirements (NFR-001 through NFR-009),
12 scope items (SC-001 through SC-012), 9 acceptance criteria (AC-001
through AC-009), 11 dependencies and constraints (DC-001 through DC-011),
5 assumptions (A-001 through A-005), and 6 risk assessment items (RA-001
through RA-006).

All content in this plan is traceable to the approved requirement and
the originating initiative. No scope beyond the approved requirement
is included.


# Template Section Mapping

This section maps the document sections to the SYS-03-PL template
required sections for validation traceability.

| Template Section | Plan Section | Notes |
|---|---|---|
| 1. Title | Plan Overview | Level-1 heading |
| 2. Document Metadata | Document Metadata | Added in refinement iter-1 |
| 3. Implementation Approach | Solution Architecture | Includes architectural decisions |
| 4. Work Breakdown Structure | Work Breakdown Structure | Added in refinement iter-1 |
| 5. Task Decomposition Strategy | Task Decomposition Strategy | Added in refinement iter-1; defers to backlog phase |
| 6. Technical Constraints | Technical Constraints | Added in refinement iter-1 |
| 7. Risk Mitigation Plan | Risk Mitigation Plan | Renamed from Risk Assessment in iter-1 |
| 8. Dependencies | Dependencies | Unchanged |
| 9. Acceptance Criteria Summary | Acceptance Criteria Summary | Added in refinement iter-1 |
| 10. Source Reference | Source Reference | Added in refinement iter-1 |

Additional sections retained from the original plan for completeness:

| Additional Section | Purpose |
|---|---|
| Requirement Traceability | Maps requirements to plan sections |
| Component Breakdown | Detailed component responsibilities |
| Integration Points | Interface contracts between components |
| Data Flow | End-to-end submission flow |
| Open Questions | Items pending clarification |


# Refinement Log

## Iteration 1 (2026-07-23)

Refinement performed in response to review findings in
console-sdlc10-support-REV-20-plan.md (decision: REJECTED).

### Changes Made

| Finding | Severity | Action Taken |
|---|---|---|
| CF-001 | Critical | Changed doc_type from system to workflow_output |
| MF-001 | Major | Added missing template sections: Document Metadata, Work Breakdown Structure, Task Decomposition Strategy, Technical Constraints, Acceptance Criteria Summary, Source Reference. Added Template Section Mapping. |
| MF-002 | Minor | Added Acceptance Criteria Summary section with AC-to-component mapping |
| MF-003 | Minor | Updated scan_reason to be initiative-specific with producing workflow name |
| MF-004 | Minor | effective_version retained as job ID (observation only, no change) |

### Sections Added

- Document Metadata
- Work Breakdown Structure (WP-1 through WP-4, referencing Component Breakdown)
- Task Decomposition Strategy (defers detailed decomposition to sdlc_40)
- Technical Constraints (TC-001 through TC-009, consolidated from existing constraints)
- Acceptance Criteria Summary (AC-001 through AC-009 mapped to plan sections and WPs)
- Source Reference (consolidated from Requirement Traceability)
- Template Section Mapping (SYS-03-PL section alignment)
- Refinement Log (this section)
