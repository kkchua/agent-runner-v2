# Layer 1 Governance Bundle Contract

- This bundle owns only the four Layer 1 governance documents under `docs/system/00_governance/bootstrap/`.
- These documents define reusable ecosystem governance, not repository-local workflow inventories or SDLC-specific outputs.
- The bundle must remain generic enough to govern plugin workflow ecosystems across repositories.
- Concrete workflow identifiers, repository-specific artifact inventories, and repository-specific scaffold names must not appear in the generated Layer 1 contract text.
- Review, validation, and audit steps must enforce scope purity, deterministic ownership, and runtime governance correctness.
- Any generated review or validation artifact is supporting evidence only and must not become part of the permanent Layer 1 document set.
- Prompt authoring for this bundle is governed by `bundle_governance/prompt_sop.md` and `bundle_governance/prompt_layout.md`.
- Prompt contract checks are declared in `bundle_governance/prompt_contract.json` and are enforced by the shared workflow bundle validator when present.
