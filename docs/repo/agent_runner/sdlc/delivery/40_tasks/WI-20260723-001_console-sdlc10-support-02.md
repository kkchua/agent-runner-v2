---
template_id: "SYS-03-TK"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "task specification for initiative execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC40TSK-20260723-37a5bd7b"
managed_by: "workflow-generated"
---


# Task Overview

This task implements the file selection callback and state management for
the operator console file picker component. It adds the FilePicker
on_result callback logic that populates the file path TextField with the
selected file path and maintains the selected path as closure state
accessible to the submit action handler. The component also exposes an
internal artifact_key property hardcoded to DRAFT_INIT_FILE for Phase 1,
supporting future extensibility without structural changes.

This is the second work item (WI-02) in the approved backlog
BACKLOG-20260723-001_console-sdlc10-support.md, belonging to Work Package
WP-1 (File Picker UI Controls). It depends on WI-01 which creates the
file picker row layout. This task adds the interactive behavior to the
static controls created by WI-01.


# Backlog Traceability

| Field | Value |
|---|---|
| Backlog Document | BACKLOG-20260723-001_console-sdlc10-support.md |
| Backlog Job ID | SDLC30BLG-20260723-6e878812 |
| Work Item ID | WI-20260723-001_console-sdlc10-support-02 |
| Work Package | WP-1 (File Picker UI Controls) |
| Parent Plan | PLAN-20260723-001_console-sdlc10-support.md |
| Plan Component | Component 1: File Picker UI Controls |
| Priority | high |
| Estimated Effort | 1 story point |

## Upstream Traceability Chain

| Document | Reference | Status |
|---|---|---|
| Initiative | INIT-20260723-001_console-sdlc10-support.md | Approved |
| Requirement | REQ-20260723-001_console-sdlc10-support.md | Approved |
| Plan | PLAN-20260723-001_console-sdlc10-support.md | Approved |
| Backlog | BACKLOG-20260723-001_console-sdlc10-support.md | Approved |

## Requirements Addressed

This work item contributes to the following requirements from the approved
requirement document:

- FR-005: File browsing and selection (callback completion)
- FR-006: Path display in text field (populates TextField on selection)
- AC-005: File selection populates the path text field with full path
- AC-009: Component exposes artifact_key set to DRAFT_INIT_FILE
- NFR-001: Use Flet controls exclusively
- NFR-002: Must work on Windows
- NFR-006: Extensibility via artifact_key property
- TC-001: Flet controls only constraint
- RA-005: Windows path format handling (backslashes and spaces)


# Task Scope

## In Scope

1. Implement the FilePicker on_result callback function that fires when
   the user selects a file from the file dialog.
2. In the callback, extract the selected file path from the FilePicker
   event result and populate the file path TextField with the full path.
3. Maintain the selected file path as a closure-level state variable
   within the app() function, accessible to the execute_action() function
   for submit processing.
4. Normalize the selected file path to an absolute path using Python
   pathlib to handle Windows path formats correctly (backslashes, spaces,
   drive letters).
5. Define an internal artifact_key variable or constant set to
   "DRAFT_INIT_FILE" to identify the input artifact type for Phase 1.
6. Ensure the selected file path state is readable by the submit action
   handler in execute_action() (to be wired in WI-07).

## Out of Scope

- File picker row layout creation (WI-01, prerequisite).
- Conditional visibility logic for the file picker row (WI-03).
- File picker state reset on hide (WI-04).
- Input artifact forwarding through the submit flow (WI-07).
- Any changes to runner_service.py or submit_commands.py.
- End-to-end regression testing (WI-08).
- File type filtering in the file dialog (OQ-001, deferred).

## Explicit Assumptions

- A-001: The operator_console/app.py module structure has not changed
  since the plan was authored. The app() closure, update_visibility()
  function, and execute_action() function are all present and accessible.
- A-002: The Flet FilePicker on_result callback receives an event object
  with a path or paths attribute containing the selected file path(s) as
  strings.
- A-003: The file picker row, TextField, and FilePicker controls created
  by WI-01 are accessible within the app() closure scope for callback
  binding.
- A-TASK-001: The selected file path can be stored as a nonlocal variable
  within the app() closure, following the existing pattern used by
  selected_run_id and active_runs variables in the current codebase.
- A-TASK-002: Python pathlib.Path can resolve the file path to an
  absolute path on Windows, handling backslashes and spaces correctly.


# Acceptance Criteria

## AC-TASK-001: File Selection Populates TextField

When the user clicks Browse and selects a file from the file dialog, the
on_result callback fires and the file path TextField is populated with
the full filesystem path of the selected file. The path is displayed as
a readable string in the TextField.

## AC-TASK-002: Selected Path Stored in Closure State

The selected file path is stored in a closure-level variable within the
app() function. This variable is accessible from the execute_action()
function for use during submit processing. The state variable is updated
each time a new file is selected.

## AC-TASK-003: Path Normalization to Absolute

The file path stored in state and displayed in the TextField is normalized
to an absolute path. On Windows, this means the path includes the drive
letter and uses backslash separators. Spaces in the path are preserved
without quoting or escaping.

## AC-TASK-004: Artifact Key Property Defined

An internal artifact_key property or constant is defined within the file
picker component scope and set to "DRAFT_INIT_FILE". This value identifies
the input artifact type for Phase 1 and can be referenced by the submit
action handler (WI-07) when constructing the input_artifacts dictionary.

## AC-TASK-005: Existing Functionality Preserved

No existing controls, event handlers, or layout structure are modified.
The callback and state management logic is additive. The existing test
suite (if any) for console functionality continues to pass.

## AC-TASK-006: Windows Path Compatibility

The callback correctly handles Windows-style file paths including:
- Paths with backslash separators (e.g., C:\Users\docs\file.md)
- Paths with spaces (e.g., C:\My Documents\file.md)
- Paths with drive letters (e.g., D:\Projects\file.md)
No path corruption or truncation occurs during callback processing.


# Technical Approach

## File Modifications

The primary file to modify is:
- agent_runner_v2/operator_console/app.py

Within the app() closure, the following additions are needed:

1. Declare a closure-level variable (e.g., selected_file_path = "") to
   store the currently selected file path. This follows the existing
   nonlocal state pattern used by selected_run_id in the current code.
2. Define an artifact_key constant (e.g., artifact_key = "DRAFT_INIT_FILE")
   within the app() closure scope.
3. Implement the on_result callback function for the FilePicker control
   created by WI-01. The callback receives the file picker event, extracts
   the selected path, normalizes it using pathlib.Path, updates the
   closure state variable, and sets the TextField value.
4. Bind the on_result callback to the FilePicker control.

## Integration with WI-01 Controls

The file picker row created by WI-01 contains a FilePicker instance, a
TextField for path display, and a Browse button. This task wires the
callback logic to those controls:

- The FilePicker on_result event triggers the path extraction and
  display update.
- The TextField value is set to the normalized absolute path string.
- The closure state variable is updated to the same path value.

## Path Normalization Strategy

Use Python pathlib.Path to normalize the selected file path:

1. Receive the raw path string from the FilePicker event.
2. Construct a pathlib.Path object from the raw string.
3. Resolve or convert to absolute path using Path.resolve() or
   Path.absolute().
4. Convert to string representation for display and state storage.

This approach handles Windows-specific path formats (backslashes, drive
letters, spaces) without manual string manipulation.

## Key Design Decisions

1. The closure-level state variable approach is chosen over a module-level
   global variable. This keeps the state scoped to the app() closure and
   follows the existing pattern in app.py where selected_run_id and
   active_runs use nonlocal declarations.
2. The artifact_key is defined as a simple string constant within the
   closure scope. This provides a single location to change the key when
   future phases introduce additional artifact types.
3. Path normalization uses pathlib rather than os.path for consistency
   with the existing import of pathlib in app.py (used by the main()
   function).
4. The on_result callback handles the single-file selection case. If
   FilePicker returns multiple paths (which is not expected for this use
   case), the callback selects the first path.

## Approach Rationale

This approach follows the existing console UI pattern in app.py where
state is maintained via closure variables and event handlers are defined
as nested functions within the app() closure. The FilePicker callback
follows the same pattern as other event handlers (e.g., update_visibility,
execute_action) in the existing code. The pathlib normalization ensures
cross-platform correctness while being minimal in scope.


# Files and Components

## Files to Modify

| File | Change Description |
|---|---|
| agent_runner_v2/operator_console/app.py | Add on_result callback, closure state variable, artifact_key constant, and path normalization logic |

## Files NOT to Modify (Constraints)

| File | Reason |
|---|---|
| agent_runner_v2/submit_commands.py | TC-003 constraint; no changes allowed |
| agent_runner_v2/backend_client.py | Not in scope for this work item |
| agent_runner_v2/operator_console/services/runner_service.py | WP-3 scope; not this work item |

## Components Affected

| Component | Location | Impact |
|---|---|---|
| Operator Console UI | agent_runner_v2/operator_console/app.py | FilePicker callback logic added |
| File Picker State | app() closure in app.py | New closure variable for selected path |
| Artifact Key | app() closure in app.py | New constant for DRAFT_INIT_FILE |

## Test Files

No new test files are created in this work item. The existing test
infrastructure should continue to pass. Callback behavior verification
is deferred to WI-08 (end-to-end regression testing).


# Dependencies

## Internal Dependencies

| Dependency | Dependency Type |
|---|---|
| WI-20260723-001_console-sdlc10-support-01 | Structural (requires file picker row, TextField, and FilePicker controls to exist) |

This work item directly extends the controls created by WI-01. The
FilePicker instance, TextField, and Browse button must be present in
the app() closure for the callback to be bound.

## Downstream Dependents

| Dependent Work Item | Dependency Type |
|---|---|
| WI-20260723-001_console-sdlc10-support-07 | Integration (requires selected path state and artifact_key for submit wiring) |

## External Prerequisites

| Dependency | Description | Status |
|---|---|---|
| DC-004 | Flet FilePicker available in installed Flet version | Assumed met |

## Parallel Opportunities

This work item must follow WI-01 and cannot be parallelized with it.
However, it can be executed in parallel with WI-03 (Visibility Extension)
once WI-01 is complete, since WI-03 depends on WI-01 but not on WI-02.


# Risk Factors

## RF-001: Flet FilePicker on_result Event Format

Risk: The Flet FilePicker on_result callback may use different event
attribute names or structures across Flet versions. The path attribute
may be named differently (e.g., path vs paths, file_name vs path).

Mitigation: Check the installed Flet version documentation during
implementation. The Flet FilePicker typically provides path (str) for
single file selection or paths (list) for multiple file selection. Handle
both cases gracefully.

## RF-002: Path Normalization Edge Cases on Windows

Risk: Windows file paths may contain edge cases such as UNC paths,
extended-length paths (\\?\ prefix), or paths with special characters
that pathlib.Path does not handle as expected.

Mitigation: Use pathlib.Path.resolve() for normalization, which handles
standard Windows paths correctly. For UNC paths or extended-length paths,
the standard FilePicker dialog is unlikely to return them in Phase 1
usage. Log a warning if normalization fails and fall back to the raw
path string.

## RF-003: Closure State Scope and Accessibility

Risk: The closure-level state variable must be accessible from both the
on_result callback and the execute_action() function. If the variable
scope is incorrect, the submit handler may not see the selected path.

Mitigation: Follow the existing pattern in app.py where nonlocal
variables (e.g., selected_run_id) are declared at the app() closure level
and accessed by nested functions. Use the nonlocal keyword in the
callback if reassignment is needed.

## RF-004: Race Conditions Between Callback and Submit

Risk: If the user clicks Run Action before the on_result callback has
completed processing, the state variable may not yet be updated.

Mitigation: Flet event handlers execute synchronously within the UI event
loop. The on_result callback completes before the next event (e.g., button
click) is processed. No explicit synchronization is needed for this
single-threaded UI model.


# Open Questions

## OQ-001: File Type Filtering

The file picker should ideally filter for .md files only. The Flet
FilePicker dialog_type and allowed_extensions parameters should be
verified for Windows compatibility. If filtering is not supported,
the solution falls back to showing all files. This question originates
from the backlog and affects WI-01 setup, but the on_result callback
in this work item should handle any file type gracefully.

Impact: Low. The callback processes whatever path the FilePicker returns
regardless of filtering.

## OQ-004: Relative vs Absolute Paths

The Flet FilePicker may return relative or absolute paths depending on
the platform. This task specifies normalization to absolute paths using
pathlib.Path.resolve(). The exact behavior of the Flet FilePicker on
Windows needs verification during implementation.

Impact: Medium. If the FilePicker returns relative paths, the
normalization step ensures correctness. If it returns absolute paths,
the normalization is a no-op.

## OQ-005: Future Extension Mechanism

Phase 1 hardcodes DRAFT_INIT_FILE. For future phases, the mechanism for
determining which artifact key to use for a given workflow needs design.
This task defines artifact_key as a closure-level constant to make future
replacement straightforward. The design should accommodate a mapping from
workflow name to artifact key in future phases.

Impact: Low for this task. The constant is defined but not consumed until
WI-07.


# Source Reference

This task specification is derived from:

- Source Backlog: BACKLOG-20260723-001_console-sdlc10-support.md (approved)
- Source Backlog Job: SDLC30BLG-20260723-6e878812
- Source Plan: PLAN-20260723-001_console-sdlc10-support.md (approved)
- Producing Workflow: sdlc_40_task_v1
- Producing Step: generate_task
- Task Job ID: SDLC40TSK-20260723-37a5bd7b

## Audit and Compliance Notes

- This task operates within Layer 3 boundaries.
- Layer 1 governance (METADATA_STANDARD.md) is treated as read-only.
- Layer 2 platform constitution (RUNTIME_MODEL.md, METADATA_CONTRACT.md) is treated as read-only.
- No governance or platform contract redefinition is included.
- The task metadata conforms to Layer 1 required fields and Layer 2 platform extensions.