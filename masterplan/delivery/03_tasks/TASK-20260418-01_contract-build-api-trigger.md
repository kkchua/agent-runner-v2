# 🧩 Task

## 📌 Metadata
- Doc Type: 03_task
- Template Version: v1
- Task ID: TASK-20260418-01
- Plan ID: PLAN-20260418-02
- Title: Contract Build API Trigger
- Status: COMPLETED
- Priority: high
- Assigned To: Qwen
- Created At: 2026-04-18
- Due At: TBD
- Source Task Graph ID: TASK-GRAPH-20260418-PLAN-20260418-02
- Source Task Node ID: TASK-20260418-01
- Review File Path: docs/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.md

---

## 🎯 Objective
Implement a public HTTP endpoint that triggers the contract build process by delegating to the existing `ContractBuildExecutor.execute_contract_build()` service method. The endpoint must accept snapshot ID, artifact definition ID, and source ID, and return the persisted contract response.

---

## 📥 Inputs
- Source plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Source task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Dependencies: None (entry task)
- Required documents:
  - `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Required data / APIs:
  - `ContractBuildExecutor.execute_contract_build(snapshot_id, artifact_definition_id, source_id)` — existing service method
  - `ukbe/app/storage/database.py` — `get_db` session dependency
  - Existing FastAPI router patterns from `ukbe/app/api/contract.py` and `ukbe/app/api/build_run.py`

---

## 📤 Outputs
- Expected artifacts:
  - `ukbe/app/api/contract_build.py` — contract-build router implementation
  - `ukbe/app/api/schemas/contract_build.py` — request/response Pydantic schemas
  - `tests/api/test_contract_build_api.py` — endpoint coverage tests
- Output folder / path: `docs/delivery/03_tasks/`
- Completion evidence:
  - Tests pass: `pytest tests/api/test_contract_build_api.py -v`
  - Endpoint is reachable via the API when router is registered (registration will be done in TASK-20260418-05)

---

## 🧠 Implementation Details
### Technical Notes
- The endpoint must reuse the existing `ContractBuildExecutor.execute_contract_build()` method — do NOT reimplement the build pipeline.
- The executor expects `snapshot_id`, `artifact_definition_id`, and `source_id` as UUIDs.
- The executor already creates build-run records and persists the contract; the API layer only needs to invoke it and serialize the result.
- Follow the existing API patterns in `ukbe/app/api/contract.py` for response serialization and error handling.

### API / Contract Notes
- Method: `POST`
- Path: `/contract-build` (router prefix: `""`, tags: `["contract-build"]`)
- Request body: JSON with `snapshot_id`, `artifact_definition_id`, `source_id` (all UUID strings)
- Response schema — **explicit definition** (must match exactly):
  ```python
  class ContractBuildResponse(BaseModel):
      contract: ContractDetail       # full ContractDetail from schemas/contract.py
      build_run_id: str | None       # build-run ID if available, None otherwise
  ```
- Error responses — **explicit exception-to-HTTP mapping**:
  | Exception                | HTTP Status | Notes                                    |
  | ------------------------ | ----------- | ---------------------------------------- |
  | `RequestValidationError` | 422         | FastAPI auto-handles Pydantic request validation errors. Do NOT override — accept 422 as the canonical code for bad request body. |
  | `BudgetExceededError`    | 500         | Budget validation failed                 |
  | `ContractAssemblyError`  | 500         | Contract assembly failed                 |
  | `ContractPersistenceError` | 500       | Contract persistence failed              |
  | `Exception` (fallback)   | 500         | Catch-all: `raise HTTPException(status_code=500, detail=str(e))` |

  **Note on 400 vs 422:** FastAPI automatically returns 422 for `RequestValidationError` (bad request body, invalid UUID format, missing fields). Do NOT catch and re-raise as 400 — let FastAPI handle it. Only explicit 400 raises are for business-logic validation failures (not applicable in this thin passthrough endpoint).

### Data / Schema Notes
- **UUID conversion boundary:** API receives UUID strings from client. Must convert explicitly before calling executor:
  ```python
  snapshot_uuid = UUID(request.snapshot_id)
  artifact_def_uuid = UUID(request.artifact_definition_id)
  source_uuid = UUID(request.source_id)
  ```
  Do NOT rely on implicit string-to-UUID conversion. Let Pydantic validate format, then construct `UUID()` explicitly at the route boundary.
- Request schema must validate that all three IDs are valid UUID strings via Pydantic `UUID4` field type.
- Response schema: `ContractBuildResponse` wraps `ContractDetail` (reuse existing schema from `ukbe/app/api/schemas/contract.py`) plus optional `build_run_id`.
- Do NOT create new ORM models or database tables — this is a thin API layer over existing service behavior.

### Allowed & Forbidden Calls
- ALLOWED: Call `ContractBuildExecutor.execute_contract_build()` with the three UUID parameters.
- ALLOWED: Use `get_db` session for dependency injection.
- FORBIDDEN: Do NOT call any other service methods beyond the executor.
- FORBIDDEN: Do NOT modify `ContractBuildExecutor` or any service-layer code.
- FORBIDDEN: Do NOT create new repository methods — use existing ones only.

---

## 🔧 Execution Steps
1. Create `ukbe/app/api/schemas/contract_build.py` with request and response Pydantic models:
   - `ContractBuildRequest`: validates `snapshot_id`, `artifact_definition_id`, `source_id` as UUID strings using Pydantic `UUID4` field type
   - `ContractBuildResponse`: wraps `ContractDetail` plus `build_run_id: str | None`
2. Create `ukbe/app/api/contract_build.py` with a POST route:
   - Accept `ContractBuildRequest` body
   - **Executor instantiation** — use a factory function following `build_run.py` pattern:
     ```python
     def _make_executor(session: AsyncSession) -> ContractBuildExecutor:
         """Instantiate ContractBuildExecutor with all required dependencies."""
         # Follow existing patterns from ukbe/app/api/build_run.py _make_service()
         # All dependencies are injected via constructor; no global singletons.
         # See ukbe/app/contract_builder/services/__init__.py for available services.
         ...
     ```
     Then in route: `executor = _make_executor(session)`
   - Convert UUID strings to `UUID` explicitly: `UUID(request.snapshot_id)` etc.
   - Call `execute_contract_build()` with the three UUIDs
   - **Extract `build_run_id` from returned contract:**
     - `execute_contract_build()` returns `ArtifactContractORM` which has `build_runs` relationship loaded
     - Extract via: `contract.build_runs[-1].build_run_id if contract.build_runs else None`
     - The executor creates the build-run AFTER persistence, so the relationship should be populated
     - If `build_runs` is empty (e.g. `build_run_service` is `None` in executor), return `build_run_id=None`
     - Do NOT query the database as a fallback — the executor is the sole producer of build-run records
   - Return `ContractBuildResponse(contract=..., build_run_id=...)`
   - Handle known exceptions with explicit HTTP status codes per mapping table above
   - Catch-all: `except Exception as e: raise HTTPException(status_code=500, detail=str(e))`
3. Create `tests/api/test_contract_build_api.py`:
   - Test successful build returns 200 with contract detail and `build_run_id != None`
   - Test invalid/missing UUIDs returns 422 (FastAPI auto-handled)
   - Test executor raises `BudgetExceededError` returns 500
   - Test executor raises `ContractAssemblyError` returns 500
   - Test executor raises `ContractPersistenceError` returns 500
   - Use existing test fixtures and mock patterns from `tests/api/`
   - **Additional test requirements:**
     - ✅ Build-run linkage test: assert `response.build_run_id is not None`
     - ⚠️ Idempotency test (aspirational, NOT enforced): Same input → same contract hash is a **good goal but NOT guaranteed in v1**. Deterministic selection, deterministic snapshot, and no timestamp variance are prerequisites. If the current pipeline does not guarantee these, SKIP this test. Do NOT enforce strict hash equality unless the pipeline is confirmed deterministic.
     - ✅ DB persistence verification: contract exists after successful build

---

## 🧪 Validation Criteria
- Acceptance checks:
  - `ukbe/app/api/contract_build.py` exists and defines a POST route at `/contract-build`
  - `ukbe/app/api/schemas/contract_build.py` exists with `ContractBuildRequest` and `ContractBuildResponse` models
  - `ContractBuildResponse` has explicit structure: `{contract: ContractDetail, build_run_id: str | None}`
  - `tests/api/test_contract_build_api.py` exists and covers success, invalid input, and executor failure cases
  - Endpoint delegates to `ContractBuildExecutor.execute_contract_build()` without reimplementation
  - No new database models, repository methods, or service-layer changes introduced
  - Exception-to-HTTP mapping matches the defined table (422 for validation, 500 for pipeline errors)
- Test cases:
  - POST `/contract-build` with valid UUIDs returns 200 and contract detail
  - POST `/contract-build` with missing/invalid UUIDs returns 422 (FastAPI auto-handled)
  - POST `/contract-build` when executor raises BudgetExceededError returns 500
  - POST `/contract-build` when executor raises ContractAssemblyError returns 500
  - POST `/contract-build` when executor raises ContractPersistenceError returns 500
  - ✅ Build-run linkage: `response.build_run_id is not None` on success
  - ✅ Idempotency (optional): same input → same contract hash
- Review requirements:
  - Code follows existing patterns in `ukbe/app/api/contract.py` and `ukbe/app/api/build_run.py`
  - Schemas follow existing Pydantic v2 patterns with `ConfigDict(from_attributes=True)`
  - Tests use existing fixture patterns from `tests/conftest.py`
  - UUID conversion is explicit at route boundary (`UUID(request.snapshot_id)`)
  - Executor instantiation uses factory function pattern (`_make_executor(session)`)
  - `build_run_id` sourced from `contract.build_runs` relationship (NOT from separate DB query)
  - Idempotency test is aspirational only — skip if pipeline is not deterministic

---

## ⚠️ Risks / Blockers
- ~~Risk: `ContractBuildExecutor` may require complex dependency injection that is not yet exposed at the API layer.~~ **RESOLVED**: Use factory function `_make_executor(session)` following `build_run.py` `_make_service()` pattern. Inspect `ukbe/app/contract_builder/services/__init__.py` for all required dependencies.
- ~~Risk: UUID serialization between Pydantic request and service layer may mismatch.~~ **RESOLVED**: Explicit `UUID()` conversion at route boundary — no implicit conversion.
- Blocker: None expected — this is an entry task with no dependencies.

---

## 🔗 References
- Related docs:
  - `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
  - `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Linked review: TBD
- Supporting examples:
  - `ukbe/app/api/contract.py` — existing contract read API patterns
  - `ukbe/app/api/build_run.py` — existing build-run read API patterns
  - `ukbe/app/api/schemas/contract.py` — existing contract schema patterns
  - `ukbe/app/api/schemas/build_run.py` — existing build-run schema patterns
  - `ukbe/app/contract_builder/services/contract_build_executor.py` — existing executor method

---

## 📝 Notes
- This task is intentionally narrow: it exposes the already-working `ContractBuildExecutor` through a public HTTP endpoint.
- Router registration will be handled in TASK-20260418-05; this task only creates the router module.
- The endpoint must not change executor behavior — it is a thin passthrough layer.
- **Architectural note:** This is the **first public entry point** into the builder pipeline. Later, the runner should call this API (not internal services) for audit consistency and observability.
- **Test strategy upgrade:** Beyond basic success/failure cases, tests must verify build-run linkage, idempotency (optional), and DB persistence.
