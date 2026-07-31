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
effective_version: "SDLC00INIT-20260730-c3962b52"
source_document: "DRAFT-INIT-20260731-002_console-workflow-favorites.md"
---

# Console Workflow Favorites

## Objective

Add a favorites mechanism to the operator console workflow dropdown, enabling
users to pin frequently used workflows for rapid access. As the number of
registered workflows grows across the SDLC chain, media generation, bootstrap
admin, and workflow builder packages, a simple pin/unpin toggle will keep
the most-used workflows immediately accessible without scrolling through the
full dropdown list.

## Problem Statement

### Current State

The operator console workflow dropdown enumerates all workflows registered in
the operator-console.json configuration file. Users must select a workflow
from this dropdown before performing any action (submit job, sync, bootstrap,
etc.). The current ConsoleConfig data model holds only a repos collection
with nested workflow entries; there is no concept of user preference or
favorites.

### Pain Points

- The workflow list grows with each new workflow package added to the
  system (SDLC chain, media generation, bootstrap admin, workflow builder).
- Users must scroll through the full dropdown to locate the workflow they
  intend to run.
- No mechanism exists to mark workflows as frequently used or to pin them
  to the top of the list.
- The dropdown renders all registered workflows uniformly, regardless of
  usage frequency.

### Why This Initiative Is Needed

Without a favorites or pinning mechanism, the workflow dropdown becomes
increasingly cumbersome as more workflows are registered. Users waste time
navigating past workflows they rarely use to reach the ones they run daily.
This degradation is proportional to the total number of registered workflows.

### Impact of Not Undertaking This Initiative

- Workflow selection time increases linearly as the list grows.
- Users may bypass the console entirely in favor of batch files or CLI
  commands, undermining the console's role as a unified control panel.
- Console user experience degrades with each new workflow addition,
  reducing adoption and satisfaction.

## Expected Outcomes

1. Users can toggle a workflow as a favorite directly from the workflow
   dropdown UI.
2. Favorited workflows are displayed in a visually distinct section at the
   top of the dropdown, separated from the full workflow list.
3. Favorites persist across console sessions via the operator-console.json
   configuration file.
4. Users can remove a workflow from favorites with the same interaction
   used to add it (toggle behavior).
5. The full workflow list below the favorites section remains fully
   functional and unchanged in behavior.

## Scope

### In Scope

- A favorite/unfavorite toggle control within the workflow dropdown UI
  for each workflow entry.
- A dedicated favorites section rendered at the top of the dropdown when
  at least one workflow is favorited.
- Persistence of favorited workflow names in the operator-console.json
  configuration file as a new top-level field.
- Loading the favorites list from operator-console.json on console
  startup.
- Writing the updated favorites list back to operator-console.json when
  a favorite is toggled.

### Out of Scope

- Drag-and-drop reordering of favorited workflows.
- Text search or filter for the full workflow list.
- Favorites support in any dropdown other than the main workflow selection
  dropdown (e.g., submit job action dropdown).
- Workflow usage statistics or automatic favorite suggestions based on
  usage patterns.
- Changes to backend API, workflow definitions, or the execution engine.
- Cross-machine synchronization of favorites.

### Boundary Conditions

- This initiative affects only the operator console UI layer and its local
  configuration persistence. It does not modify workflow definitions,
  backend services, or execution behavior.
- Favorites are stored as workflow name strings. A favorited workflow that
  is later removed from the configuration should be handled gracefully
  (e.g., ignored or displayed with a warning), but the specific handling
  is an implementation decision for the planning phase.
- The favorites feature must remain compatible with the existing repos and
  workflows data model defined in ConsoleConfig and its supporting
  dataclasses (WorkflowEntry, RepoEntry).

## Constraints

- The operator console uses the Flet UI framework. All UI changes must
  integrate with the existing Flet-based application structure in the
  operator_console app module.
- Configuration persistence must extend the existing operator-console.json
  structure. The current ConsoleConfig dataclass (models.py) and config
  loader (config.py) must be extended to support a favorites field.
- The solution must work on Windows, which is the primary development and
  deployment platform.
- No changes to backend API endpoints, workflow package definitions, or
  execution engine behavior are permitted.
- The initiative is scoped to Layer 3 workflow bundle concerns and must
  not redefine or contradict Layer 1 governance or Layer 2 platform
  constitution (as defined in LAYER_MODEL.md and METADATA_CONTRACT.md).
- The existing operator-console.example.json must be updated to document
  the new favorites field in the example configuration.

## Dependencies

- The operator-console.json configuration file must support a new top-level
  favorites field (array of workflow name strings). This requires updates
  to the ConsoleConfig dataclass in models.py and the config parsing logic
  in config.py.
- The operator-console.example.json must be updated to include the new
  favorites field as a documented example.
- The existing repos and workflows data model (ConsoleConfig, RepoEntry,
  WorkflowEntry in models.py) must remain functional and backward
  compatible alongside the favorites extension.
- No prerequisite initiatives are required. This initiative is independent
  of the planned architectural refactor (console as control panel, CLI as
  brain) and can be implemented in the current console architecture.

## Success Criteria

1. The workflow dropdown renders a favorites section at the top when at
   least one workflow is marked as a favorite.
2. Clicking the favorite toggle on an unfavorited workflow adds it to the
   favorites section immediately, with visible UI feedback.
3. Clicking the favorite toggle on a favorited workflow removes it from
   the favorites section immediately, with visible UI feedback.
4. Closing and reopening the console preserves the favorites list exactly
   as left by the user.
5. The operator-console.json file on disk contains the current favorites
   list after any toggle operation.
6. The full workflow list below the favorites section remains intact,
   scrollable, and fully functional for workflow selection.
7. The operator-console.example.json includes the new favorites field
   with documentation.

## Stakeholders

- Sponsor: Operator console users and platform maintainers.
- Primary Users: Daily operators who select workflows from the console
  dropdown to run SDLC, bootstrap, media generation, and workflow builder
  tasks.
- Review Authorities: Platform maintainers responsible for the
  operator-console module and the operator-console.json configuration
  contract.
- Affected Teams: Any team that registers workflows in the operator
  console configuration and uses the console for workflow selection.

## Notes

- The current ConsoleConfig dataclass in models.py contains only a repos
  field. The favorites feature will require adding a new field (e.g.,
  favorites as a tuple of workflow name strings) to ConsoleConfig and
  updating the config loading logic in config.py to parse and serialize
  this field.
- The current config.py load_console_config function parses only the repos
  key from the JSON payload. A favorites key will need to be added to the
  parsing logic.
- The operator-console.example.json currently contains only a repos array.
  The example must be extended to show the new favorites field.
- This initiative is independent of the planned architectural refactor
  (console as control panel, CLI as brain). The favorites feature can be
  implemented in the current console architecture and carried forward to
  any future console redesign.
- The workflow entry name field (WorkflowEntry.name) is the identifier
  used for favorites. It is assumed that workflow names are unique across
  all repos, which is already enforced by the existing duplicate-name
  validation in config.py.
