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
