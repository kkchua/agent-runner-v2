---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "Operator console UI refactor for clearer workflow separation"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Operator Console Tab-Based UI Separation

## Objective

Separate the operator console's single flat dropdown layout into two distinct
tabs -- Submit Job and Manage Runs -- so that each action mode shows only its
relevant controls, eliminating confusion about which inputs feed which action.

## Problem Statement

### Current State

The operator console presents a single row of dropdowns (Worker ID, Repository,
Workflow, Action) plus an Active Runs section below. The Submit action reads
from the repo/workflow dropdowns and dynamic input fields. All other actions
(Approve, Reject, Resume, Retry, Reset, Cancel) read from the Active Runs
dropdown. Both modes share the same flat layout.

### Pain Points

- Users cannot tell at a glance which dropdowns feed the selected action.
- The Action dropdown toggles visibility of controls (feedback field, reset
  step, start step) via show/hide hacks, creating a cluttered and inconsistent
  experience.
- Selecting a repo/workflow has no effect on run-management actions, and
  selecting an active run has no effect on Submit -- but both sets of controls
  are always visible.
- Error-prone: users may attempt to Submit when they intended to Approve, or
  vice versa, because the UI does not clearly separate the two workflows.

### Why This Initiative Is Needed

The current layout conflates two fundamentally different operations (creating
new work vs managing existing work) into a single undifferentiated view. As the
console gains more actions and inputs, the confusion will worsen rather than
improve.

### Impact of Not Undertaking This Initiative

Continued user confusion, incorrect action execution, and increasing UI
complexity as new features are added to the console.

## Expected Outcomes

- Two-tab layout: Submit Job tab and Manage Runs tab.
- Worker ID dropdown remains shared at the top, filtering both repos (tab 1)
  and active runs (tab 2).
- Submit Job tab contains: Repository, Workflow, Dynamic Inputs, Start Step,
  Submit Job button, Quit Daemon button.
- Manage Runs tab contains: Active Runs dropdown, Refresh, Auto-refresh,
  Action dropdown (Approve/Reject/Resume/Retry/Reset/Cancel), Reset Target
  Step, Feedback/Reason, Run Action button.
- Removal of visibility toggle hacks (controls are shown or hidden by tab
  membership, not by runtime show/hide logic).
- Each tab has its own execute button, removing ambiguity about what will
  happen when clicked.

## Scope

### In Scope

- Tab-based UI layout in builders.py.
- State restructuring in state.py (tab-specific widget references).
- Handler split in handlers.py (separate execute paths for each tab).
- App wiring in app.py (two execute callbacks).
- Quit Daemon button moved to Submit tab (it requires repo selection).

### Out of Scope

- No backend API changes.
- No daemon logic changes.
- No CLI changes.
- No new actions or features added to the console.
- No changes to workflow definitions or runner behavior.

## Constraints

- Must use Flet 0.86.x ft.Tabs / ft.Tab controls.
- Must preserve all existing action functionality (Submit, Approve, Reject,
  Resume, Retry, Reset, Cancel, Quit Daemon).
- Must preserve confirmation dialogs for all actions.

## Dependencies

- None. This initiative is self-contained.

## Success Criteria

- Console launches without errors.
- Two tabs render with correct controls in each tab.
- Submit tab: selecting repo and workflow populates dynamic inputs; Submit
  Job button triggers job submission with confirmation dialog.
- Manage tab: Refresh populates active runs; selecting a run and action
  triggers the correct operation with confirmation dialog.
- Quit Daemon button on Submit tab triggers confirmation dialog and sends
  quit command.
- Switching between tabs does not affect the other tab's state.

## Notes

- The existing architectural refactor plan (console CLI-only, daemon
  messenger-only) is a separate initiative. This work is independent and
  can proceed without resolving that plan first.
- The current refactored architecture (state.py, handlers.py, builders.py)
  provides a clean foundation for this change. No further architectural
  refactoring is needed.
