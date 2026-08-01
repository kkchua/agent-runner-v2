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
effective_version: "SDLC00INIT-20260731-f12a9301"
source_document: "DRAFT-INIT-20260731-001_console-tab-separation.md"
---

# Operator Console Tab-Based UI Separation

## Objective

Separate the operator console's single flat dropdown layout into two
distinct tabs - Submit Job and Manage Runs - so that each action mode
shows only its relevant controls, eliminating confusion about which
inputs feed which action.

## Problem Statement

### Current State

The operator console presents a single row of dropdowns (Worker ID,
Repository, Workflow, Action) plus an Active Runs section below. The
Submit action reads from the repo and workflow dropdowns and dynamic
input fields. All other actions (Approve, Reject, Resume, Retry, Reset,
Cancel) read from the Active Runs dropdown. Both modes share the same
flat layout. The current architecture (state.py, handlers.py,
builders.py, app.py) confirms this structure: builders.py constructs a
single Action dropdown containing Submit, Approve, Reject, Resume,
Retry, Reset, Cancel, and Quit Daemon as unified options, while
handlers.py toggles visibility of controls via show/hide logic based on
the selected action.

### Pain Points

- Users cannot tell at a glance which dropdowns feed the selected
  action.
- The Action dropdown toggles visibility of controls (feedback field,
  reset step, start step) via show/hide hacks, creating a cluttered
  and inconsistent experience.
- Selecting a repo or workflow has no effect on run-management actions,
  and selecting an active run has no effect on Submit - but both sets
  of controls are always visible.
- Error-prone: users may attempt to Submit when they intended to
  Approve, or vice versa, because the UI does not clearly separate the
  two workflows.

### Why This Initiative Is Needed

The current layout conflates two fundamentally different operations
(creating new work vs managing existing work) into a single
undifferentiated view. As the console gains more actions and inputs,
the confusion will worsen rather than improve.

### Impact of Not Undertaking This Initiative

Continued user confusion, incorrect action execution, and increasing UI
complexity as new features are added to the console. The console's
usability degrades with each additional action or input field appended
to the existing flat layout.

## Expected Outcomes

1. Two-tab layout implemented: Submit Job tab and Manage Runs tab,
   replacing the current single flat view.
2. Worker ID dropdown remains shared at the top of the console,
   filtering both repos (Submit Job tab) and active runs (Manage Runs
   tab).
3. Submit Job tab contains: Repository dropdown, Workflow dropdown,
   Dynamic Inputs, Start Step control, Submit Job button, and Quit
   Daemon button.
4. Manage Runs tab contains: Active Runs dropdown, Refresh button,
   Auto-refresh toggle, Action dropdown (Approve, Reject, Resume,
   Retry, Reset, Cancel), Reset Target Step, Feedback/Reason field,
   and Run Action button.
5. Removal of visibility toggle hacks from handlers.py. Controls are
   shown or hidden by tab membership, not by runtime show/hide logic.
6. Each tab has its own execute button, removing ambiguity about what
   will happen when clicked.
7. Output field (multiline read-only TextField) and status text
   (Text widget displaying "Ready" and status messages) remain visible
   outside the tab boundary (below both tabs), serving as shared display
   elements for both Submit Job and Manage Runs tabs. Both tabs write
   action results to the output field via the existing output_callback
   mechanism.

## Scope

### In Scope

- Tab-based UI layout refactor in builders.py, replacing the current
  flat control row with ft.Tabs containing two ft.Tab children.
- State restructuring in state.py to hold tab-specific widget
  references (separate references for Submit tab controls and Manage
  Runs tab controls).
- Handler split in handlers.py into separate execute paths for each
  tab (submit execution path and run-management execution path).
- App wiring in app.py to register two execute callbacks instead of
  the current single action-dispatched callback.
- Quit Daemon button moved to the Submit Job tab (it requires repo
  selection context).
- Removal of show/hide toggle logic in handlers.py that currently
  controls visibility of feedback fields, reset step, and start step
  based on action selection.
- Output field and status text placement outside the tab boundary
  (below both tabs) as shared display elements. These controls remain
  accessible to both tabs without being part of either tab's content.
- File picker (ft.FilePicker) retained as a page-level service (added
  to page.services in app.py), not placed inside any tab. Dynamic
  inputs in the Submit Job tab use the file picker for browse
  functionality, but the picker itself is not visually part of any tab.

### Out of Scope

- No backend API changes (daemon messenger protocol remains unchanged).
- No daemon logic changes (job execution, approval, rejection, and
  other action implementations are unaffected).
- No CLI changes (the CLI interface is a separate concern).
- No new actions or features added to the console (this is a layout
  refactor only).
- No changes to workflow definitions or runner behavior.
- No changes to the operator-console.json configuration file schema.
- No changes to the ConsoleConfig data model beyond what is needed to
  support tab-specific widget references in state.py.

### Boundary Conditions

- This initiative affects only the operator console UI layer
  (builders.py, state.py, handlers.py, app.py). It does not modify
  backend services, workflow packages, or execution engine behavior.
- The tab separation is a pure UI reorganization. All existing actions
  (Submit, Approve, Reject, Resume, Retry, Reset, Cancel, Quit Daemon)
  must continue to function identically after the refactor.
- The existing architectural separation (state.py for state,
  handlers.py for events, builders.py for UI construction, app.py for
  wiring) is preserved and extended, not replaced.
- Tab switching must not cause loss of state in either tab. Each tab
  maintains its own control state independently.
- The Worker ID dropdown, which filters data for both tabs, remains
  outside the tab boundary as a shared global control.
- The output field and status text remain outside the tab boundary
  (below both tabs) as shared display elements. Both tabs write to the
  output field via the existing output_callback in app.py. The status
  text displays operational messages regardless of which tab is active.
- The Reset Target Step dropdown in the Manage Runs tab depends on the
  workflow selected in the Submit Job tab for step name population. This
  cross-tab data dependency is acknowledged and acceptable. The
  refresh_step_options handler in handlers.py reads workflow_dd from
  ConsoleState regardless of which tab is active. The workflow selection
  made in the Submit Job tab is the source of step names for the reset
  step dropdown in the Manage Runs tab.
- The shared ft.FilePicker instance remains a page-level service (added
  to page.services in app.py), not a tab-specific visual control.
  Dynamic inputs in the Submit Job tab use the file picker for browse
  functionality via the on_browse_click handler, but the picker itself
  is not rendered inside any tab.

## Constraints

- Must use Flet ft.Tabs and ft.Tab controls for the tab-based layout.
  The Flet dependency is declared as an optional console dependency in
  pyproject.toml without a pinned version. The implementation must
  verify ft.Tabs and ft.Tab API compatibility with the Flet version
  installed at runtime.
- Must preserve all existing action functionality: Submit, Approve,
  Reject, Resume, Retry, Reset, Cancel, and Quit Daemon. Each action
  must produce the same result as it does today.
- Must preserve confirmation dialogs for all actions. The current
  confirmation dialog behavior in handlers.py must not be altered.
- Must operate on Windows, which is the primary development and
  deployment platform.
- Must remain compatible with the existing ConsoleState dataclass
  structure in state.py. Tab-specific widget references must be added
  to the existing state model without breaking current state management.
- Must remain compatible with the existing EventHandlers class in
  handlers.py. The handler split must not alter the handler
  initialization or service injection contract.
- The initiative is scoped to Layer 3 workflow bundle concerns and must
  not redefine or contradict Layer 1 governance (LAYER_MODEL.md,
  METADATA_STANDARD.md) or Layer 2 platform constitution
  (METADATA_CONTRACT.md).

## Dependencies

- The existing operator console module architecture
  (agent_runner_v2/operator_console/) provides the foundation for this
  change. The current separation into state.py, handlers.py,
  builders.py, and app.py must be preserved and extended.
- The Flet UI framework must provide ft.Tabs and ft.Tab controls with
  the API surface needed for this implementation. The Flet version
  installed in the console optional dependency group must be verified
  for compatibility.
- No prerequisite initiatives are required. This initiative is
  self-contained and independent of the planned architectural refactor
  (console as control panel, CLI as brain).
- No third-party system integrations are required. The initiative
  operates entirely within the existing console UI and its connection
  to the daemon backend via the existing services layer.
- No data or infrastructure changes are required. The initiative does
  not modify the operator-console.json configuration schema or the
  daemon communication protocol.

## Success Criteria

1. Console launches without errors and renders the two-tab layout
   (Submit Job and Manage Runs) with the Worker ID dropdown visible
   above both tabs.
2. Submit Job tab renders with Repository dropdown, Workflow dropdown,
   Dynamic Inputs area, Start Step control, Submit Job button, and Quit
   Daemon button. No Manage Runs controls are visible in this tab.
3. Manage Runs tab renders with Active Runs dropdown, Refresh button,
   Auto-refresh toggle, Action dropdown (limited to Approve, Reject,
   Resume, Retry, Reset, Cancel), Reset Target Step, Feedback/Reason
   field, and Run Action button. No Submit Job controls are visible in
   this tab.
4. Submit tab: selecting a repo and workflow populates dynamic inputs
   correctly. The Submit Job button triggers job submission with a
   confirmation dialog. The Quit Daemon button triggers a confirmation
   dialog and sends the quit command.
5. Manage tab: Refresh populates the active runs dropdown. Selecting a
   run and an action triggers the correct operation with a confirmation
   dialog. Each action (Approve, Reject, Resume, Retry, Reset, Cancel)
   produces the same result as the current flat layout.
6. Switching between tabs does not affect the other tab's state.
   Control values, selections, and dynamic inputs in each tab are
   preserved independently.
7. No show/hide toggle logic remains in handlers.py for controlling
   the visibility of feedback fields, reset step, or start step based
   on action selection. Visibility is determined solely by tab
   membership.
8. Output field and status text are visible below both tabs regardless
   of which tab is active. Submitting a job in the Submit Job tab writes
   results to the output field. Executing any action in the Manage Runs
   tab writes results to the same output field. The status text updates
   correctly for actions from both tabs.

## Stakeholders

- Sponsor: Operator console users and platform maintainers.
- Primary Users: Daily operators who use the console to submit jobs and
  manage active runs. These users are directly affected by the UI
  clarity improvement.
- Review Authorities: Platform maintainers responsible for the
  operator-console module (builders.py, state.py, handlers.py, app.py).
- Affected Teams: Any team that uses the operator console for job
  submission or run management. No backend or infrastructure teams are
  affected.

## Critique Resolution

### Finding 1: Output Field and Status Text Placement Not Specified
**Resolution:** Added output field and status text to Expected Outcomes
(item 7), Scope In Scope (placement outside tab boundary as shared
display elements), Boundary Conditions (shared display elements below
both tabs, accessible to both tabs via existing output_callback), and
Success Criteria (item 8, verifying output field visibility and write
behavior from both tabs). Both controls are confirmed in the codebase:
build_output_field (builders.py) creates the multiline read-only
TextField stored in state.output, and build_status_section (builders.py)
creates the Text widget stored in state.status_text. The append_output
callback in app.py writes to state.output for all actions.
**Affected section:** Expected Outcomes, Scope (In Scope), Boundary
Conditions, Success Criteria

### Finding 2: Cross-Tab Data Dependency for Reset Step Dropdown
**Resolution:** Added explicit acknowledgment of the cross-tab data
dependency to the Boundary Conditions section. The reset_step_dd in the
Manage Runs tab depends on workflow_dd in the Submit Job tab for step
name population. The refresh_step_options handler in handlers.py reads
self.state.workflow_dd.value to look up the workflow and load step names
from the workflow bundle. This dependency is accepted as-is: the
workflow_dd reference is already accessible from ConsoleState regardless
of which tab is active, so no architectural change is needed. The
boundary condition now documents this dependency explicitly so that
planning and implementation can account for it.
**Affected section:** Boundary Conditions

### Finding 3: Flet API Verification Not Possible in Current Environment
**Resolution:** No change needed. The initiative already acknowledges
this risk in two places: the Constraints section states that the
implementation must verify ft.Tabs and ft.Tab API compatibility with the
Flet version installed at runtime, and the Notes section states that the
Flet version must be verified for compatibility. The critique confirms
this is properly handled. The draft document's fabricated "Flet 0.86.x"
version pin was correctly removed in the initiative.
**Affected section:** None (already addressed in Constraints and Notes)

### Finding 4: File Picker Placement Implicit but Not Explicit
**Resolution:** Added explicit clarification to both the Scope In Scope
section and the Boundary Conditions section. The ft.FilePicker instance
remains a page-level service (added to page.services in app.py), not a
tab-specific visual control. Dynamic inputs in the Submit Job tab use
the file picker for browse functionality via the on_browse_click handler,
but the picker itself is not rendered inside any tab. This matches the
current architecture where build_file_picker (builders.py) creates the
picker and app.py adds it to page.services.
**Affected section:** Scope (In Scope), Boundary Conditions

### Finding 5: Draft-to-Initiative Improvements Confirmed
**Resolution:** No change needed. This finding is informational and
confirms positive improvements made from the draft to the initiative:
removal of fabricated Flet version pin, expanded Dependencies section,
added Boundary Conditions, detailed Success Criteria, app.py inclusion
in scope, and ConsoleState/EventHandlers compatibility constraints. All
improvements are acknowledged and retained.
**Affected section:** None (informational, no action required)

## Notes

- The existing architectural refactor plan (console CLI-only, daemon
  messenger-only) described in prior codebase documentation is a
  separate initiative. This work is independent and can proceed without
  resolving that plan first.
- The current refactored architecture (state.py, handlers.py,
  builders.py, app.py) provides a clean foundation for this change. No
  further architectural refactoring is needed before this initiative
  can begin.
- The Flet dependency is declared without version pinning in
  pyproject.toml (optional console group). The constraint to use
  ft.Tabs and ft.Tab controls assumes these are available in the Flet
  version installed at runtime. If the installed Flet version lacks
  these controls or has an incompatible API, a version pin or Flet
  upgrade may be required as a prerequisite.
- The Quit Daemon action is currently part of the unified Action
  dropdown. Moving it to the Submit Job tab is appropriate because it
  requires repo selection context. This does not change its
  functionality, only its UI location.
- It is assumed that the existing confirmation dialog implementation in
  handlers.py can be reused without modification for both tabs. If the
  dialog logic is tightly coupled to the current flat layout, minor
  adaptation may be needed during the planning phase.
