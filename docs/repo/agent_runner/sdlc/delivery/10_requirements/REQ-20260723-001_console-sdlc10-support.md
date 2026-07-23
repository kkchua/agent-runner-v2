---
template_id: "SYS-03-REQ"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "structured requirements derived from approved initiative"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "approved"
effective_version: "SDLC10REQ-20260723-8657f082"
managed_by: "workflow-generated"
source_document: "INIT-20260723-001_console-sdlc10-support.md"
---

# Requirements Overview

This document captures the structured requirements for adding SDLC workflow
input handling to the operator console (Flet desktop GUI) for the
sdlc_10_requirement_v1 workflow (Initiative Intake).

The operator console currently supports generic job submission but has no
awareness of SDLC workflow input requirements. Users must manually construct
CLI commands with --input KEY=VALUE arguments to submit SDLC workflows.
This initiative addresses that gap by introducing a file picker UI component,
conditional visibility logic, and input artifact forwarding through the
existing submit flow.

The solution must enable users to select a draft initiative document from the
filesystem, submit it as a job to the backend with the correct DRAFT_INIT_FILE
input artifact, and have the daemon process it through the sdlc_10 workflow
pipeline -- all through the console interface.

This is Phase 1 of a planned 8-phase console SDLC support plan. The
architecture must be extensible to support additional input artifact keys
in future phases without structural changes.

## Traceability

All requirements in this document are derived from the approved initiative
document INIT-20260723-001_console-sdlc10-support.md. Requirement identifiers
use the following scheme:

- FR-xxx: Functional Requirements
- NFR-xxx: Non-Functional Requirements
- SC-xxx: Scope Items
- AC-xxx: Acceptance Criteria
- DC-xxx: Dependencies and Constraints
- RA-xxx: Risk Assessment Items


# Functional Requirements

FR-001: File Picker UI Component
The console must provide a file picker UI component composed of a Flet
FilePicker, a TextField for the file path, and a Browse button.
[Source: Initiative "In Scope"]

FR-002: Conditional Visibility - Workflow Selection
The file picker row must become visible only when the selected workflow name
starts with "sdlc_" AND the selected action is "submit job".
[Source: Initiative "Expected Outcomes #5"]

FR-003: Conditional Visibility - Workflow Deselection
The file picker row must be hidden when a non-SDLC workflow is selected from
the workflow dropdown.
[Source: Initiative "Success Criteria"]

FR-004: Conditional Visibility - Action Change
The file picker row must be hidden when the action is changed from "submit
job" to any other action.
[Source: Initiative "Expected Outcomes #5", inferred]

FR-005: File Browsing and Selection
The file picker must allow users to browse the local filesystem and select a
draft initiative document (.md file).
[Source: Initiative "Expected Outcomes #2"]

FR-006: Path Display in Text Field
Upon file selection, the path text field must be populated with the full
filesystem path of the selected file.
[Source: Initiative "Success Criteria"]

FR-007: Input Artifact Submission
When "Run Action" is clicked with "submit job" selected, the console must pass
the selected file path as --input DRAFT_INIT_FILE=<path> to the submit command.
[Source: Initiative "In Scope", "Expected Outcomes #3"]

FR-008: Runner Service Input Artifact Support
The runner_service.submit_job() function must accept and forward input artifact
paths to the backend.
[Source: Initiative "In Scope"]

FR-009: Generic Submission Preservation
Existing generic job submission for non-SDLC workflows must continue to function
without regression. The file picker must not interfere with the current submit
commands flow.
[Source: Initiative "Constraints", "Success Criteria"]

FR-010: Workflow Dropdown Integration
The existing workflow dropdown must list sdlc_10_requirement_v1 among available
workflows without modification to the dropdown itself.
[Source: Initiative "Expected Outcomes #1"]


# Non-Functional Requirements

NFR-001: Flet Framework Compliance
All UI components must use the Flet framework, which is the existing console
dependency. No additional UI framework dependencies may be introduced.
[Source: Initiative "Constraints"]

NFR-002: Windows Platform Support
The file picker must work on Windows, the primary development platform.
[Source: Initiative "Constraints"]

NFR-003: No Backend API Changes
No changes to the backend API or daemon behavior are permitted. The console
must use the existing backend interfaces for job submission.
[Source: Initiative "Constraints", "Out of Scope"]

NFR-004: Layer 2 Metadata Compliance
Any generated or modified governed documents must conform to the Layer 2
platform metadata contract (METADATA_CONTRACT.md).
[Source: Initiative "Constraints"]

NFR-005: Layer 1 and Layer 2 Boundary Respect
The solution must not redefine or contradict Layer 1 governance or Layer 2
platform constitution.
[Source: Initiative "Constraints"]

NFR-006: Extensibility
The file picker component architecture must be extensible to support different
input artifact keys in future SDLC phases (for example, INIT_FILE for sdlc_20,
REQ_FILE for sdlc_30) without requiring structural changes.
[Source: Initiative "Expected Outcomes #6", "Notes"]

NFR-007: Console Startup Stability
The console must launch without errors when SDLC workflows are present in the
configuration.
[Source: Initiative "Success Criteria"]

NFR-008: Single Artifact Scope
Only one input artifact (DRAFT_INIT_FILE) is handled in this phase. Multi-
artifact input support is explicitly deferred.
[Source: Initiative "Boundary Conditions"]

NFR-009: Local Filesystem Only
The file picker must operate on the local filesystem only. Remote or network
file sources are not in scope.
[Source: Initiative "Boundary Conditions"]


# Scope Definition

## In Scope

SC-001: File picker UI component (Flet FilePicker + TextField + Browse button).
[Source: Initiative "In Scope"]

SC-002: Conditional visibility logic to show the file picker only when the
action is "submit job" AND the selected workflow name starts with "sdlc_".
[Source: Initiative "In Scope"]

SC-003: Pass the selected file path as --input DRAFT_INIT_FILE=<path> to the
submit command.
[Source: Initiative "In Scope"]

SC-004: Update runner_service.submit_job() to accept and forward input artifact
paths to the backend.
[Source: Initiative "In Scope"]

## Out of Scope

SC-005: Support for sdlc_20 through sdlc_80 workflows. These are separate
future phases.
[Source: Initiative "Out of Scope"]

SC-006: Artifact dropdown for selecting approved outputs from previous runs.
[Source: Initiative "Out of Scope"]

SC-007: Output display for generated artifacts after job completion.
[Source: Initiative "Out of Scope"]

SC-008: Workflow-specific input validation or schema enforcement.
[Source: Initiative "Out of Scope"]

SC-009: Changes to backend API or daemon behavior.
[Source: Initiative "Out of Scope"]

SC-010: Multi-artifact input support. Only DRAFT_INIT_FILE is handled.
[Source: Initiative "Boundary Conditions"]

SC-011: Remote or network file source support.
[Source: Initiative "Boundary Conditions"]

SC-012: Creation or modification of the sdlc_10_requirement_v1 workflow
definition. The workflow must already be defined and synced to the backend.
[Source: Initiative "Boundary Conditions"]


# Acceptance Criteria

AC-001: Console Launch
The console launches without errors when the configuration contains one or
more SDLC workflows (workflows whose name starts with "sdlc_").
[Verifies: NFR-007]

AC-002: File Picker Visibility on SDLC Workflow Selection
Selecting sdlc_10_requirement_v1 from the workflow dropdown while "submit job"
is the selected action causes the file picker row to appear in the console
interface.
[Verifies: FR-001, FR-002]

AC-003: File Picker Hidden on Non-SDLC Workflow Selection
Selecting a non-SDLC workflow from the dropdown causes the file picker row to
be hidden.
[Verifies: FR-003]

AC-004: File Picker Hidden on Non-Submit Action
Changing the action from "submit job" to another action while an SDLC workflow
is selected causes the file picker row to be hidden.
[Verifies: FR-004]

AC-005: File Path Population
Browsing and selecting a .md file through the file picker populates the path
text field with the selected file's full filesystem path.
[Verifies: FR-005, FR-006]

AC-006: Job Submission with Input Artifact
Clicking "Run Action" with "submit job" selected and a file picked submits the
job successfully, and the backend receives the DRAFT_INIT_FILE input artifact
path.
[Verifies: FR-007, FR-008]

AC-007: Daemon Processing
The daemon picks up the submitted job and processes it through the sdlc_10
workflow steps, producing the expected INIT_FILE output artifact.
[Verifies: FR-007, end-to-end validation]

AC-008: Generic Submission Regression
Existing generic job submission (non-SDLC workflows, no input artifacts)
continues to function without regression after the changes.
[Verifies: FR-009]

AC-009: Extensibility Verification
The file picker component can be extended to accept a different artifact key
(for example, INIT_FILE) in a future phase without structural changes to the
component itself.
[Verifies: NFR-006]


# Dependencies and Constraints

## External Dependencies

DC-001: Console Configuration
operator-console.example.json must have at least one repository configured with
sdlc_10_requirement_v1 in its workflow list.
[Source: Initiative "Dependencies"]

DC-002: Draft Initiative Documents
Draft initiative documents must exist in the
docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory for users
to select.
[Source: Initiative "Dependencies"]

DC-003: Backend Workflow Availability
The sdlc_10_requirement_v1 workflow must be synced to the backend and
operational before this console feature can be validated end-to-end.
[Source: Initiative "Dependencies"]

DC-004: Flet FilePicker Component
The Flet FilePicker component must be available in the version of Flet used by
the console application.
[Source: Initiative "Dependencies"]

DC-005: Runner Service Module Access
The runner_service module must be accessible and modifiable within the console
application codebase (agent_runner_v2/).
[Source: Initiative "Dependencies"]

## Technical Constraints

DC-006: Flet Framework Only
Must use the Flet UI framework, which is the existing console dependency.
[Source: Initiative "Constraints"]

DC-007: Submit Commands Integration
Must integrate with the existing submit_commands.main() flow without breaking
current generic job submission behavior.
[Source: Initiative "Constraints"]

DC-008: Windows Platform
File picker must work on Windows, the primary development platform.
[Source: Initiative "Constraints"]

DC-009: No Backend Changes
No changes to backend API or daemon behavior are permitted.
[Source: Initiative "Constraints"]

DC-010: Layer 2 Metadata Compliance
Must conform to the Layer 2 platform metadata contract (METADATA_CONTRACT.md)
for any generated or modified governed documents.
[Source: Initiative "Constraints"]

DC-011: Layer Boundary Respect
Must not redefine or contradict Layer 1 governance or Layer 2 platform
constitution.
[Source: Initiative "Constraints"]

## Assumptions

A-001: The operator console application is the Flet-based desktop GUI located
at agent_runner_v2/operator_console/.

A-002: The runner_service module referenced in the initiative corresponds to
agent_runner_v2/operator_console/services/runner_service.py.

A-003: The submit_commands module referenced in the initiative corresponds to
agent_runner_v2/submit_commands.py.

A-004: "Workflow name starts with sdlc_" is the criterion for identifying SDLC
workflows in the console UI, as stated in the initiative.

A-005: The Phase 1 implementation hardcodes DRAFT_INIT_FILE as the artifact
key, but the architecture should allow straightforward extension to other
artifact keys.


# Risk Assessment

RA-001: Flet FilePicker Platform Compatibility
Risk: The Flet FilePicker component may have behavioral differences or
limitations on Windows compared to other platforms.
Mitigation: Verify Flet FilePicker functionality on Windows during
implementation. Test file selection with various path formats (backslash,
spaces in paths, long paths).
[Source: Initiative "Constraints" - Windows requirement]

RA-002: Regression in Generic Job Submission
Risk: Changes to the submit flow to support input artifacts may break existing
generic job submission for non-SDLC workflows.
Mitigation: Implement conditional logic that only activates input artifact
forwarding when the conditions are met (SDLC workflow + submit job action).
Preserve the existing submit path for all other cases. Include regression
testing for generic submission.
[Source: Initiative "Constraints", FR-009, AC-008]

RA-003: Tight Coupling to sdlc_10 Workflow
Risk: Hardcoding DRAFT_INIT_FILE may make future extension to other workflows
more difficult.
Mitigation: Design the file picker component with an abstraction for the
artifact key, even though Phase 1 hardcodes DRAFT_INIT_FILE. The architecture
should support parameterization without structural changes.
[Source: Initiative "Expected Outcomes #6", NFR-006]

RA-004: Backend Workflow Unavailability
Risk: The sdlc_10_requirement_v1 workflow may not be synced to the backend or
may be in an inconsistent state, blocking end-to-end validation.
Mitigation: Confirm workflow availability as a prerequisite (DC-003). Design
console behavior to handle submission gracefully when the backend workflow is
unavailable (rely on existing backend error handling).
[Source: Initiative "Dependencies", DC-003]

RA-005: File Path Format Issues
Risk: Users may select files with paths containing spaces, special characters,
or very long paths that could cause issues when passed as CLI arguments.
Mitigation: Ensure the file path is properly quoted when passed to the submit
command. Validate that the path is a valid filesystem path before submission.
[Source: Initiative "Constraints" - Windows platform]

RA-006: Scope Creep from Multi-Phase Planning
Risk: Knowledge of the 8-phase master plan may lead to premature
implementation of features beyond Phase 1 scope.
Mitigation: Strictly enforce scope boundaries defined in this document. Phase 1
handles only DRAFT_INIT_FILE for sdlc_10_requirement_v1. Document extension
points for future phases but do not implement them.
[Source: Initiative "Notes", "Out of Scope"]
