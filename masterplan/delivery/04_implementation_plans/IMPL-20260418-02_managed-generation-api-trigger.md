# 📋 Implementation Plan: TASK-20260418-02 — Managed Generation API Trigger

---

## 📌 Metadata

* **Doc Type:** 04_implementation_plan
* **Template Version:** v1
* **Plan ID:** PLAN-20260418-02
* **Task ID:** TASK-20260418-02
* **Title:** Managed Generation API Trigger
* **Status:** APPROVED
* **Created At:** 2026-04-18
* **Author:** implementation_planner

---

## 🎯 Objective

Implement a thin HTTP endpoint (`POST /artifacts/generate-managed`) that accepts a `contract_id` and routes to the existing `ArtifactGenerator.generate_from_contract()` method, hard-gated to `ArtifactType.RUNNER_EXECUTION_OVERVIEW`. The endpoint must preserve the existing `/artifacts/generate` path unchanged and return a structured response wrapping the generated artifact plus the generation-run ID.

This is an exposure task — the generator already works. The implementation adds a validated HTTP surface on top of it.

---

## 📥 Inputs

| Type           | Reference            |
| -------------- | -------------------- |
| Task Document  | `docs/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.md` |
| Plan Document  | `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md` |
| Dependencies   | None (entry task in Track A) |
| Reference Code | `ukbe/app/generation/artifact_generator.py` (`generate_from_contract` method) |
| Reference Code | `ukbe/app/api/artifacts.py` (existing routes, `ArtifactResponse` schema) |
| Reference Code | `ukbe/app/api/contract_build.py` (factory pattern `_make_executor`, error mapping) |
| Reference Code | `ukbe/app/api/schemas/contract_build.py` (Pydantic v2 schema patterns) |
| Reference Code | `ukbe/app/core/canonical/models.py` (`ArtifactModel` with `generation_run_id` field) |
| Reference Code | `ukbe/app/core/canonical/enums.py` (`ArtifactType.RUNNER_EXECUTION_OVERVIEW`) |

---

## 📤 Outputs

| Artifact   | Path       | Description       |
| ---------- | ---------- | ----------------- |
| `ukbe/app/api/schemas/generation.py` | [NEW] | Request/response schemas for managed generation |
| `ukbe/app/api/artifacts.py` | [MODIFY] | Add `POST /artifacts/generate-managed` endpoint |
| `tests/api/test_generation_api.py` | [NEW] | Endpoint coverage tests |

---

## 🧠 Scope Clarification

### ✅ Included

* New request schema `GenerateManagedRequest` with required `contract_id` field (string, validated as UUID format)
* New response schema `GenerateManagedResponse` wrapping `ArtifactResponse` (reuse from `artifacts.py`) plus `generation_run_id: str | None`
* New route `POST /artifacts/generate-managed` added to existing `artifacts.py` router
* Factory function `_make_generator(session)` for `ArtifactGenerator` instantiation (following `_make_executor()` pattern from `contract_build.py`)
* Explicit UUID conversion at route boundary: `UUID(request.contract_id)`
* Error mapping: 400 (invalid/missing contract_id), 404 (contract not found / not frozen), 500 (generation failure)
* Tests for all error paths and successful generation
* Tests confirming existing `/artifacts/generate` endpoint remains unaffected

### ❌ Excluded

* Changes to `ArtifactGenerator` internals (generator is operational — do not modify)
* Changes to existing `/artifacts/generate` endpoint (preserve as-is)
* Support for artifact types other than `RUNNER_EXECUTION_OVERVIEW` (hard-gated)
* New service layers, abstractions, or persistence changes
* Contract state validation logic (delegated to generator — API maps `None` return to HTTP error)
* Router registration in master API router (handled in TASK-20260418-05)
* 422 error responses (task contract explicitly removes 422 — use 400/404/500 only)

---

## 📦 File Plan (MANDATORY)

```text
ukbe/
├── app/
│   └── api/
│       ├── artifacts.py              [MODIFY] — add managed generation endpoint + factory
│       └── schemas/
│           └── generation.py         [NEW] — request/response schemas for managed generation
│
tests/
└── api/
    └── test_generation_api.py        [NEW] — endpoint coverage tests
```

---

## 🧩 Module Responsibilities

### `ukbe/app/api/schemas/generation.py`

* **Responsibility:** Define Pydantic v2 request/response schemas for the managed generation endpoint
* **Key behavior:**
  - `GenerateManagedRequest`: contains `contract_id` field (string, required), with `field_validator` to validate UUID format
  - `GenerateManagedResponse`: wraps `ArtifactResponse` (imported from `artifacts.py`) plus `generation_run_id: str | None`
  - Use `ConfigDict(from_attributes=True)` consistent with existing schema patterns in `contract_build.py`

### `ukbe/app/api/artifacts.py` (extended)

* **Responsibility:** Host the new `POST /artifacts/generate-managed` route alongside existing artifact routes
* **Key behavior:**
  - Factory function `_make_generator(session: AsyncSession)` — instantiate `ArtifactGenerator` with all required dependencies (session, registry, generation_run_service, contract_repo)
  - Route handler: validate input, convert `contract_id` to UUID explicitly, call generator, map result to response
  - Error handling: map generator `None` return to appropriate HTTP status (404 for contract not found / not frozen, 500 for other failures)
  - Do NOT modify existing routes (`list_artifacts`, `get_artifact`, `generate_artifact`, `get_artifact_reasoning`)

### `tests/api/test_generation_api.py`

* **Responsibility:** Validate the new endpoint behaves correctly across success and error paths
* **Key behavior:**
  - Test successful generation with valid frozen contract → 200 with artifact + `generation_run_id`
  - Test missing `contract_id` → 400
  - Test invalid UUID format `contract_id` → 400
  - Test non-existent contract → 404
  - Test non-frozen contract → 404
  - Test generation failure (plugin returns None) → 500
  - Test existing `/artifacts/generate` endpoint remains functional

---

## ♻️ Reuse Strategy (CRITICAL)

| Component    | Location | Usage        |
| ------------ | -------- | ------------ |
| `ArtifactResponse` | `ukbe/app/api/artifacts.py` | Reuse as `artifact` field type in `GenerateManagedResponse` — already includes all lineage FK fields |
| `ArtifactGenerator.generate_from_contract()` | `ukbe/app/generation/artifact_generator.py` | Call directly — accepts `contract_id` (str), `artifact_type` (str | ArtifactType), returns `ArtifactModel | None` |
| `_artifact_response()` | `ukbe/app/api/artifacts.py` | Reuse to map `ArtifactModel` → `ArtifactResponse` Pydantic model |
| `ArtifactType.RUNNER_EXECUTION_OVERVIEW` | `ukbe/app/core/canonical/enums.py` | Hard-gate — pass as fixed `artifact_type` to generator |
| Factory pattern `_make_executor()` | `ukbe/app/api/contract_build.py` | Follow same pattern for `_make_generator(session)` — explicit dependency assembly |
| Pydantic v2 schema patterns | `ukbe/app/api/schemas/contract_build.py` | Use same `ConfigDict(from_attributes=True)`, `field_validator` patterns |
| Test helper patterns | `tests/api/test_contract_build_api.py` | Reuse `_make_app()` pattern (isolated FastAPI app with single router), `TestClient` usage |

Rules:

* Prefer reuse over reimplementation — do not recreate `ArtifactResponse` or `_artifact_response()`
* Only create new logic where no reusable component exists (schemas, route, tests)

---

## 🔄 Data Flow

```text
Client POST /artifacts/generate-managed
  → FastAPI validates GenerateManagedRequest body (contract_id string, UUID format validated)
  → Route handler extracts contract_id string
  → Explicit UUID() conversion at route boundary: contract_uuid = UUID(request.contract_id)
  → Factory: _make_generator(session) → ArtifactGenerator(session, registry, generation_run_service, contract_repo)
  → Call generator.generate_from_contract(contract_uuid, ArtifactType.RUNNER_EXECUTION_OVERVIEW)
  → Generator returns ArtifactModel | None
  → If None:
      → Inspect structlog for error context (contract_not_found, contract_not_frozen, other)
      → Map to HTTP 404 (contract not found / not frozen) or 500 (other failure)
  → If ArtifactModel:
      → Extract generation_run_id from artifact.generation_run_id attribute
      → Map ArtifactModel → ArtifactResponse via _artifact_response()
      → Return GenerateManagedResponse(artifact=..., generation_run_id=...)
```

Logical sequence:

1. Receive HTTP request with `contract_id` in body
2. Validate `contract_id` is present and matches UUID format (Pydantic `field_validator`)
3. Convert `contract_id` string to `UUID` explicitly at route boundary
4. Instantiate `ArtifactGenerator` via factory function with session-scoped dependencies
5. Delegate to `generate_from_contract(contract_uuid, ArtifactType.RUNNER_EXECUTION_OVERVIEW)`
6. Generator performss: contract lookup → frozen check → snapshot load → plugin execution → artifact persistence
7. If generator returns `None`: inspect available error context, map to appropriate HTTP error (404 or 500)
8. If generator returns `ArtifactModel`: extract `generation_run_id` from artifact attribute, map to `ArtifactResponse`, return wrapped response
9. Log outcome

---

## 🧪 Test Plan

### Test Files

```text
tests/api/test_generation_api.py
```

### Test Cases

* Successful generation with valid frozen contract → 200 with `artifact` (ArtifactResponse shape) and `generation_run_id` populated
* Missing `contract_id` in request body → 400 Bad Request
* Invalid UUID format `contract_id` (e.g., `"not-a-uuid"`) → 400 Bad Request
* Non-existent contract ID → 404 Not Found
* Non-frozen contract (draft status) → 404 Not Found
* Generation failure (plugin returns None for internal error) → 500 Internal Server Error
* Existing `/artifacts/generate` endpoint remains callable with `artifact_type` + `source_id` — unaffected by new route

### Test Constraints

* Use isolated FastAPI app with only the `artifacts` router included (follow `_make_app()` pattern from `test_contract_build_api.py`)
* Mock `ArtifactGenerator.generate_from_contract()` via monkeypatch on `_make_generator` factory — do not invoke real generator
* Mock `ArtifactRepo` and `ContractRepository` only if needed for factory construction — inspect `contract_build.py` for dependency assembly approach
* Deterministic fixtures only — no external dependencies beyond test database fixtures
* Use `unittest.mock.MagicMock` / `AsyncMock` consistent with existing test patterns

---

## 🔒 Constraints

* Do NOT modify `ArtifactGenerator` internals — `generate_from_contract()` is operational
* Do NOT modify existing `/artifacts/generate` endpoint — preserve as-is
* Do NOT introduce new architecture layers or service abstractions
* Do NOT duplicate contract state validation logic — generator enforces frozen-check internally
* Must follow task scope strictly — only `RUNNER_EXECUTION_OVERVIEW` artifact type supported
* Must maintain compatibility with existing `ArtifactResponse` schema pattern
* Router registration in master API router is handled in TASK-20260418-05 (separate task)

---

## ⚠️ Risks & Mitigations

| Risk       | Impact     | Mitigation     |
| ---------- | ---------- | -------------- |
| `ArtifactGenerator` constructor dependencies may have changed since last inspection | Medium | Inspect `artifact_generator.py` `__init__` signature before implementing `_make_generator()` — adapt factory to match actual parameters |
| `_artifact_response()` helper may not handle all `ArtifactModel` fields | Low | Inspect `_artifact_response()` in `artifacts.py` — confirm it maps `generation_run_id`, `contract_id`, `build_run_id`, `artifact_definition_id` fields |
| Error context from generator `None` return may not be easily inspectable | Medium | Generator logs error context via structlog — inspect available log keys (`contract_not_found`, `contract_not_frozen`) to determine HTTP mapping strategy. If context is not available, default to 500 for all `None` returns |
| `ArtifactType.RUNNER_EXECUTION_OVERVIEW` enum value may differ from expected | Low | Inspect `ukbe/app/core/canonical/enums.py` to confirm exact enum name and value before use |
| Test monkeypatching of `_make_generator` may not isolate generator correctly | Medium | Follow the exact monkeypatch pattern from `test_contract_build_api.py` (e.g., `monkeypatch.setattr("ukbe.app.api.artifacts._make_generator", lambda session: mock_generator)`) |

---

## 📦 Dependencies

* None (this is an entry task in Track A)
* Reference implementations (not dependencies):
  - `ukbe/app/api/contract_build.py` — factory pattern, error mapping, test structure
  - `ukbe/app/api/schemas/contract_build.py` — Pydantic schema patterns
  - `tests/api/test_contract_build_api.py` — test helper patterns, mock setup

---

## 🧾 Notes

* This task is about exposure, not reinvention — the generator already works for `RUNNER_EXECUTION_OVERVIEW`
* The endpoint is intentionally thin: validate input, call generator, return result
* Error mapping uses 400/404/500 only — no 422, as the client never provides `artifact_type` (it is hard-gated internally)
* UUID conversion is explicit at route boundary (`UUID(request.contract_id)`) — do not rely on implicit string coercion
* `generation_run_id` is sourced from `artifact.generation_run_id` attribute (confirmed present in `ArtifactModel` at line 139 of `models.py`) — no separate DB query needed
* Contract state validation (frozen check) is enforced by the generator — the API layer does NOT duplicate this logic
* The `_make_generator()` factory should assemble dependencies explicitly (session, PluginRegistry, load_all_plugins, GenerationRunService, ContractRepository) — inspect `artifact_generator.py` `__init__` to confirm required parameters before implementation

---

## ✅ Ready for Execution

This plan is ready for the Executor agent if:

* File plan is complete
* Scope is clearly bounded
* Reuse strategy is defined
* No ambiguity remains
