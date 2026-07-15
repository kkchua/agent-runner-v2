# CLAUDE.md

<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->

- Bundle: `00_layer1_governance_bootstrap_v1`
- Label: 00_layer1_governance_bootstrap_v1
- Canonical source: `bundle_governance\core_governance.md`
- Governance manifest: `bundle_governance.toml`

## Canonical Guidance

# Layer 1 Governance Bundle Contract

- This bundle owns only the four Layer 1 governance documents under `docs/system/00_governance/bootstrap/`.
- These documents define reusable ecosystem governance, not repository-local workflow inventories or SDLC-specific outputs.
- The bundle must remain generic enough to govern plugin workflow ecosystems across repositories.
- Concrete workflow identifiers, repository-specific artifact inventories, and repository-specific scaffold names must not appear in the generated Layer 1 contract text.
- Review, validation, and audit steps must enforce scope purity, deterministic ownership, and runtime governance correctness.
- Any generated review or validation artifact is supporting evidence only and must not become part of the permanent Layer 1 document set.

## Artifact Registry

| Artifact Key | Required | Path | Description |
|---|---|---|---|
| `SYSTEM_DOCS_INDEX` | yes | `docs/system/00_governance/bootstrap/README.md` | Canonical Layer 1 ecosystem documentation index. |
| `SYSTEM_DOC_STANDARD` | yes | `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | Canonical Layer 1 documentation contract. |
| `BUNDLE_TAXONOMY` | yes | `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | Canonical Layer 1 bundle taxonomy and ownership rules. |
| `RUNTIME_GOVERNANCE` | yes | `docs/system/00_governance/bootstrap/RUNTIME_GOVERNANCE.md` | Canonical Layer 1 runtime operating model. |
| `SYSTEM_DOCS_VALIDATION` | no | `docs/system/00_governance/bootstrap/<job_id>-layer1-governance-validation.md` | Deterministic validation report for Layer 1 governance checks. |
| `REVIEW_FILE_SUGGESTED` | no | `docs/system/00_governance/bootstrap/<job_id>-layer1-governance-review.md` | Reviewer or audit output used for refinement loops. |
