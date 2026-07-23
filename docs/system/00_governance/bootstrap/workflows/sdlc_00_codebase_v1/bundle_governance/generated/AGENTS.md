# AGENTS.md

<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->

- Bundle: `sdlc_00_codebase_v1`
- Label: sdlc_00_codebase_v1
- Canonical source: `bundle_governance\core_governance.md`
- Governance manifest: `bundle_governance.toml`

## Canonical Guidance

# Codebase Sync Bundle Contract

- This bundle belongs to Layer 3 and manages periodic synchronization of repository source code to codebase documentation.
- Its permanent output set is limited to the codebase inventory, change impact reports, sync logs, and publish manifests defined in the workflow.
- Layer 1 governance and Layer 2 platform core documents are out of scope for this bundle.
- Temporary review, validation, and audit artifacts are evidence only and must never be treated as permanent authority.
- Source code modules under the project root are read-only reference inputs — the workflow must not modify them.
- Staged run outputs live under `docs/repo/codebase/runs/<job_id>/`.
- Publish moves approved content into `docs/repo/codebase/current/` and records a manifest while retaining historical snapshots under `docs/repo/codebase/history/<job_id>/`.
- Backups are created under `docs/repo/codebase/backups/BACKUP-<job_id>/` before each sync cycle.
- Human approval is required at the review_sync_log step before validation and publish proceed.

## Artifact Registry

| Artifact Key | Required | Path | Description |
|---|---|---|---|
| `CODEBASE_BACKUP` | no | `docs/repo/codebase/backups/BACKUP-<job_id>/` | Pre-sync backup of codebase docs. |
| `CODEBASE_CHANGE_IMPACT` | yes | `docs/repo/codebase/runs/<job_id>/04_changes/<job_id>-reconcile.md` | Staged change impact report. |
| `CODEBASE_INVENTORY` | yes | `docs/repo/codebase/runs/<job_id>/01_inventory/codebase_inventory.md` | Staged codebase inventory. |
| `SYNC_LOG` | no | `docs/repo/codebase/runs/<job_id>/sync_logs/SYNC-<job_id>.md` | Sync operation log. |
| `REVIEW_FILE_SUGGESTED` | no | `docs/repo/codebase/runs/<job_id>/sync_logs/<job_id>-review.md` | Review output for sync log and staged docs. |
| `VALIDATION_FILE` | no | `docs/repo/codebase/runs/<job_id>/04_changes/<job_id>-reconcile-validation.md` | Deterministic validation report for staged codebase docs. |
| `CODEBASE_PUBLISH_MANIFEST` | no | `docs/repo/codebase/current/codebase_manifest.json` | Active publish manifest for the codebase docs. |
| `CODEBASE_PUBLISH_MANIFEST_HISTORY` | no | `docs/repo/codebase/history/<job_id>/codebase_manifest.json` | Historical publish manifest snapshot for audit trail. |
