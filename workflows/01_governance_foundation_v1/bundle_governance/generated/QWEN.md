# QWEN.md

<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->

- Bundle: `01_governance_foundation_v1`
- Label: 01_governance_foundation_v1
- Canonical source: `bundle_governance\core_governance.md`
- Governance manifest: `bundle_governance.toml`

## Canonical Guidance

# Governance Foundation Bundle Contract

- This bundle belongs to Layer 1 and may generate only governance artifacts.
- Its permanent output set is limited to the Layer 1 governance foundation documents defined in the masterplan and governance specification.
- Runtime architecture, install flow, publish mechanics, registry operations, and platform-specific operating standards are out of scope.
- Temporary review, validation, and audit artifacts are evidence only and must never be treated as permanent Layer 1 authority.
- Human-authored documents under `masterplan/` are reference inputs only and must not be rewritten by this workflow.
- Staged run outputs live under `docs/system/00_governance/foundation/runs/<job_id>/`.
- Publish moves approved content into `docs/system/00_governance/foundation/current/` and records a manifest while retaining historical snapshots.
- Prompt authoring for this bundle is governed by `bundle_governance/prompt_sop.md` and `bundle_governance/prompt_layout.md`.
- Allowed action types are governed by `bundle_governance/action_policy.md`.
- Review and audit behavior is governed by `bundle_governance/review_audit_contract.md`.
- Machine-checkable prompt constraints are declared in `bundle_governance/prompt_contract.json`.

## Artifact Registry

| Artifact Key | Required | Path | Description |
|---|---|---|---|
| `L1_FOUNDATION_INDEX` | yes | `docs/system/00_governance/foundation/runs/<job_id>/README.md` | Staged Layer 1 governance foundation index. |
| `L1_LAYER_MODEL` | yes | `docs/system/00_governance/foundation/runs/<job_id>/LAYER_MODEL.md` | Staged Layer 1 layer model document. |
| `L1_DOCUMENT_AUTHORITY` | yes | `docs/system/00_governance/foundation/runs/<job_id>/DOCUMENT_AUTHORITY.md` | Staged Layer 1 authority standard. |
| `L1_BUNDLE_TAXONOMY` | yes | `docs/system/00_governance/foundation/runs/<job_id>/BUNDLE_TAXONOMY.md` | Staged Layer 1 bundle taxonomy. |
| `L1_GOVERNANCE_LIFECYCLE` | yes | `docs/system/00_governance/foundation/runs/<job_id>/GOVERNANCE_LIFECYCLE.md` | Staged Layer 1 lifecycle standard. |
| `L1_METADATA_STANDARD` | yes | `docs/system/00_governance/foundation/runs/<job_id>/METADATA_STANDARD.md` | Staged Layer 1 metadata standard. |
| `GOVERNANCE_CONTEXT_INVENTORY` | no | `docs/system/00_governance/foundation/runs/<job_id>/<job_id>-governance-context-inventory.md` | Run-scoped governance context inventory. |
| `GOVERNANCE_FOUNDATION_VALIDATION` | no | `docs/system/00_governance/foundation/runs/<job_id>/<job_id>-governance-foundation-validation.md` | Deterministic validation report for the staged governance foundation set. |
| `REVIEW_FILE_SUGGESTED` | no | `docs/system/00_governance/foundation/runs/<job_id>/<job_id>-governance-foundation-review.md` | Review output used for refinement loops. |
| `AUDIT_FILE_SUGGESTED` | no | `docs/system/00_governance/foundation/runs/<job_id>/<job_id>-governance-foundation-audit.md` | Final semantic audit output. |
| `GOVERNANCE_PUBLISH_MANIFEST` | no | `docs/system/00_governance/foundation/current/governance_set_manifest.json` | Active publish manifest for the Layer 1 governance foundation set. |
| `GOVERNANCE_PUBLISH_MANIFEST_HISTORY` | no | `docs/system/00_governance/foundation/history/<job_id>/governance_set_manifest.json` | Historical publish manifest snapshot for audit trail. |
