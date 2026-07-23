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
effective_version: "SDLC40TSK-20260723-5d347d98"
managed_by: "workflow-generated"
---


# Task Overview

This task implements the file picker row layout for the operator console,
which is the foundational UI component for SDLC workflow input artifact
selection. The task creates a new row of Flet controls in the operator
console application consisting of a FilePicker component, a TextField for
file path display, and a Browse button. This row will be integrated into
the existing console layout without restructuring existing controls.

This is the first work item (WI-01) in the approved backlog
BACKLOG-20260723-001_console-sdlc10-support.md, belonging to Work Package
WP-1 (File Picker UI Controls). It is a foundational item with no upstream
dependencies -- subsequent work items for visibility logic, state
management, and submission wiring all depend on this component being in
place.


# Backlog Traceability

| Field | Value |
|---|---|
| Backlog Document | BACKLOG-20260723-001_console-sdlc10-support.md |
| Backlog Job ID | SDLC30BLG-20260723-6e878812 |
| Work Item ID | WI-20260723-001_console-sdlc10-support-01 |
| Work Package | WP-1 (File Picker UI Controls) |
| Parent Plan | PLAN-20260723-001_console-sdlc10-support.md |
| Plan Component | Component 1: File Picker UI Controls |
| Priority | high |
| Estimated Effort | 2 story points |

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

- FR-001: File picker UI for selecting draft initiative documents
- AC-002: File picker row visible when SDLC workflow and submit job are selected (partial -- layout only, visibility is WI-03)
- NFR-001: Use Flet controls exclusively
- NFR-002: Must work on Windows
- TC-001: Flet controls only constraint
- TC-004: Local filesystem only constraint


# Task Scope

## In Scope

1. Create a new Flet FilePicker component instance within the app()
   closure in app.py.
2. Create a TextField control to display the selected file path (read-only
   display of the chosen file path).
3. Create a Browse button (ElevatedButton or similar) that triggers the
   FilePicker dialog.
4. Arrange these three controls into a new ft.Row layout element.
5. Integrate the new row into the existing page layout in app.py without
   restructuring or removing existing controls.
6. Set the row to be initially hidden (visible=False) since visibility
   logic is the responsibility of WI-03.

## Out of Scope

- File selection callback and state management (WI-02).
- Conditional visibility logic based on workflow and action selection
  (WI-03).
- File picker state reset on hide (WI-04).
- Input artifact forwarding through the submit flow (WI-07).
- Any changes to runner_service.py or submit_commands.py.
- End-to-end regression testing (WI-08).

## Explicit Assumptions

- A-001: The operator_console/app.py module structure has not changed
  since the plan was authored. Confirmed by source code inspection --
  the app() closure, update_visibility() function, and execute_action()
  function are all present and accessible.
- A-002: The Flet version installed supports FilePicker on Windows.
  This must be verified during implementation.
- A-TASK-001: The FilePicker row will be placed in the page layout near
  the existing submit_row (initiative_tf and coder_tf row) to maintain
  visual grouping of submission-related controls.


# Acceptance Criteria

## AC-TASK-001: File Picker Row Exists in Layout

The console layout contains a new ft.Row control with three child
elements: a FilePicker instance, a TextField for file path display, and
a Browse button. The row is added to the page layout within the app()
closure.

## AC-TASK-002: Flet Controls Only

All controls in the new row use Flet (ft) component classes exclusively.
No custom widgets, HTML elements, or third-party UI libraries are used.
This verifies NFR-001 compliance for this work item.

## AC-TASK-003: Row Initially Hidden

The file picker row is created with visible=False (or equivalent
mechanism) so it does not appear in the console UI until visibility
logic is implemented in WI-03.

## AC-TASK-004: Existing Layout Preserved

No existing controls, event handlers, or layout structure are modified,
removed, or relocated. The new row is added as an additional element.
The existing test suite (if any) for console layout continues to pass.

## AC-TASK-005: Windows Compatibility

The FilePicker control is instantiated and the layout renders without
errors on Windows. The control uses the local filesystem only (TC-004).


# Technical Approach

## File Modifications

The primary file to modify is:
- agent_runner_v2/operator_console/app.py

Within the app() closure, the following additions are needed:

1. Import or reference ft.FilePicker (already available via the flet
   import at the top of the function scope).
2. Instantiate a FilePicker control.
3. Instantiate a TextField for file path display (read-only).
4. Instantiate a Browse button that triggers file_picker.pick_files().
5. Create an ft.Row containing these three controls.
6. Add the row to the page layout (ft.Column controls list).

## Integration Point

The existing layout in app.py uses a top-level ft.Column with spacing=16
that contains all console controls. The new file picker row should be
inserted into this column, positioned near the submit_row (which contains
initiative_tf and coder_tf) to maintain visual grouping of
submission-related controls.

## Key Design Decisions

1. The Browse button on_click handler uses an async callback (on_browse)
   that awaits file_picker.pick_files() and populates the TextField with
   the selected file path. In Flet 0.86.1, pick_files() is async and
   returns list[FilePickerFile] directly -- no separate on_result callback
   is needed. Full state management (visibility toggling, state reset)
   remains the responsibility of WI-02 and later work items.
2. The TextField will be set to read_only=True to prevent manual editing
   of the file path.
3. The row will be wrapped in a reference variable (e.g., file_picker_row)
   so that subsequent work items (WI-03, WI-04) can toggle its visibility.

## Approach Rationale

This approach follows the existing console UI pattern in app.py where
controls are instantiated as local variables within the app() closure
and composed into ft.Row and ft.Column layout elements. The file picker
row follows the same pattern as submit_row (ft.Row with wrap=True) to
maintain consistency.


# Files and Components

## Files to Modify

| File | Change Description |
|---|---|
| agent_runner_v2/operator_console/app.py | Add FilePicker, TextField, Browse button, and ft.Row to the app() closure layout |

## Files NOT to Modify (Constraints)

| File | Reason |
|---|---|
| agent_runner_v2/submit_commands.py | TC-003 constraint; no changes allowed |
| agent_runner_v2/backend_client.py | Not in scope for this work item |
| agent_runner_v2/operator_console/services/runner_service.py | WP-3 scope; not this work item |

## Components Affected

| Component | Location | Impact |
|---|---|---|
| Operator Console UI | agent_runner_v2/operator_console/app.py | New UI row added to page layout |
| Flet FilePicker | New import/usage in app.py | New Flet control instantiated |

## Test Files

No new test files are created in this work item. The existing test
infrastructure should continue to pass. End-to-end testing is deferred
to WI-08.


# Dependencies

## Internal Dependencies

This work item has no upstream dependencies. It is a foundational item
that other work items depend on.

| Dependent Work Item | Dependency Type |
|---|---|
| WI-20260723-001_console-sdlc10-support-02 | Structural (requires file picker row) |
| WI-20260723-001_console-sdlc10-support-03 | Structural (requires file picker row reference) |

## External Prerequisites

| Dependency | Description | Status |
|---|---|---|
| DC-004 | Flet FilePicker available in installed Flet version | Assumed met |
| DC-001 | Console config must include at least one repository workflow list | Assumed met |

## Parallel Opportunities

This work item can be executed in parallel with
WI-20260723-001_console-sdlc10-support-05 (submit_job Parameter) since
UI and service layers are independent.


# Risk Factors

## RF-001: Flet FilePicker Windows Compatibility

Risk: The Flet FilePicker may have platform-specific behavior or
limitations on Windows that are not documented.

Mitigation: Verify FilePicker availability and basic functionality during
implementation. The Flet version is already installed for the console
dependency group. If FilePicker is not available, investigate alternative
Flet file selection mechanisms.

## RF-002: Layout Integration Conflicts

Risk: Adding a new row to the existing page layout could cause visual
overlapping or layout issues with existing controls.

Mitigation: The existing layout uses ft.Column with spacing=16 and
ft.Row with wrap=True, which provides flexible layout behavior. The new
row will follow the same pattern. Test visually on Windows after
integration.

## RF-003: FilePicker API Differences Across Flet Versions

Risk: The FilePicker API may differ between Flet versions. The
pick_files() method signature or event handling may vary.

Mitigation: Check the installed Flet version and consult its API
documentation during implementation. Use the documented API for the
installed version.

## RF-004: Module Structure Drift

Risk: The backlog assumption A-001 states the app.py module structure
has not changed. If significant refactoring has occurred, the
integration point may differ from the plan.

Mitigation: Verified by source code inspection that the app() closure
structure is intact. The page.add() call with ft.Column controls list
is present at lines 557-605 of app.py.


# Open Questions

## OQ-001: File Type Filtering

The file picker should ideally filter for .md files only. The Flet
FilePicker dialog_type and allowed_extensions parameters should be
verified for Windows compatibility. If filtering is not supported,
the solution falls back to showing all files.

Impact: Affects the FilePicker instantiation in this work item.

## OQ-004: Relative vs Absolute Paths

The Flet FilePicker may return relative or absolute paths depending on
the platform. The solution should normalize to absolute paths before
submission. The exact behavior on Windows needs verification.

Impact: Affects how the file path is captured in WI-02 but should be
considered during the FilePicker setup in this work item.

## OQ-005: Future Extension Mechanism

Phase 1 hardcodes DRAFT_INIT_FILE. For future phases, the mechanism
for determining which artifact key to use for a given workflow needs
design. This is deferred but should be considered during component
design to ensure the file picker row structure accommodates future
needs.

Impact: May influence naming conventions and component structure in
this work item.


# Source Reference

This task specification is derived from:

- Source Backlog: BACKLOG-20260723-001_console-sdlc10-support.md (approved)
- Source Backlog Job: SDLC30BLG-20260723-6e878812
- Source Plan: PLAN-20260723-001_console-sdlc10-support.md (approved)
- Producing Workflow: sdlc_40_task_v1
- Producing Step: generate_task
- Task Job ID: SDLC40TSK-20260723-5d347d98

## Audit and Compliance Notes

- This task operates within Layer 3 boundaries.
- Layer 1 governance (METADATA_STANDARD.md) is treated as read-only.
- Layer 2 platform constitution (RUNTIME_MODEL.md, METADATA_CONTRACT.md) is treated as read-only.
- No governance or platform contract redefinition is included.
- The task metadata conforms to Layer 1 required fields and Layer 2 platform extensions.
