---
template_id: "SYS-03-REQ"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "structured requirements derived from approved initiative"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "SDLC10REQ-GEN-20260723-001"
managed_by: "workflow-generated"
source_document: "INIT-20260723-004_console-sdlc10-support.md"
---

# Requirements Overview

This document captures the structured requirements for adding SDLC workflow
input handling to the operator console (Flet desktop GUI) for the initiative
intake workflow (sdlc_00_init_doc_v1).

The operator console currently supports generic job submission via the "Submit"
action but has no awareness of SDLC workflow input requirements. Users must
manually construct CLI commands with --input KEY=VALUE arguments to submit SDLC
workflows. This initiative addresses that gap by introducing a file picker UI
component, conditional visibility logic, and input artifact forwarding through
the existing submit flow.

The solution must enable users to select a draft initiative document from the
local filesystem, submit it as a job to the backend with the correct
DRAFT_INIT_FILE input artifact, and have the daemon process it through the
sdlc_00_init_doc_v1 workflow to produce an approved INIT_FILE.

This is Phase 1 of an eight-phase console SDLC support plan. Subsequent phases
will extend the console to support additional SDLC workflows (sdlc_10 through
sdlc_80) with appropriate input artifact selection.

## Source Initiative Reference

- Approved initiative: INIT-20260723-004_console-sdlc10-support.md
- Target workflow: sdlc_00_init_doc_v1
- Input artifact: DRAFT_INIT_FILE
- Output artifact: INIT_FILE

# Functional Requirements

## FR-001: File Picker UI Component

The console must provide a file picker row consisting of a Flet FilePicker, a
read-only TextField displaying the selected file path, and a Browse button. The
file picker must allow users to select Markdown (.md) files from the local
filesystem.

Traceability: Initiative Section "Scope - In Scope" (file picker UI component).

## FR-002: Conditional Visibility of File Picker Row

The file picker row must be visible only when BOTH of the following conditions
are met:
1. The selected action is "Submit" (submit job).
2. The selected workflow name starts with the prefix "sdlc_".

When either condition is not met, the file picker row must be hidden from the
user interface.

Traceability: Initiative Section "Expected Outcomes" item 5, and Section
"Scope - In Scope" (conditional visibility).

## FR-003: Draft Initiative Document Selection

Users must be able to browse and select a DRAFT_INIT_FILE (Markdown format)
from the local filesystem through the file picker. The selected file path must
be displayed in the read-only TextField.

Traceability: Initiative Section "Expected Outcomes" item 2.

## FR-004: Input Artifact Forwarding to Submit Command

When the user clicks "Run Action" with "Submit" selected, the console must pass
the selected file path as --input DRAFT_INIT_FILE=<path> to the submit command.
The runner_service.submit_job() method must accept an input_artifacts parameter
and forward it as --input KEY=VALUE arguments to submit_commands.main().

Traceability: Initiative Section "Expected Outcomes" item 3, and Section
"Scope - In Scope" (pass selected file path, update runner_service).

## FR-005: SDLC Directory Resolution for File Picker

When the Browse button is clicked for a known SDLC input artifact key, the file
picker must set its root directory to the corresponding SDLC delivery
subdirectory within the selected repository. For DRAFT_INIT_FILE, this is
docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives.

Traceability: Derived from initiative Section "Dependencies" (draft initiative
documents location) and codebase SDLC_INPUT_DIRS mapping.

## FR-006: Extensibility for Future SDLC Workflows

The file picker component architecture must be extensible to support different
input artifact keys in future phases. The current implementation may hardcode
DRAFT_INIT_FILE for Phase 1, but the structure must accommodate additional
artifact keys (for example, INIT_FILE for sdlc_10, REQ_FILE for sdlc_20)
without requiring structural refactoring.

Traceability: Initiative Section "Boundary Conditions" (extensible to support
different input artifact keys).

## FR-007: Non-SDLC Workflow Submission Continuity

The console must continue to function correctly for non-SDLC workflows. Generic
job submission must work without regression. No file picker artifacts shall be
passed for non-SDLC workflow submissions.

Traceability: Initiative Section "Boundary Conditions" (continue to function
correctly for non-SDLC workflows) and Section "Success Criteria" (non-SDLC
regression).

## FR-008: Dynamic Input Fields from Workflow Definition

The console must dynamically generate input fields based on the selected
workflow's bundle definition. For each required input artifact key ending with
"_FILE", a file picker row with Browse button must be displayed. For non-file
input keys, a text input field must be displayed.

Traceability: Initiative Section "Scope - In Scope" (wire the existing file
picker to submit job action flow) and codebase rebuild_input_fields() pattern.

## FR-009: Input Path Resolution

The console must resolve input values to absolute file paths before passing them
to the submit command. If the user provides a filename only (not an absolute
path), the console must resolve it relative to the known SDLC delivery
subdirectory for that artifact key. If the file does not exist, an error must
be reported to the user.

Traceability: Derived from initiative Section "Success Criteria" and codebase
resolve_input_path() pattern.

## FR-010: Error Display for Input Resolution Failures

If the selected file does not exist or cannot be resolved, the console must
display a clear error message indicating which artifact key failed and the
expected directory path. The error must be shown via the existing error dialog
mechanism or in the output field.

Traceability: Derived from initiative Section "Success Criteria" and codebase
error handling patterns.

# Non-Functional Requirements

## NFR-001: Flet UI Framework Compatibility

All UI components must use the Flet UI framework. The existing console
dependency on Flet must be maintained. No additional UI framework dependencies
shall be introduced.

Traceability: Initiative Section "Constraints" (must use Flet UI framework).

## NFR-002: Windows Platform Compatibility

The file picker must work correctly on Windows, which is the primary development
platform. File path handling must use Windows-compatible path conventions.

Traceability: Initiative Section "Constraints" (file picker must work on
Windows).

## NFR-003: No Backend API Changes

No changes to the backend API, daemon behavior, or workflow definitions are
required or permitted. All changes must be confined to the operator_console
package and its services.

Traceability: Initiative Section "Constraints" (no changes to backend API) and
Section "Scope - Out of Scope".

## NFR-004: Submit Command Interface Preservation

The console must integrate with the existing submit_commands.main() flow without
changing the submit command interface. The --input KEY=VALUE argument format
must continue to be supported.

Traceability: Initiative Section "Constraints" (integrate with existing
submit_commands.main() flow) and Section "Dependencies" (submit_commands.main()
must support --input KEY=VALUE).

## NFR-005: Architectural Extensibility

The console architecture must remain extensible for future SDLC workflow phases
without requiring structural refactoring. The dynamic input field mechanism must
support adding new artifact keys and workflow-specific input requirements.

Traceability: Initiative Section "Constraints" (architecture must remain
extensible) and Section "Boundary Conditions".

## NFR-006: Console Startup Stability

The console must launch without errors when SDLC workflows are present in the
configuration. No startup failures or regressions shall be introduced by the
new functionality.

Traceability: Initiative Section "Success Criteria" (console launches without
errors).

## NFR-007: Code Containment

All code changes must be confined to the operator_console package and its
services. No modifications to core runner modules, daemon, backend client, or
workflow definitions are permitted.

Traceability: Initiative Section "Constraints" (all changes confined to
operator_console package).

# Scope Definition

## In Scope

1. File picker UI component (Flet FilePicker, read-only TextField, Browse
   button) connected to the submit action.
2. Conditional visibility logic: show file picker row only when action is
   "Submit" AND selected workflow name starts with "sdlc_".
3. Passing selected file path as --input DRAFT_INIT_FILE=<path> to the submit
   command.
4. Updating runner_service.submit_job() to accept an input_artifacts parameter
   and forward it as --input KEY=VALUE arguments.
5. Wiring the existing file picker in operator_console/app.py to the submit job
   action flow.
6. SDLC directory resolution for the file picker root directory.
7. Input path resolution from filename to absolute path using SDLC_INPUT_DIRS
   mapping.

## Out of Scope

1. Support for sdlc_10 through sdlc_80 workflows (separate phases per the
   masterplan SDLC_CONSOLE_APP_PLAN.md).
2. Artifact dropdown for selecting approved outputs from previous runs.
3. Output display for generated artifacts after job completion.
4. Workflow-specific input validation or schema enforcement.
5. Changes to backend API, daemon behavior, or workflow definitions.
6. Modifications to the submit_commands.main() interface.
7. Changes to any module outside the operator_console package.

## Boundary Conditions

- Phase 1 targets sdlc_00_init_doc_v1 exclusively. This workflow takes
  DRAFT_INIT_FILE as input and produces INIT_FILE. Other SDLC workflows require
  different input artifact keys and will be handled in subsequent phases.
- The file picker component must be architecturally extensible to support
  different input artifact keys in future phases but hardcodes DRAFT_INIT_FILE
  for this phase.
- The console must continue to function correctly for non-SDLC workflows
  (generic job submission without file picker input).
- No changes to the backend, daemon, or workflow definition layer are required.

# Acceptance Criteria

## AC-001: Console Launches with SDLC Workflows

Given the console configuration includes at least one repository with
sdlc_00_init_doc_v1 in its workflow list, when the console is launched, then
the console starts without errors and the workflow dropdown includes
sdlc_00_init_doc_v1.

## AC-002: File Picker Visible for SDLC Submit

Given sdlc_00_init_doc_v1 is selected in the workflow dropdown, and the action
is "Submit", when the UI renders, then the file picker row (TextField + Browse
button) for DRAFT_INIT_FILE is visible.

## AC-003: File Picker Hidden for Non-SDLC Workflows

Given a non-SDLC workflow is selected in the workflow dropdown, when the UI
renders, then the file picker row is not visible.

## AC-004: File Picker Hidden for Non-Submit Actions

Given sdlc_00_init_doc_v1 is selected in the workflow dropdown, and the action
is NOT "Submit" (for example, "Approve" or "Reject"), when the UI renders, then
the file picker row is not visible.

## AC-005: Browse and Select Draft Initiative

Given the file picker row is visible, when the user clicks Browse and selects a
.md file, then the file path is populated in the read-only TextField and the
path points to a valid file on the filesystem.

## AC-006: Successful Job Submission with Input Artifact

Given a valid DRAFT_INIT_FILE is selected and the user clicks "Run Action" with
"Submit", then the job is submitted to the backend with the argument --input
DRAFT_INIT_FILE=<absolute-path> and the backend receives the correct artifact
path.

## AC-007: Daemon Processes Submitted Job

Given a job is submitted with a valid DRAFT_INIT_FILE input artifact, when the
daemon picks up the job, then the job is processed through the
sdlc_00_init_doc_v1 workflow and an approved INIT_FILE artifact is produced.

## AC-008: Non-SDLC Submission Regression

Given a non-SDLC workflow is selected and the user clicks "Run Action" with
"Submit", then the job is submitted successfully without any file picker
artifacts being passed in the --input arguments.

## AC-009: Error Handling for Missing File

Given a DRAFT_INIT_FILE value that does not resolve to an existing file, when
the user clicks "Run Action" with "Submit", then an error message is displayed
indicating the file was not found and the expected directory path.

## AC-010: Dynamic Workflow Input Adaptation

Given different SDLC workflows are selected (when available), when the UI
renders, then the input fields adapt to show the required input artifacts for
each workflow as defined in its bundle definition.

# Dependencies and Constraints

## External Dependencies

1. **Console Configuration**: operator-console.example.json (or the active
   operator-console.json) must have at least one repository configured with
   sdlc_00_init_doc_v1 in its workflow list.

2. **Draft Initiative Documents**: Draft initiative documents must exist in the
   docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory for the
   file picker to have files to select.

3. **Workflow Availability**: The sdlc_00_init_doc_v1 workflow must be synced to
   the backend and available in the workflow dropdown.

4. **Submit Command Interface**: The submit_commands.main() function must
   continue to support the --input KEY=VALUE argument format.

5. **Flet Framework**: The Flet Python framework must be installed with the
   FilePicker component available.

6. **Workflow Package Loader**: The workflow_packages.loader module must be able
   to parse the workflow bundle definition and expose required_inputs for the
   init step.

## Technical Constraints

1. Must use Flet UI framework (existing console dependency).
2. Must integrate with existing submit_commands.main() without changing its
   interface.
3. File picker must work on Windows (primary development platform).
4. No changes to backend API or daemon behavior are required or permitted.
5. All changes must be confined to the operator_console package and its
   services.
6. The console architecture must remain extensible for future SDLC workflow
   phases without structural refactoring.
7. The artifact key name must use the canonical form DRAFT_INIT_FILE as defined
   in artifact_keys.py and constants.py.

## Assumptions

1. The existing file picker component in operator_console/app.py (Flet FilePicker
   and associated controls) is functional and can be wired to the submit flow.
2. The SDLC_INPUT_DIRS mapping in app.py correctly maps DRAFT_INIT_FILE to the
   draft initiatives directory.
3. The sdlc_00_init_doc_v1 workflow bundle definition declares DRAFT_INIT_FILE
   as a required input for its init step.
4. The runner_service.submit_job() method can be extended to accept
   input_artifacts without breaking existing callers.
5. The FilePicker.pick_files() API supports root_directory and file type
   filtering on Windows.

# Risk Assessment

## R-001: File Picker API Behavior on Windows

- Risk: The Flet FilePicker pick_files() API may have platform-specific behavior
  differences on Windows (for example, root_directory support, path format).
- Severity: Medium
- Mitigation: Test file picker on Windows early in implementation. If
  root_directory is not respected, fall back to last-used directory or
  user home directory.

## R-002: Workflow Bundle Loading Failures

- Risk: The workflow package loader may fail to parse certain bundle definitions
  or the init step may not declare required_inputs correctly, causing the
  dynamic input panel to show errors.
- Severity: Medium
- Mitigation: The console already handles bundle loading errors gracefully with
  error messages displayed in the dynamic input panel. Maintain this error
  handling pattern.

## R-003: Input Path Resolution Edge Cases

- Risk: File path resolution may fail for edge cases such as relative paths,
  paths with special characters, or paths that cross directory boundaries.
- Severity: Low
- Mitigation: Use Path objects for all path operations. Validate that resolved
  paths exist before submitting. Provide clear error messages for unresolvable
  paths.

## R-004: Regression in Non-SDLC Workflow Submission

- Risk: Changes to the submit flow may inadvertently affect non-SDLC workflow
  submissions by passing empty or incorrect input artifacts.
- Severity: High
- Mitigation: Ensure that input_artifacts is only populated when dynamic input
  fields have values. Verify that non-SDLC workflows (which have no dynamic
  input fields) do not pass any --input arguments. Include regression test
  for non-SDLC submission.

## R-005: Future Phase Extensibility

- Risk: The Phase 1 implementation may be too tightly coupled to
  sdlc_00_init_doc_v1 specifics, making it difficult to extend for subsequent
  SDLC workflow phases.
- Severity: Medium
- Mitigation: Use the dynamic input field mechanism (rebuild_input_fields) that
  reads required inputs from the workflow bundle definition. The SDLC_INPUT_DIRS
  mapping already supports all known artifact keys. Ensure the file picker
  component is generic per artifact key.

## R-006: Concurrent File Picker State

- Risk: The shared file picker with active_file_key state may cause incorrect
  file assignment if the user switches workflow while a file picker dialog is
  open.
- Severity: Low
- Mitigation: Use per-field browse handlers (closure-captured key parameter)
  rather than a single shared active_file_key to avoid state conflicts. The
  existing code pattern in app.py already uses closure-captured key parameters
  for Browse button handlers.
