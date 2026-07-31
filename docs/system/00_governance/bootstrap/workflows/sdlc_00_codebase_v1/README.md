# sdlc_00_codebase_v1 — Codebase Documentation Sync

## Purpose

Periodically scans the repository source code and syncs it into structured codebase documentation. Keeps `docs/repo/codebase/current/` up to date with inventory, module docs, and change impact reports.

**Standalone maintenance workflow** — does not feed artifacts into the sdlc_10–sdlc_80 delivery chain. Downstream workflows reference its output as read-only context.

## Prerequisites

- Layer 1 governance bootstrapped
- Layer 2 platform published

## Inputs

None. Scans the filesystem directly.

## Outputs

| Artifact | Path |
|----------|------|
| `CODEBASE_BACKUP` | `docs/repo/codebase/backups/BACKUP-<job_id>/` |
| `CODEBASE_INVENTORY` | `docs/repo/codebase/runs/<job_id>/01_inventory/` |
| `CODEBASE_CHANGE_IMPACT` | `docs/repo/codebase/runs/<job_id>/04_changes/` |
| `SYNC_LOG` | `docs/repo/codebase/runs/<job_id>/sync_logs/` |
| `VALIDATION_FILE` | `docs/repo/codebase/runs/<job_id>/` |
| Published docs | `docs/repo/codebase/current/` |
| History archive | `docs/repo/codebase/history/<job_id>/` |

## Step Sequence

| # | Step | Type | Coder | Description |
|---|------|------|-------|-------------|
| 1 | `create_backup` | Action | — | Archive previous codebase docs |
| 2 | `sync_codebase_docs` | Action | — | Scan repo, generate/update inventory + module docs |
| 3 | `generate_sync_log` | Action | — | Produce change impact report |
| 4 | `review_sync_log` | Prompt | reviewer | Review sync accuracy **[HUMAN GATE]** |
| 5 | `refine_codebase_docs` | Prompt | architect | Fix per review findings (loop → step 4, max 2) |
| 6 | `validate_codebase_docs` | Action | — | Validate frontmatter and structure |
| 7 | `publish_codebase_docs` | Action | — | Copy to `current/` with manifest |
| 8 | `commit_changes` | Action | — | Finalize |
| 9 | `stepCompletion` | Action | — | Terminal |

## How to Run

```bash
ukbe-run-agent run --template-group sdlc_00_codebase_v1
```

## When to Run

- After significant code changes (new modules, refactors, deletions)
- Periodically as part of documentation maintenance
- Before running SDLC delivery workflows that reference codebase docs
