---
doc_type: "execution_plan"
authority: "human-approved"
status: active
created_at: 2026-07-22
---

# SDLC Workflow Scaffold Execution Plan

## Status

**In Progress** -- Workflow chain corrected, L3 spec updated, sdlc_00 scaffold updated. Remaining: update sdlc_10-80 workflow.toml/output_paths/prompts to match new chain.

Update this file after each step completes. Cross-session durable.

---

## Key Decisions

| Decision | Value |
|----------|-------|
| Delivery path | `docs/repo/agent_runner/sdlc/delivery/` (per L3 spec) |
| Scaffold output | Follows L2 platform pattern: stage → publish → init to global |
| Scaffold staging | `docs/system/00_governance/platform/agent_runner/sdlc/runs/<job_id>/` |
| Scaffold publish | `docs/system/00_governance/platform/agent_runner/sdlc/current/` |
| Scaffold global | `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/` (via init) |
| Scaffold contents | `00_governance/`, `01_templates/`, `02_agents/` (universal, shared across all repos) |
| Repo-local delivery | `docs/repo/agent_runner/sdlc/delivery/` (per-repo initiative docs ONLY) |
| bundle_loader.py | Generic scan already handles `platform/` subdirs — no changes needed |
| sdlc_00 naming | Both `sdlc_00_delivery_scaffold_v1` and `sdlc_00_codebase_v1` at sdlc_00 level |
| Prompt style | Follows sdlc_10 pattern (Objective / Layer Boundary / Reference Inputs / etc.) |
| Master templates | `masterplan/delivery/00_templates/` = design reference ONLY, remove after scaffold workflow is built |
| Agent contracts | `masterplan/delivery/08_agents/` = design reference ONLY, remove after scaffold workflow is built |
| masterplan/ purpose | Planning only — not a runtime path for SDLC workflows |
| Runtime templates (global) | `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/01_templates/` (via init from scaffold workflow) |
| Runtime agents (global) | `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/02_agents/` (via init from scaffold workflow) |
| SDLC workflows reference | L3 spec + global runtime templates/agents |

---

## Steps

### Step 0: Housekeeping [DONE]
- [x] Clear existing todo list
- [x] Write this execution plan file
- [x] Update this file with progress after each step

### Step 1: Update L3 Specification [DONE]
File: `masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md`
- [x] Add `sdlc_00_delivery_scaffold_v1` to workflow family table
- [x] Add delivery scaffold to dependency chain
- [x] Add `01_templates/` and `02_agents/` to delivery folder structure
- [x] Add workflow specification section for `sdlc_00_delivery_scaffold_v1`
- [x] Add template-to-workflow mapping table
- [x] Add agent-to-workflow mapping table

### Step 2: Update L3 Implementation Plan [DONE]
File: `masterplan/LAYER3_AI_DRIVEN_SDLC_IMPLEMENTATION_PLAN.md`
- [x] Add Phase 0.4: sdlc_00_delivery_scaffold_v1
- [x] Add scaffold phase details for workflows 20-80

### Step 3: Create sdlc_00_delivery_scaffold_v1 [DONE]
Directory: `workflows/sdlc_00_delivery_scaffold_v1/`
- [x] `workflow.toml`
- [x] `prompts/01_generate_templates.txt`
- [x] `prompts/02_generate_agent_contracts.txt`
- [x] `prompts/03_review_scaffold.txt`
- [x] `prompts/04_refine_scaffold.txt`
- [x] `context_extensions.py`
- [x] `output_paths.py`

### Step 4: Scaffold sdlc_20_planning_v1 [DONE]
Directory: `workflows/sdlc_20_planning_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 5: Scaffold sdlc_30_backlog_v1 [DONE]
Directory: `workflows/sdlc_30_backlog_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 6: Scaffold sdlc_40_task_v1 [DONE]
Directory: `workflows/sdlc_40_task_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 7: Scaffold sdlc_50_implementation_v1 [DONE]
Directory: `workflows/sdlc_50_implementation_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 8: Scaffold sdlc_60_execution_v1 [DONE]
Directory: `workflows/sdlc_60_execution_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 9: Scaffold sdlc_70_validation_v1 [DONE]
Directory: `workflows/sdlc_70_validation_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 10: Scaffold sdlc_80_review_v1 [DONE]
Directory: `workflows/sdlc_80_review_v1/`
- [x] workflow.toml, 3 prompts, context_extensions.py, output_paths.py

### Step 11: Update sdlc_10 delivery path [DONE]
Change `docs/repo/sdlc/delivery/` to `docs/repo/agent_runner/sdlc/delivery/` in:
- [x] `workflows/sdlc_10_requirement_v1/output_paths.py`
- [x] `workflows/sdlc_10_requirement_v1/context_extensions.py`
- [x] `workflows/sdlc_10_requirement_v1/workflow.toml`

### Step 12: Bootstrap propagation [SKIPPED]
- [x] User decided: no bootstrap copy, focus on workflows/ folder only

### Step 13: Verify [DONE]
- [x] All 9 workflows verified: 54 files, correct paths, consistent routing

---

## Template-to-Workflow Mapping

| Master Template | Agent Contract | SDLC Workflow |
|---|---|---|
| `01_initiative.template.md` | (user input) | sdlc_10 |
| `02_plan.template.md` | AGENT-planner.md | sdlc_20 |
| `02b_task_graph.template.md` | AGENT-task-decomposer.md | sdlc_30 |
| `03_task.template.md` | AGENT-task-decomposer.md | sdlc_40 |
| `04_implementation_plan.template.md` | AGENT-implementation-planner.md | sdlc_50 |
| (execution -- code changes) | AGENT-executor.md | sdlc_60 |
| `05_validation.template.md` | AGENT-reviewer.md | sdlc_70 |
| `04_review.template.md` + `06_memory.template.md` | AGENT-reviewer.md + AGENT-memory-manager.md | sdlc_80 |

---

## Workflow Scaffold Pattern

Each SDLC workflow follows this common structure:

```
workflows/sdlc_NN_xxx_v1/
  workflow.toml           # Steps: generate -> review -> refine -> promote -> stepCompletion
  prompts/
    01_generate_<artifact>.txt    # References master template structure
    02_review_<artifact>.txt      # Review criteria based on template
    03_refine_<artifact>.txt      # Refinement rules
  context_extensions.py   # L1/L2 roots, codebase root, SDLC delivery paths
  output_paths.py         # Artifact key -> path mapping
  bundle_governance/      # Governance files
```

---

## sdlc_00_delivery_scaffold_v1 Specification

**Purpose:** Generate master document templates and agent contracts for the SDLC delivery system.

**Output path:** `docs/repo/agent_runner/sdlc/delivery/` (project-local delivery root)

**Steps:**
1. `generate_templates` (prompt) -- Generate all 01_templates/ files
2. `generate_agent_contracts` (prompt) -- Generate all 02_agents/ files
3. `review_scaffold` (prompt) -- Review templates + agent contracts for consistency
4. `refine_scaffold` (prompt) -- Refine based on review (if needed)
5. `stepCompletion` (action) -- Finalize

**Outputs:**
- `01_templates/template_registry.md`
- `01_templates/WORKFLOW_SOP_v1.md`
- `01_templates/01_initiative.template.md`
- `01_templates/02_plan.template.md`
- `01_templates/02b_task_graph.template.md`
- `01_templates/03_task.template.md`
- `01_templates/04_implementation_plan.template.md`
- `01_templates/04_review.template.md`
- `01_templates/05_validation.template.md`
- `01_templates/06_memory.template.md`
- `02_agents/AGENTS.md`   
- `02_agents/AGENT-planner.md`
- `02_agents/AGENT-task-decomposer.md`
- `02_agents/AGENT-implementation-planner.md`
- `02_agents/AGENT-executor.md`
- `02_agents/AGENT-reviewer.md`
- `02_agents/AGENT-memory-manager.md`
- `02_agents/DELIVERY_STATUS_RULES_v1.md`

---

## Progress Log

| Date | Step | Status | Notes |
|------|------|--------|-------|
| 2026-07-22 | Plan approved | Done | User approved scaffold plan |
| 2026-07-22 | Step 0: Write plan file | Done | This file |
| 2026-07-22 | Step 1: Update L3 Spec | Done | Added sdlc_00_delivery_scaffold_v1 spec, mappings, dependency chain, folder structure |
| 2026-07-22 | Step 2: Update L3 Impl Plan | Done | Added Phase 0.4 |
| 2026-07-22 | Step 3: Create sdlc_00 | Done | workflow.toml, 4 prompts, context_extensions.py, output_paths.py |
| 2026-07-22 | Step 4: Scaffold sdlc_20 | Done | Agent created workflow |
| 2026-07-22 | Step 5: Scaffold sdlc_30 | Done | Agent created workflow |
| 2026-07-22 | Step 6: Scaffold sdlc_40 | Done | Agent created workflow |
| 2026-07-22 | Step 7: Scaffold sdlc_50 | Done | Agent created workflow |
| 2026-07-22 | Step 8: Scaffold sdlc_60 | Done | Agent created workflow |
| 2026-07-22 | Step 9: Scaffold sdlc_70 | Done | Agent created workflow |
| 2026-07-22 | Step 10: Scaffold sdlc_80 | Done | Agent created workflow |
| 2026-07-22 | Step 11: Update sdlc_10 path | Done | Fixed delivery path in 3 files |
| 2026-07-22 | Step 12: Bootstrap | Skipped | User: focus on workflows/ only |
| 2026-07-22 | Step 13: Verify all | Done | 9 workflows, 54 files, all pass |
| 2026-07-22 | Step 14a: L3 spec update | Done | Corrected workflow chain, folder structure, 11 templates, naming convention |
| 2026-07-22 | Step 14c: sdlc_00 scaffold update | Done | workflow.toml, output_paths.py, prompts updated for 11 templates |
| 2026-07-22 | Step 14b: sdlc_10 workflow.toml | Needs Review | Updated to INIT_DOC chain but user flagged logic is wrong — relook tomorrow |
| 2026-07-22 | Step 14b: sdlc_10 output_paths | Done | DRAFT_INIT_DOC, INIT_DOC paths |
| 2026-07-22 | Step 14b: sdlc_20-80 workflow.toml | **TODO** | Need to update artifact keys for new chain |
| 2026-07-22 | Step 14b: sdlc_20-80 output_paths | **TODO** | Need to update artifact keys and paths |
| 2026-07-22 | Step 14b: sdlc_10-80 prompts | **TODO** | Need to rename prompt files and update content |
| 2026-07-22 | Step 14d: Console UI scanner | **TODO** | Deferred |

---

## Step 14: Console UI — Delivery Document Scanner [PENDING]

### Problem

When submitting a job via the operator console, the user must manually type artifact paths. This is error-prone. The console should scan the delivery directory for available input documents and present them in a dropdown.

### Corrected Workflow Chain

Each workflow takes the previous step's output as input and produces a new document:

```
sdlc_10: DRAFT_INIT_DOC → INIT-DOC     (using 01_initiative.template.md)
sdlc_20: INIT-DOC       → REQ-DOC      (using 02_requirement.template.md)
sdlc_30: REQ-DOC        → PLAN-DOC     (using 03_plan.template.md)
sdlc_40: PLAN-DOC       → BACKLOG-DOC  (using 04_task_graph.template.md)
sdlc_50: BACKLOG-DOC    → TASK-DOC     (using 05_task.template.md)
sdlc_60: TASK-DOC       → IMPL-DOC     (using 06_implementation_plan.template.md)
sdlc_70: IMPL-DOC       → VALIDATE-DOC (using 07_validation.template.md)
sdlc_80: VALIDATE-DOC   → REV + MEM + CLOSE (new workflow)
```

### Template Mapping (1 DOC = 1 template)

| # | Template Filename | Produces | Used By | Source |
|---|---|---|---|---|
| 01 | `01_DRAFT_INIT_template.md` | DRAFT-INIT-DOC | User-authored (input to sdlc_10) | From old `01_initiative` |
| 02 | `02_INIT_template.md` | INIT-DOC | sdlc_10 | **NEW** (split from old 01) |
| 03 | `03_REQ_template.md` | REQ-DOC | sdlc_20 | From old `02_plan` |
| 04 | `04_PLAN_template.md` | PLAN-DOC | sdlc_30 | From old `02b_task_graph` |
| 05 | `05_BACKLOG_template.md` | BACKLOG-DOC | sdlc_40 | From old `03_task` |
| 06 | `06_TASK_template.md` | TASK-DOC | sdlc_50 | From old `04_implementation_plan` |
| 07 | `07_IMPL_template.md` | IMPL-DOC | sdlc_60 | From old `05_validation` |
| 08 | `08_VALID_template.md` | VALIDATE-DOC | sdlc_70 | From old `04_review` |
| 09 | `09_REV_template.md` | REV-DOC | sdlc_80 | **NEW** |
| 10 | `10_MEM_template.md` | MEM-DOC | sdlc_80 | From old `06_memory` |
| 11 | `11_CLOSE_template.md` | CLOSE-DOC | sdlc_80 | **NEW** |

**3 new templates** must be created from scratch: `02_INIT`, `09_REV`, `11_CLOSE`.

### Delivery Folder Structure (input scan dirs)

| Workflow Selected | Required Input | Scan Directory |
|---|---|---|
| sdlc_10 | DRAFT_INIT_DOC | `draft_initiatives/` |
| sdlc_20 | INIT-DOC | `initiatives/` |
| sdlc_30 | REQ-DOC | `requirements/` |
| sdlc_40 | PLAN-DOC | `plans/` |
| sdlc_50 | BACKLOG-DOC | `backlogs/` |
| sdlc_60 | TASK-DOC | `tasks/` |
| sdlc_70 | IMPL-DOC | `implementations/` |
| sdlc_80 | VALIDATE-DOC | `validations/` |

### Implementation

**File:** `agent_runner_v2/operator_console/app.py`

1. **Add `ARTIFACT_SCAN_DIRS` mapping** — workflow_name → (artifact_key, subdirectory)
2. **Add `scan_delivery_documents()` helper** — scans dir for .md files, sorted DESC
3. **Add `delivery_doc_dd` dropdown** — auto-populated on workflow selection
4. **Modify `on_workflow_changed()`** — trigger scan when workflow changes
5. **Modify `execute_action()`** — pass selected file as artifact path

### Also Requires

- [x] Update L3 spec delivery folder structure (add `draft_initiatives/`, `initiatives/`)
- [x] Update sdlc_00 scaffold prompts + output_paths + workflow.toml (11 template names)
- [x] Update sdlc_10 workflow.toml + output_paths (INIT_DOC chain) — **NEEDS FULL REVIEW: logic is wrong**
- [ ] Update sdlc_20 through sdlc_80 workflow.toml files (correct input/output artifact keys)
- [ ] Update sdlc_20 through sdlc_80 output_paths.py files (correct paths)
- [ ] Rename sdlc_10 through sdlc_80 prompt files to match new step names
- [ ] Update template-to-workflow mapping table in L3 spec (done)
- [ ] Console UI delivery document scanner (deferred)
