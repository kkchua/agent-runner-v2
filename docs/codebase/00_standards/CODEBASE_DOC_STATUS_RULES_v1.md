---
title: "Codebase Documentation Status Rules v1"
template_id: "CODEBASE-DOC-STATUS-RULES-v1"
status: "active"
version: "1.0"
generated: "2026-07-04T07:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Codebase Documentation Status Rules v1

## Core Principles

1. **Every file has exactly one status.** Inventory entries and doc files each carry exactly one status at any time. No file has multiple statuses simultaneously.
2. **Status reflects current reality.** A doc's status must match its actual state relative to the source code it describes, not the desired or planned state.
3. **Staleness is flagged, not hidden.** Documentation that may be outdated is explicitly marked (`stale_pending`) rather than silently left unchanged.
4. **Supersession is traceable.** When a doc is replaced, the old version remains accessible with a pointer to the replacement. No doc is ever deleted.
5. **Transitions are deterministic.** Only explicitly allowed status transitions may occur. All others are forbidden by default.

## Inventory Status Model

Every entry in `docs/codebase/01_inventory/codebase_inventory.md` has one of these statuses:

| Status | Meaning |
|--------|---------|
| `active` | Doc exists and is current (verified against source) |
| `stale_pending` | Doc exists but may be outdated (verification needed or source changed without doc update) |
| `missing` | Source file exists but no doc exists yet |
| `orphaned` | Doc exists but source file has been deleted or moved |
| `superseded` | Doc has been replaced by a newer version |

### Status Transition Rules

Arrow form: `missing → active → stale_pending → active`
Arrow form (supersession): `active → superseded` or `stale_pending → superseded`
Arrow form (orphan): `active → orphaned`

| From | To | Trigger |
|------|----|---------|
| _(none)_ | `missing` | New source file detected during sync scan |
| `missing` | `active` | Doc created for the source file |
| `active` | `stale_pending` | Source file changed without co-change doc update; or sync scan detects mismatch |
| `stale_pending` | `active` | Doc updated to match current source; verified by sync or review |
| `active` | `superseded` | Doc replaced by a newer version |
| `stale_pending` | `superseded` | Stale doc replaced by a newer version |
| `active` | `orphaned` | Source file deleted/moved |
| `orphaned` | _(none)_ | Terminal — no transitions from orphaned. Doc is preserved for audit trail. |
| `superseded` | _(none)_ | Terminal — superseded docs are never reactivated |

### Forbidden Inventory Transitions

| Forbidden | Reason |
|-----------|--------|
| `superseded → active` | Superseded docs are terminal; create a new doc instead |
| `superseded → stale_pending` | Superseded docs are not updated; they are replaced |
| `orphaned → active` | Orphaned docs are terminal; create a new doc for the new source |
| `orphaned → stale_pending` | Orphaned docs are not updated |
| `missing → stale_pending` | Missing means no doc exists; cannot be stale |
| `active → missing` | An active doc exists; it cannot become "missing" |
| Any status → `draft` | Inventory entries do not have a draft state |

## Document Status Model

Every codebase doc file (in `02_modules/` or `03_components/`) carries a status in its frontmatter:

| Status | Meaning |
|--------|---------|
| `active` | Current and accurate |
| `stale_pending` | May be inaccurate, awaiting update |
| `superseded` | Replaced by a newer doc |

### Doc Status Transition Rules

Arrow form: `active → stale_pending → active` (update cycle)
Arrow form: `active → superseded` (replacement)
Arrow form: `stale_pending → superseded` (replacement of stale doc)

| From | To | Trigger |
|------|----|---------|
| _(creation)_ | `active` | Doc created for a source file |
| `active` | `stale_pending` | Source changed without co-change update; sync detected mismatch |
| `stale_pending` | `active` | Doc updated to match current source |
| `active` | `superseded` | Replaced by a newer doc |
| `stale_pending` | `superseded` | Replaced by a newer doc |

### Doc Status Consistency Rule

The doc file status must always match the corresponding inventory entry status. When the inventory changes, the doc frontmatter is updated in the same delivery task (or flagged if the task cannot update it).

| Inventory Status | Doc File Status |
|-----------------|-----------------|
| `active` | `active` |
| `stale_pending` | `stale_pending` |
| `superseded` | `superseded` |
| `missing` | (no doc file exists) |
| `orphaned` | `active` or `stale_pending` (file remains but source is gone) |

## Supersession Rules

When a codebase doc is replaced:

1. **The old file is renamed**, not deleted. Filename changes from `MODULENAME.md` to `MODULENAME.md.superseded`.
2. **Frontmatter updated** on the old file: `status: superseded`, `superseded_by: "{new_filename}"`.
3. **New file created** with `status: active` and frontmatter field `supersedes: "{old_filename}.superseded"`.
4. **Inventory updated** to mark the old entry `superseded` and the new entry `active`.
5. **No orphaned references.** Any doc that references the old file must be updated to reference the new file. If this is not possible in the current task, the reference is flagged as broken.

### Supersession Chain

Supersession creates a chain:

```
v1.md.superseded ← supersedes: none
v2.md.superseded ← supersedes: v1.md.superseded
v3.md (active)  ← supersedes: v2.md.superseded
```

Each doc in the chain points to its predecessor. The active doc is at the head of the chain. Superseded docs form a linked list back to the original.

### Supersession Forbidden Transitions

| Forbidden | Reason |
|-----------|--------|
| `superseded → active` | Superseded docs are terminal; create a new doc instead |
| `superseded → stale_pending` | Superseded docs are not updated; they are replaced |
| Delete superseded file | Superseded files are preserved for audit trail |
| Reactivate superseded doc | Once superseded, always superseded |

### Supersession Edge Cases

| Scenario | Action |
|----------|--------|
| Source file reappears at same path after doc was superseded | Create a new doc with `status: active`; do not reactivate the superseded doc |
| Source file moves to a new path | Supersede old doc; create new doc at new path |
| Doc is superseded while in `stale_pending` | Rename with `.superseded`, set status to `superseded` |
| Multiple docs claim to supersede the same predecessor | Reject — only one doc may supersede a given predecessor |

## Update Triggers

Documentation must be updated when any of these events occur:

| Trigger | Scope | Timing |
|---------|-------|--------|
| Source file modified (function/class change) | Affected doc(s) | Same delivery task (co-change rule) |
| New source file added | Inventory + new doc | Same delivery task |
| Source file deleted | Inventory + doc retirement | Same delivery task |
| Import relationship changes | All affected module docs | Same delivery task (impact propagation) |
| `40_documentation_sync_v1` detects drift | Affected docs | Flagged for next delivery cycle |
| Scheduled sync cycle | Full inventory | Per sprint/milestone |
| Human-reported inaccuracy | Affected doc(s) | Emergency correction or next cycle |
| Architecture profile selection changes | Affected docs | Next delivery task that touches affected modules |
| Migration mode change | Affected docs | Per migration mode requirements |

### Update Priority

When multiple triggers fire simultaneously, prioritize as follows:

1. **Critical stale guidance** (active misdirection) — immediate correction
2. **Co-change updates** (source modified in same task) — same delivery task
3. **Impact propagation** (importers of changed module) — same delivery task
4. **Sync-detected drift** — next delivery cycle
5. **Human-reported inaccuracy** — next delivery cycle (or emergency if critical)

## Traceability

Every codebase doc maintains traceability links:

- **Source path** — the file the doc describes (frontmatter `source_path`).
- **Covered by** — which delivery task created or last updated the doc (frontmatter `last_updated_by`).
- **Changed by** — which change record documents the last significant update (frontmatter `change_record`).
- **Supersedes / Superseded by** — chain of doc versions (frontmatter `supersedes` / `superseded_by`).
- **Coverage tier** — which tier (A-F) the source file belongs to (frontmatter `coverage_tier`).
- **Depth mode** — stub, summary, or full (frontmatter `depth_mode`).

### Traceability Requirements

| Artifact | Required Links |
|----------|---------------|
| Inventory entry | `source_path`, `status`, `doc_file` (if exists) |
| Module doc | `source_path`, `status`, `coverage_tier`, `depth_mode`, `last_updated_by` |
| Component doc | `covered_modules[]`, `status`, `last_updated_by` |
| Change record | `parent_task` (if from delivery), `affected_docs[]`, `affected_modules[]` |

These links enable:

- **Backward traceability** — from any doc to its source file and the delivery task that created/updated it.
- **Forward traceability** — from any source file to its current doc and all superseded predecessors.
- **Impact analysis** — when a source file changes, which docs are affected?
- **Audit trail** — who updated what, when, and why.

## Removal Rules

Codebase docs are **never deleted**. The retirement sequence is:

### Superseded Docs

1. Mark doc status as `superseded`.
2. Update inventory entry to `superseded`.
3. Rename file with `.superseded` suffix.
4. Add `superseded_by` pointer to frontmatter.
5. Update any docs that reference the old file.

### Orphaned Docs (source removed with no replacement)

1. Mark doc status as `orphaned` (if source was deleted) or `superseded` (if source was merged into another module).
2. Update inventory entry to match.
3. The file remains for audit purposes.
4. A cleanup task may be created to archive orphaned docs into a single `05_archives/` subdirectory, but the files are not deleted.

### Emergency Cleanup

**Exception:** Auto-generated backup files (`.bak`, `.tmp`) are not covered by this rule and may be cleaned freely.

### Removal Forbidden Actions

| Forbidden | Reason |
|-----------|--------|
| Delete a doc file | Docs are preserved for audit trail |
| Delete a superseded doc | Superseded docs are terminal and preserved |
| Delete an orphaned doc without archiving | Orphaned docs must be archived, not deleted |
| Remove an inventory entry | Inventory entries are never removed; they transition to terminal states |
