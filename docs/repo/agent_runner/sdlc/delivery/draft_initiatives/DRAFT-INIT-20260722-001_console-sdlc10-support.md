---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "Draft initiative for console app SDLC Phase 1 support"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Operator Console SDLC Phase 1 - Initiative Intake Support

## Objective

Add SDLC workflow support to the operator console for sdlc_10_requirement_v1
(Initiative Intake). The console must allow users to select a draft initiative
document, submit it as a job to the backend, and have the daemon process it
through the sdlc_10 workflow.

## Problem Statement

### Current State

The operator console (Flet desktop GUI) currently supports generic job
submission via the "submit job" action, but has no awareness of SDLC workflow
input requirements. Users must manually construct CLI commands or batch files
to submit SDLC workflows with the correct input artifacts.

### Pain Points

- No file picker in the console for selecting draft initiative documents.
- Users must know the exact artifact key names (DRAFT_INIT_DOC) and construct
  --input KEY=VALUE arguments manually.
- No visual feedback on which workflows require which inputs.
- The console workflow dropdown lists all workflows but does not adapt its UI
  to workflow-specific requirements.

### Why This Initiative Is Needed

The operator console is the primary user interface for managing workflow runs.
Without SDLC-specific input handling, users cannot efficiently submit SDLC
workflow jobs through the console. This blocks the test-driving of the SDLC
workflow chain on real internal tool development.

### Impact of Not Undertaking This Initiative

- SDLC workflows remain unusable from the console UI.
- Users must fall back to batch files or CLI for SDLC job submission.
- The SDLC workflow chain cannot be validated end-to-end through the console.

## Expected Outcomes

- Users can select sdlc_10_requirement_v1 from the workflow dropdown and see
  a file picker for the draft initiative document.
- Users can browse and select a DRAFT_INIT file from the filesystem.
- Clicking "Run Action" with "submit job" selected submits the job to the
  backend with the correct DRAFT_INIT_DOC input artifact path.
- The daemon picks up the job and processes it through the sdlc_10 workflow.
- The file picker is only visible when an SDLC workflow is selected and the
  action is "submit job".

## Scope

### In Scope

- File picker UI component (Flet FilePicker + TextField + Browse button).
- Conditional visibility: show file picker only when action is "submit job"
  AND selected workflow name starts with "sdlc_".
- Pass selected file path as --input DRAFT_INIT_DOC=<path> to submit command.
- Update runner_service.submit_job() to accept and forward input artifacts.

### Out of Scope

- Support for sdlc_20 through sdlc_80 workflows (separate phases).
- Artifact dropdown for selecting approved outputs from previous runs.
- Output display for generated artifacts after job completion.
- Workflow-specific input validation or schema enforcement.

## Constraints

- Must use Flet UI framework (existing console dependency).
- Must integrate with existing submit_commands.main() flow.
- File picker must work on Windows (primary development platform).
- No changes to backend API or daemon behavior required.

## Dependencies

- operator-console.example.json must have at least one repo configured with
  sdlc_10_requirement_v1 in its workflow list.
- Draft initiative documents must exist in the
  docs/repo/agent_runner/sdlc/delivery/draft_initiatives/ directory.
- The sdlc_10_requirement_v1 workflow must be synced to the backend.

## Success Criteria

- Console launches without errors with SDLC workflows in the config.
- Selecting sdlc_10_requirement_v1 shows the file picker row.
- Selecting a non-SDLC workflow hides the file picker row.
- Browsing and selecting a .md file populates the path text field.
- Clicking "Run Action" with "submit job" submits successfully and the
  backend receives the DRAFT_INIT_DOC input artifact path.
- The daemon processes the submitted job through sdlc_10 workflow steps.

## Notes

This is Phase 1 of the console SDLC support plan. The plan document at
masterplan/SDLC_CONSOLE_APP_PLAN.md lists all 8 phases. Each phase will be
implemented as a separate SDLC workflow cycle, using the SDLC process itself
to develop the console app features.

The file picker implementation should be generic enough to support different
input artifact keys in future phases (e.g., INIT_DOC for sdlc_20, REQ_DOC
for sdlc_30). The Phase 1 implementation hardcodes DRAFT_INIT_DOC but the
architecture should allow easy extension.
