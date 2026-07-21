# Masterplan Index &amp; Implementation Status

## Status Definitions

| Status | Meaning |
|---|---|
| **Draft** | Written but not yet reviewed or accepted as the target design. |
| **Confirmed** | Reviewed and accepted as the authoritative design. Ready for implementation. |
| **Implemented** | Workflow package built, synced to backend, and running. |

---

## Specs

| Document | Layer | Status |
|---|---|---|
| [LAYER_ARCHITECTURE_MASTERPLAN.md](LAYER_ARCHITECTURE_MASTERPLAN.md) | All | **Confirmed** |
| [LAYER1_GOVERNANCE_SPECIFICATION.md](LAYER1_GOVERNANCE_SPECIFICATION.md) | Layer 1 | **Confirmed** |
| [LAYER2_PLATFORM_CORE_SPECIFICATION.md](LAYER2_PLATFORM_CORE_SPECIFICATION.md) | Layer 2 | **Implemented** |

---

## Workflows

| Workflow | Layer | Status | Notes |
|---|---|---|---|
| `01_governance_foundation_v1` | Layer 1 | **Implemented** | Shipped in v0.4.0. Produces the active Layer 1 governance set. |
| `02_platform_core_foundation_v1` | Layer 2 | **Implemented** | Shipped in v0.4.0 (post-release). Produces the active Layer 2 platform constitution for agent-runner-v2. |
| `00_bootstrap_lifecycle_admin_v1` | Layer 3 | **Implemented** | Shipped in v0.4.0. Validates, publishes, inits, and syncs bootstrap workflows. |
| `00_repo_master_docs_bootstrap_v1` | Layer 3 | **Implemented** | Legacy workflow. Generates repo-level codebase and governance docs. |

---

## Future

- Additional Layer 3 workflow bundles (TBD)
- Layer 2 spec de-hardcoded from `agent-runner-v2` to `{PLATFORM}` for reuse across other platforms
