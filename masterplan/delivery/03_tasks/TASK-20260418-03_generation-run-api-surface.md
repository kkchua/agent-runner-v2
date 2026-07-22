# 🧩 Task Document

## 📌 Metadata
- Doc Type: 03_task
- Template Version: v1
- Task ID: TASK-20260418-03
- Plan ID: PLAN-20260418-02
- Title: Generation-Run API Surface
- Status: COMPLETED
- Priority: medium
- Assigned To: Chua
- Created At: 2026-04-18
- Due At: TBD
- Source Task Graph ID: TASK-GRAPH-20260418-PLAN-20260418-02
- Source Task Node ID: TASK-20260418-03
- Review File Path: docs/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.md
- Review Notes: Added 5 critical fixes: (1) explicit response schema, (2) UUID boundary enforcement, (3) pagination contract with defaults, (4) deterministic ordering, (5) status enum consistency

---

## 🎯 Objective
Implement read/list/latest HTTP routes for generation-run audit records so that generation runs are queryable through the public API and preserve lifecycle fields for audit and lineage tracking.

---

## 📥 Inputs
- Source plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Source task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Dependencies: None (Track A independent task)
- Required documents:
  - Existing generation-run service: `ukbe/app/generation/services/generation_run_service.py`
  - Existing generation-run ORM model: `ukbe/app/storage/models/generation_run.py`
  - Existing generation-run repository: `ukbe/app/storage/repositories/generation_run_repo.py`
  - Existing API router patterns: `ukbe/app/api/router.py`, `ukbe/app/api/artifacts.py`
- Required data / APIs:
  - Existing `GenerationRunService` methods for read/list/latest operations
  - FastAPI router registration via `APIRouter`

---

## 📤 Outputs
- Expected artifacts:
  - `ukbe/app/api/generation_run.py` — generation-run router implementation with read/list/latest endpoints
  - `ukbe/app/api/schemas/generation_run.py` — request/response Pydantic schemas for generation-run endpoints
  - `tests/api/test_generation_run_api.py` — endpoint coverage tests for all three routes
- Output folder / path: `ukbe/app/api/`, `ukbe/app/api/schemas/`, `tests/api/`
- Completion evidence: All three routes return correct data and pass tests; lifecycle fields (status, timestamps, contract_id, artifact_definition_id, source_id) are preserved in responses

---

## 🧠 Implementation Details

### Technical Notes
- Reuse existing `GenerationRunService` methods; do NOT duplicate service-layer logic in the router
- Follow the same router pattern as existing API routers (e.g., `artifacts.py`, `contract.py`)
- Generation-run records are already persisted by the managed generation flow; this task only exposes reads

### API / Contract Notes

- **GET `/generation-runs/{run_id}`** — Retrieve a single generation run by ID
  - Path param `run_id` must be validated as UUID: `UUID(run_id)` → HTTP 422 if invalid
  - Returns full generation run record with all lifecycle fields (see `GenerationRunResponse` schema)
  - 404 if not found

- **GET `/generation-runs`** — List generation runs
  - Supports pagination query parameters with **explicit defaults**:
    - `limit` default = 50, max = 100 (enforced via Pydantic `Field`)
    - `offset` default = 0 (enforced via Pydantic `Field`)
  - Supports optional filter by `source_id`, `contract_id`, `artifact_definition_id`, `status`
    - All filter UUID values must be validated: `UUID(filter_value) if provided`
  - Returns `GenerationRunListResponse` with `items`, `total`, `offset`, `limit`
  - **Ordering**: `ORDER BY created_at DESC` (enforced at repository query level)
  - Returns empty list `{"items": [], "total": 0, "offset": 0, "limit": 50}` when no runs match

- **GET `/generation-runs/latest`** — Get the most recent generation run
  - Supports optional filter by `source_id`, `contract_id`, `artifact_definition_id`
    - All filter UUID values must be validated: `UUID(filter_value) if provided`
  - Returns the single most recent run ordered by `created_at DESC`
  - 404 if no runs match the filter

- All responses must serialize generation-run records through Pydantic response schemas defined in `schemas/generation_run.py`
- Route prefix: `/generation-runs`
- Router tag: `generation-runs`
- **Status enum**: `status ∈ {pending, running, completed, failed}` (documented, not DB-enforced yet)

### Data / Schema Notes

#### ⚠️ CRITICAL: Explicit Response Schema (DO NOT REPEAT EARLIER MISTAKE)

Response schemas must be **explicitly locked** — no partial fields, no inference, no dynamic serialization.

```python
class GenerationRunResponse(BaseModel):
    id: str
    source_id: str | None
    contract_id: str | None
    artifact_definition_id: str | None
    Status: COMPLETED
    created_at: datetime
    updated_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    error_message: str | None
```

```python
class GenerationRunListResponse(BaseModel):
    items: list[GenerationRunResponse]
    total: int
    offset: int
    limit: int
```

#### ⚠️ CRITICAL: UUID Boundary Enforcement

- All `run_id` path parameters must be validated: `UUID(run_id)`
- All `contract_id`, `source_id`, `artifact_definition_id` filter parameters must be validated: `UUID(filter_value) if provided`
- Invalid UUID format must return HTTP 422 (FastAPI default validation error)

#### ⚠️ CRITICAL: Pagination Contract (Explicit Defaults)

- `limit` default = **50**
- `limit` max = **100**
- `offset` default = **0**
- These defaults must be enforced at the schema level via Pydantic `Field(default=..., le=...)`
- Agent must NOT omit pagination parameters — API behavior becomes inconsistent without them

#### ⚠️ CRITICAL: Deterministic Ordering

- All list and latest endpoints must use: `ORDER BY created_at DESC`
- This must be enforced at the **repository query level**, not just in service layer
- Without explicit ordering, results are non-deterministic across runs

#### ⚠️ CRITICAL: Status Enum Consistency

- `status` field must be documented as: `status ∈ {pending, running, completed, failed}`
- Even if not DB-enforced yet, the schema must document allowed values
- Define `GENERATION_RUN_STATUS_VALUES = {"pending", "running", "completed", "failed"}` in the schema module
- Future enforcement can be added as a validator once the enum is documented

#### Schema Definitions

- Request schemas: `GenerationRunListQuery` (query params for list endpoint), `GenerationRunLatestQuery` (query params for latest endpoint)
- Response schemas: `GenerationRunResponse` (single run), `GenerationRunListResponse` (paginated list)
- Response schemas must include lifecycle fields exactly as defined above — no deviations
- Do NOT introduce new database columns or modify the generation-run model; this is a read-only exposure task

---

## 🔧 Execution Steps

### Phase 1: Repository & Service Layer Extensions
1. Add `list()` method to `GenerationRunRepository` with support for:
   - Filters: `source_id`, `contract_id`, `artifact_definition_id`, `status`
   - Pagination: `limit`, `offset`
   - Ordering: `ORDER BY created_at DESC` (deterministic)
   - Return: `list[GenerationRunORM]`

2. Add `list()` method to `GenerationRunService` that delegates to repository `list()`
   - Must accept same filter + pagination params
   - Must validate UUID filters before calling repository

3. Add `get_latest()` method to `GenerationRunRepository` with support for:
   - Filters: `source_id`, `contract_id`, `artifact_definition_id`
   - Ordering: `ORDER BY created_at DESC LIMIT 1`
   - Return: `GenerationRunORM | None`

4. Add `get_latest()` method to `GenerationRunService` that delegates to repository `get_latest()`
   - Must validate UUID filters before calling repository

### Phase 2: Schema Definitions
5. Create `ukbe/app/api/schemas/generation_run.py` with:
   - `GENERATION_RUN_STATUS_VALUES = {"pending", "running", "completed", "failed"}`
   - `GenerationRunResponse` with explicit fields (see Data/Schema Notes)
   - `GenerationRunListResponse` with `items`, `total`, `offset`, `limit`
   - `GenerationRunListQuery` with pagination defaults (`limit=50`, `offset=0`, max `limit=100`)
   - `GenerationRunLatestQuery` with optional filters
   - `_generation_run_response()` mapping helper
   - `_extract_error_message()` helper for error_context extraction

### Phase 3: API Router Implementation
6. Create `ukbe/app/api/generation_run.py` with three endpoints:
   - `GET /{run_id}` — single run retrieval (UUID validation on path param)
   - `GET /` — list runs with optional filters and pagination (UUID validation on filter params)
   - `GET /latest` — latest run retrieval with optional filters (UUID validation on filter params)
7. Wire all three endpoints to delegate to `GenerationRunService` methods
8. Ensure all responses use Pydantic response schemas (no raw ORM objects)

### Phase 4: Router Registration
9. Register `generation_run` router in `ukbe/app/api/router.py`

### Phase 5: Tests
10. Create `tests/api/test_generation_run_api.py` with all test cases listed in Validation Criteria
11. Verify endpoints return correct data and lifecycle fields through local test execution

---

## 🧪 Validation Criteria

### Acceptance checks:
- `GET /generation-runs/{run_id}` returns a single generation run with all lifecycle fields when the run exists
- `GET /generation-runs/{run_id}` returns 404 when the run does not exist
- `GET /generation-runs/{run_id}` returns HTTP 422 when `run_id` is not a valid UUID
- `GET /generation-runs` returns a `GenerationRunListResponse` with `items`, `total`, `offset`, `limit` fields
- `GET /generation-runs` returns paginated list with default `limit=50`, `offset=0` when not specified
- `GET /generation-runs` respects `limit` and `offset` query parameters (max limit=100)
- `GET /generation-runs` returns results ordered by `created_at DESC`
- `GET /generation-runs` supports optional filters: `source_id`, `contract_id`, `artifact_definition_id`, `status`
- `GET /generation-runs` returns HTTP 422 when filter values are not valid UUIDs
- `GET /generation-runs/latest` returns the most recent generation run matching the optional filters
- `GET /generation-runs/latest` returns 404 when no runs match the filter
- `GET /generation-runs/latest` returns HTTP 422 when filter values are not valid UUIDs
- All responses serialize through Pydantic schemas (no raw ORM objects in responses)
- `status` field values are documented as `{pending, running, completed, failed}`

### Test cases:
- `test_get_generation_run_success` — valid run_id returns correct run with all lifecycle fields
- `test_get_generation_run_not_found` — invalid run_id returns 404
- `test_get_generation_run_invalid_uuid` — non-UUID run_id returns 422
- `test_list_generation_runs` — returns paginated list with correct structure (`items`, `total`, `offset`, `limit`)
- `test_list_generation_runs_empty` — returns empty list with correct pagination structure when no runs exist
- `test_list_generation_runs_default_pagination` — uses default `limit=50`, `offset=0` when not specified
- `test_list_generation_runs_pagination_respected` — respects custom `limit` and `offset` params
- `test_list_generation_runs_max_limit` — rejects `limit > 100` with 422
- `test_list_generation_runs_filter_by_source` — filter by source_id works correctly
- `test_list_generation_runs_filter_by_contract` — filter by contract_id works correctly
- `test_list_generation_runs_filter_by_status` — filter by status works correctly
- `test_list_generation_runs_invalid_uuid_filter` — non-UUID filter value returns 422
- `test_list_generation_runs_ordering` — results are ordered by `created_at DESC`
- `test_get_latest_generation_run` — returns most recent run
- `test_get_latest_generation_run_not_found` — returns 404 when no runs match filter
- `test_get_latest_generation_run_with_filters` — latest with source_id and contract_id filters
- `test_get_latest_generation_run_invalid_uuid` — non-UUID filter value returns 422
- `test_generation_run_response_schema` — GenerationRunResponse has all required fields
- `test_generation_run_list_response_schema` — GenerationRunListResponse has items, total, offset, limit

### Review requirements:
- Router follows existing UKBE API patterns and conventions
- Schemas are defined separately from router logic
- No service-layer logic is duplicated in the router
- No database model changes are introduced
- Tests use existing test fixtures and follow project test conventions
- UUID validation is enforced at the API boundary (path params and filter params)
- Pagination defaults are explicit and documented
- Ordering is deterministic (`ORDER BY created_at DESC`)
- Status enum values are documented in schema module

---

## ⚠️ Risks / Blockers

### Risks (Medium)
- **Repository lacks general `list()` method** — Current repo only has `list_by_contract()`. Must add a general `list()` with dynamic filter support. This is straightforward but requires careful SQL construction for optional filters.
- **Repository lacks `get_latest()` method** — Must add new query method. Simple addition, but needs testing.
- **ORM field naming mismatch** — Response schema uses `id` but ORM uses `generation_run_id`; response uses `status` but ORM uses `run_status`. Mapping helper must handle this correctly.
- **`source_id` and `artifact_definition_id` may not exist on ORM** — The current `GenerationRunORM` has `contract_id` and `build_run_id` but may not have `source_id` or `artifact_definition_id` directly. Must verify via `contract` relationship or note as gap for follow-up task.

### Blockers (Low)
- If `source_id` or `artifact_definition_id` are not directly on the ORM, filters for those fields must either:
  - Be implemented via JOIN through the `contract` relationship (if contract has these fields)
  - Be deferred to a follow-up task with a note in the response
- No other blockers expected since this is a read-only exposure task

---

## 🔗 References
- Related docs:
  - Plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
  - Task Graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
  - Generation-run service: `ukbe/app/generation/services/generation_run_service.py`
  - Generation-run model: `ukbe/app/storage/models/generation_run.py`
- Linked review: TBD
- Supporting examples:
  - `ukbe/app/api/artifacts.py` — existing artifact router pattern
  - `ukbe/app/api/contract.py` — existing contract router pattern
  - `ukbe/app/api/build_run.py` — existing build-run read pattern

---

## 📝 Notes
- This task is narrow and read-only; it does not mutate generation-run records
- The goal is public exposure of an already-working audit surface, not redesign
- Lifecycle fields are critical for lineage tracking and must be preserved in all responses
