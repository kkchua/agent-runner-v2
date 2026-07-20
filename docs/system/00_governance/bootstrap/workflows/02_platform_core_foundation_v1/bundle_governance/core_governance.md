# Platform Core Foundation Bundle Contract

- This bundle belongs to Layer 2 and may generate only platform core artifacts for agent-runner-v2.
- Its permanent output set is limited to the Layer 2 platform constitution documents defined in the masterplan and platform core specification.
- Layer 1 governance redefinition, Layer 3 bundle-specific drift, and operational bootstrap mechanics are out of scope.
- Temporary review, validation, and audit artifacts are evidence only and must never be treated as permanent Layer 2 authority.
- Human-authored documents under `masterplan/` are reference inputs only and must not be rewritten by this workflow.
- Source code modules (runtime context, coder registry, constants, daemon, etc.) are read-only reference inputs — the workflow must not modify them.
- Staged run outputs live under `docs/system/00_governance/platform/runs/<job_id>/`.
- Publish moves approved content into `docs/system/00_governance/platform/current/` and records a manifest while retaining historical snapshots.
- Prompt authoring for this bundle is governed by `bundle_governance/prompt_sop.md` and `bundle_governance/prompt_layout.md`.
- Allowed action types are governed by `bundle_governance/action_policy.md`.
- Review and audit behavior is governed by `bundle_governance/review_audit_contract.md`.
- Machine-checkable prompt constraints are declared in `bundle_governance/prompt_contract.json`.
