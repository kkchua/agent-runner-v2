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
lifecycle_status: "approved"
effective_version: "SDLC00INIT-20260723-54c92390"
source_document: "DRAFT-INIT-20260722-001_console-sdlc10-support.md"
---

# Operator Console SDLC Phase 1 - Initiative Intake Support

## Objective

Add SDLC workflow input handling to the operator console (Flet desktop GUI)
for the sdlc_10_requirement_v1 workflow (Initiative Intake). The console must
enable users to select a draft initiative document from the filesystem, submit
it as a job to the backend with the correct DRAFT_INIT_FILE input artifact,
and have the daemon process it through the sdlc_10 workflow pipeline.

## Problem Statement

The operator console currently supports generic job submission via the "submit
job" action but has no awareness of SDLC workflow input requirements. Users
must manually construct CLI commands or batch files to submit SDLC workflows
with the correct input artifacts.

Pain points:

- No file picker in the console for selecting draft initiative documents.
- Users must know the exact artifact key name (DRAFT_INIT_FILE) and construct
  --input KEY=VALUE arguments manually.
- No visual feedback on which workflows require which input artifacts.
- The console workflow dropdown lists all workflows but does not adapt its
  interface to workflow-specific input requirements.

This initiative is needed because the operator console is the primary user
interface for managing workflow runs. Without SDLC-specific input handling,
users cannot efficiently submit SDLC workflow jobs through the console. This
blocks the validation of the SDLC workflow chain on real internal tool
development tasks.

Impact of not undertaking this initiative:

- SDLC workflows remain unusable from the console interface.
- Users must fall back to batch files or CLI for SDLC job submission.
- The SDLC workflow chain cannot be validated end-to-end through the console.

## Expected Outcomes

1. Users can select sdlc_10_requirement_v1 from the workflow dropdown and see
   a file picker for the draft initiative document.
2. Users can browse and select a draft initiative file (DRAFT_INIT_FILE) from
   the filesystem through the console interface.
3. Clicking "Run Action" with "submit job" selected submits the job to the
   backend with the correct DRAFT_INIT_FILE input artifact path.
4. The daemon picks up the submitted job and processes it through the
   sdlc_10 workflow pipeline.
5. The file picker is only visible when an SDLC workflow is selected and the
   action is "submit job".
6. The file picker component is architecturally extensible to support
   different input artifact keys in future SDLC phases.

## Scope

### In Scope

- File picker UI component (Flet FilePicker + TextField + Browse button).
- Conditional visibility logic: show the file picker only when the action is
  "submit job" AND the selected workflow name starts with "sdlc_".
- Pass the selected file path as --input DRAFT_INIT_FILE=<path> to the submit
  command.
- Update runner_service.submit_job() to accept and forward input artifact
  paths to the backend.

### Out of Scope

- Support for sdlc_20 through sdlc_80 workflows (separate future phases).
- Artifact dropdown for selecting approved outputs from previous runs.
- Output display for generated artifacts after job completion.
- Workflow-specific input validation or schema enforcement.
- Changes to backend API or daemon behavior.

### Boundary Conditions

- This initiative covers console-only changes. No backend workflow definition
  changes are included.
- The sdlc_10_requirement_v1 workflow must already be defined and synced to
  the backend. This initiative does not create or modify the workflow.
- Only one input artifact (DRAFT_INIT_FILE) is handled. Multi-artifact input
  support is deferred to a future phase.
- The file picker operates on the local filesystem only. Remote or network
  file sources are not in scope.

## Constraints

- Must use the Flet UI framework, which is the existing console dependency.
- Must integrate with the existing submit_commands.main() flow without
  breaking current generic job submission behavior.
- File picker must work on Windows, the primary development platform.
- No changes to backend API or daemon behavior are permitted within this
  initiative.
- Must conform to the Layer 2 platform metadata contract (METADATA_CONTRACT.md)
  for any generated or modified governed documents.
- Must not redefine or contradict Layer 1 governance or Layer 2 platform
  constitution.

## Dependencies

- operator-console.example.json must have at least one repository configured
  with sdlc_10_requirement_v1 in its workflow list.
- Draft initiative documents must exist in the
  docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/ directory.
- The sdlc_10_requirement_v1 workflow must be synced to the backend and
  operational.
- The Flet FilePicker component must be available in the version of Flet
  used by the console application.
- The runner_service module must be accessible and modifiable within the
  console application codebase (agent_runner_v2/).

## Success Criteria

- The console launches without errors when SDLC workflows are present in the
  configuration.
- Selecting sdlc_10_requirement_v1 from the workflow dropdown causes the
  file picker row to appear in the console interface.
- Selecting a non-SDLC workflow causes the file picker row to be hidden.
- Browsing and selecting a .md file through the file picker populates the
  path text field with the selected file path.
- Clicking "Run Action" with "submit job" submits the job successfully and
  the backend receives the DRAFT_INIT_FILE input artifact path.
- The daemon processes the submitted job through the sdlc_10 workflow steps
  and produces the expected INIT_FILE output artifact.
- Existing generic job submission (non-SDLC workflows) continues to function
  without regression.

## Stakeholders

- Sponsor: Project maintainer (operator console development initiative).
- Primary users: Developers and operators who use the console to submit and
  manage SDLC workflow jobs.
- Review authorities: Layer 2 platform maintainers (agent-runner-v2 platform
  constitution compliance).
- Affected teams: Console application developers, SDLC workflow developers,
  and operators who validate the SDLC delivery chain end-to-end.

## Notes

This initiative is Phase 1 of the console SDLC support plan. The master plan
document at masterplan/SDLC_CONSOLE_APP_PLAN.md lists all 8 phases. Each
phase will be implemented as a separate SDLC workflow cycle, using the SDLC
process itself to develop the console application features.

The file picker implementation should be architecturally generic enough to
support different input artifact keys in future phases (for example, INIT_FILE
for sdlc_20, REQ_FILE for sdlc_30). The Phase 1 implementation hardcodes
DRAFT_INIT_FILE but the architecture should allow straightforward extension
without structural changes.

The codebase areas likely affected include: the operator console UI layer
(Flet components and layout), the runner_service module (submit_job function),
and the submit_commands integration point.