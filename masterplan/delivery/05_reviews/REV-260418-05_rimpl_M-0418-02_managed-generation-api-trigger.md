# 🔍 Review: IMPL-20260418-02 — Managed Generation API Trigger

## 📌 Metadata
- Doc Type: 04_review
- Template Version: v1
- Review ID: REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger
- Related Doc Type: 04_implementation_plan
- Related Doc ID: IMPL-20260418-02
- Title: Review of Implementation Plan — Managed Generation API Trigger
- Reviewer: Qwen Code (Reviewer Agent)
- Status: approved
- Review Date: 2026-04-18

---

## 🎯 Review Objective
Evaluate the implementation plan `IMPL-20260418-02_managed-generation-api-trigger.md` for scope accuracy, dependency correctness, completeness, readiness for execution, and alignment with the approved task document `TASK-20260418-02` and task graph `TASK-GRAPH-20260418-PLAN-20260418-02`. Specifically assess whether the plan over-assumes existing codebase/schema/API details or introduces speculative technical design beyond verified upstream artifacts.

---

## 📄 Summary of Reviewed Content
The implementation plan defines a thin HTTP endpoint (`POST /artifacts/generate-managed`) that accepts a `contract_id` and delegates to the existing `ArtifactGenerator.generate_from_contract()` method, hard-gated to `ArtifactType.RUNNER_EXECUTION_OVERVIEW`. The plan specifies:
- New request/response schemas in `ukbe/app/api/schemas/generation.py`
- A new route in `ukbe/app/api/artifacts.py` with a factory function `_make_generator(session)`
- Endpoint coverage tests in `tests/api/test_generation_api.py`
- Explicit UUID conversion at the route boundary
- Error mapping (400/404/500, no 422)
- Reuse of existing `ArtifactResponse`, `_artifact_response()`, and factory patterns

---

## ✅ Strengths
- **Grounded in verified upstream artifacts**: The plan correctly identifies `ArtifactGenerator.generate_from_contract(contract_id: str, artifact_type: str | ArtifactType) -> ArtifactModel | None` — confirmed in `artifact_generator.py` line 164-167.
- **`ArtifactModel` has `generation_run_id` field**: Confirmed in `ukbe/app/core/canonical/models.py` line 139 — the plan correctly sources `generation_run_id` from `artifact.generation_run_id` without a separate DB query.
- **`ArtifactType.RUNNER_EXECUTION_OVERVIEW` exists**: Confirmed in `ukbe/app/core/canonical/enums.py` — the enum value `RUNNER_EXECUTION_OVERVIEW = "runner_execution_overview"` is present.
- **`ArtifactResponse` already includes lineage FK fields**: Confirmed in `ukbe/app/api/artifacts.py` — `generation_run_id`, `contract_id`, `build_run_id`, `artifact_definition_id` are all present.
- **`_artifact_response()` maps all lineage FK fields via `getattr()`**: Confirmed in `ukbe/app/api/artifacts.py` — the helper already handles `generation_run_id`, `contract_id`, `build_run_id`, `artifact_definition_id`.
- **Factory pattern follows verified precedent**: The `_make_executor(session)` pattern in `contract_build.py` is correctly referenced as the template for `_make_generator(session)`.
- **Scope is tightly bounded**: The plan explicitly excludes changes to `ArtifactGenerator` internals, existing `/artifacts/generate` endpoint, and router registration (deferred to TASK-20260418-05).
- **Error mapping aligns with generator behavior**: The plan correctly maps `None` returns from `generate_from_contract()` to HTTP errors, matching the generator's internal logging keys (`contract_not_found`, `contract_not_frozen`).
- **Test plan mirrors verified patterns**: The test structure follows `test_contract_build_api.py` conventions (isolated app, factory monkeypatching, `TestClient` usage).

---

## ❌ Issues Identified
| Issue | Severity | Recommendation |
|---|---|---|
| Plan states "422 removed entirely" but UUID format validation via Pydantic `field_validator` will still produce 422 if FastAPI's default validation exception handler is not overridden | medium | Either override FastAPI's default validation exception handler for this route to map 422 → 400, or accept that malformed UUID strings will return 422 (FastAPI default). The task contract says "no 422" but Pydantic UUID validation will produce 422 unless explicitly suppressed. Clarify in plan whether a custom exception handler will be added or whether UUID format validation should be done manually in route body (returning 400). |
| `_make_generator()` factory must assemble `ArtifactGenerator` with all dependencies — plan lists parameters but does not explicitly verify the actual `__init__` signature matches | low | The plan correctly includes this as a risk mitigation step ("Inspect `artifact_generator.py` `__init__` signature before implementing"). The actual `__init__` signature (confirmed in `artifact_generator.py` lines 37-51) includes `session`, `registry`, `generation_run_service`, `contract_repo`, and optional `llm_service`, `prompt_builder`, `schema_validator`. The factory as proposed in the plan only passes the first four — this is sufficient since the optional params have defaults. No action needed, but executor should verify. |
| Plan proposes inspecting structlog for error context when generator returns `None` — structlog is not easily inspectable from the route handler | low | The generator logs error context (`contract_not_found`, `contract_not_frozen`) but these are not returned to the caller. The plan acknowledges this risk and provides a fallback ("default to 500 for all `None` returns"). Executor should implement a simpler approach: return 404 for `None` with a generic "contract not available" message, or 500 if the failure reason is unclear. |

---

## 🔧 Suggested Improvements
- Consider adding a custom FastAPI exception handler for `RequestValidationError` scoped to this route only, mapping UUID format validation errors to HTTP 400 instead of 422 — or perform UUID validation manually in the route body using `try/except ValueError` on `UUID(request.contract_id)`.
- The `_make_generator()` factory should be documented with a comment noting that `ArtifactGenerator.__init__` has optional parameters (`llm_service`, `prompt_builder`, `schema_validator`) that are not needed for managed generation and should be left as defaults.

---

## 📏 Validation Against Acceptance Criteria
| Criterion | Result | Notes |
|---|---|---|
| Plan aligns with TASK-20260418-02 scope | pass | Endpoint accepts `contract_id`, routes to `generate_from_contract()`, hard-gated to `RUNNER_EXECUTION_OVERVIEW` |
| Plan preserves existing `/artifacts/generate` | pass | Explicitly excluded from modifications |
| File plan is complete | pass | Three files: new schemas, modified artifacts.py, new tests |
| Reuse strategy is defined | pass | Reuses `ArtifactResponse`, `_artifact_response()`, factory pattern, test patterns |
| No speculative upstream assumptions | pass | All referenced methods, fields, and enums confirmed in codebase |
| Error mapping is defined | pass | 400/404/500 mapping documented; 422 handling needs minor clarification (see issues) |
| Test plan covers success and error paths | pass | Six test cases covering all defined error conditions + existing endpoint preservation |
| Dependencies correctly identified | pass | No hard dependencies; reference implementations correctly identified as non-blocking |
| Router registration deferred correctly | pass | Explicitly excluded and assigned to TASK-20260418-05 |
| `generation_run_id` sourcing is correct | pass | Sourced from `artifact.generation_run_id` — confirmed present in `ArtifactModel` |

---

## 📊 Final Decision
- Decision: approved
- Rationale: The implementation plan is executor-ready and technically grounded in verified upstream artifacts. All referenced methods (`generate_from_contract`), enums (`ArtifactType.RUNNER_EXECUTION_OVERVIEW`), model fields (`generation_run_id`), schema patterns (`ArtifactResponse`), and factory patterns (`_make_executor`) have been confirmed in the actual codebase. The plan is narrowly scoped, correctly defers router registration, and provides a complete file plan, data flow, reuse strategy, and test plan. One minor issue (422 vs 400 for UUID validation) is identified but is an implementation detail that the executor can resolve by performing manual UUID validation in the route body rather than relying on Pydantic field validators.
- Required next action: Proceed to implementation. Executor should verify `ArtifactGenerator.__init__` signature before implementing `_make_generator()` and handle UUID validation manually to avoid FastAPI 422 responses.

---

## 🔗 References
- Reviewed document: `docs/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.md`
- Governing task: `docs/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.md`
- Governing task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Verified upstream code:
  - `ukbe/app/generation/artifact_generator.py` — `generate_from_contract()` signature (line 164), `__init__` (line 37), error logging keys
  - `ukbe/app/api/artifacts.py` — `ArtifactResponse`, `_artifact_response()`, existing routes
  - `ukbe/app/core/canonical/models.py` — `ArtifactModel.generation_run_id` (line 139)
  - `ukbe/app/core/canonical/enums.py` — `ArtifactType.RUNNER_EXECUTION_OVERVIEW`
  - `ukbe/app/api/contract_build.py` — `_make_executor()` factory pattern
  - `tests/api/test_contract_build_api.py` — test helper patterns

---

## 📝 Notes
- This review validates the implementation plan's technical grounding, not the implementation itself.
- The 422-vs-400 issue for UUID validation is an implementation-level detail — the plan should note that manual UUID validation in the route body (via `try/except ValueError`) avoids FastAPI's default 422 responses.
- The `_make_generator()` factory should match the actual `ArtifactGenerator.__init__` signature, which has been verified and is compatible with the plan's proposed parameters.
- New review docs under `docs/delivery/05_reviews/` use the `REV-{YYMMDD}-{SEQ}_{STEP}_{TID}_{slug}.md` naming contract.
