---
title: Codebase Inventory Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: CODEBASE-INV-TEMPLATE-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Inventory Template

> Artifact key: `CODEBASE_INVENTORY_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `CODEBASE-INV-TEMPLATE-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for codebase inventory entries. Every inventory instance must conform to this structure. The inventory covers all source file types and supports four defined statuses.

---

## Template Fields

Every inventory entry MUST include the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Stable, unique identifier for the inventory entry |
| `path` | string | yes | Repository-relative path to the file or module |
| `file_type` | enum | yes | One of the supported file types (see File Type Coverage) |
| `status` | enum | yes | One of: `current`, `needs_update`, `pending_review`, `superseded` |
| `owner_doc_path` | string | yes | Path to the documentation file that owns/reference this entry |
| `documentation_mode` | enum | yes | One of: `documented`, `inventoried_only`, `protected`, `not_applicable` |
| `last_verified_by_change` | string | yes | The commit SHA, change ID, or date when this entry was last verified as accurate |
| `description` | string | yes | Brief description of the file/module's role |
| `profile_metadata` | object | conditional | Architecture profile information (populated when a change introduces or replaces a declared architecture standard) |

### Conditional Fields

| Field | Type | When Required | Description |
|---|---|---|---|
| `profile_metadata.current_profile` | string | When profile is declared or changing | The architecture profile this file belongs to |
| `profile_metadata.target_profile` | string | When profile is changing | The target architecture profile |
| `profile_metadata.migration_mode` | string | When profile is changing | `active` / `greenfield` / `brownfield` / `n/a` |
| `superseded_by` | string | When status is `superseded` | Path or ID of the replacing entry |
| `stale_reason` | string | When status is `needs_update` | Reason the entry is stale |
| `review_notes` | string | When status is `pending_review` | Notes for the reviewer |

---

## Entry Template

```yaml
- id: "{ENTRY_ID}"
  path: "{REPO_RELATIVE_PATH}"
  file_type: "{FILE_TYPE}"
  status: "{STATUS}"
  owner_doc_path: "{OWNER_DOC_PATH}"
  documentation_mode: "{MODE}"
  last_verified_by_change: "{CHANGE_ID_OR_DATE}"
  description: "{DESCRIPTION}"
  profile_metadata:  # Optional — populate when profile is declared or changing
    current_profile: "{CURRENT_PROFILE}"
    target_profile: "{TARGET_PROFILE}"
    migration_mode: "{MIGRATION_MODE}"
```

---

## Status Definitions

| Status | Definition | Transition Rules |
|---|---|---|
| `current` | The entry accurately reflects the current state of the code. The corresponding documentation (if any) is up to date. | May transition to `needs_update` when code changes; may transition to `superseded` when replaced. |
| `needs_update` | The code has changed since the entry was last verified, and the entry no longer accurately reflects the current state. | Must transition to `current` after documentation is updated, or to `pending_review` if the change is ambiguous. |
| `pending_review` | The entry may or may not be stale; it requires human or agent review to determine its accuracy. | Must transition to `current`, `needs_update`, or `superseded` after review. |
| `superseded` | The entry has been replaced by a newer entry. The file may still exist but is no longer tracked by this entry. | Terminal state. May transition back to `current` only if the superseding entry is itself invalidated. |

---

## File Type Coverage

The inventory MUST cover all source file types discovered in the repository:

| File Type | Extension / Pattern | Inventory Behavior | Documentation Mode |
|---|---|---|---|
| Python module | `*.py` | Full entry with description | `documented` (module doc in `docs/codebase/02_modules/`) |
| JSON config | `*.json` (e.g., `config.json`, `meta.json`, `bundle_map.json`) | Entry with description | `inventoried_only` |
| Prompt template | `*.txt` under `bootstrap/workflows/*/prompts/` | Entry with description | `inventoried_only` |
| Batch script | `*.bat`, `*.ps1` | Entry with description | `inventoried_only` |
| Markdown context | `*.md` (e.g., `QWEN.md`, `README.md`, `MANIFEST.in`) | Entry with description | `inventoried_only` or `protected` |
| Architecture-site output | `docs/system/02_architecture_site/**` | Entry with description | `protected` |
| Package metadata | `pyproject.toml`, `MANIFEST.in`, `setup.cfg` | Entry with description | `inventoried_only` |
| Test file | `test_*.py`, `*_test.py` | Entry with description | `inventoried_only` |
| Init module | `__init__.py` | Entry with description | `inventoried_only` |
| Other source | Any other source file | Entry with description | `inventoried_only` or `not_applicable` |

---

## Notes

- The live codebase inventory (`docs/codebase/01_inventory/codebase_inventory.md`) MUST use `template_id: CODEBASE-INV-v1` (registry-aligned), not the legacy `CB-01` marker.
- The `profile_metadata` block is conditional — it MUST be populated when a change introduces or replaces a declared architecture standard, and MAY be omitted otherwise.
- Every entry MUST have a `last_verified_by_change` field — this is the primary mechanism for detecting staleness.
