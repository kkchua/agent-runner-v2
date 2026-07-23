---
template_id: "SYS-03-IM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "implementation plan for task execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC50IMP-20260723-0d2cb761"
managed_by: "workflow-generated"
---


# Implementation Overview

This document provides the structured implementation plan for work item
WI-20260723-001_console-sdlc10-support-01, which introduces a file picker
row layout into the operator console application. The implementation adds
a new ft.Row containing a FilePicker, a read-only TextField for file path
display, and a Browse button to the existing page layout in
agent_runner_v2/operator_console/app.py. The row is initially hidden and
follows the same layout pattern as the existing submit_row. No callbacks,
visibility logic, or state management are implemented in this work item;
those are deferred to subsequent work items WI-02 and WI-03.


# Task Traceability

## Source Task

| Field | Value |
|---|---|
| Task Document | WI-20260723-001_console-sdlc10-support-01.md |
| Task Job ID | SDLC40TSK-20260723-5d347d98 |
| Task Status | Approved |
| Work Item ID | WI-20260723-001_console-sdlc10-support-01 |
| Work Package | WP-1 (File Picker UI Controls) |

## Acceptance Criteria

| AC | Description | Verification Method |
|---|---|---|
| AC-TASK-001 | File picker row exists in layout with FilePicker, TextField, and Browse button | Source code inspection of app.py; verify ft.Row with child controls in page.add() controls list |
| AC-TASK-002 | All controls use Flet (ft) component classes exclusively | Source code inspection; no custom widgets or third-party libraries in the new row |
| AC-TASK-003 | Row initially hidden (visible=False) | Source code inspection; verify visible=False on the file_picker_row |
| AC-TASK-004 | Existing layout preserved; no existing controls modified or removed | Diff review of app.py; existing test suite continues to pass |
| AC-TASK-005 | FilePicker instantiates without errors on Windows | Manual verification or import check; local filesystem only |

## Upstream Traceability Chain

| Document | Reference | Status |
|---|---|---|
| Initiative | INIT-20260723-001_console-sdlc10-support.md | Approved |
| Requirement | REQ-20260723-001_console-sdlc10-support.md | Approved |
| Plan | PLAN-20260723-001_console-sdlc10-support.md | Approved |
| Backlog | BACKLOG-20260723-001_console-sdlc10-support.md | Approved |


# Implementation Strategy

## Overall Approach

The implementation follows the existing control instantiation pattern in
app.py. Controls are created as local variables within the app() closure,
composed into ft.Row layout elements, and added to the top-level ft.Column
via page.add(). The file picker row will follow the same pattern as
submit_row (ft.Row with wrap=True) to maintain visual and structural
consistency.

The change is additive only. No existing controls, event handlers, or
layout structure will be modified, removed, or relocated. The new row
will be inserted into the page layout column near the submit_row to
maintain visual grouping of submission-related controls.

## Design Principles

1. Additive only: The change adds new controls without touching existing ones.
2. Pattern consistency: The new row follows the same ft.Row pattern as submit_row and init_row.
3. Reference variable: The row is assigned to a named variable (file_picker_row) so subsequent work items can toggle visibility.
4. Async callback pattern: In Flet 0.86.1, FilePicker.pick_files() is async and returns list[FilePickerFile]. The Browse button on_click uses an async callback (on_browse) that awaits pick_files() and populates the TextField with the selected file path.
5. Read-only display: The TextField is set to read_only=True to prevent manual path editing.


# Step-by-Step Plan

## Step 1: Verify Flet FilePicker Availability

Verify that the installed Flet version supports ft.FilePicker on Windows.
Check the Flet version in the project dependencies and confirm that
ft.FilePicker is importable.

- Action: Check flet version via .venv/Scripts/python -c "import flet; print(flet.__version__)"
- Expected: FilePicker class is available in the ft module.
- Risk: If FilePicker is not available, the implementation must be adjusted or deferred.

## Step 2: Instantiate FilePicker Control in app() Closure

Within the app() function in agent_runner_v2/operator_console/app.py,
create a new ft.FilePicker instance. This instance should be created
as a local variable alongside other control instantiations (near
initiative_tf and coder_tf, around lines 162-163).

- Variable name: file_picker
- Type: ft.FilePicker
- Additional setup: Add to page.services so it functions correctly (FilePicker is a Service in Flet 0.86.1, not a regular Control).
- In Flet 0.86.1, pick_files() is async and returns list[FilePickerFile]. No separate on_result callback is needed.

## Step 3: Instantiate TextField for File Path Display

Create a new ft.TextField instance to display the selected file path.

- Variable name: file_path_tf
- Type: ft.TextField
- Properties: label="Input File", read_only=True, expand=True
- The read_only=True property prevents manual editing of the path.
- The expand=True property allows the TextField to fill available space in the row.

## Step 4: Instantiate Browse Button

Create a new ft.ElevatedButton that triggers the FilePicker dialog.

- Variable name: browse_btn
- Type: ft.ElevatedButton
- Properties: text="Browse"
- The on_click handler uses an async callback (on_browse) that awaits file_picker.pick_files() and populates file_path_tf with the selected file path. In Flet 0.86.1, pick_files() is async and returns list[FilePickerFile] directly -- no separate on_result callback is needed.

## Step 5: Create File Picker Row

Create an ft.Row containing the visible controls.

- Variable name: file_picker_row
- Type: ft.Row
- Controls: [file_path_tf, browse_btn]
- Properties: wrap=True (matching submit_row and init_row pattern)
- Visibility: visible=False (per AC-TASK-003)
- Note: The FilePicker is added to page.services, not to the row. The row contains only the visible UI controls (TextField and Browse button).

## Step 6: Integrate Row into Page Layout

Add the file_picker_row to the top-level ft.Column controls list in the
page.add() call. Insert the new row near submit_row (line 599) to maintain
visual grouping of submission-related controls.

- Placement: After submit_row in the controls list.
- Also add file_picker to page.services before page.add().
- Verify no existing controls are reordered or removed.

## Step 7: Verify Implementation

Run the existing test suite to confirm no regressions. Verify that:
- The file_picker_row variable is present in app.py.
- The row contains the TextField and Browse button.
- The row is set to visible=False.
- The file_picker is in page.services.
- No existing controls have been modified.

## Step 8: Document Changes

Record the changes made in the codebase documentation if required by
CODEBASE_DOC_SOP.md.


# Code Changes

## Files to Modify

### agent_runner_v2/operator_console/app.py

This is the only file that requires modification. All changes are within
the app() closure.

#### Change 1: Instantiate new controls

Location: Near lines 162-163 where initiative_tf and coder_tf are
instantiated. Add the following control instantiations:

- file_picker = ft.FilePicker()
- file_path_tf = ft.TextField(label="Input File", read_only=True, expand=True)
- async def on_browse(e): files = await file_picker.pick_files(file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["md"]); if files: file_path_tf.value = files[0].path or ""; page.update()
- browse_btn = ft.ElevatedButton("Browse", on_click=on_browse)

#### Change 2: Add file_picker to page.services

Location: Before page.add(), add the file_picker to page.services:

- page.services.append(file_picker)

#### Change 3: Create file_picker_row

Location: Near line 536 where submit_row and init_row are created.

- file_picker_row = ft.Row([file_path_tf, browse_btn], wrap=True, visible=False)

#### Change 4: Add file_picker_row to page layout

Location: Inside the page.add(ft.Column(controls=[...])) call at
lines 557-605. Add file_picker_row to the controls list, positioned
after submit_row (line 599).

## Files NOT to Modify

| File | Reason |
|---|---|
| agent_runner_v2/submit_commands.py | TC-003 constraint; explicitly out of scope |
| agent_runner_v2/backend_client.py | Not in scope for this work item |
| agent_runner_v2/operator_console/services/runner_service.py | WP-3 scope; not this work item |
| Any test files | No new tests created in this work item; deferred to WI-08 |

## Control Naming Convention

| Control | Variable Name | Type | Purpose |
|---|---|---|---|
| File picker dialog | file_picker | ft.FilePicker | Native file selection dialog |
| File path display | file_path_tf | ft.TextField | Shows selected file path (read-only) |
| Browse button | browse_btn | ft.ElevatedButton | Triggers file picker dialog |
| File picker row | file_picker_row | ft.Row | Container for file picker UI controls |


# Testing Strategy

## Unit Testing

No new unit tests are created in this work item. The task specification
explicitly states that no new test files are required. The existing
test infrastructure should continue to pass without modification.

## Regression Verification

After implementation, run the existing test suite:

```
.venv/Scripts/pytest tests/unit/ -x -q
```

Verify that all existing tests pass. Any failures indicate an unintended
modification to existing controls or layout structure.

## Manual Verification

1. Launch the operator console and verify it starts without errors.
2. Verify the file picker row is not visible in the UI (visible=False).
3. Verify no existing controls have been visually displaced or altered.

## Acceptance Criteria Verification

| AC | Method |
|---|---|
| AC-TASK-001 | Source code inspection: confirm ft.Row with FilePicker, TextField, Browse button in page layout |
| AC-TASK-002 | Source code inspection: confirm only ft.* classes used in the new row |
| AC-TASK-003 | Source code inspection: confirm visible=False on file_picker_row |
| AC-TASK-004 | Git diff review: confirm only additive changes to app.py; run existing tests |
| AC-TASK-005 | Import verification: confirm ft.FilePicker is available; console starts without errors on Windows |


# Rollback Plan

## Rollback Strategy

The implementation is a single-file, additive change. Rollback is
straightforward:

1. Revert the changes to agent_runner_v2/operator_console/app.py using git checkout or git revert.
2. No database, configuration, or external service changes are involved.
3. No other files are modified, so no cascading rollback is needed.

## Partial Rollback

If only partial changes cause issues, the following can be reverted independently:
- The file_picker_row can be removed from the page layout without affecting other controls.
- The file_picker can be removed from page.services.
- The control instantiations can be removed.

## Pre-Rollback Checklist

Before reverting:
1. Capture the current diff for reference.
2. Document any observations about the failure mode.
3. Revert the changes to app.py.
4. Verify existing tests pass after revert.


# Dependencies

## Internal Dependencies

This work item has no upstream dependencies. It is a foundational item
that subsequent work items depend on:

| Dependent Work Item | Dependency Type | Description |
|---|---|---|
| WI-20260723-001_console-sdlc10-support-02 | Structural | Requires file_picker_row and its controls for callback wiring |
| WI-20260723-001_console-sdlc10-support-03 | Structural | Requires file_picker_row reference for visibility toggling |
| WI-20260723-001_console-sdlc10-support-04 | Structural | Requires file_picker_row reference for state reset |

## External Prerequisites

| Dependency | Description | Status | Verification Method |
|---|---|---|---|
| DC-004 | Flet FilePicker available in installed Flet version | Assumed met | Import check during Step 1 |
| DC-001 | Console config includes at least one repository workflow list | Assumed met | Existing console configuration |

## Parallel Opportunities

This work item can be executed in parallel with
WI-20260723-001_console-sdlc10-support-05 (submit_job Parameter) since
the UI layer and service layer changes are independent.


# Open Questions

## OQ-001: File Type Filtering

The file picker should ideally filter for .md files only. The Flet
FilePicker dialog_type and allowed_extensions parameters need
verification for Windows compatibility. If filtering is not supported,
the solution falls back to showing all files.

Impact: May affect the FilePicker instantiation in Step 2. The
implementation should use allowed_extensions=["md"] if supported, but
must not break if the parameter is unavailable.

Resolution approach: Check the installed Flet version documentation
during Step 1. If allowed_extensions is supported, include it. If not,
omit it and document the limitation for future work items.

## OQ-004: Relative vs Absolute Paths

The Flet FilePicker may return relative or absolute paths depending on
the platform. The solution should normalize to absolute paths before
submission. This is primarily a WI-02 concern but should be considered
during FilePicker setup.

Impact: Does not block this work item. The file_picker and file_path_tf
controls are created without path normalization logic. WI-02 will handle
path normalization in the on_browse callback.

## OQ-005: Future Extension Mechanism

Phase 1 hardcodes DRAFT_INIT_FILE. For future phases, the mechanism for
determining which artifact key to use for a given workflow needs design.
This is deferred but should be considered during component design.

Impact: The variable naming (file_picker, file_path_tf, file_picker_row)
is generic enough to accommodate future extension. No structural changes
are needed for this work item.


# Source Reference

This implementation plan is derived from:

- Source Task: WI-20260723-001_console-sdlc10-support-01.md (approved)
- Source Task Job: SDLC40TSK-20260723-5d347d98
- Source Plan: PLAN-20260723-001_console-sdlc10-support.md (approved)
- Source Backlog: BACKLOG-20260723-001_console-sdlc10-support.md (approved)
- Producing Workflow: sdlc_50_implementation_v1
- Producing Step: generate_implementation
- Implementation Job ID: SDLC50IMP-20260723-0d2cb761

## Audit and Compliance Notes

- This implementation plan operates within Layer 3 boundaries.
- Layer 1 governance (METADATA_STANDARD.md) is treated as read-only.
- Layer 2 platform constitution (RUNTIME_MODEL.md, METADATA_CONTRACT.md) is treated as read-only.
- No governance or platform contract redefinition is included.
- The plan metadata conforms to Layer 1 required fields and Layer 2 platform extensions.
- The doc_type "workflow_output" is used per METADATA_CONTRACT.md for Layer 3 workflow-generated outputs.
