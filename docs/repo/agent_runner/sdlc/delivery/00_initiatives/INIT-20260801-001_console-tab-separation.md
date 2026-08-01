---
template_id: "SYS-03-IN"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Initiative document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "SDLC00INIT-20260731-ee7151bb"
source_document: "DRAFT-INIT-20260731-001_console-tab-separation.md"
---

# Operator Console Tab-Based UI Separation

## Objective

Restructure the operator console from a single flat dropdown layout into a
two-tab interface (Submit Job and Manage Runs) so that each action mode
exposes only its relevant controls, eliminating ambiguity about which inputs
feed which action.

## Problem Statement

The current operator console presents a single row of dropdowns (Worker ID,
Repository, Workflow, Action) plus an Active Runs section below. All
controls -- submit-related, run-management-related, and shared -- are always
visible regardless of which action is selected. The Action dropdown toggles
visibility of conditional controls (feedback field, reset step, start step)
via show/hide logic at runtime.

Current state pain points:

- Users cannot determine at a glance which dropdowns feed the selected
  action. The Submit action reads from repo/workflow dropdowns and dynamic
  input fields, while all other actions (Approve, Reject, Resume, Retry,
  Reset, Cancel) read from the Active Runs dropdown, but both sets of
  controls remain visible at all times.

- The runtime show/hide toggling creates a cluttered and inconsistent
  experience. Controls appear and disappear based on the Action dropdown
  selection rather than structural UI membership.

- Selecting a repo/workflow has no effect on run-management actions, and
  selecting an active run has no effect on Submit, yet both sets of
  controls coexist in a single undifferentiated view.

- Error-prone operation: users may attempt to Submit when they intended to
  Approve, or vice versa, because the UI does not clearly separate the two
  workflows into distinct interaction contexts.

Why this initiative is needed:

The current layout conflates two fundamentally different operations --
creating new work (Submit) and managing existing work (run actions) -- into
a single view. As the console gains more actions and inputs over time, the
confusion will worsen rather than improve.

Impact of not undertaking this initiative:

Continued user confusion, incorrect action execution, and increasing UI
complexity as new features are added to the console.

## Expected Outcomes

Prioritized list of concrete, measurable outcomes:

1. Two-tab layout implemented. The console renders two distinct tabs
   labeled "Submit Job" and "Manage Runs", replacing the current flat
   layout.

2. Worker ID dropdown remains shared at the top, filtering both
   repositories (tab 1) and active runs (tab 2).

3. Submit Job tab contains all submit-related controls: Repository
   dropdown, Workflow dropdown, Dynamic Inputs section, Start Step
   dropdown, Submit Job button, and Quit Daemon button.

4. Manage Runs tab contains all run-management controls: Active Runs
   dropdown, Refresh button, Auto-refresh checkbox, Action dropdown
   (Approve/Reject/Resume/Retry/Reset/Cancel), Reset Target Step
   dropdown, Feedback/Reason field, and Run Action button.

5. Removal of all runtime visibility toggle hacks. Controls are shown or
   hidden by tab membership rather than by conditional visible=True/False
   logic driven by the Action dropdown.

6. Each tab has its own execute button, removing ambiguity about what will
   happen when clicked.

7. Tab switching preserves independent state. Switching between tabs does
   not reset or affect the other tab's selected values.

8. Output field and status text remain visible outside the tab boundary
   (below both tabs), serving as shared display elements for both Submit
   Job and Manage Runs tabs.

## Scope

### In Scope

- Tab-based UI layout in builders.py. Replace the current flat
  build_main_layout function with a two-tab structure using Flet tab
  controls. The Worker ID dropdown and console title remain outside the
  tabs as shared elements.

- State restructuring in state.py. Reorganize ConsoleState widget
  references to reflect tab-specific groupings. Remove or repurpose
  widget references that are no longer needed under the tab model.

- Handler split in handlers.py. Separate the single execute callback into
  distinct execution paths for each tab. The Submit tab execute callback
  handles job submission; the Manage Runs tab execute callback handles
  run-management actions.

- App wiring in app.py. Connect two separate execute callbacks to the
  two tabs instead of the current single on_execute callback routed
  through the Action dropdown.

- Quit Daemon button relocated to the Submit Job tab. This button
  requires repository selection context, making it a submit-tab concern.

- Output field and status text positioned outside the tab boundary
  (below both tabs) as shared display elements. The output field
  (build_output_field) and status text (build_status_section) are
  written to by both tabs via existing callbacks and must remain
  visible regardless of which tab is active.

### Out of Scope

- No backend API changes. The runner_service.py and backend_service.py
  interfaces remain unchanged.

- No daemon logic changes. The daemon process, polling, and worker
  lifecycle are not affected.

- No CLI changes. The console command-line arguments and entry point are
  not affected.

- No new actions or features added to the console. This is a pure UI
  restructuring of existing functionality.

- No changes to workflow definitions or runner behavior. The SDLC
  workflow pipeline and step execution logic are untouched.

- No changes to the Active Runs data model or refresh mechanism.

### Boundary Conditions

- The console must continue to support both desktop and web (--web) launch
  modes, as determined by the existing --web CLI flag.

- The console configuration file (console config) and its repository/
  workflow discovery mechanism remain unchanged.

- The single-instance enforcement (check_single_instance) behavior is
  unchanged.

- The output text field and status text remain accessible from both tabs
  or are positioned outside the tab area. Specifically, the output field
  (multiline read-only TextField) and status text widget are placed below
  both tabs in the main layout column, serving as shared display elements
  for both the Submit Job and Manage Runs tabs.

- The Reset Target Step dropdown in the Manage Runs tab depends on the
  workflow selected in the Submit Job tab for step name population. This
  cross-tab data dependency is acknowledged and acceptable. The
  refresh_step_options handler in handlers.py reads workflow_dd from
  ConsoleState regardless of which tab is active. Tab state independence
  (Expected Outcome 7) applies to UI selection state, not to data
  dependencies required for populating dropdown options.

- The shared ft.FilePicker instance remains a page-level service (added
  to page.services in app.py), not a tab-specific visual control. Dynamic
  inputs in the Submit Job tab use the file picker for browse
  functionality via the on_browse_click handler, but the picker itself
  is not rendered inside any tab.

## Constraints

Technical constraints:

- Must use Flet ft.Tabs / ft.Tab controls for the tab structure. The
  exact API depends on the installed Flet version. The Flet dependency
  is declared in pyproject.toml without version pinning. The draft
  initiative references Flet 0.86.x; the actual installed version must
  be verified before implementation begins.

- Must preserve all existing action functionality: Submit, Approve,
  Reject, Resume, Retry, Reset, Cancel, and Quit Daemon. No action may
  be removed or have its behavior altered.

- Must preserve all existing confirmation dialogs for every action.

- Must maintain compatibility with the existing ConsoleState dataclass
  model in state.py and the EventHandlers class in handlers.py.

Architectural constraints:

- The operator_console package is organized into builders.py, state.py,
  handlers.py, app.py, models.py, config.py, and services/. The tab
  restructuring must work within this existing module decomposition.

- The existing separation of UI construction (builders), state management
  (state), event handling (handlers), and app wiring (app) must be
  preserved. No module should be merged or eliminated.

- The UIBuilder class in builders.py currently delegates to
  build_main_layout. The tab layout must follow the same builder
  pattern.

## Dependencies

- No prerequisite initiatives are required. This initiative is
  self-contained.

- No third-party system changes are required. The console communicates
  with the same backend and daemon as today.

- No data or infrastructure changes are required.

- The initiative depends on the existing refactored architecture
  (state.py, handlers.py, builders.py) which provides the clean module
  boundaries needed for this restructuring. This architecture is already
  in place.

## Success Criteria

The following specific, testable criteria determine initiative success:

1. Console launches without errors in both desktop and web modes.

2. Two tabs render with correct controls in each tab. The Submit Job tab
   shows Repository, Workflow, Dynamic Inputs, Start Step, and Quit
   Daemon. The Manage Runs tab shows Active Runs, Refresh, Auto-refresh,
   Action (Approve/Reject/Resume/Retry/Reset/Cancel), Reset Target Step,
   and Feedback/Reason.

3. Submit tab functionality: selecting a repository and workflow
   populates dynamic inputs correctly. The Submit Job button triggers
   job submission with the existing confirmation dialog.

4. Manage tab functionality: the Refresh button populates active runs.
   Selecting a run and an action triggers the correct operation with
   the existing confirmation dialog.

5. Quit Daemon button on the Submit tab triggers the existing
   confirmation dialog and sends the quit command.

6. Tab state independence: switching between tabs does not reset or
   alter the other tab's selected values or input state.

7. No runtime visibility toggling: no control relies on visible=True/
   False logic driven by the Action dropdown selection. Controls are
   shown or hidden exclusively by tab membership.

8. All existing confirmation dialogs continue to appear for every action.

9. Output field and status text are visible outside the tab boundary
   (below both tabs) in both desktop and web modes. Action results from
   either tab appear in the output field. Status messages appear in the
   status text.

## Stakeholders

- Sponsor: Platform operator / project maintainer.

- Primary users: Operators who use the console to submit workflow runs
  and manage active runs (approve, reject, resume, retry, reset, cancel).

- Review authorities: Platform owner (Layer 2 governance).

- Affected teams: None beyond the platform maintainer. The console is a
  developer/operations tool used locally.

## Notes

- The existing architectural refactor plan (console CLI-only, daemon
  messenger-only) described in docs/developer/ARCHITECTURAL_REFACTOR.md
  is a separate initiative. This work is independent and can proceed
  without resolving that plan first.

- The current refactored architecture (state.py, handlers.py,
  builders.py) provides a clean foundation for this change. No further
  architectural refactoring is needed as a prerequisite.

- Assumption: The Flet version installed in the target environment
  provides ft.Tabs and ft.Tab controls. The exact API surface must be
  verified against the installed Flet version before implementation
  begins, as the dependency in pyproject.toml is unpinned.

- The output text field and status text placement has been resolved
  (see Expected Outcome 8, In Scope, Boundary Conditions, Success
  Criterion 9). They are positioned outside the tab boundary (below
  both tabs) as shared display elements for both tabs.

- The operator_console package files directly affected:
  builders.py (layout restructuring), state.py (widget reference
  reorganization), handlers.py (execute callback split), app.py
  (tab wiring). Files not affected: models.py, config.py, services/.
