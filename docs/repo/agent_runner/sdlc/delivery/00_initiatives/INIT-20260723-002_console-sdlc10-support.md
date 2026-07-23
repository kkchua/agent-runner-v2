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
lifecycle_status: "draft"
effective_version: "{job_id}"
source_document: "DRAFT-INIT-20260722-001_console-sdlc10-support.md"
---

# Operator Console SDLC Phase 1 - Initiative Intake Support

## Objective

Add SDLC workflow input-artifact support to the operator console (Flet desktop GUI) for the sdlc_10_requirement_v1 workflow. The console must allow users to select a draft initiative document from the filesystem, submit it as a job to the backend with the correct DRAFT_INIT_FILE input artifact, and have the daemon process it through the sdlc_10 workflow. This is Phase 1 of a multi-phase console SDLC support plan.

## Problem Statement

### Current State

The operator console currently supports generic job submission via the "submit job" action but has no awareness of SDLC workflow input requirements. The console already includes a Flet FilePicker component, a browse button, and a path text field, but these elements are always visible regardless of the selected action or workflow. The runner_service.submit_job() method does not accept or forward input artifact parameters to the underlying submit command.

Users must manually construct CLI commands with --input KEY=VALUE arguments to submit SDLC workflows with the correct input artifacts, or use batch files that hardcode these arguments.

### Pain Points

- The file picker row is unconditionally visible in the console UI, providing no contextual guidance about when it is relevant.
- Users must know the exact artifact key name (DRAFT_INIT_FILE) and construct --input arguments manually.
- There is no visual feedback on which workflows require which input artifacts.
- The console workflow dropdown lists all workflows but does not adapt its interface to workflow-specific input requirements.
- The runner_service.submit_job() method does not support passing input artifact paths, so even if a user selects a file, the path cannot be forwarded to the backend.

### Why This Initiative Is Needed

The operator console is the primary user interface for managing workflow runs. Without SDLC-specific input handling, users cannot efficiently submit SDLC workflow jobs through the console. This blocks the test-driving of the SDLC workflow chain on real internal tool development.

### Impact of Not Undertaking This Initiative

- SDLC workflows remain unusable from the console UI for job submission.
- Users must fall back to batch files or CLI for SDLC job submission.
- The SDLC workflow chain cannot be validated end-to-end through the console.
- The console cannot demonstrate its role as the primary operator interface for the platform.

## Expected Outcomes

1. Users can select sdlc_10_requirement_v1 from the workflow dropdown and see a file picker for the draft initiative document, shown only when the action is "submit job" and the selected workflow name starts with "sdlc_".
2. Users can browse and select a DRAFT_INIT_FILE (.md) from the filesystem using the existing Flet FilePicker component.
3. Clicking "Run Action" with "submit job" selected submits the job to the backend with the correct --input DRAFT_INIT_FILE=<path> argument.
4. The daemon picks up the submitted job and processes it through the sdlc_10 workflow steps.
5. Selecting a non-SDLC workflow or a non-submit action hides the file picker row, keeping the UI clean.

## Scope

### In Scope

- Conditional visibility logic for the file picker row: show only when action is "submit job" AND the selected workflow name starts with "sdlc_".
- Integration of the selected file path into the job submission flow via runner_service.submit_job(), passing it as an input artifact to the underlying submit command.
- Update runner_service.submit_job() to accept and forward an input_artifacts dictionary (or equivalent parameter) that maps artifact keys to file paths.
- Pass the selected file path as --input DRAFT_INIT_FILE=<path> when the submit action is executed for an SDLC workflow.

### Out of Scope

- Support for sdlc_20 through sdlc_80 workflows (each will be a separate phase).
- Artifact dropdown for selecting approved outputs from previous runs as input to downstream workflows.
- Output display for generated artifacts after job completion.
- Workflow-specific input validation or schema enforcement (e.g., checking that the selected file has valid frontmatter).
- Changes to the backend API or daemon behavior.
- Changes to the submit_commands module (it already supports --input KEY=VALUE).

### Boundary Conditions

- This initiative covers only the console UI and its direct service layer (runner_service.py and app.py). It does not modify workflow definitions, backend client behavior, or the SDLC workflow chain itself.
- The file picker implementation must be generic enough to support different input artifact keys in future phases (e.g., INIT_FILE for sdlc_20, REQ_FILE for sdlc_30), but Phase 1 hardcodes DRAFT_INIT_FILE.
- The console must continue to function correctly for all existing non-SDLC workflows without regression.

## Constraints

- Must use the Flet UI framework, which is the existing console dependency.
- Must integrate with the existing submit_commands.main() flow, which already supports --input KEY=VALUE arguments.
- File picker must work on Windows, which is the primary development platform.
- No changes to the backend API or daemon behavior are permitted.
- No changes to the sdlc_10_requirement_v1 workflow definition are permitted.
- The console must remain compatible with the existing console configuration model (operator-console.example.json).
- The artifact key DRAFT_INIT_FILE is defined by the SDLC workflow chain and must be used exactly as specified.

## Dependencies

- The operator console configuration (operator-console.example.json or equivalent) must have at least one repository configured with sdlc_10_requirement_v1 in its workflow list.
- Draft initiative documents must exist in the docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory for end-to-end testing.
- The sdlc_10_requirement_v1 workflow must be synced to the backend for job submission to succeed.
- The Flet library version installed in the virtual environment must support the FilePicker API (pick_files method with allowed_extensions parameter). The current codebase already uses this API successfully.
- The backend service must be running and accessible at the configured backend_url for daemon-mode job submission.

## Success Criteria

1. The console launches without errors when SDLC workflows are present in the configuration.
2. Selecting sdlc_10_requirement_v1 with action "submit job" shows the file picker row.
3. Selecting a non-SDLC workflow hides the file picker row.
4. Selecting an action other than "submit job" hides the file picker row, regardless of workflow selection.
5. Browsing and selecting a .md file populates the path text field with the absolute file path.
6. Clicking "Run Action" with "submit job" submits successfully and the backend receives the DRAFT_INIT_FILE input artifact path via --input.
7. The daemon processes the submitted job through the sdlc_10 workflow steps without errors attributable to the console submission.
8. Existing non-SDLC workflow submissions continue to work without regression.

## Stakeholders

- Sponsor: Platform operator / repository owner (human-authored masterplan author).
- Primary users: Developers and operators who use the console to manage SDLC workflow runs.
- Review authorities: Platform core maintainers responsible for the operator console module (agent_runner_v2/operator_console/).
- Affected teams: SDLC workflow users who rely on the console as their primary interface; any downstream consumers of jobs submitted through the console.

## Notes

- This is Phase 1 of the console SDLC support plan. The masterplan at masterplan/SDLC_CONSOLE_APP_PLAN.md lists all 8 phases. Each phase will be implemented as a separate SDLC workflow cycle, using the SDLC process itself to develop the console app features.
- The draft initiative used DRAFT_INIT_DOC as the artifact key name. The canonical artifact key for this input is DRAFT_INIT_FILE, as defined by the SDLC workflow chain and the Layer 2 platform artifact conventions. This document uses DRAFT_INIT_FILE consistently.
- The console already contains a FilePicker component, browse button, and path text field (defined in app.py). These components exist but are not wired into the submission flow and lack conditional visibility logic. This initiative builds on the existing components rather than replacing them.
- The runner_service.submit_job() method currently accepts initiative_id and coder parameters but not input artifacts. The submit_commands.main() function already supports --input KEY=VALUE arguments. The gap is in the service layer that connects the console UI to the submit command.
- The file picker architecture should allow easy extension to different input artifact keys in future phases without modifying the core submission flow.
