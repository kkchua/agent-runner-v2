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
