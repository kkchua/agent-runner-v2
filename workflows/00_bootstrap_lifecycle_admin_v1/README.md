# 00_bootstrap_lifecycle_admin_v1 — Bootstrap Lifecycle Admin (BCS-compliant)

## Purpose

Validates workflow bundle integrity, publishes the bootstrap runtime package from repo source of truth, initializes the global runner home, and syncs workflow definitions to the backend. This is the **infrastructure workflow** for bootstrapping the agent-runner platform.

## Prerequisites

- Repository contains valid workflow bundles under `workflows/`
- Bootstrap source docs exist at `docs/system/00_governance/bootstrap/`

## Inputs

| Artifact | Source | Description |
|----------|--------|-------------|
| *(none)* | — | This workflow operates on repo state, not input artifacts |

## Outputs

| Artifact | Path |
|----------|------|
| `BOOTSTRAP_SUMMARY` | `docs/system/00_governance/bootstrap/{job_id}-bootstrap-lifecycle-summary.md` |

## Step Sequence

| # | Step | Type | Description |
|---|------|------|-------------|
| 1 | `validate_bootstrap_lifecycle_sources` | Action | Validate workflow bundle integrity and bootstrap docs |
| 2 | `publish_bootstrap_lifecycle_bundle` | Action | Rebuild packaged bootstrap from repo source of truth |
| 3 | `init_bootstrap_lifecycle_workspace` | Action | Initialize global runner home from packaged bootstrap |
| 4 | `sync_workflow_definitions` | Action | Sync workflow definitions to backend |
| 5 | `write_bootstrap_lifecycle_summary` | Action | Write lifecycle summary report |
| 6 | `stepCompletion` | Action | Terminal |

## Implementations

| Name | Label | Description |
|------|-------|-------------|
| `standard` | Standard | Validates, publishes, and initializes the bootstrap runtime package |

## How to Run

```bash
ukbe-run-agent run --template-group 00_bootstrap_lifecycle_admin_v1
```
