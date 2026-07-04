---
title: Codebase Documentation Status Rules
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_sop
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Codebase Documentation Status Rules

## Core Principles

1. **Every codebase document has a status.** No document exists without an explicit status. The absence of a status means the document is non-compliant.

2. **Status transitions are governed.** Documents move between statuses according to defined rules. Arbitrary status changes are forbidden.

3. **Supersession is explicit.** When a document is replaced, the supersession relationship is recorded in both the old and new document. Orphaned superseded documents are non-compliant.

4. **Staleness is actionable.** A stale document is not merely outdated — it is a governance finding that requires repair, supersession, or archival.

5. **Traceability is mandatory.** Every status change must be attributable to a specific trigger, workflow step, or reconciliation action.

## Inventory Status Model

The codebase inventory tracks the status of every documented file in the repository.

### Inventory Statuses

| Status | Meaning | Transition |
|---|---|---|
| `active` | The documented file exists and the documentation is current | Default for new entries |
| `stale` | The documented file exists but the documentation is outdated | Detected by `40_documentation_sync_v1` or `validate_codebase_docs` |
| `superseded` | The documented file has been replaced by another | Requires supersession link |
| `archived` | The documented file no longer exists in the codebase | Requires removal from active inventory |
| `missing` | The inventory references a file that does not exist | Detected by `scan_repo_codebase`; requires investigation |

### Inventory Status Transitions

```
(new) → active
active → stale (when code changes without doc update)
active → superseded (when replaced by another document)
active → archived (when the source file is removed)
stale → active (when documentation is repaired)
stale → superseded (when the document is replaced rather than repaired)
superseded → archived (when the superseding document is also removed)
missing → active (when the file is restored)
missing → archived (when the file is confirmed removed)
```

### Forbidden Inventory Transitions

- `archived → active` (archived is terminal; create a new entry)
- `superseded → active` (superseded documents do not become active again)
- `stale → missing` (a stale document's source file still exists)

## Document Status Model

Each codebase document carries its own status in frontmatter.

### Document Statuses

| Status | Meaning | Required Action |
|---|---|---|
| `active` | Document is current and accurate | None |
| `stale` | Document does not match current code | Repair or supersede |
| `superseded` | Document has been replaced | Link to replacement |
| `archived` | Document is no longer relevant | Move to archive |
| `draft` | Document is being authored | Complete and activate |

### Document Status Transitions

```
(new) → draft
draft → active (when approved)
active → stale (when code changes without doc update)
active → superseded (when replaced)
stale → active (when repaired)
stale → superseded (when replaced rather than repaired)
superseded → archived (when no longer needed for reference)
draft → archived (when abandoned)
```

### Document Status in Frontmatter

```yaml
---
status: active
last_updated: 2026-07-04
superseded_by: null
supersedes: null
---
```

When a document is superseded:

```yaml
---
status: superseded
last_updated: 2026-06-01
superseded_by: docs/codebase/02_modules/new_module_v2.md
---
```

## Supersession Rules

### Supersession Protocol

1. **Create the replacement document** with `status: active` and `supersedes: <old_path>`
2. **Update the old document** with `status: superseded` and `superseded_by: <new_path>`
3. **Update the inventory** to reference the new document
4. **Record the supersession** in the change record (`docs/codebase/04_changes/`)

### Supersession Constraints

- A document can supersede at most one prior document (1:1 relationship)
- A document can be superseded by at most one replacement (1:1 relationship)
- Circular supersession is forbidden (A supersedes B supersedes A)
- Superseded documents MUST NOT be deleted — they remain for historical reference
- Superseded documents MUST carry a link to their replacement

### Supersession Detection

`40_documentation_sync_v1` detects situations requiring supersession:
- A document describes a module that has been fundamentally restructured
- A document's information is so outdated that repair is impractical
- A module has been split into multiple modules, requiring multiple replacement documents

## Update Triggers

### Mandatory Update Triggers

The following events MUST trigger a codebase documentation update:

1. **Public API change**: Function signatures, class interfaces, or module exports change
2. **Configuration change**: Required config keys change, defaults change, or new keys are added
3. **Architecture change**: Module boundaries shift, new modules are added, modules are removed
4. **Workflow change**: New workflow families are added or existing ones change structure
5. **Dependency change**: New dependencies are added or existing ones removed (the runner is intentionally dep-free — any dependency addition is significant)
6. **Sidecar schema change**: The `meta.json` schema evolves

### Discretionary Update Triggers

The following events MAY trigger a documentation update:

1. **Internal refactor**: Code reorganized without API change — doc review recommended
2. **Test additions**: New tests may warrant module doc updates if they reveal new behavior
3. **Documentation improvements**: Typos, clarity improvements, formatting fixes

### Update Trigger Enforcement

- `20_initiative_intake_v1` captures which triggers are active for the initiative
- `30_delivery_planning_v1` converts triggers into task-level documentation obligations
- `31_task_execution_v1` executes the documentation updates
- `40_documentation_sync_v1` detects triggers that were missed

## Traceability

### Required Traceability

Every codebase documentation update MUST be traceable to:
1. The code change that triggered the update
2. The task that executed the update
3. The delivery that contained the task
4. The initiative that scoped the delivery

### Change Records

Significant documentation changes are recorded in `docs/codebase/04_changes/`:
- Module restructuring
- Supersession events
- New module documentation
- Inventory reconciliation results

### Inventory Traceability

The codebase inventory (`docs/codebase/01_inventory/codebase_inventory.md`) records:
- When each entry was created
- When each entry was last updated
- Which delivery cycle last touched the entry
- The current status of the entry

## Removal Rules

### When Documents May Be Removed

Codebase documents are rarely removed. Removal is permitted only when:

1. **The source file no longer exists** AND the document has been archived
2. **The document is superseded** AND the superseding document is complete
3. **The document describes a feature that has been permanently removed** AND no historical reference value remains

### Removal Protocol

1. **Archive first**: Move the document to `archived` status
2. **Update inventory**: Remove or archive the inventory entry
3. **Record the removal**: Create a change record in `docs/codebase/04_changes/`
4. **Validate**: Ensure no other documents reference the removed document

### Protected Document Removal

Workflow-generated documents (`managed_by: workflow-generated`) MUST NOT be manually removed. They can only be:
- Regenerated by a workflow re-run
- Superseded by a newer version from the same workflow
- Archived by the workflow that manages them

### Forbidden Removals

- Removing a document to hide stale content (supersede or repair instead)
- Removing a superseded document that still has reference value
- Removing any document without a change record
- Removing a document that is referenced by other active documents
