# QWEN.md

<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->

- Bundle: `00_core_governance_bootstrap_v1`
- Label: 00_core_governance_bootstrap_v1
- Canonical source: `bundle_governance\core_governance.md`
- Governance manifest: `bundle_governance.toml`

## Canonical Guidance

# Core Governance Bundle Contract

This workflow bundle owns only ecosystem-level governance for the agent-runner documentation model.

## Scope

- Govern the universal documentation contract for the agent-runner ecosystem.
- Govern the three-layer documentation model:
  - ecosystem master docs define universal rules
  - workflow bundle master docs travel with each installed bundle in the global runner home
  - repo-local generated docs live under `docs/repo/*`
- Govern only the four canonical ecosystem master docs under `docs/system/00_governance/bootstrap/`.

## Non-Scope

- Do not classify repo-derived analysis as core governance.
- Do not treat codebase scans, system overviews, audience outputs, or delivery run state as canonical governance.
- Do not claim ownership of repo-local outputs under `docs/repo/*`.
- Do not mutate unrelated root guidance files as part of this bundle.

## Operational Rules

- The canonical source of truth for this bundle is its workflow-owned governance manifest plus this document.
- Bundle-local agent adapter files are generated from this canonical source and must not drift independently.
- During publish or install, the generated adapter files must travel with the bundle into the global runner home.
- When prompt instructions conflict with repo-local stale docs, this bundle contract wins.

## Enabled Extensions

### Artifact Registry Rules

This bundle's owned artifact set is limited to the four core governance documents plus deterministic review and validation outputs used by its own loop.

Reject any interpretation that expands ownership into repo bootstrap analysis, codebase scans, delivery outputs, or audience documentation.

The artifact registry is authoritative for bundle scope checks, publish/install packaging, and prompt-time instruction alignment.

### Review and Recovery Rules

Review and audit steps must compare the generated governance docs against both the workflow prompt requirements and the actual repository structure.

When a reviewer rejects the docs, refinement must update only the owned core governance files and then return to the deterministic review path.

Validation is deterministic and should fail fast on ownership drift, stale mixed-doc assumptions, or bundle taxonomy mistakes before the final audit approves accuracy.

## Artifact Registry

| Artifact Key | Required | Path | Description |
|---|---|---|---|
| `SYSTEM_DOCS_INDEX` | yes | `docs/system/00_governance/bootstrap/README.md` | Canonical ecosystem documentation index. |
| `SYSTEM_DOC_STANDARD` | yes | `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | Canonical documentation contract for ecosystem governance. |
| `BUNDLE_TAXONOMY` | yes | `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | Canonical bundle taxonomy and ownership rules. |
| `RUNTIME_GOVERNANCE` | yes | `docs/system/00_governance/bootstrap/RUNTIME_GOVERNANCE.md` | Canonical runtime operating model for Layer 1 ecosystem governance. |
| `SYSTEM_DOCS_VALIDATION` | no | `docs/system/00_governance/bootstrap/<job_id>-core-governance-validation.md` | Deterministic validation report for core governance checks. |
| `REVIEW_FILE_SUGGESTED` | no | `docs/system/00_governance/bootstrap/<job_id>-core-governance-review.md` | Deterministic reviewer or audit output used for refinement loops. |
