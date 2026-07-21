# QWEN.md

<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->

- Bundle: `02_agent_runner_platform_v1`
- Label: 02_agent_runner_platform_v1
- Canonical source: `bundle_governance\core_governance.md`
- Governance manifest: `bundle_governance.toml`

## Canonical Guidance

# Platform Core Foundation Bundle Contract

- This bundle belongs to Layer 2 and may generate only platform core artifacts for agent-runner-v2.
- Its permanent output set is limited to the Layer 2 platform constitution documents defined in the masterplan and platform core specification.
- Layer 1 governance redefinition, Layer 3 bundle-specific drift, and operational bootstrap mechanics are out of scope.
- Temporary review, validation, and audit artifacts are evidence only and must never be treated as permanent Layer 2 authority.
- Human-authored documents under `masterplan/` are reference inputs only and must not be rewritten by this workflow.
- Source code modules (runtime context, coder registry, constants, daemon, etc.) are read-only reference inputs — the workflow must not modify them.
- Staged run outputs live under `docs/system/00_governance/platform/agent_runner/runs/<job_id>/`.
- Publish moves approved content into `docs/system/00_governance/platform/agent_runner/current/` and records a manifest while retaining historical snapshots.
- Prompt authoring for this bundle is governed by `bundle_governance/prompt_sop.md` and `bundle_governance/prompt_layout.md`.
- Allowed action types are governed by `bundle_governance/action_policy.md`.
- Review and audit behavior is governed by `bundle_governance/review_audit_contract.md`.
- Machine-checkable prompt constraints are declared in `bundle_governance/prompt_contract.json`.

## Artifact Registry

| Artifact Key | Required | Path | Description |
|---|---|---|---|
| `L2_PLATFORM_INDEX` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/README.md` | Staged Layer 2 platform core index. |
| `L2_RUNTIME_MODEL` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/RUNTIME_MODEL.md` | Staged Layer 2 runtime model document. |
| `L2_BUNDLE_AUTHORING_CONTRACT` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/BUNDLE_AUTHORING_CONTRACT.md` | Staged Layer 2 bundle authoring contract. |
| `L2_SHARED_SERVICES` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/SHARED_SERVICES.md` | Staged Layer 2 shared services document. |
| `L2_METADATA_CONTRACT` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/METADATA_CONTRACT.md` | Staged Layer 2 metadata contract. |
| `L2_VALIDATION_CONTRACT` | yes | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/VALIDATION_CONTRACT.md` | Staged Layer 2 validation contract. |
| `PLATFORM_CONTEXT_INVENTORY` | no | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/<job_id>-platform-context-inventory.md` | Run-scoped platform context inventory. |
| `PLATFORM_CORE_VALIDATION` | no | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/<job_id>-platform-core-validation.md` | Deterministic validation report for the staged platform core set. |
| `REVIEW_FILE_SUGGESTED` | no | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/<job_id>-platform-core-review.md` | Review output used for refinement loops. |
| `AUDIT_FILE_SUGGESTED` | no | `docs/system/00_governance/platform/agent_runner/runs/<job_id>/<job_id>-platform-core-audit.md` | Final semantic audit output. |
| `PLATFORM_PUBLISH_MANIFEST` | no | `docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json` | Active publish manifest for the Layer 2 platform core set. |
| `PLATFORM_PUBLISH_MANIFEST_HISTORY` | no | `docs/system/00_governance/platform/agent_runner/history/<job_id>/platform_set_manifest.json` | Historical publish manifest snapshot for audit trail. |
