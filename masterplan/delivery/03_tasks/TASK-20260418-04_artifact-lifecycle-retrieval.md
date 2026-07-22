# 🧩 Task: Artifact Lifecycle Retrieval

## 📌 Metadata
- Doc Type: 03_task
- Template Version: v1
- Task ID: TASK-20260418-04
- Plan ID: PLAN-20260418-02
- Source Task Graph ID: TASK-GRAPH-20260418-PLAN-20260418-02
- Source Task Node ID: TASK-20260418-04
- Review File Path:
- Title: Artifact Lifecycle Retrieval
- Status: COMPLETED
- Priority: medium
- Assigned To: Qwen Code
- Created By: codex
- Created At: 2026-04-19
- Due At: TBD

---

## 🎯 Objective
Deliver read-only artifact lifecycle retrieval for the already-persisted managed slice. The task must expose three public retrieval capabilities through a dedicated router module and a matching repository layer:

1. Retrieve a single artifact by `generation_run_id`.
2. Retrieve the latest artifact for an `artifact_definition_id`.
3. Retrieve the full artifact history for an `artifact_definition_id`, newest first.

This task is limited to lifecycle-aware retrieval only. It does not change artifact generation, artifact persistence shape, or master router registration.

---

## 📥 Inputs
- Source plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Source task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Dependencies: None
- Required documents:
  - `ukbe/app/api/artifacts.py` - existing artifact response mapping and route conventions
  - `ukbe/app/api/schemas/artifacts.py` - existing `ArtifactResponse` contract
  - `ukbe/app/storage/repositories/artifact_repo.py` - existing artifact persistence/read patterns
  - `docs/architecture/07_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V4_2026-04-18.md` - lifecycle retrieval gap definition
  - `docs/architecture/08_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V5_2026-04-18.md` - updated lifecycle retrieval target state
- Required data / APIs:
  - `ArtifactRepo.get_artifact()`
  - `ArtifactRepo.list_by_artifact_definition_id()`
  - Existing `ArtifactResponse` shape, including lineage fields
  - `ArtifactRepo.get_by_generation_run_id(run_id) -> ArtifactORM | None`
  - `ArtifactRepo.get_latest_by_definition_id(definition_id) -> ArtifactORM | None`
  - `ArtifactRepo.list_by_definition_id(definition_id) -> list[ArtifactORM]`

---

## 📤 Outputs
- Expected artifacts:
  - `docs/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.md`
  - `docs/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json`
  - `ukbe/app/api/artifact_history.py`
  - `ukbe/app/storage/repositories/artifact_repo.py`
  - `tests/api/test_artifact_history_api.py`
- Output folder / path:
  - `docs/delivery/03_tasks/`
  - `ukbe/app/api/`
  - `ukbe/app/storage/repositories/`
  - `tests/api/`
- Completion evidence:
  - The router module imports cleanly.
  - The repository module exposes the lifecycle read helpers needed by the router.
  - The API tests cover successful retrieval, missing-record 404s, invalid UUID 422s, and history ordering.

---

## 🧠 Implementation Details
### Technical Notes
- Required capabilities:
  - The new router module must be self-contained and read-only.
  - The router must use the existing `ArtifactResponse` contract; no new response models are allowed.
  - `GET /artifacts/by-run/{run_id}` must return the artifact linked to the provided generation run.
  - `GET /artifacts/by-definition/{definition_id}/latest` must return the newest artifact for that definition.
  - `GET /artifacts/by-definition/{definition_id}/history` must return all matching artifacts ordered newest first.
  - `history` is a collection response and must return `200` with an empty list when no artifacts match.
  - `latest` and `by-run` are singular lookups and must return `404` when no artifact matches.
  - `run_id` and `definition_id` path parameters must be validated as UUID strings at the route boundary and return `422` on invalid input.

### API / Contract Notes
- The router prefix must be `/artifacts`.
- The router tag must be `artifacts`.
- The route set in this task is limited to:
  - `GET /artifacts/by-run/{run_id}`
  - `GET /artifacts/by-definition/{definition_id}/latest`
  - `GET /artifacts/by-definition/{definition_id}/history`
- The allowed call order inside each handler is:
  1. Validate the path parameter.
  2. Call the read-only repository helper.
  3. Map the ORM object(s) to `ArtifactResponse`.
  4. Return the HTTP response.
- Forbidden calls in this task:
  - No generation or persistence writes.
  - No contract lookup.
  - No generation-run service calls.
  - No master API router registration.
  - No new DTOs or schema objects.

### Data / Schema Notes
- `by-run` must resolve from the existing `generation_run_id` lineage field on artifacts.
- `latest` and `history` must resolve from the existing `artifact_definition_id` lineage field on artifacts.
- `history` ordering must be deterministic and newest-first using `ORDER BY created_at DESC`.
- `artifact.created_at` is the canonical timestamp for ordering lifecycle retrieval results.
- The repository changes must remain read-only and must not alter existing artifact creation behavior.

---

## 🔧 Execution Steps
1. Update `ukbe/app/storage/repositories/artifact_repo.py` to add read-only lifecycle retrieval helpers for generation-run lookup, definition latest lookup, and definition history lookup; the helpers must return a single ORM row or an ordered list as appropriate, and the verifiable state is that the repository can answer run-based and definition-based retrieval requests without modifying any stored records.
2. Create `ukbe/app/api/artifact_history.py` with `router = APIRouter(prefix="/artifacts", tags=["artifacts"])` and implement `GET /artifacts/by-run/{run_id}`, `GET /artifacts/by-definition/{definition_id}/latest`, and `GET /artifacts/by-definition/{definition_id}/history`; each handler must use `ArtifactRepo` plus the existing `ArtifactResponse` mapping contract, and the verifiable state is that the router module exposes all three retrieval routes.
3. Add `tests/api/test_artifact_history_api.py` to mount the new router on a FastAPI test app and verify success, 404, 422, and history-ordering behavior for all three routes; the verifiable state is a passing test module that independently proves the router and repository changes satisfy the lifecycle retrieval contract.

---

## 🧪 Validation Criteria
- Acceptance checks:
  - [ ] `python -c 'from ukbe.app.api.artifact_history import router'` exits with code `0`.
  - [ ] `python -c 'from ukbe.app.storage.repositories.artifact_repo import ArtifactRepo'` exits with code `0`.
  - [ ] `pytest tests/api/test_artifact_history_api.py -v` exits with code `0`.
  - [ ] `GET /artifacts/by-run/{run_id}` returns a single artifact response when the generation run exists.
  - [ ] `GET /artifacts/by-run/{run_id}` returns HTTP `404` when no artifact exists for that generation run.
  - [ ] `GET /artifacts/by-definition/{definition_id}/latest` returns the newest artifact for the definition.
  - [ ] `GET /artifacts/by-definition/{definition_id}/latest` returns HTTP `404` when no artifact exists for that definition.
  - [ ] `GET /artifacts/by-definition/{definition_id}/history` returns a list ordered newest-first.
  - [ ] `GET /artifacts/by-definition/{definition_id}/history` returns HTTP `200` with an empty list when no artifacts exist for that definition.
  - [ ] Invalid UUID path values for `run_id` or `definition_id` return HTTP `422`.
- Test cases:
  - [ ] Router tests cover all three routes with deterministic mocked repository responses.
  - [ ] Repository tests cover generation-run lookup, definition latest lookup, and definition history ordering.
  - [ ] Response payloads preserve the existing `ArtifactResponse` lineage fields.
- Review requirements:
  - [ ] The task stays read-only and does not change generation or persistence behavior.
  - [ ] No master router registration is added in this task.
  - [ ] No new response models or schema modules are introduced.

---

## ⚠️ Risks / Blockers
- History ordering can become ambiguous if the repository query does not enforce a stable descending sort.
- A mismatch between the router lookup key and the stored lineage field would make the endpoint appear functional but return empty results.
- If the router introduces a new schema instead of reusing `ArtifactResponse`, the API contract will drift from the existing artifact surface.

---

## 🔗 References
- Related docs:
  - `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
  - `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
  - `docs/architecture/07_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V4_2026-04-18.md`
  - `docs/architecture/08_UKBE_ARTIFACT_BUILDER_GAP_ANALYSIS_V5_2026-04-18.md`
- Linked review: 
- Supporting examples:
  - `ukbe/app/api/artifacts.py`
  - `ukbe/app/api/schemas/artifacts.py`
  - `ukbe/app/storage/repositories/artifact_repo.py`

---

## 📝 Notes
- Preserve the Plan ID exactly as `PLAN-20260418-02`.
- Preserve the Task Node ID exactly as `TASK-20260418-04`.
- This task intentionally stops before router registration. That is reserved for the follow-on integration task.
