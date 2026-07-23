---
template_id: "SYS-03-BL"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "backlog for initiative execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC30BLG-20260723-6e878812"
managed_by: "workflow-generated"
---

# Backlog Overview

This backlog decomposes the approved plan PLAN-20260723-001_console-sdlc10-support.md
into ordered work items for execution. The plan introduces SDLC workflow
input handling to the operator console (a Flet-based desktop GUI for the
agent-runner-v2 platform). The current console supports generic job
submission but has no awareness of SDLC workflow input requirements. Users
must manually construct CLI commands with --input KEY=VALUE arguments to
submit SDLC workflows.

The solution introduces three coordinated capabilities:

1. A file picker UI component that allows users to select draft initiative
   documents from the local filesystem.
2. Conditional visibility logic that shows the file picker only when an
   SDLC workflow is selected and the action is "submit job".
3. Input artifact forwarding through the existing submit flow, passing
   the selected file path as DRAFT_INIT_FILE to the backend.

This is Phase 1 of a planned multi-phase console SDLC support plan. The
architecture is designed to be extensible to support additional input
artifact keys in future phases without structural changes.

The work is organized into four work packages derived from the plan
component breakdown:

- WP-1: File Picker UI Controls (2 work items)
- WP-2: Conditional Visibility Logic (2 work items)
- WP-3: Runner Service Input Artifact Support (2 work items)
- WP-4: Submit Action Integration (2 work items)

Total work items: 8

Total estimated effort: 10 story points (relative scale).

High-level ordering rationale: WP-1 and WP-3 are foundational and have
no inter-dependencies. They can be worked in parallel. WP-2 depends on
WP-1 (requires the file picker row to exist). WP-4 integrates all other
work packages and must be executed last.

This backlog operates within Layer 3 boundaries. It does not redefine or
contradict Layer 1 governance (METADATA_STANDARD.md) or Layer 2 platform
constitution (RUNTIME_MODEL.md, METADATA_CONTRACT.md).


# Plan Traceability

This backlog is derived from the following approved documents:

| Document | Reference | Status |
|---|---|---|
| Initiative | INIT-20260723-001_console-sdlc10-support.md | Approved |
| Requirement | REQ-20260723-001_console-sdlc10-support.md | Approved |
| Plan | PLAN-20260723-001_console-sdlc10-support.md | Approved |
| Plan Review | console-sdlc10-support-REV-20-plan.md | Passed |

## Key Plan Components Addressed

| Plan Component | Description | Backlog Coverage |
|---|---|---|
| Component 1 | File Picker UI Controls | WI-20260723-001_console-sdlc10-support-01, WI-20260723-001_console-sdlc10-support-02 |
| Component 2 | Conditional Visibility Logic | WI-20260723-001_console-sdlc10-support-03, WI-20260723-001_console-sdlc10-support-04 |
| Component 3 | Runner Service Input Artifact Support | WI-20260723-001_console-sdlc10-support-05, WI-20260723-001_console-sdlc10-support-06 |
| Component 4 | Submit Action Integration | WI-20260723-001_console-sdlc10-support-07, WI-20260723-001_console-sdlc10-support-08 |

## Work Package Mapping

| Work Package | Plan Section | Backlog Items |
|---|---|---|
| WP-1 | Component Breakdown: File Picker UI Controls | WI-20260723-001_console-sdlc10-support-01, WI-20260723-001_console-sdlc10-support-02 |
| WP-2 | Component Breakdown: Conditional Visibility Logic | WI-20260723-001_console-sdlc10-support-03, WI-20260723-001_console-sdlc10-support-04 |
| WP-3 | Component Breakdown: Runner Service Input Artifact Support | WI-20260723-001_console-sdlc10-support-05, WI-20260723-001_console-sdlc10-support-06 |
| WP-4 | Component Breakdown: Submit Action Integration | WI-20260723-001_console-sdlc10-support-07, WI-20260723-001_console-sdlc10-support-08 |

## Requirement Traceability Summary

The plan addresses 10 functional requirements (FR-001 through FR-010),
9 non-functional requirements (NFR-001 through NFR-009), and 9 acceptance
criteria (AC-001 through AC-009). All work items in this backlog are
derived from the plan and trace back to these requirements. No scope
beyond the approved plan is included.


# Work Items

## WI-20260723-001_console-sdlc10-support-01: Implement File Picker Row Layout

Parent Work Package: WP-1

Description: Create a new row of Flet controls in operator_console/app.py
consisting of a FilePicker component, a TextField for file path display,
and a Browse button. The row must be integrated into the existing console
layout without restructuring existing controls. This is the foundational
UI component upon which visibility and submission logic depend.

Affected codebase areas:
- operator_console/app.py (within the app() closure, layout section)
- Flet FilePicker import and initialization

Constraints:
- Must use Flet controls only (TC-001, NFR-001).
- Must operate on the local filesystem only (TC-004, NFR-009).
- Must work on Windows (TC-002, NFR-002).

Assumptions:
- The operator_console/app.py module structure has not changed since the
  plan was authored.
- The Flet version installed supports FilePicker on Windows (DC-004).

Priority: high
Estimated effort: 2 story points


## WI-20260723-001_console-sdlc10-support-02: Implement File Selection Callback and State Management

Parent Work Package: WP-1

Description: Implement the FilePicker on_result callback to populate
the TextField with the selected file path. Maintain the selected file
path as state accessible to the submit action handler. The component
must expose an internal artifact_key property (hardcoded to
DRAFT_INIT_FILE for Phase 1) to support future extensibility (NFR-006).

Affected codebase areas:
- operator_console/app.py (FilePicker on_result handler, state variables)

Constraints:
- Must handle Windows path formats including backslashes and spaces
  (RA-005).
- Must normalize to absolute paths where possible (OQ-004).
- Must use Flet controls only (TC-001).

Assumptions:
- The Flet FilePicker returns filesystem paths as strings.
- The selected path can be stored in a module-level variable or closure
  state accessible to the execute_action() function.

Priority: high
Estimated effort: 1 story point


## WI-20260723-001_console-sdlc10-support-03: Extend update_visibility for SDLC Workflow Detection

Parent Work Package: WP-2

Description: Extend the existing update_visibility() function in
operator_console/app.py to evaluate whether the file picker row should
be visible. The condition requires both: (a) the selected workflow name
starts with "sdlc_", and (b) the selected action is "submit job". When
both conditions are true, set the file picker row visible attribute to
true and call page.update(). When either condition is not met, hide the
row.

Affected codebase areas:
- operator_console/app.py (update_visibility function)

Constraints:
- Must integrate with the existing update_visibility() flow without
  introducing a separate visibility system (plan architectural decision).
- Must respond to both workflow dropdown changes and action dropdown
  changes.

Assumptions:
- The existing on_workflow_changed() and on_repo_changed() handlers
  already trigger update_visibility() (plan Integration Point 2).

Priority: high
Estimated effort: 1 story point


## WI-20260723-001_console-sdlc10-support-04: Implement File Picker State Reset on Hide

Parent Work Package: WP-2

Description: When the file picker row is hidden (due to non-SDLC
workflow selection or non-submit action change), clear the selected
file path state and reset the TextField to empty. This prevents stale
data from being submitted on subsequent actions.

Affected codebase areas:
- operator_console/app.py (update_visibility function, state reset logic)

Constraints:
- Must reset state atomically with the visibility change.
- Must not trigger spurious submission events.

Assumptions:
- The file picker row visibility and state reset are handled within the
  same update_visibility() call to avoid race conditions.

Priority: medium
Estimated effort: 1 story point


## WI-20260723-001_console-sdlc10-support-05: Add input_artifacts Parameter to submit_job Method

Parent Work Package: WP-3

Description: Extend the RunnerActionService.submit_job() method in
operator_console/services/runner_service.py to accept an optional
input_artifacts parameter (dict of key-value pairs). When input_artifacts
is provided and non-empty, append --input KEY=VALUE arguments to the CLI
argument list before invoking submit_commands.main(). When not provided
or empty, the behavior must be identical to the current implementation
to preserve generic submission (FR-009, AC-008).

Affected codebase areas:
- operator_console/services/runner_service.py (RunnerActionService.submit_job)

Constraints:
- The parameter must be optional with a default of None or empty dict.
- Must not break existing callers that do not pass input_artifacts
  (FR-009, RA-002).
- Must not modify submit_commands.py (TC-003).

Assumptions:
- The _invoke() method uses direct function invocation (func(argv))
  rather than shell execution, so shell quoting issues do not apply
  (plan RA-005 mitigation).

Priority: high
Estimated effort: 1 story point


## WI-20260723-001_console-sdlc10-support-06: Verify CLI Argument Construction for Input Artifacts

Parent Work Package: WP-3

Description: Verify and test that the --input KEY=VALUE arguments
constructed by submit_job() are correctly parsed by the existing
argparse configuration in submit_commands.main(). Confirm that the
_parse_kv() function correctly builds the input_payload dict and that
BackendClient.submit_run() receives it without modification. No changes
to submit_commands.py or backend_client.py are expected.

Affected codebase areas:
- operator_console/services/runner_service.py (argument construction)
- Verification against agent_runner_v2/commands/submit_commands.py
- Verification against agent_runner_v2/client/backend_client.py

Constraints:
- Must not modify submit_commands.py (TC-003).
- Must not modify backend_client.py.
- The _invoke() method uses direct function invocation (func(argv)),
  so shell quoting issues do not apply (RA-005).

Assumptions:
- The existing argparse --input handler in submit_commands.py accepts
  multiple --input arguments.
- The _parse_kv() function correctly handles single key-value pairs.

Priority: medium
Estimated effort: 1 story point


## WI-20260723-001_console-sdlc10-support-07: Wire File Picker State to Submit Action Handler

Parent Work Package: WP-4

Description: In the execute_action() function of operator_console/app.py,
when the "submit job" action is triggered and an SDLC workflow is selected
with a file picked, construct the input_artifacts dictionary with the
DRAFT_INIT_FILE key and the selected file path as the value. Pass
input_artifacts to runner_service.submit_job(). When the workflow is
non-SDLC or no file is selected, call submit_job() without
input_artifacts (preserving generic submission behavior per FR-009).

Affected codebase areas:
- operator_console/app.py (execute_action function)

Constraints:
- Must validate that the file path is non-empty before including it
  in input_artifacts.
- Must handle the case where the file picker is visible but no file
  has been selected (show error or warning per OQ-003).

Assumptions:
- The execute_action() function has access to the file path state
  maintained by WI-20260723-001_console-sdlc10-support-02.
- The runner_service instance is accessible from within execute_action().

Priority: high
Estimated effort: 2 story points


## WI-20260723-001_console-sdlc10-support-08: End-to-End Regression Testing

Parent Work Package: WP-4

Description: Perform end-to-end regression testing to verify:
(a) SDLC workflow submission with DRAFT_INIT_FILE input artifact works
correctly through the full data flow (console to daemon), (b) generic
non-SDLC workflow submission continues to work without regression
(AC-008), (c) the file picker visibility toggles correctly on workflow
and action changes (AC-002, AC-003, AC-004), and (d) the console
launches without errors when SDLC workflows are present in config
(AC-001).

Affected codebase areas:
- tests/ (new or extended test files for console SDLC submission)
- operator_console/app.py (integration verification)
- operator_console/services/runner_service.py (integration verification)

Constraints:
- Tests must cover both SDLC and non-SDLC submission paths.
- Tests must run on Windows (TC-002).

Assumptions:
- The test infrastructure supports Flet component testing or mocking.
- The sdlc_10_requirement_v1 workflow is available on the backend for
  end-to-end validation (DC-003).

Audit and compliance sensitivity: This work item validates that no
regression is introduced to existing submission flows. Test results
serve as evidence for AC-008 compliance.

Priority: high
Estimated effort: 1 story point


# Prioritization

The following priority ordering is derived from the plan dependency
structure and risk assessment.

## Priority Levels

| Priority | Work Items | Rationale |
|---|---|---|
| high | WI-20260723-001_console-sdlc10-support-01, WI-20260723-001_console-sdlc10-support-02, WI-20260723-001_console-sdlc10-support-03, WI-20260723-001_console-sdlc10-support-05, WI-20260723-001_console-sdlc10-support-07, WI-20260723-001_console-sdlc10-support-08 | Foundational or integration-critical items |
| medium | WI-20260723-001_console-sdlc10-support-04, WI-20260723-001_console-sdlc10-support-06 | State management and verification items |

## Execution Order

1. WI-20260723-001_console-sdlc10-support-01 (File Picker Row Layout) and
   WI-20260723-001_console-sdlc10-support-05 (submit_job Parameter) can
   begin in parallel. These are foundational with no dependencies.
2. WI-20260723-001_console-sdlc10-support-02 (File Selection Callback)
   follows WI-20260723-001_console-sdlc10-support-01.
3. WI-20260723-001_console-sdlc10-support-03 (Visibility Extension)
   follows WI-20260723-001_console-sdlc10-support-01.
4. WI-20260723-001_console-sdlc10-support-04 (State Reset) follows
   WI-20260723-001_console-sdlc10-support-03.
5. WI-20260723-001_console-sdlc10-support-06 (CLI Argument Verification)
   follows WI-20260723-001_console-sdlc10-support-05.
6. WI-20260723-001_console-sdlc10-support-07 (Submit Action Wiring)
   requires WI-20260723-001_console-sdlc10-support-02,
   WI-20260723-001_console-sdlc10-support-03,
   WI-20260723-001_console-sdlc10-support-05.
7. WI-20260723-001_console-sdlc10-support-08 (Regression Testing)
   requires WI-20260723-001_console-sdlc10-support-07 and should be the
   final item executed.

## Critical Path

The critical path runs through:
WI-20260723-001_console-sdlc10-support-01 ->
WI-20260723-001_console-sdlc10-support-02 ->
WI-20260723-001_console-sdlc10-support-03 ->
WI-20260723-001_console-sdlc10-support-07 ->
WI-20260723-001_console-sdlc10-support-08.

WP-3 items (WI-20260723-001_console-sdlc10-support-05,
WI-20260723-001_console-sdlc10-support-06) are on a parallel track that
merges at WI-20260723-001_console-sdlc10-support-07.


# Dependencies

## Inter-Item Dependencies

| Work Item | Depends On | Dependency Type |
|---|---|---|
| WI-20260723-001_console-sdlc10-support-01 | None | Foundational |
| WI-20260723-001_console-sdlc10-support-02 | WI-20260723-001_console-sdlc10-support-01 | Structural (requires file picker row) |
| WI-20260723-001_console-sdlc10-support-03 | WI-20260723-001_console-sdlc10-support-01 | Structural (requires file picker row reference) |
| WI-20260723-001_console-sdlc10-support-04 | WI-20260723-001_console-sdlc10-support-03 | Logical (extends visibility hide behavior) |
| WI-20260723-001_console-sdlc10-support-05 | None | Independent (service layer change) |
| WI-20260723-001_console-sdlc10-support-06 | WI-20260723-001_console-sdlc10-support-05 | Verification (requires parameter implementation) |
| WI-20260723-001_console-sdlc10-support-07 | WI-20260723-001_console-sdlc10-support-02, WI-20260723-001_console-sdlc10-support-03, WI-20260723-001_console-sdlc10-support-05 | Integration (wires UI to service) |
| WI-20260723-001_console-sdlc10-support-08 | WI-20260723-001_console-sdlc10-support-07 | End-to-end (requires full integration) |

## Parallel Opportunities

- WI-20260723-001_console-sdlc10-support-01 and
  WI-20260723-001_console-sdlc10-support-05 can be worked in parallel
  (UI and service layers are independent).
- WI-20260723-001_console-sdlc10-support-03 and
  WI-20260723-001_console-sdlc10-support-06 can be worked in parallel
  once their respective predecessors complete.

## External Prerequisites

| Dependency | Description | Status |
|---|---|---|
| DC-001 | Console config must include sdlc_10_requirement_v1 in at least one repository workflow list | Assumed met |
| DC-002 | Draft initiative documents exist on local filesystem for user selection | Assumed met |
| DC-003 | sdlc_10_requirement_v1 workflow synced to backend and operational | Assumed met |
| DC-004 | Flet FilePicker available in installed Flet version | Assumed met |
| DC-005 | runner_service module accessible and modifiable within console codebase | Assumed met |


# Acceptance Criteria

High-level acceptance criteria for each work item, mapped from the
plan acceptance criteria and requirements.

## WI-20260723-001_console-sdlc10-support-01: File Picker Row Layout

- The console layout contains a new row with FilePicker, TextField,
  and Browse button (verifies AC-002 partial).
- The row uses Flet controls exclusively (verifies NFR-001).
- The row is initially hidden (no visibility logic in this item).

## WI-20260723-001_console-sdlc10-support-02: File Selection Callback and State

- Clicking Browse opens a file dialog.
- Selecting a file populates the TextField with the full file path
  (verifies AC-005).
- The selected path is accessible to the submit handler.
- The component exposes an artifact_key property set to DRAFT_INIT_FILE
  (verifies AC-009).

## WI-20260723-001_console-sdlc10-support-03: Visibility Extension

- File picker row appears when SDLC workflow + submit job are selected
  (verifies AC-002).
- File picker row is hidden when non-SDLC workflow is selected
  (verifies AC-003).
- File picker row is hidden when non-submit action is selected
  (verifies AC-004).
- Console launches without errors with SDLC workflows in config
  (verifies AC-001).

## WI-20260723-001_console-sdlc10-support-04: State Reset on Hide

- When the file picker row is hidden, the TextField is cleared and the
  internal path state is reset.
- No stale file path persists across visibility transitions.

## WI-20260723-001_console-sdlc10-support-05: input_artifacts Parameter

- submit_job() accepts an optional input_artifacts parameter.
- When provided, --input KEY=VALUE arguments are appended to the CLI
  argument list.
- When not provided, behavior is identical to the previous implementation
  (verifies AC-008 partial).

## WI-20260723-001_console-sdlc10-support-06: CLI Argument Verification

- The --input arguments constructed by submit_job() are correctly parsed
  by submit_commands.main() argparse.
- The input_payload dict is correctly built by _parse_kv().
- BackendClient.submit_run() receives input_payload without modification.

## WI-20260723-001_console-sdlc10-support-07: Submit Action Wiring

- Selecting an SDLC workflow, picking a file, and clicking Run Action
  submits a job with DRAFT_INIT_FILE in input_artifacts (verifies AC-006).
- Selecting a non-SDLC workflow and clicking Run Action submits without
  input_artifacts (verifies AC-008).
- If the file picker is visible but no file is selected, an error or
  warning is displayed (addresses OQ-003).

## WI-20260723-001_console-sdlc10-support-08: Regression Testing

- All acceptance criteria AC-001 through AC-009 pass.
- Generic submission (non-SDLC) works without regression (verifies AC-008).
- SDLC submission with input artifact completes end-to-end (verifies AC-007).
- Tests run on Windows (verifies NFR-002).


# Effort Estimates

## Relative Effort by Work Item

| Work Item | Effort (story points) | Confidence |
|---|---|---|
| WI-20260723-001_console-sdlc10-support-01 | 2 | High (well-defined UI layout) |
| WI-20260723-001_console-sdlc10-support-02 | 1 | High (standard Flet callback) |
| WI-20260723-001_console-sdlc10-support-03 | 1 | Medium (visibility logic extension) |
| WI-20260723-001_console-sdlc10-support-04 | 1 | High (simple state reset) |
| WI-20260723-001_console-sdlc10-support-05 | 1 | High (optional parameter addition) |
| WI-20260723-001_console-sdlc10-support-06 | 1 | Medium (verification, may uncover issues) |
| WI-20260723-001_console-sdlc10-support-07 | 2 | Medium (integration wiring) |
| WI-20260723-001_console-sdlc10-support-08 | 1 | Medium (test coverage) |

## Effort by Work Package

| Work Package | Total Effort | Items |
|---|---|---|
| WP-1 | 3 story points | WI-20260723-001_console-sdlc10-support-01, WI-20260723-001_console-sdlc10-support-02 |
| WP-2 | 2 story points | WI-20260723-001_console-sdlc10-support-03, WI-20260723-001_console-sdlc10-support-04 |
| WP-3 | 2 story points | WI-20260723-001_console-sdlc10-support-05, WI-20260723-001_console-sdlc10-support-06 |
| WP-4 | 3 story points | WI-20260723-001_console-sdlc10-support-07, WI-20260723-001_console-sdlc10-support-08 |
| Total | 10 story points | 8 items |

## Confidence Notes

- Overall confidence is medium-high. The plan is well-scoped and the
  codebase areas are well-understood from the codebase inventory.
- The primary uncertainty is in
  WI-20260723-001_console-sdlc10-support-06 (CLI argument verification)
  where runtime behavior of the existing argparse pipeline needs
  confirmation.
- WI-20260723-001_console-sdlc10-support-07 effort could increase if
  error handling for missing files (OQ-003) requires more complex UI
  state management than anticipated.
- Story points use a relative scale where 1 point represents a small,
  well-defined change in a single file.


# Open Questions

The following items from the plan require clarification before or during
implementation. They are carried forward from the plan document.

## OQ-001: File Type Filtering

The file picker should ideally filter for .md files only. The Flet
FilePicker dialog_type and allowed_extensions parameters should be
verified for Windows compatibility. If filtering is not supported,
the solution falls back to showing all files. This affects
WI-20260723-001_console-sdlc10-support-01.

## OQ-002: File Path Validation

Should the console validate that the selected file exists and is
readable before submission? The backend will reject invalid paths,
but client-side validation could improve user experience. The scope
of validation (existence, readability, file size) needs clarification.
This affects WI-20260723-001_console-sdlc10-support-07.

## OQ-003: Error Handling for Missing File

If the user clicks Run Action with the file picker visible but no file
selected, should the console show an error dialog or silently proceed
without the input artifact? The recommended approach is to show an
error, but confirmation is needed. This affects
WI-20260723-001_console-sdlc10-support-07.

## OQ-004: Relative vs Absolute Paths

The Flet FilePicker may return relative or absolute paths depending on
the platform. The solution should normalize to absolute paths before
submission. The exact behavior on Windows needs verification. This
affects WI-20260723-001_console-sdlc10-support-02.

## OQ-005: Future Extension Mechanism

Phase 1 hardcodes DRAFT_INIT_FILE. For future phases, the mechanism
for determining which artifact key to use for a given workflow needs
design. Options include configuration mapping, workflow metadata, or
hardcoded mapping. This is deferred but should be considered during
implementation to ensure component design accommodates future needs.
This affects WI-20260723-001_console-sdlc10-support-02.


# Source Reference

This backlog is derived from:

- Source Plan: PLAN-20260723-001_console-sdlc10-support.md (approved)
- Source Plan Job: SDLC20PLN-20260723-5c08a3d0
- Producing Workflow: sdlc_30_backlog_v1
- Producing Step: generate_backlog
- Backlog Job ID: SDLC30BLG-20260723-6e878812

## Assumptions

- A-001: The operator_console/app.py module structure has not changed
  since the plan was authored. The update_visibility() function and
  execute_action() function are present and accessible.
- A-002: The Flet version installed supports FilePicker on Windows.
- A-003: The submit_commands.main() function accepts argv as a
  parameter for direct invocation.
- A-004: No other work items or changes are in progress that modify
  the affected files.
- A-005: The sdlc_10_requirement_v1 workflow is identified by its name
  prefix "sdlc_" in the workflow dropdown.
