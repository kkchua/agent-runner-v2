# 🧠 Initiative

## 📌 Metadata
- Doc Type: 01_initiative
- Template Version: v1
- Initiative ID: INIT-20260418-04
- Title: Managed Artifact Control Plane Exposure v1
- Status: APPROVED
- Owner: Chua
- Workflow Governance In Scope: NO
- Created At: 2026-04-18
- Approved At: TBD

---

## 🎯 Objective
Expose the already validated managed artifact slice for `ArtifactType.RUNNER_EXECUTION_OVERVIEW` as a public control-plane workflow. The internal Builder → Generator → Consumer flow already works through service-layer entrypoints; this initiative makes that flow callable, readable, and reviewable through the public HTTP surface without redesigning the underlying builder or generator logic.

---

## 💡 Problem Statement
V5 shows the core system is not broken. The current limitation is that the working managed slice is still hidden behind internal service calls.

The following end-to-end flow is already proven working:
- ArtifactDefinition created and managed via API
- Inventory discovery triggered via API
- InventorySnapshot assembled deterministically and persisted
- Contract built via `ContractBuildExecutor`
- Managed generation executed via `contract_id`
- GenerationRun recorded with lifecycle tracking
- Artifact persisted with full lineage FKs
- Artifact retrieved via API
- Artifact consumed as bounded runner context

What is missing is the public interface that lets users and UKBE itself exercise that flow directly.

---

## 🚀 Expected Outcomes

### Business Outcomes
- UKBE exposes a usable public Builder → Generator control-plane path for the proven managed slice
- Operators and internal clients can verify the flow without direct service-layer invocation
- The system can demonstrate that the managed slice is operational, not merely planned

### Technical Outcomes
- Public HTTP endpoints exist for contract build triggering, managed generation triggering, generation-run retrieval, and lifecycle-aware artifact retrieval
- The validated runner-overview slice remains intact while being exposed through the public API
- Router registration and API documentation reflect the new control-plane surface

### User Outcomes
- Users can trigger the managed slice through HTTP
- Users can inspect generation runs and retrieve artifacts by lifecycle context
- Users can distinguish between a working system and a missing interface

---

## 📦 Scope

### Included
- Public contract-build trigger for the validated managed slice
- Public managed-generation trigger using `contract_id`
- Generation-run read/list/latest API surface
- Lifecycle-aware artifact retrieval by generation run and artifact definition
- Router registration and API documentation updates
- Public end-to-end validation of the managed slice

### Excluded
- New artifact types beyond `RUNNER_EXECUTION_OVERVIEW`
- Builder redesign
- Generator redesign
- New selection intelligence or LLM selection work
- Workflow governance redesign
- Broad contract-governance expansion beyond the current control-plane need

---

## ⚙️ Constraints
- Technical constraints: reuse existing Builder and Generator service-layer behavior; do not rewrite the proven slice
- Timeline constraints: keep the work narrow and sequenced around public exposure
- Resource constraints: avoid broad refactors across the storage or execution layers
- Compliance / policy constraints: Workflow Governance In Scope remains `NO`

---

## 🧩 Dependencies
- Internal systems:
  - Existing contract build executor
  - Existing managed artifact generator
  - Existing generation-run persistence layer
  - Existing contract and artifact read APIs
- External services: None
- Teams / owners: UKBE delivery team
- Predecessor initiatives / plans:
  - `INIT-20260417-01_artifact-builder-inventory-discovery-v1.md`
  - `INIT-20260416-02_managed-generation-boundary-v1.md`
  - `docs/architecture/08_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V5_2026-04-18.md`

---

## 📏 Success Criteria
- The validated managed slice is exposed through public HTTP routes
- The new routes do not change the behavior of the proven internal flow
- Generation runs are queryable through HTTP
- Artifacts are retrievable by lifecycle context
- Public validation shows the exposed interface matches the already working system

---

## 🔗 References
- Related docs:
  - `docs/architecture/08_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V5_2026-04-18.md`
  - `docs/architecture/07_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V4_2026-04-18.md`
- Supporting notes:
  - `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-01_generation-run-orm-service.md`
  - `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-02_dual-mode-artifact-generator.md`
  - `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-07_contract-bound-managed-generation.md`
  - `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-05_builder-api-endpoint-integration.md`

---

## 📝 Notes
- This initiative explicitly treats the managed slice as already working and focuses on exposure, not reinvention
- The core message is: the system works, the interface is missing
- Any later work on additional artifact types or LLM audit harmonization should be handled as separate follow-up initiatives

---

## ✅ Approval
- Approved By:
- Decision Date:
- Decision Notes:
