# Deployment Handoff — Plan-First Review Workflow

**Planning folder:** `Planning/20261025-01_PlanFirstAutomation/`
**Date:** 2026-10-25
**Workflow:** `plan_first_review_v1`

## Summary

Implements the `plan_first_review_v1` workflow — a structured plan-first review cycle with Codex reviewer and Qwen planner roles, including unauthorized write detection, atomic folder allocation, and layered path constants.

## New files

### Workflow package

| Path | Purpose |
|------|---------|
| `workflows/plan_first_review_v1/workflow.toml` | Step definitions, routing, coder roles, refinement limits, detection flag |
| `workflows/plan_first_review_v1/actions.py` | prepare_request (atomic folder claim), promote_plan, step_completion |
| `workflows/plan_first_review_v1/context_extensions.py` | Per-step artifact path resolution using layered constants |
| `workflows/plan_first_review_v1/impls/standard/impl.yaml` | Standard implementation slot bindings |
| `workflows/plan_first_review_v1/prompts/formalize_requirements/standard.txt` | Codex reviewer prompt — formalize raw request |
| `workflows/plan_first_review_v1/prompts/generate_plan/standard.txt` | Qwen planner prompt — generate implementation plan |
| `workflows/plan_first_review_v1/prompts/codex_review/standard.txt` | Codex reviewer prompt — review plan |
| `workflows/plan_first_review_v1/prompts/refine_plan/standard.txt` | Qwen planner prompt — refine plan from review feedback |
| `workflows/plan_first_review_v1/README.md` | Workflow documentation with operator commands |

### Tests

| Path | Purpose |
|------|---------|
| `tests/unit/test_plan_first_review_v1.py` | 56 unit tests covering all workflow phases |
| `tests/unit/test_run_agent_status.py` | 4 tests including regression for `import json` shadowing fix |

### Process

| Path | Purpose |
|------|---------|
| `SOP.md` | Architecture, implementation, and validation SOP defining Codex/Qwen/User roles |
| `VALIDATION_REPORT.md` | Test results, failure triage, regression documentation |

## Modified files

### Runtime — unauthorized write detection

| Path | Change |
|------|--------|
| `agent_runner_v2/exceptions.py` | Added `UnauthorizedWriteError` with `unauthorized_paths` list |
| `agent_runner_v2/step_runner.py` | Added `_snapshot_all_files()`, `_build_allowed_paths()`, `_verify_no_unauthorized_writes()`, `_is_subpath()`; integrated detection into `run_step()` on both success and failure paths |
| `agent_runner_v2/workflow_packages/base.py` | Added `enable_unauthorized_write_detection: bool = False` to `WorkflowBundle` |
| `agent_runner_v2/workflow_packages/loader.py` | Extract flag in `_parse_bundle()`, adapt in `bundle_to_template_group_dict()` |

### Runtime — path constants

| Path | Change |
|------|--------|
| `agent_runner_v2/constants.py` | Added `PLANNING_BASE`, `_planning_folder_path()`, `_planning_artifact_path()`, `ARTIFACT_PATH_RAW_REQUEST()`, `ARTIFACT_PATH_REQUIREMENTS()`, `ARTIFACT_PATH_QWEN_PLAN()`, `ARTIFACT_PATH_CODEX_REVIEW()`, `ARTIFACT_PATH_BASELINE_DIR()`, `ARTIFACT_PATH_BASELINE_REQUEST()` |
| `agent_runner_v2/artifact_keys.py` | Added `ARTIFACT_KEY_RAW_REQUEST`, `ARTIFACT_KEY_PLANNING_FOLDER`, `ARTIFACT_KEY_REQUIREMENTS`, `ARTIFACT_KEY_QWEN_PLAN`, `ARTIFACT_KEY_CODEX_REVIEW` |

### Runtime — job state and routing

| Path | Change |
|------|--------|
| `agent_runner_v2/job_state.py` | Added `change_requirements()` for multi-baseline support, model approval tracking, stale approval cleanup |
| `agent_runner_v2/v2/workflow_router.py` | Routing adjustments for plan-first workflow |
| `agent_runner_v2/run_agent.py` | CLI command additions (continue-refinement, stop-and-archive, change-requirements) |
| `agent_runner_v2/runner_actions.py` | Runner action support |
| `agent_runner_v2/cli_runtime.py` | CLI runtime adjustments |
| `agent_runner_v2/manual_runtime.py` | Manual runtime adjustments |
| `agent_runner_v2/step_execution_runtime.py` | Step execution runtime |
| `agent_runner_v2/sync_workflows.py` | Workflow sync updates |
| `agent_runner_v2/workflow_package_validator.py` | Validator updates |

### Registry

| Path | Change |
|------|--------|
| `workflows/_registry/coder_roles.json` | Added `plan_standard`, `reviewer_standard` coder roles |
| `workflows/_registry/role_policies.json` | Added `plan_standard`, `reviewer_standard` role policies |

### Documentation

| Path | Change | Deployment target |
|------|--------|-------------------|
| `source/README.md` | Added Plan-First Workflow section with quick start, operator commands, and documentation links | `README.md` (repo root) |
| `source/AGENTS.md` | Added Plan-First Review Workflow section with pipeline, operator commands table, key features | `AGENTS.md` (repo root) |

## Database scripts

None

## Deployment order and verification

1. **Merge dev branch** — All changes are in the `dev` branch. Deployment is a standard git merge to `master`.
2. **No database migration** — No schema changes.
3. **No environment variable changes** — Uses existing `TOKEN_PLAN_API_KEY` and coder configurations.
4. **Verify workflow loads and runs:**
   ```bash
   ukbe-run-agent run --template-group plan_first_review_v1 --set RAW_REQUEST_FILE=path/to/request.md
   ```
   Replace `path/to/request.md` with the path to a raw request markdown file.
5. **Verify tests pass:**
   ```bash
   .venv\Scripts\python -m pytest tests/unit/test_plan_first_review_v1.py tests/unit/test_run_agent_status.py -v
   ```
   Expected: 60 passed (56 workflow + 4 status/regression)

## Known limitations

- Unauthorized write detection is **post-hoc reporting** — it detects and reports writes after they occur but does not prevent them at the filesystem level.
- Detection only applies to prompt-driven steps when `enable_unauthorized_write_detection = true` is set in workflow.toml.
- Planning folder allocation is atomic per-process; concurrent processes on the same machine are safe via `mkdir(exist_ok=False)` + retry.
