# 📋 Implementation Plan: TASK-20260418-03 — Generation-Run API Surface

---

## 📌 Metadata

* **Doc Type:** 04_implementation_plan
* **Template Version:** v1
* **Plan ID:** PLAN-20260418-02
* **Task ID:** TASK-20260418-03
* **Title:** Generation-Run API Surface
* **Status:** APPROVED
* **Created At:** 2026-04-18
* **Author:** implementation_planner
* **Review File Path:** docs/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.md

---

## 🎯 Objective

Implement three read-only HTTP routes for generation-run audit records — single retrieval, paginated list, and latest — so that generation runs are queryable through the public API and preserve lifecycle fields for audit and lineage tracking.

This is a **read-only exposure task**. No mutation of generation-run records. No database model changes.

---

## 📥 Inputs

| Type           | Reference            |
| -------------- | -------------------- |
| Task Document  | docs/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.md |
| Plan Document  | docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md |
| Dependencies   | None (Track A independent task) |
| Reference Code | ukbe/app/api/build_run.py, ukbe/app/api/contract.py, ukbe/app/api/artifacts.py, ukbe/app/api/contract_build.py |

---

## 📤 Outputs

| Artifact   | Path       | Description       |
| ---------- | ---------- | ----------------- |
| Schema module | `ukbe/app/api/schemas/generation_run.py` | Request/response Pydantic schemas for generation-run endpoints |
| Router module | `ukbe/app/api/generation_run.py` | FastAPI router with three read endpoints |
| Router registration | `ukbe/app/api/router.py` | Wire the new router into the master API router |
| Repository extension | `ukbe/app/storage/repositories/generation_run_repo.py` | Add `list()` and `get_latest()` persistence methods |
| Service extension | `ukbe/app/generation/services/generation_run_service.py` | Add `list()` general method and `get_latest()` method |
| Test file | `tests/api/test_generation_run_api.py` | Endpoint coverage tests for all three routes |

---

## 🧠 Scope Clarification

### ✅ Included

* Three GET endpoints: `GET /generation-runs/{run_id}`, `GET /generation-runs`, `GET /generation-runs/latest`
* Pydantic request/response schemas with explicit field definitions
* Repository-level query methods for general list (with dynamic filters) and get_latest
* Service-layer delegation to repository methods
* UUID validation at API boundary for path params and filter params
* Pagination with explicit defaults (`limit=50`, `offset=0`, max `limit=100`)
* Deterministic ordering (`ORDER BY created_at DESC`) at repository query level
* Public status contract documentation (`{pending, running, completed, failed}`) with explicit mapping from the current stored enum values
* Router registration in master `api_router`
* Test coverage for all validation criteria listed in the task document

### ❌ Excluded

* Any mutation endpoints (create, update, delete generation runs)
* Database model changes or new columns
* `source_id` or `artifact_definition_id` filters via JOIN through the contract relationship — these fields are **not directly on** `GenerationRunORM`. The task lists them as filters but the ORM only has `contract_id` and `build_run_id` as FKs. These filters must be addressed as follows:
  - `contract_id` filter: supported directly (column exists on ORM)
  - `status` filter: supported directly (`run_status` column exists)
  - `source_id` filter: supported via `JOIN` from `GenerationRunORM.contract_id` to `ArtifactContractORM.source_id`
  - `artifact_definition_id` filter: supported via `JOIN` from `GenerationRunORM.contract_id` to `ArtifactContractORM.artifact_definition_id`
* New architecture layers or service components
* Modification of existing generation-run lifecycle behavior

---

## 📦 File Plan (MANDATORY)

```text
/home/kengkoon/projects/ukbe/
├── ukbe/app/api/schemas/generation_run.py       [NEW]
├── ukbe/app/api/generation_run.py               [NEW]
├── ukbe/app/api/router.py                       [MODIFY] — register generation_run router
├── ukbe/app/storage/repositories/generation_run_repo.py  [MODIFY] — add list() and get_latest()
├── ukbe/app/generation/services/generation_run_service.py  [MODIFY] — extend list() and add get_latest()
└── tests/api/test_generation_run_api.py         [NEW]
```

---

## 🧩 Module Responsibilities

### `ukbe/app/api/schemas/generation_run.py`

* **Responsibility:** Define all Pydantic request/response schemas for generation-run API endpoints
* **Key behaviors:**
  - `GENERATION_RUN_STATUS_VALUES` constant documenting allowed status values
  - `GenerationRunResponse` — explicit response schema with all lifecycle fields, including `failed_at: datetime | None` serialized as `None` when no value exists on the ORM
  - `GenerationRunListResponse` — paginated list response with `items`, `total`, `offset`, `limit`
  - `GenerationRunListQuery` — query param schema with pagination defaults and optional filters
  - `GenerationRunLatestQuery` — query param schema for latest endpoint with optional filters
  - `_generation_run_response()` mapping helper (ORM → Pydantic)
  - `_extract_error_message()` helper for error_context extraction

### `ukbe/app/api/generation_run.py`

* **Responsibility:** FastAPI router with three GET endpoints for generation-run reads
* **Key behaviors:**
  - `GET /{run_id}` — delegates to `GenerationRunService.get()`, returns `GenerationRunResponse`
  - `GET /` — delegates to `GenerationRunService.list()`, returns `GenerationRunListResponse`
  - `GET /latest` — delegates to `GenerationRunService.get_latest()`, returns `GenerationRunResponse`
  - UUID validation on path params and filter params at route boundary
  - Exception mapping: 404 for not-found, 422 for invalid UUID

### `ukbe/app/storage/repositories/generation_run_repo.py` (extension)

* **Responsibility:** Add general-purpose read queries to the existing repository
* **Key behaviors:**
  - `list()` — supports optional filters (`contract_id`, `run_status`, plus JOIN-based filters for `source_id` and `artifact_definition_id` through contract), pagination (`limit`, `offset`), ordering (`created_at DESC`), returns `list[GenerationRunORM]`
  - `get_latest()` — supports optional filters (`source_id`, `contract_id`, `artifact_definition_id`), returns single most recent `GenerationRunORM | None`

### `ukbe/app/generation/services/generation_run_service.py` (extension)

* **Responsibility:** Extend existing service with general list and get_latest delegation
* **Key behaviors:**
  - Extend existing `list()` method (currently only supports `contract_id` filter and logs a warning for unfiltered calls) to support general filters and pagination
  - Add `get_latest()` method delegating to repository `get_latest()`
  - UUID validation on filter params before calling repository

### `ukbe/app/api/router.py` (extension)

* **Responsibility:** Register the new generation_run router in the master API router
* **Key behaviors:** Import the router and call `api_router.include_router()`

### `tests/api/test_generation_run_api.py`

* **Responsibility:** Validate all three endpoints return correct data and lifecycle fields
* **Key behaviors:** Follow existing test patterns from `tests/api/test_build_run_api.py`

---

## ♻️ Reuse Strategy (CRITICAL)

| Component    | Location | Usage        |
| ------------ | -------- | ------------ |
| `GenerationRunService` | `ukbe/app/generation/services/generation_run_service.py` | Already has `get()` and partial `list()` — extend, do not replace |
| `GenerationRunRepository` | `ukbe/app/storage/repositories/generation_run_repo.py` | Already has `get_by_id()`, `list_by_contract()`, `update_*()` — add `list()` and `get_latest()` |
| `GenerationRunORM` | `ukbe/app/storage/models/generation_run.py` | Existing ORM — inspect column names for schema mapping (PK is `generation_run_id`, status is `run_status`) |
| `GenerationRunNotFoundError` | `ukbe/app/generation/exceptions.py` | Existing exception for 404 mapping |
| `GenerationRunStatus`, `GenerationRunStage` | `ukbe/app/generation/enums.py` | Existing enums — internal stored values are `{started, in_progress, completed, failed}`; public API contract is `{pending, running, completed, failed}` and the mapping helper must reconcile them explicitly |
| FastAPI router pattern | `ukbe/app/api/build_run.py` | Reuse same `_make_service()`, `_make_repo()`, endpoint structure, exception mapping |
| Test pattern | `tests/api/test_build_run_api.py` | Reuse same test structure: `_make_orm()` factory, `_make_app()`, `monkeypatch` service methods, `TestClient` |
| Schema pattern | `ukbe/app/api/schemas/build_run.py` | Reuse same `_mapping_helper()` pattern, `ConfigDict(from_attributes=True)` |

---

## 🔄 Data Flow

### Endpoint 1: `GET /generation-runs/{run_id}` — Single Run Retrieval

```
HTTP GET /generation-runs/{run_id}
→ FastAPI route receives run_id (path param)
→ UUID validation at route boundary (UUID(run_id) → 422 if invalid)
→ Instantiate GenerationRunService with current DB session
→ Delegate to service.get(run_id)
  → Delegate to repository.get_by_id(run_id)
    → SELECT FROM generation_runs WHERE generation_run_id = ?
    → Return GenerationRunORM | None
  → If None → raise GenerationRunNotFoundError
→ Map ORM to GenerationRunResponse via _generation_run_response()
→ Return HTTP 200 with JSON response
```

Exception mapping:
- `GenerationRunNotFoundError` → HTTP 404
- Invalid UUID → HTTP 422 (FastAPI default validation)

### Endpoint 2: `GET /generation-runs` — Paginated List

```
HTTP GET /generation-runs?source_id=...&contract_id=...&artifact_definition_id=...&status=...&limit=...&offset=...
→ FastAPI route receives query params via GenerationRunListQuery
→ Pydantic validates: limit default=50, max=100; offset default=0
→ UUID validation on filter params (source_id, contract_id, artifact_definition_id if provided)
→ Instantiate GenerationRunService with current DB session
→ Delegate to service.list(filters..., limit, offset)
  → Delegate to repository.list(filters..., limit, offset)
    → Build SELECT with optional WHERE clauses (dynamic filters)
    → For source_id/artifact_definition_id filters: JOIN `GenerationRunORM.contract` to `ArtifactContractORM` and filter on `ArtifactContractORM.source_id` / `ArtifactContractORM.artifact_definition_id`
    → ORDER BY created_at DESC
    → LIMIT ? OFFSET ?
    → Return list[GenerationRunORM]
  → Return list[GenerationRunORM]
→ Map each ORM to GenerationRunResponse via _generation_run_response()
→ Construct GenerationRunListResponse(items=..., total=..., offset=..., limit=...)
→ Return HTTP 200 with JSON response (empty list when no matches)
```

### Endpoint 3: `GET /generation-runs/latest` — Latest Run

```
HTTP GET /generation-runs/latest?source_id=...&contract_id=...&artifact_definition_id=...
→ FastAPI route receives query params via GenerationRunLatestQuery
→ UUID validation on filter params (source_id, contract_id, artifact_definition_id if provided)
→ Instantiate GenerationRunService with current DB session
→ Delegate to service.get_latest(filters...)
  → Delegate to repository.get_latest(filters...)
    → Build SELECT with optional WHERE clauses
    → For source_id/artifact_definition_id filters: JOIN `GenerationRunORM.contract` to `ArtifactContractORM` and filter on `ArtifactContractORM.source_id` / `ArtifactContractORM.artifact_definition_id`
    → ORDER BY created_at DESC LIMIT 1
    → Return GenerationRunORM | None
  → Return GenerationRunORM | None
→ If None → HTTP 404
→ Map ORM to GenerationRunResponse via _generation_run_response()
→ Return HTTP 200 with JSON response
```

---

## ⚠️ Schema Reconciliation (MANDATORY — Before Implementation)

### ORM Field Name Mapping

Inspect `ukbe/app/storage/models/generation_run.py` to confirm actual column names before implementing the response schema mapping:

| Response Schema Field | ORM Column (verify) | Notes |
| --------------------- | ------------------- | ----- |
| `id` | `generation_run_id` (PK) | Response uses `id` — mapping helper must rename |
| `source_id` | **NOT on ORM directly** | Must resolve via `contract.source_id` relationship or note as gap |
| `contract_id` | `contract_id` | Direct column — verify nullable |
| `artifact_definition_id` | **NOT on ORM directly** | Must resolve via `contract.artifact_definition_id` relationship or note as gap |
| `status` | `run_status` | Mapping helper must rename and normalize internal values to the public contract |
| `created_at` | `created_at` | Direct |
| `updated_at` | `updated_at` | Direct |
| `started_at` | `started_at` | Direct, nullable |
| `completed_at` | `completed_at` | Direct, nullable |
| `failed_at` | **NOT on ORM** | Include in response schema as `datetime | None`; serialize as `None` when no value exists on the ORM |
| `error_message` | Derived from `error_context` | Extract via `_extract_error_message()` helper |

### Status Enum Reconciliation

Inspect `ukbe/app/generation/enums.py` — actual `GenerationRunStatus` values are:
- `started`, `in_progress`, `completed`, `failed`

Task requires documenting status as: `{pending, running, completed, failed}`

**Reconcile before implementation:** Treat the task-facing values as the public API contract and map the stored enum values explicitly in the schema helper:
- `started` → `pending`
- `in_progress` → `running`
- `completed` → `completed`
- `failed` → `failed`

Define `GENERATION_RUN_STATUS_VALUES` with the public contract values and keep the internal-to-public mapping in the schema module so the response surface is consistent.

### `source_id` and `artifact_definition_id` Filter Resolution

The task lists these as list/latest endpoint filters, but `GenerationRunORM` does not have these columns directly. Use the existing `contract` relationship to resolve them:

- `GenerationRunORM.contract` → `ArtifactContractORM.source_id`
- `GenerationRunORM.contract` → `ArtifactContractORM.artifact_definition_id`

**Implementation contract:** repository `list()` and `get_latest()` must apply the JOIN-based filters whenever either of those query parameters is present. This is not a deferred gap and does not require a model change.

---

## 🧪 Test Plan

### Test Files

```text
tests/api/test_generation_run_api.py
```

### Test Behaviors to Validate

**Single retrieval (`GET /generation-runs/{run_id}`):**
- Valid run_id returns correct run with all lifecycle fields mapped correctly
- Non-existent run_id returns 404
- Non-UUID run_id returns 422

**List endpoint (`GET /generation-runs`):**
- Returns paginated list with correct structure (`items`, `total`, `offset`, `limit`)
- Returns empty list with correct pagination structure when no runs exist
- Uses default `limit=50`, `offset=0` when pagination params not specified
- Respects custom `limit` and `offset` params
- Rejects `limit > 100` with 422
- Filter by `contract_id` works correctly
- Filter by `status` works correctly
- Non-UUID filter value returns 422
- Results are ordered by `created_at DESC`

**Latest endpoint (`GET /generation-runs/latest`):**
- Returns most recent run
- Returns 404 when no runs match filter
- Works with `source_id` and `contract_id` filters
- Works with `artifact_definition_id` filter
- Non-UUID filter value returns 422

**Schema validation:**
- `GenerationRunResponse` has all required fields including lifecycle fields
- `GenerationRunListResponse` has `items`, `total`, `offset`, `limit`
- Status field values reflect the public contract values and are reconciled from the stored enum values

### Test Constraints

* Use `monkeypatch` to mock service methods (follow `test_build_run_api.py` pattern)
* Use `MagicMock` for ORM-like fixtures (follow existing `_make_build_run_orm()` pattern)
* Use `TestClient` for endpoint testing
* No external dependencies beyond existing test database fixtures
* Deterministic fixtures only
* Follow existing test class organization (e.g., `TestGetBuildRun`, `TestListBuildRuns`)

---

## 🔒 Constraints

* Do NOT modify unrelated modules
* Do NOT introduce new architecture layers
* Must follow task scope strictly — read-only exposure only
* Must preserve lifecycle fields exactly as defined in the response schema
* Must reuse existing `GenerationRunService` and `GenerationRunRepository` — do not duplicate service-layer logic in the router
* Must use Pydantic response schemas for all endpoints (no raw ORM serialization)
* Must not change database model or add new columns

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| ORM field naming mismatch — response schema uses `id` but ORM uses `generation_run_id`; response uses `status` but ORM uses `run_status` | Medium | `_generation_run_response()` mapping helper must handle renaming explicitly — verify column names in `GenerationRunORM` before implementation |
| `source_id` and `artifact_definition_id` not directly on `GenerationRunORM` | Medium | Implement JOIN through `contract` relationship in repository queries; if JOIN proves complex, defer with TODO comment and document in risk notes |
| `failed_at` column does not exist on ORM | Low | Include `failed_at` in `GenerationRunResponse` as nullable and serialize `None` when the ORM has no value; do not omit it |
| Status enum mismatch — task says `{pending, running, completed, failed}` but actual enum is `{started, in_progress, completed, failed}` | Medium | Keep the public response contract as `{pending, running, completed, failed}` and use the explicit stored-to-public mapping in the schema helper; do not document the stored enum values as the API contract |
| Existing `list()` method on service only supports `contract_id` filter and returns empty list for unfiltered calls | Medium | Extend the existing method to support general filters — inspect current implementation and adapt rather than replace |
| Repository `list()` method does not exist yet (only `list_by_contract()`) | Medium | Add new `list()` method with dynamic filter support — follow pattern from existing `list_by_contract()` |

---

## 📦 Dependencies

* None (Track A independent task per plan document)
* Relies on existing `GenerationRunService`, `GenerationRunRepository`, `GenerationRunORM` — all confirmed operational

---

## 🧾 Notes

* This task is narrow and read-only; it does not mutate generation-run records
* The goal is public exposure of an already-working audit surface, not redesign
* Lifecycle fields are critical for lineage tracking and must be preserved in all responses
* The `/latest` route should be registered BEFORE the `/{run_id}` route in the router to avoid path collision (FastAPI matches routes in registration order) — this follows the same pattern used in `build_run.py` where `/contracts/{contract_id}/build-runs/latest` is registered after the list route
* `failed_at` must remain present in the response schema as a nullable field even though the ORM does not expose a backing column
* Follow the `_make_service()` / `_make_repo()` factory pattern from `build_run.py` for dependency injection consistency
* When implementing the repository `list()` method with dynamic filters, use conditional `.where()` clauses rather than raw SQL — maintain SQLAlchemy expression patterns consistent with existing repository methods

---

## ✅ Ready for Execution

This plan is ready for the Executor agent if:

* File plan is complete
* Scope is clearly bounded
* Reuse strategy is defined
* Schema reconciliation items are identified with inspect/reconcile language
* No ambiguity remains beyond what the reconcile steps will resolve
