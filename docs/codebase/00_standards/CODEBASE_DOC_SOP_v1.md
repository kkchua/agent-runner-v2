---
title: "Codebase Documentation SOP v1"
template_id: "CODEBASE-DOC-SOP-v1"
status: "active"
version: "1.0"
generated: "2026-07-04T07:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Codebase Documentation SOP v1

## Purpose

This Standard Operating Procedure governs how codebase documentation is created, maintained, validated, and retired across the repository. It ensures that documentation coverage stays proportional to code complexity, that stale guidance is identified and flagged, and that documentation updates are treated as first-class delivery obligations — not optional cleanup.

Codebase documentation covers:

- **Module docs** (`docs/codebase/02_modules/`) — per-module descriptions of Python modules, scripts, config files, and test files.
- **Component docs** (`docs/codebase/03_components/`) — higher-level groupings of related modules (e.g., "actions", "commands", "bootstrap").
- **Inventory** (`docs/codebase/01_inventory/`) — the master list of every tracked file and its doc status.
- **Change records** (`docs/codebase/04_changes/`) — impact analysis for significant changes.
- **Standards** (`docs/codebase/00_standards/`) — this SOP and its companion status rules.

This SOP defines the full lifecycle contract across `20_initiative_intake_v1`, `30_delivery_planning_v1`, `31_task_execution_v1`, and `40_documentation_sync_v1`.

## Coverage Model

Every file in the repository falls into one of these coverage tiers:

| Tier | Scope | Doc Required? | Granularity |
|------|-------|---------------|-------------|
| **A: Source code** | Python modules, shell scripts | Yes | Per-module in `02_modules/` |
| **B: Bootstrap artifacts** | Workflow templates, prompts, mappings | Yes | Per-directory grouping in `03_components/`, key files in `02_modules/` |
| **C: Configuration** | `pyproject.toml`, `.gitignore`, etc. | Yes | Per-file in `02_modules/` |
| **D: Tests** | Test modules | Yes | Per-file in `02_modules/` |
| **E: Documentation** | `.md` files under `docs/` | Tracked in inventory only | No separate doc required |
| **F: Generated/binary** | Compiled artifacts, vendored deps | Excluded | Not tracked |

**Completeness rule:** Every file in tiers A-D must appear in the inventory (`docs/codebase/01_inventory/codebase_inventory.md`) and have either a stub, summary, or full doc in `02_modules/` or `03_components/`.

### Coverage Depth Modes

Each documented file operates at one of three depth modes, chosen by complexity:

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Stub** | One-line summary, imports only | Trivial files (re-exports, `__init__.py`) |
| **Summary** | Function signatures + one-line descriptions | Medium-complexity files (3-10 functions, simple logic) |
| **Full** | Detailed descriptions of every function/class, parameter semantics, side effects, call relationships | High-complexity files (workflow orchestration, state management, cross-cutting concerns) |

## Documentation Modes

### Creation Mode

Documentation is created when:

1. A new source file is added to the repository (during `31_task_execution_v1` execution phase).
2. A new component grouping emerges (multiple modules share a logical concern).
3. A bootstrap workflow is added or modified.

Creation rules:

- New files go into the inventory with status `active`.
- A doc file is created in `02_modules/` or `03_components/` at the appropriate depth mode.
- The doc must reference the source file path and its coverage tier.
- Creation is part of the delivery task's acceptance criteria.

### Update Mode

Documentation is updated when:

1. Source code changes affect documented functions, classes, or module responsibilities.
2. New imports introduce new cross-module dependencies.
3. Parameter signatures change (addition, removal, rename).
4. Behavioral changes make existing descriptions inaccurate.

Update rules:

- The update is triggered by the same delivery task that modifies the source code.
- The codebase doc update is part of the task's acceptance criteria.
- If the doc cannot be updated in the current cycle, it is flagged as `stale_pending` in the inventory.
- The reviewer verifies that doc updates match the code changes (accuracy, not just existence).

### Review Mode

Documentation is reviewed when:

1. The `40_documentation_sync_v1` workflow runs (scheduled or on-demand).
2. A reviewer detects potential staleness during a delivery review.

Review rules:

- The review compares the documented description against the actual source code.
- Discrepancies are flagged in the inventory and a change record is created.
- Stale docs are not auto-corrected; they are flagged for a future delivery task.
- Critical stale guidance (active misdirection) triggers emergency correction.

### Retirement Mode

Documentation is retired when:

1. The source file is deleted or moved.
2. The module is merged into another module.
3. The file is downgraded to tier F (generated/binary).

Retirement rules:

- The doc file is **not deleted**. It is renamed with a `.superseded` suffix and its frontmatter status is set to `superseded`.
- The inventory entry status changes to `superseded` with a pointer to the replacement (if any).
- A superseded doc is never reactivated. If the source returns, a new doc is created.

## Freshness Rules

| Rule | Description |
|------|-------------|
| **Co-change rule** | If a source file changes, its documentation must be updated in the same delivery task. Delayed updates are `stale_pending`. |
| **Sync-cycle rule** | The `40_documentation_sync_v1` workflow must run at least once per sprint (or per delivery milestone) to catch any missed co-change updates. |
| **Staleness threshold** | Documentation that has not been verified against current code in the last 30 days is marked `stale_pending` in the inventory. |
| **Impact propagation** | When a module that is imported by other modules changes, all importing modules' docs must be checked for stale cross-reference info. |
| **Bootstrap freeze** | Bootstrap workflow templates are immutable at runtime. Doc updates to bootstrap files only occur when the repo bootstrap source changes, not when runtime bundles change. |
| **Emergency correction** | Critical stale guidance (active misdirection) must be corrected immediately, bypassing normal initiative flow but still requiring a change record and sidecar. |

## Stale Content Policy

| Severity | Definition | Action |
|----------|-----------|--------|
| **Critical** | Doc describes behavior that the code no longer performs (active misdirection) | Immediate correction via emergency task |
| **High** | Doc omits a significant function, class, or parameter | Correction in next delivery cycle |
| **Medium** | Doc has outdated examples or imprecise descriptions | Correction within current sprint |
| **Low** | Doc has minor formatting issues or outdated references | Correction in next sync cycle |

**Emergency correction** bypasses the normal initiative→plan→task flow but still requires:

1. A minimal change record in `docs/codebase/04_changes/`.
2. A `meta.json` sidecar confirming the correction.
3. Inventory update to reflect the corrected status.

## Ecosystem Baseline

Codebase documentation operates within the same ecosystem baseline as the delivery lifecycle. The universal baseline applies to every repository; repo-selected profiles and migration modes refine how documentation coverage and depth are applied.

### Universal Baseline

The following codebase documentation rules apply to every governed repository, regardless of domain, size, or technology:

1. **Coverage completeness.** Every source file (tiers A-D) appears in the inventory with an explicit status. No file is undocumented.
2. **Three depth modes.** Each documented file uses stub, summary, or full depth based on complexity. Trivial files (re-exports, `__init__.py`) use stub; complex modules use full.
3. **Co-change rule.** Source file changes trigger documentation updates in the same delivery task.
4. **Supersession over deletion.** Doc files are never deleted. Replaced docs are renamed with `.superseded` suffix and marked in inventory.
5. **Freshness enforcement.** Stale docs beyond 30 days are flagged. Critical misdirection triggers emergency correction.
6. **Impact propagation.** When a module with importers changes, all importing modules' docs are checked for stale cross-references.
7. **Bootstrap freeze.** Bootstrap workflow templates are immutable at runtime. Doc updates only occur when the repo bootstrap source changes.

### Repo-Selected Architecture Profile

When a repository selects an architecture profile (see `WORKFLOW_SOP_v1.md` / Ecosystem Baseline), the codebase documentation model extends accordingly:

| Profile | Documentation Extension |
|---------|------------------------|
| **none** (default) | Universal baseline only. No architecture-specific docs required. |
| **ddd** | Aggregate docs required for each bounded context; ubiquitous vocabulary section in component docs |
| **eda** | Event catalog in component docs; producer/consumer mapping per event type |
| **layered** | Layer membership declared in every module doc; layer violation flagged by reviewer |
| **clean** | Domain vs. adapter boundary declared in module docs; adapter interfaces documented |

**Important:** These profile-specific documentation requirements are **conditional**, not universal. A repository without an explicit profile selection has no architecture-specific documentation obligations beyond the universal baseline. DDD, EDA, and similar architecture documentation standards are conditional profile choices, not universal defaults.

### Migration Mode

Migration mode affects how the codebase documentation lifecycle handles transitional documentation states:

| Mode | Effect on Documentation |
|------|------------------------|
| **none** (default) | Standard lifecycle. No special documentation handling. |
| **bootstrap** | Initial full inventory scan and doc generation; all files get docs at appropriate depth |
| **format-migration** | Workflow bundle format docs regenerated after each sync; legacy format docs marked superseded |
| **docs-reconciliation** | Continuous drift detection; all flagged docs batched into remediation initiatives |

### Conditional Standards

The following documentation standards are **not** part of the universal baseline. They apply only when explicitly selected via architecture profile, migration mode, or repo-specific governance extension:

- Aggregate boundary documentation (DDD profile only)
- Event schema and catalog documentation (EDA profile only)
- Layer membership declarations (layered profile only)
- Domain/adapter boundary declarations (clean profile only)
- Continuous reconciliation scanning (docs-reconciliation migration mode only)

## Workflow Integration

The codebase documentation lifecycle integrates with the delivery workflow families at four points. This defines the full lifecycle contract across all four workflow families.

### `20_initiative_intake_v1` — Capture Documentation Scope and Stale-Guidance Risk

When an initiative is captured, it must identify:

- Which source files will change? (maps to modules/components)
- Which existing docs reference those files?
- Which existing docs contain guidance that may become stale if the change proceeds?
- What is the stale-guidance risk level for each affected doc?

The initiative document includes a **Documentation Scope** section listing all affected doc files and their stale-guidance risk level. This scope becomes the input for the planning phase.

**Key obligations:**
- Documentation scope is mandatory for every initiative.
- Stale-guidance risk must be assessed for every affected doc.
- If no source files change, documentation scope may be empty, but this must be explicitly stated.

### `30_delivery_planning_v1` — Convert Documentation Scope into Plan/Task Obligations

The planning phase converts the documentation scope from the initiative into concrete obligations:

- Each task that modifies source code must include a **Documentation Update** subtask.
- The task spec's acceptance criteria must include "all affected codebase docs updated and validated."
- If the plan introduces new modules or components, the task-graph includes doc-creation obligations.
- Plan-level documentation obligations summarize the aggregate doc-update work across all tasks.

**Key obligations:**
- Documentation obligations are first-class tasks, not afterthoughts.
- Tasks that modify code without doc-update obligations are incomplete.
- The plan must account for impact propagation (importers of changed modules).

### `31_task_execution_v1` — Execute and Validate Codebase Documentation Updates as Part of Task Completion

During task execution:

- The executor updates all codebase docs identified in the task's doc-update obligations.
- The reviewer verifies that doc updates match the code changes (not just that they exist, but that they are accurate).
- The validator confirms that no affected doc was left unupdated.
- If a doc cannot be updated (complexity, uncertainty), it is flagged as `stale_pending` and the memory record documents the gap.

**Key obligations:**
- Documentation updates are part of the task's acceptance criteria.
- A task is not complete until its documentation obligations are fulfilled or explicitly flagged.
- The reviewer checks documentation accuracy, not just existence.
- The validator runs structural checks on updated docs (frontmatter, cross-references).

### `40_documentation_sync_v1` — Reconcile Current Code Against Active Documentation and Flag Stale Guidance

The documentation sync workflow is the **single source of truth for current-state reconciliation**:

1. **Scan** — walks all source files in the repository and compares against the inventory.
2. **Detect** — identifies missing docs (new files without docs), orphaned docs (docs for deleted files), and stale docs (docs that don't match current source).
3. **Report** — produces a drift report listing all discrepancies with severity levels.
4. **Flag** — updates inventory entries to `stale_pending` for docs that need correction.
5. **Reconcile** — does **not** auto-correct docs. It identifies gaps and flags them for delivery tasks.

**Key obligations:**
- `40_documentation_sync_v1` is the single current-truth synchronization workflow.
- No other workflow may perform current-truth synchronization.
- The sync must cover all tiers A-D in the coverage model.
- The drift report must include counts for missing, orphaned, and stale docs.
- System docs and operations guidance are included in the sync scope.

## File-Type Rules

| File Type | Doc Location | Depth Mode Default | Notes |
|-----------|-------------|--------------------|-------|
| Python module (`.py`) | `02_modules/` | Summary or Full | Based on complexity |
| Shell script (`.bat`, `.sh`) | `02_modules/` | Stub or Summary | Usually simple |
| Workflow prompt (`.txt`) | `03_components/` (workflow-families) | Summary | Grouped by workflow family |
| Workflow mapping (`.json`) | `03_components/` (workflow-families) | Stub | Structure-only |
| Config file (`.toml`, `.yaml`, `.json`) | `02_modules/` | Stub | Purpose + key fields |
| Test file (`test_*.py`) | `02_modules/` | Summary | Test categories and coverage |
| Markdown doc (`.md`) | Inventory only | N/A | Tracked, no separate doc |
| `__init__.py` | `02_modules/` | Stub | Package purpose only |
| Generated binary/artifact | Not tracked | N/A | Tier F exclusion |

## Validation

### Inventory Validation

The inventory file must satisfy:

1. Every file in tiers A-D appears exactly once.
2. Every entry has a `status` field (`active`, `superseded`, `stale_pending`, `missing`, `orphaned`).
3. Every `active` entry references an existing doc file in `02_modules/` or `03_components/`.
4. No `superseded` entry points to a non-existent file without a supersession pointer.
5. Every `missing` entry has a corresponding source file that exists but lacks documentation.
6. Every `orphaned` entry has a doc file whose source no longer exists.

### Doc File Validation

Every codebase doc file must satisfy:

1. Frontmatter contains `title`, `status`, `doc_type` (`module` or `component`), `source_path`.
2. The `managed_by: workflow-generated` field is present for generated docs.
3. The file contains at minimum: a description paragraph, a summary of key functions/classes, and a notes section.
4. Cross-references to other docs use relative paths that resolve.
5. The doc file status matches the corresponding inventory entry status.

### Sync Validation

After `40_documentation_sync_v1` runs, the drift report must:

1. List all missing docs (source file exists, no doc).
2. List all orphaned docs (doc exists, source file missing).
3. List all stale docs (doc exists but description mismatches source).
4. Include counts for each category.
5. Identify any critical stale guidance requiring emergency correction.
6. Cover system docs (`docs/system/`) and operations guidance (`docs/delivery/`) in addition to codebase docs.

### Workflow Integration Validation

The following cross-workflow validations are enforced:

| Validation | Method | Pass Criteria |
|------------|--------|---------------|
| Initiative has documentation scope | `validate_delivery_docs` | Documentation Scope section present with risk levels |
| Plan converts scope to obligations | `validate_delivery_docs` | Plan references initiative's doc scope; tasks have doc-update subtasks |
| Task execution includes doc updates | `validate_delivery_docs` | Doc updates present for all tasks with code changes |
| Sync produces drift report | `validate_delivery_docs` | Drift report with counts and severity levels |
