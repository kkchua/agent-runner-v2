---
template_id: "SYS-03-IN"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved initiative document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC00INIT-20260723-8831adbd"
source_document: "DRAFT-INIT-20260722-001_console-sdlc10-support.md"
---

# Operator Console SDLC Phase 1 - Initiative Intake Support

## Objective

Add SDLC workflow input handling to the operator console (Flet desktop GUI) for
the initiative intake workflow (sdlc_00_init_doc_v1). The console must allow
users to select a draft initiative document through a file picker, submit it as
a job to the backend with the correct DRAFT_INIT_FILE input artifact, and have
the daemon process it through the sdlc_00_init_doc_v1 workflow to produce an
approved INIT_FILE.

## Problem Statement

### Current State

The operator console (Flet desktop GUI) supports generic job submission via the
"submit job" action but has no awareness of SDLC workflow input requirements.
Users must manually construct CLI commands or batch files to submit SDLC
workflows with the correct input artifacts.

### Pain Points

- No file picker connection in the console for selecting draft initiative
  documents. A file picker UI component exists in the console codebase but is
  not wired to the submit_job action.
- Users must know the exact artifact key name (DRAFT_INIT_FILE) and construct
  --input KEY=VALUE arguments manually via the CLI.
- No visual feedback on which workflows require which inputs.
- The console workflow dropdown lists all workflows but does not adapt its UI to
  workflow-specific input requirements.
- The runner_service.submit_job() method does not accept or forward input
  artifact arguments to the submit command.

### Why This Initiative Is Needed

The operator console is the primary user interface for managing workflow runs.
Without SDLC-specific input handling, users cannot efficiently submit SDLC
workflow jobs through the console. This blocks test-driving the SDLC workflow
chain on real internal tool development.

### Impact of Not Undertaking This Initiative

- SDLC workflows remain unusable from the console UI.
- Users must fall back to batch files or CLI for SDLC job submission.
- The SDLC workflow chain cannot be validated end-to-end through the console.
- The first step of the console SDLC support plan (eight phases total) cannot
  be completed, blocking all subsequent phases.

## Expected Outcomes

1. (Highest priority) Users can select sdlc_00_init_doc_v1 from the workflow
   dropdown and see a file picker row for selecting a draft initiative document.
2. Users can browse and select a DRAFT_INIT_FILE (Markdown format) from the
   local filesystem through the file picker.
3. Clicking "Run Action" with "submit job" selected submits the job to the
   backend with the correct --input DRAFT_INIT_FILE=<path> argument.
4. The daemon picks up the job and processes it through the sdlc_00_init_doc_v1
   workflow, producing an approved INIT_FILE.
5. The file picker row is visible only when the selected workflow name starts
   with "sdlc_" AND the action is "submit job".

## Scope

### In Scope

- File picker UI component: Flet FilePicker plus read-only TextField plus
  Browse button. The component already exists in the console codebase and needs
  to be connected to the submit action.
- Conditional visibility: show file picker row only when action is "submit job"
  AND selected workflow name starts with "sdlc_".
- Pass selected file path as --input DRAFT_INIT_FILE=<path> to the submit
  command.
- Update runner_service.submit_job() to accept an input_artifacts parameter and
  forward it as --input KEY=VALUE arguments to submit_commands.main().
- Wire the existing file picker in operator_console/app.py to the submit job
  action flow.

### Out of Scope

- Support for sdlc_10 through sdlc_80 workflows (separate phases per the
  masterplan SDLC_CONSOLE_APP_PLAN.md).
- Artifact dropdown for selecting approved outputs from previous runs.
- Output display for generated artifacts after job completion.
- Workflow-specific input validation or schema enforcement.
- Changes to backend API, daemon behavior, or workflow definitions.

### Boundary Conditions

- Phase 1 targets sdlc_00_init_doc_v1 exclusively. This workflow takes
  DRAFT_INIT_FILE as input and produces INIT_FILE. Other SDLC workflows
  (sdlc_10 through sdlc_80) require different input artifact keys and will be
  handled in subsequent phases.
- The file picker component must be architecturally extensible to support
  different input artifact keys in future phases (for example, INIT_FILE for
  sdlc_10, REQ_FILE for sdlc_20) but hardcodes DRAFT_INIT_FILE for this phase.
- The console must continue to function correctly for non-SDLC workflows
  (generic job submission without file picker input).
- No changes to the backend, daemon, or workflow definition layer are required.
  All changes are confined to the console UI and its service layer.

## Constraints

- Must use Flet UI framework (existing console dependency).
- Must integrate with the existing submit_commands.main() flow without changing
  the submit command interface.
- File picker must work on Windows (primary development platform).
- No changes to backend API or daemon behavior are required or permitted.
- The console architecture must remain extensible for future SDLC workflow
  phases without requiring structural refactoring.
- All changes must be confined to the operator_console package and its services.

## Dependencies

- operator-console.example.json (or the active operator-console.json) must have
  at least one repository configured with sdlc_00_init_doc_v1 in its workflow
  list.
- Draft initiative documents must exist in the
  docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory.
- The sdlc_00_init_doc_v1 workflow must be synced to the backend and available
  in the workflow dropdown.
- The submit_commands.main() function must continue to support the --input
  KEY=VALUE argument format.

## Success Criteria

- Console launches without errors with SDLC workflows in the configuration.
- Selecting sdlc_00_init_doc_v1 from the workflow dropdown shows the file
  picker row.
- Selecting a non-SDLC workflow hides the file picker row.
- Browsing and selecting a .md file populates the path text field correctly.
- Clicking "Run Action" with "submit job" submits the job successfully and the
  backend receives the DRAFT_INIT_FILE input artifact path via --input
  DRAFT_INIT_FILE=<path>.
- The daemon processes the submitted job through the sdlc_00_init_doc_v1
  workflow and produces an approved INIT_FILE artifact.
- Non-SDLC workflow job submission continues to work without regression (no
  file picker artifacts are passed).

## Stakeholders

- Sponsor: Platform owner (agent-runner-v2).
- Primary users: SDLC workflow operators who submit workflow jobs through the
  console GUI.
- Review authorities: Platform reviewer (for code review of console changes).
- Affected teams: Console development (operator_console package), SDLC workflow
  development.

## Notes

- This is Phase 1 of the console SDLC support plan. The plan document at
  SDLC_CONSOLE_APP_PLAN.md lists all eight phases. Each phase will be
  implemented as a separate SDLC workflow cycle, using the SDLC process itself
  to develop the console app features.
- The draft initiative referenced sdlc_10_requirement_v1 as the target workflow
  for Phase 1. This initiative corrects the workflow reference to
  sdlc_00_init_doc_v1 based on the actual workflow definitions:
  sdlc_00_init_doc_v1 takes DRAFT_INIT_FILE as input and produces INIT_FILE,
  while sdlc_10_requirement_v1 takes INIT_FILE as input and produces REQ_FILE.
  The described functionality (selecting a draft initiative document and
  submitting with DRAFT_INIT_FILE) aligns with sdlc_00_init_doc_v1.
- The draft initiative used the artifact key name DRAFT_INIT_DOC. This
  initiative uses the canonical key name DRAFT_INIT_FILE as defined in
  artifact_keys.py and constants.py.
- The file picker UI component already exists in operator_console/app.py
  (Flet FilePicker, TextField, and Browse button) but is not connected to the
  submit_job action. The primary implementation work is wiring this existing
  component to the submit flow and extending runner_service.submit_job() to
  accept and forward input_artifacts.
- The masterplan SDLC_CONSOLE_APP_PLAN.md also references sdlc_10 for Phase 1
  but lists the correct input/output mapping (DRAFT_INIT_FILE -> INIT_FILE).
  The workflow name in the masterplan should be corrected to sdlc_00_init_doc_v1
  in a subsequent update.
- There are eight SDLC workflows in the chain: sdlc_00 through sdlc_80. This
  Phase 1 initiative addresses only the first workflow (sdlc_00_init_doc_v1).
  Future phases will extend the console to support the remaining workflows with
  appropriate input artifact selection.
