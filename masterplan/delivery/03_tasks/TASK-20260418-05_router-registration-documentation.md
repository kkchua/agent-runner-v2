# 🧩 Task: Router Registration & Documentation

## 📌 Metadata
- Doc Type: 03_task
- Template Version: v1
- Task ID: TASK-20260418-05
- Plan ID: PLAN-20260418-02
- Source Task Graph ID: TASK-GRAPH-20260418-PLAN-20260418-02
- Source Task Node ID: TASK-20260418-05
- Review File Path:
- Title: Router Registration & Documentation
- Status: COMPLETED
- Priority: medium
- Assigned To: Qwen Code
- Created By: codex
- Created At: 2026-04-19
- Due At: TBD

---

## 🎯 Objective
Register the already implemented public routers in the master API router so the new public control-plane routes are exposed through the FastAPI application and appear in generated OpenAPI documentation. This task is registration-only: it must not change router implementations, schema modules, service behavior, or OpenAPI source data manually.

The exposed route set that must become visible through `api_router` is:

- `POST /contract-build`
- `POST /artifacts/generate-managed`
- `GET /generation-runs`
- `GET /generation-runs/latest`
- `GET /generation-runs/{run_id}`
- `GET /artifacts/by-run/{run_id}`
- `GET /artifacts/by-definition/{definition_id}/latest`
- `GET /artifacts/by-definition/{definition_id}/history`

The existing `/artifacts` routes and `/generation-runs` routes must remain unchanged except for being reachable through the master router.

---

## 📥 Inputs
- Source plan: `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
- Source task graph: `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Dependencies:
  - `TASK-20260418-01`
  - `TASK-20260418-02`
  - `TASK-20260418-03`
  - `TASK-20260418-04`
- Required documents:
  - `ukbe/app/api/router.py`
  - `ukbe/app/api/contract_build.py`
  - `ukbe/app/api/artifact_history.py`
  - `ukbe/app/api/artifacts.py`
  - `ukbe/app/api/generation_run.py`
  - `ukbe/app/main.py`
- Required data / APIs:
  - Existing router symbols exported by the implemented modules:
    - `router` from `ukbe.app.api.contract_build`
    - `router` from `ukbe.app.api.artifact_history`
    - `router` from `ukbe.app.api.artifacts`
    - `router` from `ukbe.app.api.generation_run`
  - `create_app()` in `ukbe.app.main` includes `api_router`
  - FastAPI OpenAPI generation from registered routers

---

## 📤 Outputs
- Expected artifacts:
  - `ukbe/app/api/router.py`
- Output folder / path:
  - `ukbe/app/api/`
- Completion evidence:
  - `from ukbe.app.api.router import api_router` imports successfully
  - `create_app().openapi()` includes the new route paths and the correct router tags
  - The `/artifacts` prefix remains shared by `artifacts_router` and `artifact_history_router`, with no path collisions

---

## 🧠 Implementation Details
### Technical Notes
- This is a router-registration task only.
- Do not edit `ukbe/app/api/contract_build.py`, `ukbe/app/api/artifact_history.py`, `ukbe/app/api/artifacts.py`, or `ukbe/app/api/generation_run.py`.
- Do not add new schemas, services, repositories, or manual OpenAPI documents.
- Do not change the app factory or FastAPI configuration; the existing `create_app()` path must continue to include `api_router`.

### API / Contract Notes
- Update `ukbe/app/api/router.py` with these exact import statements:
  - `from ukbe.app.api.contract_build import router as contract_build_router`
  - `from ukbe.app.api.artifact_history import router as artifact_history_router`
- Keep the existing `from ukbe.app.api.artifacts import router as artifacts_router` and `from ukbe.app.api.generation_run import router as generation_run_router` imports unchanged.
- Update `api_router` registration so both new routers are included:
  - `api_router.include_router(contract_build_router)`
  - `api_router.include_router(artifact_history_router)`
- Preserve the existing registrations for all current routers, including `artifacts_router` and `generation_run_router`.
- Shared-prefix rule:
  - `artifacts_router` and `artifact_history_router` both use the `/artifacts` prefix.
  - Their route paths are distinct and do not collide.
  - No special ordering rule is required beyond keeping both routers registered on `api_router`.
- OpenAPI exposure is automatic from router inclusion.
  - No separate docs file is edited.
  - No manual path or tag registration is allowed.

### Data / Schema Notes
- No response model, request model, or database schema changes are permitted in this task.
- The only behavioral change is that the already-implemented routes become visible through the main API router and therefore through generated OpenAPI output.

---

## 🔧 Execution Steps
1. Update `ukbe/app/api/router.py` to add the exact imports for `contract_build_router` and `artifact_history_router` while preserving all existing router imports unchanged; the verifiable state is that the module still imports cleanly after the new symbols are added.
2. Update `ukbe/app/api/router.py` to include `contract_build_router` and `artifact_history_router` on `api_router` without removing any existing `include_router(...)` calls; the verifiable state is that the master router exposes the full route set listed in the Objective.
3. Leave `ukbe/app/main.py` unchanged so `create_app()` continues to mount `api_router` and surface the registered paths in OpenAPI; the verifiable state is that application-level docs reflect the new routes without any manual documentation edits.

---

## 🧪 Validation Criteria
- Acceptance checks:
  - [ ] `python -c 'from ukbe.app.api.router import api_router'` exits with code `0`.
  - [ ] `python -c 'from ukbe.app.main import create_app; payload = create_app().openapi(); assert "/contract-build" in payload["paths"]; assert "/artifacts/generate-managed" in payload["paths"]; assert "/generation-runs" in payload["paths"]; assert "/generation-runs/latest" in payload["paths"]; assert "/generation-runs/{run_id}" in payload["paths"]; assert "/artifacts/by-run/{run_id}" in payload["paths"]; assert "/artifacts/by-definition/{definition_id}/latest" in payload["paths"]; assert "/artifacts/by-definition/{definition_id}/history" in payload["paths"]'` exits with code `0`.
  - [ ] `python -c 'from ukbe.app.main import create_app; payload = create_app().openapi(); assert "contract-build" in payload["paths"]["/contract-build"]["post"]["tags"]; assert "artifacts" in payload["paths"]["/artifacts/by-run/{run_id}"]["get"]["tags"]; assert "generation-runs" in payload["paths"]["/generation-runs/latest"]["get"]["tags"]'` exits with code `0`.
  - [ ] The shared `/artifacts` prefix remains available for both the existing artifact routes and the new lifecycle routes.
- Test cases:
  - [ ] The OpenAPI document contains the full route set listed in the Objective.
  - [ ] The OpenAPI document shows the expected router tags for `contract-build`, `artifacts`, and `generation-runs`.
  - [ ] The master router import succeeds without requiring any other module edits.
- Review requirements:
  - [ ] Only `ukbe/app/api/router.py` is modified by this task.
  - [ ] No route implementation logic is changed in the underlying router modules.
  - [ ] No manual OpenAPI or documentation file is introduced.

---

## ⚠️ Risks / Blockers
- If a new router is omitted from `api_router`, the underlying route module will still exist but the application and OpenAPI will not expose it.
- If the shared `/artifacts` prefix is registered inconsistently, the public surface can appear incomplete even though the route module is implemented.
- If `create_app()` is changed instead of `api_router`, the registration contract becomes harder to review and is out of scope for this task.

---

## 🔗 References
- Related docs:
  - `docs/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md`
  - `docs/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md`
- Linked review:
  - `docs/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json`
- Supporting examples:
  - `ukbe/app/api/router.py`
  - `ukbe/app/main.py`
  - `ukbe/app/api/artifacts.py`
  - `ukbe/app/api/contract_build.py`
  - `ukbe/app/api/artifact_history.py`
  - `ukbe/app/api/generation_run.py`

---

## 📝 Notes
- Preserve the Plan ID exactly as `PLAN-20260418-02`.
- Preserve the Task Node ID exactly as `TASK-20260418-05`.
- This task is intentionally narrow and ends at router registration plus OpenAPI exposure.
- The actual endpoint implementations are out of scope and must be treated as already delivered by the dependent tasks.
