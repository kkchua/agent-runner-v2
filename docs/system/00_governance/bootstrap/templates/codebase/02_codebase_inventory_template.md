---
template_id: CODEBASE-INV-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Inventory Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `CODEBASE-INV-v1` |
| **Status** | Active |
| **Generated** | 2026-07-03 |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `generate_templates` |
| **Version** | 1.0.0 |
| **Managed By** | workflow-generated |

## Template Fields

Each inventory entry uses the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| **file_path** | Yes | Relative path from repo root |
| **file_type** | Yes | Extension or category (e.g., `py`, `json`, `sh`, `md`, `txt`, `toml`) |
| **owner_doc_path** | No | Path to the owning module or component doc (e.g., `docs/codebase/02_modules/agent_runner_v2_actions.md`) |
| **documentation_mode** | Yes | `stub` / `summary` / `full` — depth of documentation |
| **status** | Yes | `current` / `needs_update` / `pending_review` / `superseded` |
| **last_verified_by_change** | No | Change record ID that last verified this entry (e.g., `CHANGE-XXXX-v1`) |
| **last_modified** | No | ISO timestamp of last source file modification |
| **doc_last_updated** | No | ISO timestamp of last documentation update |
| **repo_profile** | No | Architecture profile when applicable (e.g., `modular-monolith`, `ddd/eda`, `layered`) |
| **profile_changed_at** | No | Timestamp when profile was introduced or changed (only when change introduces new standard) |
| **migration_mode** | No | Migration mode when profile is changing (`greenfield` / `incremental` / `refactoring` / `legacy-merge`) |

## Entry Template

<!-- Template for a single inventory entry. Copy this format for each file. -->

```
| `file_path` | `file_type` | `owner_doc_path` | `documentation_mode` | `status` | `last_verified_by_change` | `last_modified` | `doc_last_updated` |
```

### Example Entry

```
| `agent_runner_v2/actions/execute_t2i.py` | `py` | `docs/codebase/02_modules/agent_runner_v2_actions.md` | `full` | `current` | `CHANGE-0001-v1` | `2026-07-03T22:00:00+08:00` | `2026-07-03T22:48:00+08:00` |
```

## Status Definitions

| Status | Meaning | Transition From | Transition To |
|--------|---------|-----------------|---------------|
| **`current`** | Documentation is up-to-date with the source code | `pending_review` (after validation) | `needs_update` (when source changes) |
| **`needs_update`** | Source code has changed; documentation is behind | `current` (when source changes) | `pending_review` (when doc is updated) |
| **`pending_review`** | Documentation has been updated; awaiting validation | `needs_update` (after doc update) | `current` (after validation) or `needs_update` (if validation fails) |
| **`superseded`** | Replaced by a newer document or no longer relevant | `current` or `needs_update` | Terminal (archived) |

### Status Lifecycle

```
[current] ──(source changes)──▶ [needs_update] ──(doc updated)──▶ [pending_review]
                                                                        │
                                              ┌─────────────────────────┘
                                              │
                                     (validation passes)
                                              │
                                              ▼
                                          [current]

[neds_update] / [current] ──(replaced)──▶ [superseded]
```

## File Type Coverage

The inventory must cover ALL source file types in the repository:

### Source Code Files

| File Type | Extension | Coverage Level |
|-----------|-----------|---------------|
| Python | `.py` | Full — every module tracked |
| JavaScript | `.js`, `.mjs` | Full |
| TypeScript | `.ts`, `.tsx` | Full |
| Shell scripts | `.sh` | Full |
| Batch scripts | `.bat` | Full |
| PowerShell | `.ps1` | Full |

### Configuration and Data Files

| File Type | Extension | Coverage Level |
|-----------|-----------|---------------|
| TOML | `.toml` | Full |
| JSON | `.json` | Full |
| YAML | `.yaml`, `.yml` | Full |
| Environment | `.env`, `.env.example` | Summary |
| Text | `.txt` | Summary |

### Workflow Files

| File Type | Extension | Coverage Level |
|-----------|-----------|---------------|
| Prompt templates | `.txt` in workflow dirs | Summary |
| Workflow JSON | `.json` in workflow dirs | Summary |
| Model mapping | `.json` | Full |

### Test Files

| File Type | Extension | Coverage Level |
|-----------|-----------|---------------|
| Python tests | `test_*.py` | Full |
| Other tests | `*_test.*` | Full |

### Documentation Files

| File Type | Extension | Coverage Level |
|-----------|-----------|---------------|
| Markdown | `.md` in `docs/` | Full |
| Markdown | `.md` at repo root | Summary |

### Other File Types

Any file type not explicitly listed above must be tracked at minimum as a **summary** entry. The inventory is comprehensive — no source file is excluded.
