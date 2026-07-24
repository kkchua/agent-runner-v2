# Workflow Compliance Status

> **Audit date:** 2026-07-24
> **Scope:** All 14 workflow packages under `workflows/`
> **Reference:** [WORKFLOW_CREATION_GUIDE.md](WORKFLOW_CREATION_GUIDE.md)

---

## Summary

| Metric | Count |
|---|---|
| Total workflows | 14 |
| Fully compliant (all required files) | 0 |
| Has `workflow.toml` | 14/14 |
| Has `context_extensions.py` | 14/14 |
| Has `WorkflowExtensions` class | 11/14 |
| Has `bundle_governance.toml` | 3/14 |
| Has `prompts/` directory | 13/14 |
| Has `stepCompletion` terminal step | 14/14 |
| Has `README.md` | 0/14 |

---

## File Presence Matrix

| Workflow | workflow.toml | context_extensions.py | WorkflowExtensions class | bundle_governance.toml | prompts/ | actions.py | install.py | output_paths.py | bundle_governance/ | README.md |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `00_bootstrap_lifecycle_admin_v1` | YES | YES | **NO** (legacy) | **NO** | **NO** | YES | NO | NO | **NO** | NO |
| `01_governance_foundation_v1` | YES | YES | **NO** (legacy) | YES (12) | YES (4) | YES | NO | **YES** (legacy) | YES | NO |
| `02_agent_runner_platform_v1` | YES | YES | **NO** (legacy) | YES (12) | YES (4) | YES | NO | **YES** (legacy) | YES | NO |
| `sdlc_00_codebase_v1` | YES | YES | YES | YES (8) | YES (2) | YES | NO | NO | YES | NO |
| `sdlc_00_delivery_scaffold_v1` | YES | YES | YES | **NO** | YES (4) | YES | YES | NO | **NO** | NO |
| `sdlc_00_init_doc_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_10_requirement_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_20_planning_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_30_backlog_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_40_task_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_50_implementation_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_60_execution_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_70_validation_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |
| `sdlc_80_review_v1` | YES | YES | YES | **NO** | YES (4) | NO | NO | NO | **NO** | NO |

---

## Structural Compliance

### `workflow.toml` — Init step style

| Style | Workflows |
|---|---|
| `[workflow.init]` sub-table | 00_bootstrap, 01_governance, 02_agent_runner |
| `init_step` flat key | All 11 SDLC workflows |

Both styles work. The flat key is simpler and preferred for new workflows.

### `workflow.toml` — Version format

| Format | Workflows |
|---|---|
| `version = "1"` | 00_bootstrap, 01_governance, 02_agent_runner |
| `version = "1.0.0"` | All 11 SDLC workflows |

Minor inconsistency. Not a functional issue.

### `workflow.toml` — Terminal step

**14/14 compliant.** All workflows end with `stepCompletion` using `step_completion` action.

### `workflow.toml` — `promotes` key placement

**All compliant.** All 9 workflows with promote steps have `promotes` at the `[[step]]` top level.

### `workflow.toml` — `on_reject_refine`

**13/14 have refinement loops.** Only `00_bootstrap` has a degenerate case (`max_iterations = 0`).

### `workflow.toml` — `on_exhaust_replan`

**0/14 have replan sections.** This feature is defined in the loader but unused across all workflows.

---

## `context_extensions.py` — Implementation Patterns

### Two patterns in use

| Pattern | Workflows | Description |
|---|---|---|
| **Legacy standalone functions** | 00_bootstrap, 01_governance, 02_agent_runner | Module-level `build_context_extensions()` function, no class |
| **WorkflowExtensions class** | All 11 SDLC workflows | Proper subclass with `register_artifact_keys()` + `build_context_extensions()` |

### Issues found

| Issue | Workflow | Severity |
|---|---|---|
| Undefined `workspace_root` variable | `sdlc_10_requirement_v1` | **Bug** — references `workspace_root` without importing it |
| Unused `import datetime as dt` | `sdlc_00_codebase_v1` | Minor — dead import |
| Duplicated `_extract_slug_from_path()` | 8 SDLC workflows | Maintenance — same function copy-pasted |
| Hardcoded governance root paths | 11 workflows | Maintenance — `"bundles/core/current/foundation"` duplicated |
| Inconsistent runtime context imports | All | Style — some use `GLOBAL_RUNNER_HOME`, others use `get_runner_home()` |

### `init()` method

**0/14 implement `init()`.** The base class defines it as a no-op. Only
`sdlc_00_delivery_scaffold_v1` has a separate `install.py` for global
installation, but it does not implement `init()` in the extensions class.

---

## Legacy Artifacts

| File | Workflows | Status |
|---|---|---|
| `output_paths.py` | 01_governance, 02_agent_runner | **Dead code** — replaced by `context_extensions.py` `register_artifact_keys()` |

These files should be removed after confirming no imports reference them.

---

## Workflow-by-Workflow Assessment

### Bootstrap Tier (L1/L2 Governance)

#### `00_bootstrap_lifecycle_admin_v1`

- **Type:** Action-only pipeline (5 action steps + stepCompletion)
- **Compliance:** Uses legacy standalone function pattern for context_extensions
- **Missing:** `bundle_governance.toml`, `prompts/` (N/A — all actions), `README.md`
- **Notes:** No prompt steps, so no `prompts/` needed. No artifact registry.
- **Recommendation:** Migrate `context_extensions.py` to `WorkflowExtensions` class.

#### `01_governance_foundation_v1`

- **Type:** Mixed generate/review/refine/audit with governance adapters
- **Compliance:** Has full `bundle_governance/` directory with adapters
- **Missing:** `README.md`
- **Issues:** Legacy `output_paths.py` (dead code), legacy standalone function pattern
- **Recommendation:** Remove `output_paths.py`, migrate to `WorkflowExtensions` class.

#### `02_agent_runner_platform_v1`

- **Type:** Same pattern as 01_governance
- **Compliance:** Has full `bundle_governance/` directory
- **Missing:** `README.md`
- **Issues:** Same as 01_governance — legacy `output_paths.py`, standalone functions
- **Recommendation:** Remove `output_paths.py`, migrate to `WorkflowExtensions` class.

### SDLC Foundation Tier

#### `sdlc_00_codebase_v1`

- **Type:** Mixed action + prompt (codebase documentation sync)
- **Compliance:** Has `bundle_governance.toml` (8 artifacts), proper `WorkflowExtensions` class
- **Missing:** `README.md`
- **Issues:** Unused `import datetime`, prompt numbering starts at 04 (01-03 removed)
- **Notes:** `commit_changes` step has no `[step.artifacts]` — only non-terminal step without artifacts
- **Recommendation:** Remove unused import.

#### `sdlc_00_delivery_scaffold_v1`

- **Type:** Prompt-driven with review/refine (template + agent contract generation)
- **Compliance:** Proper `WorkflowExtensions` class, has `install.py`
- **Missing:** `bundle_governance.toml`, `bundle_governance/`, `README.md`
- **Notes:** Only workflow with `install.py`. Registers SDLC delivery artifact keys globally.
- **Recommendation:** Add `bundle_governance.toml` for artifact registry validation.

### SDLC Chain Tier (sdlc_10 through sdlc_80)

All 9 workflows follow the same pattern:

```
generate → technical_critique → review → [refine ↔ review] → promote → stepCompletion
```

| Workflow | Primary Artifact | Role Policies | Promotes |
|---|---|---|---|
| `sdlc_00_init_doc_v1` | INIT_FILE | architect, reviewer | INIT_FILE |
| `sdlc_10_requirement_v1` | REQ_FILE | architect, reviewer | REQ_FILE |
| `sdlc_20_planning_v1` | PLAN_FILE | architect, reviewer | PLAN_FILE |
| `sdlc_30_backlog_v1` | BACKLOG_FILE | architect, reviewer | BACKLOG_FILE |
| `sdlc_40_task_v1` | TASK_FILE | architect, reviewer | TASK_FILE |
| `sdlc_50_implementation_v1` | IMPL_FILE | architect, reviewer | IMPL_FILE |
| `sdlc_60_execution_v1` | EXEC_FILE | architect, reviewer | EXEC_FILE |
| `sdlc_70_validation_v1` | VAL_FILE | architect, reviewer | VAL_FILE |
| `sdlc_80_review_v1` | REV_FILE + MEM_FILE + CLOSE_FILE | architect, reviewer | promote_all |

**Common issues across all 9:**
- Missing `bundle_governance.toml` (no artifact registry)
- Missing `bundle_governance/` directory (no governance adapters)
- Missing `README.md`
- Duplicated `_extract_slug_from_path()` helper
- Hardcoded governance root construction

**Specific issues:**
- `sdlc_10_requirement_v1`: **Bug** — undefined `workspace_root` variable in `build_context_extensions()`
- `sdlc_40_task_v1`: Uses `{work_item}` placeholder instead of `{seq}` — unique pattern
- `sdlc_80_review_v1`: Uses `promote_all` action with list of 3 artifacts

---

## Recommendations

### High Priority

1. **Fix `sdlc_10_requirement_v1` bug** — `workspace_root` is referenced but not imported in `build_context_extensions()`. Should be:
   ```python
   from agent_runner_v2.runtime_context import get_workspace_root
   effective_root = Path(project_root or get_workspace_root() or Path.cwd())
   ```

2. **Remove dead `output_paths.py`** from `01_governance_foundation_v1` and `02_agent_runner_platform_v1` after confirming no imports.

### Medium Priority

3. **Migrate legacy `context_extensions.py`** in 00_bootstrap, 01_governance, 02_agent_runner to `WorkflowExtensions` class pattern.

4. **Add `bundle_governance.toml`** to SDLC chain workflows (sdlc_00_init through sdlc_80) for artifact registry validation and backend sync.

5. **Extract `_extract_slug_from_path()`** to a shared utility module to eliminate duplication across 8 files.

### Low Priority

6. **Add `README.md`** to all 14 workflows.

7. **Standardize version format** — pick either `"1"` or `"1.0.0"` across all workflows.

8. **Standardize runtime context imports** — prefer `get_runner_home()` over `GLOBAL_RUNNER_HOME` for consistency.

9. **Extract hardcoded governance root paths** into shared constants to eliminate duplication across 11 files.

---

## `_registry/` Directory

Shared configuration files used by all workflows:

| File | Purpose |
|---|---|
| `role_policies.json` | Role policy → coder/model mappings |
| `coder_roles.json` | Role → coder assignments |
| `coder_roles_opencode.json` | OpenCode-specific role mappings |
| `coder_roles_qwen.json` | Qwen-specific role mappings |
| `coder_connections.json` | Provider connection definitions |
