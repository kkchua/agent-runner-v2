# 📋 Implementation Plan: TASK-20260418-01 — Contract Build API Trigger

---

## 📌 Metadata

* **Doc Type:** 04_implementation_plan
* **Template Version:** v1
* **Plan ID:** PLAN-20260418-02
* **Task ID:** TASK-20260418-01
* **Title:** Contract Build API Trigger
* **Status:** APPROVED
* **Created At:** 2026-04-18
* **Author:** implementation_planner

---

## 🎯 Objective

Implement a thin HTTP endpoint (`POST /contract-build`) that accepts three UUID identifiers (`snapshot_id`, `artifact_definition_id`, `source_id`), delegates to the existing `ContractBuildExecutor.execute_contract_build()` service method, and returns a serialized contract response with optional build-run linkage. This is the first public entry point into the builder pipeline — the endpoint is a passthrough layer that does not modify executor behavior.

---

## 📥 Inputs

| Type           | Reference            |
| -------------- | -------------------- |
| Task Document  | `docs/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.md` |
| Plan Document  | `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md` |
| Dependencies   | None (entry task) |
| Reference Code | See "Reuse Strategy" section |

---

## 📤 Outputs

| Artifact   | Path       | Description       |
| ---------- | ---------- | ----------------- |
| Request/Response Schemas | `ukbe/app/api/schemas/contract_build.py` | Pydantic v2 models for build request and response |
| Router Implementation | `ukbe/app/api/contract_build.py` | POST `/contract-build` endpoint |
| Endpoint Tests | `tests/api/test_contract_build_api.py` | Success, validation, and failure coverage |

---

## 🧠 Scope Clarification

### ✅ Included

* Create `ContractBuildRequest` Pydantic schema with `snapshot_id`, `artifact_definition_id`, `source_id` as `UUID4` fields
* Create `ContractBuildResponse` Pydantic schema wrapping `ContractDetail` + `build_run_id: str | None`
* Create POST `/contract-build` route with explicit UUID conversion at route boundary
* Implement `_make_executor(session)` factory function following `build_run.py` `_make_service()` pattern
* Delegate to `ContractBuildExecutor.execute_contract_build(snapshot_uuid, artifact_def_uuid, source_uuid)`
* Extract `build_run_id` from returned contract's `build_runs` relationship (no separate DB query)
* Map known exceptions to HTTP status codes per task contract (422 auto-handled, 500 for pipeline errors)
* Test coverage for success, invalid input (422), and executor failure cases (500)

### ❌ Excluded

* Router registration in master `api_router.py` — handled in TASK-20260418-05
* Modifications to `ContractBuildExecutor` or any service-layer code
* New repository methods or database schema changes
* New ORM models or persistence logic
* Idempotency enforcement (aspirational test only, skip if pipeline is not deterministic)
* Any business-logic validation beyond Pydantic UUID format checking

---

## 📦 File Plan (MANDATORY)

```text
<repo_root>/
├── ukbe/app/api/schemas/contract_build.py      [NEW]
├── ukbe/app/api/contract_build.py              [NEW]
└── tests/api/test_contract_build_api.py        [NEW]
```

---

## 🧩 Module Responsibilities

### `ukbe/app/api/schemas/contract_build.py`

* **Responsibility:** Define Pydantic v2 request and response schemas for the contract-build endpoint.
* **Key behavior:**
  - `ContractBuildRequest`: validates `snapshot_id`, `artifact_definition_id`, `source_id` as `UUID4` fields using Pydantic's built-in UUID validation (ensures format correctness, triggers 422 on invalid format)
  - `ContractBuildResponse`: wraps `ContractDetail` (imported from `ukbe/app/api/schemas/contract.py`) plus optional `build_run_id: str | None`
  - Both schemas use `ConfigDict(from_attributes=True)` following existing pattern in `schemas/contract.py` and `schemas/build_run.py`

### `ukbe/app/api/contract_build.py`

* **Responsibility:** Define the POST `/contract-build` route that receives request body, instantiates executor, delegates to service, and returns serialized response.
* **Key behavior:**
  - Router with `prefix=""` and `tags=["contract-build"]` (task contract specifies prefix `""`, path `/contract-build` is set on the route itself)
  - `_make_executor(session: AsyncSession)` factory function: instantiates `ContractBuildExecutor` with all required constructor dependencies, following the `_make_service()` pattern from `build_run.py`
  - Route handler: validates request via Pydantic, converts UUID strings to `UUID` explicitly, calls executor, extracts `build_run_id` from contract relationship, returns `ContractBuildResponse`
  - Exception handling: let FastAPI handle 422 for `RequestValidationError`; catch `BudgetExceededError`, `ContractAssemblyError`, `ContractPersistenceError`, and fallback `Exception` — all map to HTTP 500

### `tests/api/test_contract_build_api.py`

* **Responsibility:** Validate endpoint behavior for success, invalid input, and executor failure scenarios.
* **Key behavior:**
  - Test successful build returns 200 with contract detail and non-None `build_run_id`
  - Test invalid/missing UUIDs return 422 (FastAPI auto-handled)
  - Test executor raises `BudgetExceededError` → 500
  - Test executor raises `ContractAssemblyError` → 500
  - Test executor raises `ContractPersistenceError` → 500
  - Verify build-run linkage (`response.build_run_id is not None` on success)
  - Verify DB persistence (contract exists after successful build) — use real or mocked session as appropriate
  - Follow existing test patterns from `tests/api/test_contract_api.py` and `tests/api/test_build_run_api.py`

---

## ♻️ Reuse Strategy (CRITICAL)

| Component    | Location | Usage        |
| ------------ | -------- | ------------ |
| `ContractDetail` | `ukbe/app/api/schemas/contract.py` | Imported and reused as nested field in `ContractBuildResponse.contract` — do NOT redefine contract schema fields |
| `ContractBuildExecutor` | `ukbe/app/contract_builder/services/contract_build_executor.py` | Core service method `execute_contract_build()` — delegate only, do NOT reimplement pipeline |
| `BudgetExceededError`, `ContractAssemblyError`, `ContractPersistenceError` | `ukbe/app/contract_builder/exceptions.py` | Exception types for HTTP error mapping — import and catch, do NOT redefine |
| `get_db` | `ukbe/app/storage/database.py` | FastAPI `Depends()` for async session injection — standard pattern |
| `_make_service()` pattern | `ukbe/app/api/build_run.py` | Template for `_make_executor()` factory function — follow same dependency wiring approach |
| Test patterns | `tests/api/test_contract_api.py`, `tests/api/test_build_run_api.py` | `_make_*_orm()` helper pattern, `monkeypatch` for service method overrides, `_make_app()` router isolation |
| `ContractRepository` | `ukbe/app/contract_builder/persistence/repository.py` | May be needed in `_make_executor()` for persister instantiation — inspect constructor chain |

**Rules:**
* All schemas reuse existing `ContractDetail` — no field duplication
* All service delegation goes through `ContractBuildExecutor.execute_contract_build()` — no pipeline reimplementation
* All test patterns follow existing `tests/api/` conventions — no new fixture frameworks
* All error handling uses existing exception types from `contract_builder/exceptions.py`

---

## 🔄 Data Flow

```text
POST /contract-build
  → FastAPI validates request body against ContractBuildRequest (UUID4 fields)
  → Route handler receives AsyncSession via Depends(get_db)
  → Route handler instantiates executor via _make_executor(session)
  → Route handler converts UUID strings to UUID objects explicitly
  → executor.execute_contract_build(snapshot_uuid, artifact_def_uuid, source_uuid)
    → SelectionProposalStage.execute_proposal() → SelectionProposalStageResult
    → SelectedDocumentRowDeriver.derive_rows() → rows with placeholder tokens
    → RowBudgetEnricher.enrich_rows() → rows with real token/cost estimates
    → BudgetValidator.validate() → raises BudgetExceededError on failure
    → FrozenContractAssembler.assemble() → FrozenContractAssembly
    → FrozenContractPersister.persist() → ArtifactContractORM
    → BuildRunService.create_build_run() → build_run_id (if build_run_service is not None)
    → ContractGovernanceService.request_governance() (if governance_service is not None)
    → Returns ArtifactContractORM with build_runs relationship loaded
  → Route handler extracts build_run_id from contract.build_runs[-1] if present, else None
  → Route handler maps ORM to ContractDetail via existing helper pattern
  → Returns ContractBuildResponse(contract=..., build_run_id=...)
```

**Exception flow:**
```text
BudgetExceededError → HTTP 500
ContractAssemblyError → HTTP 500
ContractPersistenceError → HTTP 500
Exception (fallback) → HTTP 500
RequestValidationError → HTTP 422 (FastAPI auto-handled, do NOT intercept)
```

---

## 🧪 Test Plan

### Test Files

```text
tests/api/test_contract_build_api.py
```

### Test Cases

* **Success case** — POST `/contract-build` with valid UUIDs returns 200, `ContractBuildResponse.contract` populated with contract detail fields, `build_run_id` is non-None
* **Invalid UUID format** — POST with malformed UUID strings returns 422 (FastAPI auto-handled)
* **Missing required fields** — POST with missing `snapshot_id`/`artifact_definition_id`/`source_id` returns 422
* **BudgetExceededError** — monkeypatch executor to raise `BudgetExceededError`, assert HTTP 500
* **ContractAssemblyError** — monkeypatch executor to raise `ContractAssemblyError`, assert HTTP 500
* **ContractPersistenceError** — monkeypatch executor to raise `ContractPersistenceError`, assert HTTP 500
* **Build-run linkage** — on success, assert `response.build_run_id is not None` (verifies executor's build-run creation ran)
* **DB persistence verification** — after successful build, verify contract record exists in database (use test session or integration-style assertion)
* **Schema model tests** — verify `ContractBuildRequest` and `ContractBuildResponse` can be constructed from ORM-like objects and attribute accessors

### Test Constraints

* No external dependencies beyond existing test database and app fixtures
* Use `monkeypatch` to override executor method (follow `test_contract_api.py` pattern of monkeypatching service/repository methods)
* Deterministic fixtures only — use `MagicMock` to simulate ORM responses
* Follow existing `_make_*_orm()` helper patterns from `test_contract_api.py` and `test_build_run_api.py`
* Router isolation: test endpoint with isolated FastAPI app including only `contract_build` router (do NOT depend on full app stack)

---

## 🔒 Constraints

* Do NOT modify `ContractBuildExecutor` or any service-layer code
* Do NOT create new repository methods or database schema changes
* Do NOT modify `ukbe/app/api/router.py` — router registration is TASK-20260418-05 scope
* Do NOT introduce new architecture layers or exception types
* Must follow existing API patterns from `ukbe/app/api/contract.py` and `ukbe/app/api/build_run.py`
* Must use `UUID()` explicit conversion at route boundary — no implicit string-to-UUID conversion
* Must extract `build_run_id` from `contract.build_runs` relationship — no separate DB query fallback
* Must let FastAPI handle 422 for `RequestValidationError` — do NOT catch and re-raise as 400

---

## ⚠️ Risks & Mitigations

| Risk       | Impact     | Mitigation     |
| ---------- | ---------- | -------------- |
| `_make_executor()` requires many constructor dependencies — inspect `ContractBuildExecutor.__init__` and all transitive service constructors to confirm required dependencies before implementation | Medium | Inspect `ukbe/app/contract_builder/services/` for each service's `__init__` signature; wire all dependencies in factory function; use existing session where applicable |
| `ArtifactContractORM.build_runs` relationship may not be loaded after `persist()` — verify relationship loading strategy (selectinload vs lazy) | Medium | Inspect `ArtifactContractORM` ORM model definition to confirm `build_runs` relationship configuration; if lazy-loaded, executor may need to refresh or explicitly load — reconcile before extraction logic |
| Executor's `build_run_service` may be `None` in some configurations — `build_runs` relationship could be empty | Low | Task contract already accounts for this: extract via `contract.build_runs[-1].build_run_id if contract.build_runs else None` — safe fallback |
| Test mocking of executor may not match real behavior — monkeypatch at correct boundary | Low | Monkeypatch `ContractBuildExecutor.execute_contract_build` directly (not internal service methods) to test the API layer in isolation; follow existing `test_contract_api.py` monkeypatch patterns |

---

## 📦 Dependencies

* None (entry task per task graph)
* Reuses existing `ContractBuildExecutor` and all its transitive dependencies (already operational per plan)

---

## 🧾 Notes

* This task creates the **first public entry point** into the builder pipeline. The endpoint is intentionally thin — it validates input, delegates to the executor, and serializes output.
* Router registration will be handled in TASK-20260418-05; this task only creates the router module.
* The `_make_executor()` factory function is the most complex part of this task — it must wire all `ContractBuildExecutor` constructor dependencies. Inspect each service's `__init__` to confirm required arguments before implementation.
* Idempotency test is aspirational only — skip if the pipeline is not confirmed deterministic (per task contract).
* The `build_run_id` extraction relies on the executor creating the build-run AFTER persistence (step 7 in executor flow). The relationship should be populated on the returned ORM.

---

## ✅ Ready for Execution

This plan is ready for the Executor agent if:

* File plan is complete
* Scope is clearly bounded
* Reuse strategy is defined
* No ambiguity remains
