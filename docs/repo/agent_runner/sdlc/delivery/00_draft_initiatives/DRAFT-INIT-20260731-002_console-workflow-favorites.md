---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "Draft initiative for console workflow favorites feature"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Console Workflow Favorites

## Objective

Add a favorites feature to the operator console workflow dropdown so users
can save frequently used workflows and access them without scrolling through
the full list. As the number of registered workflows grows, a simple
pin/unpin mechanism will keep the most-used workflows one click away.

## Problem Statement

### Current State

The operator console workflow dropdown lists all workflows registered in
the operator-console.json config file. Users select a workflow from this
dropdown before performing any action (submit job, sync, bootstrap, etc.).

### Pain Points

- The workflow list is growing with each new workflow package added to the
  system (SDLC chain, media generation, bootstrap admin, workflow builder).
- Users must scroll up and down through the full dropdown to find the
  workflow they want to run.
- No mechanism to mark workflows as frequently used or pin them to the top.
- The dropdown shows all workflows regardless of how often they are used.

### Why This Initiative Is Needed

Without a favorites or pinning mechanism, the workflow dropdown becomes
increasingly cumbersome as more workflows are registered. Users waste time
scrolling through workflows they rarely use to find the ones they run daily.

### Impact of Not Undertaking This Initiative

- Workflow selection becomes slower as the list grows.
- Users may resort to batch files or CLI to avoid the dropdown entirely,
  defeating the purpose of the console as a unified control panel.
- The console UX degrades with each new workflow addition.

## Expected Outcomes

- Users can mark a workflow as a favorite from the workflow dropdown.
- Favorited workflows appear in a dedicated section at the top of the
  dropdown, separated from the full list.
- Favorites persist across console sessions via operator-console.json.
- Users can remove a workflow from favorites with the same ease as adding it.

## Scope

### In Scope

- Favorite/unfavorite toggle mechanism in the workflow dropdown UI.
- Favorites section displayed at the top of the dropdown, visually
  separated from the full workflow list.
- Persistence of favorite workflow names in operator-console.json config.
- Loading favorites from config on console startup.

### Out of Scope

- Drag-and-drop reordering of favorites.
- Text search or filter for the full workflow list.
- Favorites support in the submit job action dropdown (main list only).
- Workflow usage statistics or automatic favorite suggestions.

## Constraints

- Must use Flet UI framework (existing console dependency).
- Must integrate with the existing operator-console.json config structure.
- Must work on Windows (primary development platform).
- No changes to backend API or workflow definitions required.

## Dependencies

- operator-console.example.json must support a new favorites field in the
  config structure.
- The existing workflow config (repos + workflows list) must remain
  functional alongside the favorites feature.

## Success Criteria

- The workflow dropdown displays a favorites section at the top when at
  least one workflow is favorited.
- Clicking the favorite toggle on a workflow adds it to the favorites
  section immediately.
- Clicking the favorite toggle on a favorited workflow removes it from
  favorites immediately.
- Closing and reopening the console preserves the favorites list.
- The operator-console.json file contains the favorites list after a
  favorite is added.
- The full workflow list below the favorites section remains intact and
  functional.

## Notes

- The existing operator-console.json already contains repos and workflows
  arrays. The favorites field would be a new top-level array of workflow
  name strings.
- This initiative is independent of the planned architectural refactor
  (console as control panel, CLI as brain). The favorites feature can be
  implemented in the current console architecture and carried forward.
