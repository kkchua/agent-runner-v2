# 🧩 Task Document

## 📌 Metadata
- Doc Type: 03_task
- Template Version: v1
- Task ID: TASK-20260418-02
- Plan ID: PLAN-20260418-02
- Source Task Graph ID: TASK-GRAPH-20260418-PLAN-20260418-02
- Source Task Node ID: TASK-20260418-02
- Title: Managed Generation API Trigger
- Status: COMPLETED
- Priority: high
- Assigned To: Qwen Code
- Created At: 2026-04-18
- Due At: TBD
- Review File Path: docs/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.md

---

## 🎯 Objective
Implement a public HTTP endpoint that accepts a `contract_id` and routes to `ArtifactGenerator.generate_from_contract()` for the `RUNNER_EXECUTION_OVERVIEW` artifact type. This endpoint must preserve the existing direct generation path (`/artifacts/generate`) and only target the managed runner-overview slice.

---

## 📥 Inputs
- Source plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Source task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Dependencies: None (this is an entry task in Track A)
- Required documents:
  - Existing `ArtifactGenerator.generate_from_contract()` method signature and behavior
  - Existing `/artifacts/generate` endpoint pattern for consistency
- Required data / APIs:
  - `ArtifactGenerator.generate_from_contract(contract_id, artifact_type)` — already implemented
  - `ArtifactType.RUNNER_EXECUTION_OVERVIEW` — the only allowed artifact type for this endpoint

---

## 📤 Outputs
- Expected artifacts:
  - `ukbe/app/api/artifacts.py` — extended with new managed-generation endpoint
  - `ukbe/app/api/schemas/generation.py` — request/response schemas for managed generation
  - `tests/api/test_generation_api.py` — endpoint coverage tests
- Output folder / path: `docs/delivery/03_tasks/`
- Completion evidence:
  - New endpoint is callable and returns the result of `generate_from_contract()`
  - Tests confirm the endpoint accepts `contract_id` and routes correctly
  - Existing `/artifacts/generate` endpoint remains unchanged

---

## 🧠 Implementation Details
### Technical Notes
- The `ArtifactGenerator.generate_from_contract()` method already exists and is operational
- This task adds a thin HTTP layer on top of that method — no changes to the generator itself
- The endpoint must be scoped to `RUNNER_EXECUTION_OVERVIEW` only (hard-gated)
- The endpoint should return the generated `ArtifactModel` or appropriate error responses

### API / Contract Notes
- New endpoint: `POST /artifacts/generate-managed` (route added to existing `ukbe/app/api/artifacts.py` router)
- Request body must contain: `contract_id` (string/UUID)
- Response schema — **explicit definition** (must match exactly):
  ```python
  class GenerateManagedResponse(BaseModel):
      artifact: ArtifactResponse       # full ArtifactResponse from artifacts.py
      generation_run_id: str | None    # generation-run ID if available, None otherwise
  ```
  This matches the lineage model established in TASK-01 (`ContractBuildResponse` wraps `ContractDetail` + run ID).
- Error handling — **explicit exception-to-HTTP mapping**:
  | Condition                        | HTTP Status | Notes                                    |
  | -------------------------------- | ----------- | ---------------------------------------- |
  | `contract_id` missing/invalid    | 400         | Explicit validation in route body        |
  | Contract not found               | 404         | Generator returns `None` with log `contract_not_found` |
  | Contract not frozen              | 404         | Generator returns `None` with log `contract_not_frozen` |
  | Generation failure (internal)    | 500         | Generator returns `None` for any other reason |

  **Note on 422:** Removed entirely. The client never provides `artifact_type` — it is hard-gated to `RUNNER_EXECUTION_OVERVIEW` internally. A 422 for artifact-type mismatch is an internal logic error, not a client error. Use 400/404/500 only.

### Data / Schema Notes
- Request schema in `ukbe/app/api/schemas/generation.py`:
  - `GenerateManagedRequest`: contains `contract_id` field (required, string). Use Pydantic `field_validator` to validate UUID format.
  - `GenerateManagedResponse`: wraps `ArtifactResponse` (reuse existing schema from `artifacts.py`) plus `generation_run_id: str | None`
- **UUID conversion boundary:** API receives `contract_id` as string from client. Must convert explicitly before calling generator:
  ```python
  contract_uuid = UUID(request.contract_id)
  ```
  Do NOT rely on implicit string coercion. Validate UUID format in request schema, then construct `UUID()` explicitly at the route boundary (same pattern as TASK-01).
- Reuse existing `ArtifactResponse` pattern from `artifacts.py` for consistency. The `ArtifactResponse` model already includes `generation_run_id`, `contract_id`, `build_run_id` fields.

---

## 🔧 Execution Steps
1. **Create request/response schemas** in `ukbe/app/api/schemas/generation.py`:
   - Define `GenerateManagedRequest` with required `contract_id` field (string, validated as UUID format via `field_validator`)
   - Define `GenerateManagedResponse` with explicit structure:
     ```python
     class GenerateManagedResponse(BaseModel):
         artifact: ArtifactResponse
         generation_run_id: str | None
     ```

2. **Add managed-generation endpoint** to `ukbe/app/api/artifacts.py`:
   - Create `POST /artifacts/generate-managed` route
   - Accept `GenerateManagedRequest` body
   - **Generator instantiation** — use a factory function following TASK-01 `_make_executor()` pattern:
     ```python
     def _make_generator(session: AsyncSession) -> ArtifactGenerator:
         """Instantiate ArtifactGenerator with all required dependencies."""
         from ukbe.app.generation.services.generation_run_service import GenerationRunService
         from ukbe.app.contract_builder.persistence.repository import ContractRepository
         from ukbe.app.plugin_runtime.loader import load_all_plugins
         from ukbe.app.plugin_runtime.registry import PluginRegistry

         registry = PluginRegistry()
         load_all_plugins(registry)
         generation_run_service = GenerationRunService(session)
         contract_repo = ContractRepository()
         return ArtifactGenerator(
             session=session,
             registry=registry,
             generation_run_service=generation_run_service,
             contract_repo=contract_repo,
         )
     ```
     Then in route: `generator = _make_generator(session)`
   - Convert `contract_id` to UUID explicitly: `contract_uuid = UUID(request.contract_id)`
   - Call `generator.generate_from_contract(contract_uuid, ArtifactType.RUNNER_EXECUTION_OVERVIEW)`
   - **Extract `generation_run_id` from returned artifact:**
     - `generate_from_contract()` returns `ArtifactModel | None`
     - `ArtifactModel` has `generation_run_id` attribute — extract directly: `artifact.generation_run_id`
     - If generator returns `None`, map to appropriate HTTP error (see error table below)
   - Return `GenerateManagedResponse(artifact=..., generation_run_id=...)`
   - Handle errors per the explicit mapping table above

3. **Write tests** in `tests/api/test_generation_api.py`:
   - Test successful generation with valid `contract_id` → 200 with artifact + `generation_run_id`
   - Test missing `contract_id` → 400
   - Test invalid UUID format `contract_id` → 400
   - Test non-existent contract → 404
   - Test non-frozen contract → 404
   - Test generation failure → 500
   - Test that existing `/artifacts/generate` endpoint is unaffected

4. **Verify endpoint visibility** in OpenAPI:
   - Confirm the new route appears in `/docs` Swagger UI
   - Confirm request/response schemas are documented

---

## 🧪 Validation Criteria
- Acceptance checks:
  - `POST /artifacts/generate-managed` endpoint exists and is callable
  - Endpoint accepts `contract_id` and routes to `ArtifactGenerator.generate_from_contract()`
  - Endpoint returns `GenerateManagedResponse` with explicit structure: `{artifact: ArtifactResponse, generation_run_id: str | None}`
  - Existing `/artifacts/generate` endpoint remains functional and unchanged
  - Error responses match the defined contract (400, 404, 500 — no 422)
  - Contract state validation (frozen check) is enforced by the generator, NOT duplicated in the API layer

- Test cases:
  - Valid `contract_id` + frozen contract → 200 with artifact + `generation_run_id != None`
  - Missing `contract_id` → 400 Bad Request
  - Invalid UUID format `contract_id` → 400 Bad Request
  - Non-existent contract → 404 Not Found
  - Non-frozen contract → 404 Not Found
  - Generation failure (plugin returns None) → 500 Internal Server Error
  - Existing `/artifacts/generate` → still works with `artifact_type` + `source_id`

- Review requirements:
  - No changes to `ArtifactGenerator` internals
  - No changes to `/artifacts/generate` existing route
  - Schemas follow Pydantic v2 patterns consistent with existing `ukbe/app/api/schemas/`
  - Endpoint follows FastAPI patterns consistent with existing routes in `artifacts.py`
  - UUID conversion is explicit at route boundary (`UUID(request.contract_id)`)
  - Generator instantiation uses factory function pattern (`_make_generator(session)`)
  - `generation_run_id` sourced from `artifact.generation_run_id` attribute (NOT from separate DB query)
  - Contract state validation delegated to generator — API maps `None` return to HTTP error

---

## ⚠️ Risks / Blockers
- ~~`ArtifactGenerator` requires multiple dependencies (session, registry, generation_run_service, contract_repo) — ensure they are injected correctly via FastAPI dependencies~~ **RESOLVED**: Use factory function `_make_generator(session)` with explicit instantiation — see Execution Step 2 for exact code.
- ~~Contract state validation source unclear~~ **RESOLVED**: Generator enforces frozen-check internally. API does NOT duplicate this logic. API maps `None` return from generator → appropriate HTTP error based on available context.
- If `generate_from_contract()` behavior changes upstream, this endpoint may need adjustment (but that is out of scope for this task)
- Test fixtures must include a frozen contract with valid snapshot and artifact definition

---

## 🔗 References
- Related docs:
  - Plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
  - Task Graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
  - Existing artifact generator: `ukbe/app/generation/artifact_generator.py` (`generate_from_contract` method)
  - Existing artifacts API: `ukbe/app/api/artifacts.py`
  - Existing schema patterns: `ukbe/app/api/schemas/contract_build.py`
- Linked review: TBD
- Supporting examples:
  - `POST /artifacts/generate` — existing enqueue pattern for reference
  - `POST /contract-build` — similar thin API wrapper pattern

---

## 📝 Notes
- This task is about exposure, not reinvention — the generator already works
- Keep the endpoint thin: validate input, call generator, return result
- Do NOT introduce new abstractions or service layers
- Do NOT modify the existing `/artifacts/generate` endpoint
- Router registration is handled in TASK-20260418-05 (separate task)
