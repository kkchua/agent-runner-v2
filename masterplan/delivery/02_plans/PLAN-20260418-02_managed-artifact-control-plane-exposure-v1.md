# 📋 Plan

## 📌 Metadata
- Doc Type: 02_plan
- Template Version: v1
- Plan ID: PLAN-20260418-02
- Initiative ID: INIT-20260418-04
- Title: Managed Artifact Control Plane Exposure v1
- Status: COMPLETED
- Owner: Chua
- Created At: 2026-04-18
- Review File Path: docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md

---

## 🎯 Plan Objective
Expose the already validated `RUNNER_EXECUTION_OVERVIEW` managed artifact slice through public HTTP routes without changing the underlying Builder or Generator behavior. The plan makes the working internal flow callable through the public control plane, then validates that the exposed interface matches the system that already works.

---

## 🧠 Strategy Overview
This plan uses a two-layer approach:

**Track A - Public Exposure**: implement the missing HTTP surfaces for contract build triggering, managed generation, generation-run reads, and artifact lifecycle reads.

**Track B - Control Plane Integration**: register the routers, update API documentation, and validate the end-to-end public flow against the already proven managed slice.

The plan is intentionally narrow. It exposes the working slice rather than redesigning the slice itself.

---

## Proven Working Slice

The following end-to-end flow is already implemented and validated for `ArtifactType.RUNNER_EXECUTION_OVERVIEW`:

1. ArtifactDefinition created and managed via API
2. Inventory discovery triggered via API
3. InventorySnapshot assembled deterministically and persisted
4. Contract built via `ContractBuildExecutor`
5. Managed generation executed via `contract_id`
6. GenerationRun recorded with lifecycle tracking
7. Artifact persisted with full lineage FKs
8. Artifact retrieved via API
9. Artifact consumed as bounded runner context

This confirms the Builder → Generator → Consumer lifecycle is operational for a single artifact slice, but not yet fully exposed as a public control-plane workflow.

---

## 🧭 Scope Mapping

- TASK-20260418-01 -> Included Scope: Public contract-build trigger; Success Criteria: A user-callable API can start contract creation from validated Builder data
- TASK-20260418-02 -> Included Scope: Public managed-generation trigger; Success Criteria: A user-callable API can trigger managed generation from `contract_id`
- TASK-20260418-03 -> Included Scope: Generation-run read/list/latest API surface; Success Criteria: Generation runs are queryable through HTTP
- TASK-20260418-04 -> Included Scope: Lifecycle-aware artifact retrieval; Success Criteria: Artifacts are retrievable by generation run and artifact definition lifecycle context
- TASK-20260418-05 -> Included Scope: Router registration and documentation; Success Criteria: New routes are visible in OpenAPI and available through the main API router
- TASK-20260418-06 -> Included Scope: Public flow validation; Success Criteria: The exposed public interface matches the proven managed slice

---

## 🚫 Explicitly Excluded / Not Planned

- New artifact types beyond `RUNNER_EXECUTION_OVERVIEW`
- Builder redesign
- Generator redesign
- New selection intelligence or LLM selection work
- Workflow governance redesign
- Broad contract-governance expansion
- New ingestion or discovery behavior
- Snapshot model redesign
- Public repair or mutation tooling for lineage records

---

## 📐 Architecture Context

### Existing Delivered Components

| Component | Location | Status |
|-----------|----------|--------|
| Contract build executor | `ukbe/app/contract_builder/services/contract_build_executor.py` | ✅ Operational |
| Managed generator | `ukbe/app/generation/artifact_generator.py` | ✅ Operational |
| Generation-run service | `ukbe/app/generation/services/generation_run_service.py` | ✅ Operational |
| Contract read API | `ukbe/app/api/contract.py` | ✅ Operational |
| Artifact read API | `ukbe/app/api/artifacts.py` | ✅ Operational |
| Inventory discovery API | `ukbe/app/api/artifact_definitions.py` | ✅ Operational |
| Build-run read API | `ukbe/app/api/build_run.py` | ✅ Operational |
| Runner-overview plugin | `ukbe/plugins/outputs/runner_execution_overview.py` | ✅ Operational |

### Missing Public Surfaces

| Gap | Resolution |
|-----|------------|
| No public contract-build trigger | Add a thin contract-build API that calls the existing executor |
| No public managed-generation trigger | Add a contract-aware generation API that calls `generate_from_contract()` |
| No generation-run HTTP surface | Add read/list/latest routes for generation runs |
| No lifecycle-aware artifact retrieval | Add artifact retrieval by generation run and definition history/latest |

---

## 📋 Task Breakdown

| Task ID | Task Name | Description | Owner | Priority | Depends On |
|---|---|---|---|---|---|
| TASK-20260418-01 | Contract Build API Trigger | Implement the public contract-build endpoint that reuses the existing builder executor | Chua | high | |
| TASK-20260418-02 | Managed Generation API Trigger | Implement the public `contract_id`-driven generation endpoint for the managed slice | Chua | high | |
| TASK-20260418-03 | Generation-Run API Surface | Implement read/list/latest routes for generation-run audit records | Chua | medium | |
| TASK-20260418-04 | Artifact Lifecycle Retrieval | Implement artifact retrieval by generation run and definition lifecycle context | Chua | medium | |
| TASK-20260418-05 | Router Registration & Documentation | Register the new routers in the master API router and update API docs | Chua | medium | TASK-20260418-01, TASK-20260418-02, TASK-20260418-03, TASK-20260418-04 |
| TASK-20260418-06 | Public Slice Validation | Validate the end-to-end exposed workflow against the already proven managed slice | Chua | high | TASK-20260418-05 |

---

## Execution Phases

### Phase 1 - Public Surface Implementation
- TASK-20260418-01
- TASK-20260418-02
- TASK-20260418-03
- TASK-20260418-04

### Phase 2 - Integration
- TASK-20260418-05

### Phase 3 - Validation
- TASK-20260418-06

---

## 📦 Deliverables

| Deliverable | Output Path | Filename | Description |
|-------------|-------------|----------|-------------|
| Contract Build API | `ukbe/app/api/contract_build.py` | `contract_build.py` | New router for the public contract-build trigger |
| Contract Build Schemas | `ukbe/app/api/schemas/contract_build.py` | `contract_build.py` | Request/response models for build triggering |
| Managed Generation API | `ukbe/app/api/artifacts.py` | `artifacts.py` (extended) | New contract-aware generation endpoint |
| Managed Generation Schemas | `ukbe/app/api/schemas/generation.py` | `generation.py` | Request/response models for managed generation |
| Generation-Run API | `ukbe/app/api/generation_run.py` | `generation_run.py` | New router for generation-run reads |
| Generation-Run Schemas | `ukbe/app/api/schemas/generation_run.py` | `generation_run.py` | Request/response models for generation-run reads |
| Artifact Lifecycle API | `ukbe/app/api/artifact_history.py` | `artifact_history.py` | New router for artifact lifecycle queries |
| Artifact Repo Extensions | `ukbe/app/storage/repositories/artifact_repo.py` | `artifact_repo.py` (extended) | Add lineage-aware retrieval helpers |
| Router Registration | `ukbe/app/api/router.py` | `router.py` (extended) | Register all new routers |
| Public Flow Validation | `tests/integration/test_public_managed_artifact_slice.py` | `test_public_managed_artifact_slice.py` | End-to-end validation of the exposed slice |

---

## 🔄 Data Flow

```text
Public HTTP request
→ thin API router
→ existing service-layer component
→ database persistence / retrieval
→ public response
```

1. Receive a public contract-build request and hand it to the existing contract build executor.
2. Receive a public managed-generation request and hand it to `ArtifactGenerator.generate_from_contract()`.
3. Persist and read generation-run audit records through the existing generation-run service and repository layer.
4. Retrieve artifacts by generation-run and definition lifecycle context using lineage-aware repository queries.
5. Register all routers and expose the routes in OpenAPI.
6. Validate the full flow end to end against the already proven managed slice.

---

## 🧪 Test Plan

### Test Files

```text
tests/api/test_contract_build_api.py
tests/api/test_generation_run_api.py
tests/api/test_artifact_history_api.py
tests/api/test_public_control_plane_registration.py
tests/integration/test_public_managed_artifact_slice.py
```

### Test Cases

* public contract-build trigger returns a contract response and reuses the existing executor
* public managed-generation trigger accepts `contract_id` and routes to the managed generator
* generation-run read/list/latest endpoints serialize correctly and preserve lifecycle fields
* artifact lifecycle endpoints return generation-run and definition-scoped results
* router registration exposes the new routes in the master API router and OpenAPI
* the full exposed slice still returns the same managed artifact content and lineage that the internal slice already proved

### Test Constraints

* No external dependencies beyond the existing test database and app fixtures
* Deterministic fixtures only
* Keep the tests focused on public exposure and lineage correctness

---

## 🔒 Constraints

* Do NOT modify unrelated modules
* Do NOT introduce new architecture layers
* Must follow task scope strictly
* Must preserve the already validated internal Builder → Generator → Consumer behavior
* Must keep the managed slice limited to `RUNNER_EXECUTION_OVERVIEW`

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Public routes could drift from the proven internal flow | High | Reuse existing service-layer methods and validate against the proven slice |
| Lineage retrieval may require new repository helpers | Medium | Add minimal read-only helpers and keep query ordering explicit |
| Router registration could be overlooked or partially applied | Medium | Keep registration as a dedicated integration task |
| Validation could prove the new interface but miss lineage regressions | High | Assert contract, build-run, generation-run, and artifact lineage in the same flow |

---

## 📦 Dependencies

* `INIT-20260418-04_managed-artifact-control-plane-exposure-v1.md`
* `docs/architecture/08_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V5_2026-04-18.md`
* `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-07_contract-bound-managed-generation.md`
* `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-01_generation-run-orm-service.md`
* `docs/delivery/04_implementation_plans/Completed/IMPL-20260417-05_builder-api-endpoint-integration.md`

---

## 🧾 Notes

* This plan is intentionally about exposure, not reinvention
* The working slice is already there; the missing piece is the public surface
* Any later work on additional artifact types or LLM lineage harmonization should be handled in separate initiatives

---

## ✅ Ready for Execution

This plan is ready for the Executor agent if:

* File plan is complete
* Scope is clearly bounded
* Reuse strategy is defined
* No ambiguity remains
