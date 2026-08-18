# Workflow Contract Registry — Master Plan

**Status:** Draft  
**Created:** 2026-08-18  
**Related:** AGBv2 Architecture, workflow.toml, Backend API  

---

## 1. Objective

Enable contract-based workflow discovery and chaining:

1. **Contract-based discovery:** "I have X, want Y" — system returns workflows matching the contract
2. **Workflow chaining:** Output from Workflow A → Input to Workflow B (automated or assisted)
3. **Smart orchestration foundation:** Future autonomous workflow selection and composition

---

## 2. Design Principle: Root-Level Contract (Option A)

Contracts are declared **once per workflow in root `workflow.toml`**, not per-implementation.

```toml
[workflow.contract]
inputs = ["DRAFT_INIT_FILE", "PRODUCT_BRIEF_FILE"]
outputs = ["WORKFLOW_SPEC_FILE", "IMPL_SPEC_FILE"]
```

**Rationale:**
- Single source of truth — the workflow's purpose is defined at the root level
- Implementations only override execution strategy, not contract
- Backend stores one contract per workflow, not per impl
- Simplifies discovery queries — no need to filter by impl

---

## 3. Contract Schema

```toml
[workflow.contract]
# Required inputs (must be provided by caller)
inputs = ["ARTIFACT_KEY_1", "ARTIFACT_KEY_2"]

# Optional inputs (may be provided, fallback to defaults)
optional_inputs = ["CONFIG_FILE"]

# Outputs produced by any successful execution
outputs = ["OUTPUT_ARTIFACT_1", "OUTPUT_ARTIFACT_2"]

# Human-readable description of the transformation
input_output_description = "Generates implementation specs from draft initiative"

# Category for grouping in discovery UI
category = "scaffolding"

# Tags for search/filter
tags = ["codegen", "spec", "sdlc"]
```

---

## 4. Phase Breakdown

### Phase 1: Contract Storage & Sync

**Goal:** Backend stores and returns workflow contracts.

**Files to Modify:**
- `workflows/<name>/workflow.toml` — Add `[workflow.contract]` section
- `agent_runner_v2/workflow_packages/loader.py` — Parse contract into WorkflowBundle
- `agent_runner_v2/sync_workflows.py` — Include contract in sync payload
- Backend `WorkflowDefinition` model — Add contract fields

**Tasks:**
1. **Runner: Add contract parsing**
   - Update `WorkflowBundle` dataclass with `contract` field
   - Parse `[workflow.contract]` from TOML in loader

2. **Runner: Include contract in sync**
   - Update `convert_to_v2_format()` to include contract dict

3. **Backend: Add contract columns**
   - Migration: Add `contract_definition` JSONB column to `workflow` table
   - ORM model: Add `contract` relationship

4. **Backend: Store contract on sync**
   - Extract `contract` from sync payload
   - Store as JSONB

**Verification:**
- Sync workflow with contract — backend stores it
- GET workflow returns contract in definition

---

### Phase 2: Contract Query API

**Goal:** Backend exposes endpoints to query contracts.

**New Endpoints:**

```
GET /api/workflows?has_input=ARTIFACT_KEY&has_output=ARTIFACT_KEY
GET /api/workflows/contracts (list all contracts)
GET /api/workflows/{name}/contract (single contract)
```

**Tasks:**
1. **Backend: Contract filtering query**
   - Add query params: `has_input`, `has_output`, `category`, `tags`
   - Return workflows matching ANY of the provided inputs/outputs

2. **Backend: Contract listing endpoint**
   - `GET /api/workflows/contracts` returns lightweight list
   - Fields: workflow_name, label, inputs[], outputs[], category

3. **Runner: Add to backend_client.py**
   - `list_workflows_by_contract()` method
   - `get_workflow_contract()` method

**Verification:**
- Query by input artifact → returns workflows that consume it
- Query by output artifact → returns workflows that produce it

---

### Phase 3: Discovery API

**Goal:** "I have X, want Y" matching.

**New Endpoint:**

```
POST /api/workflows/discover
{
  "have_inputs": ["DRAFT_INIT_FILE"],
  "want_outputs": ["WORKFLOW_SPEC_FILE"],
  "match_mode": "exact" | "subset" | "superset"
}
```

**Response:**
```json
{
  "matches": [
    {
      "workflow_name": "workflow_builder_v2",
      "label": "Workflow Builder V2",
      "match_score": 1.0,
      "missing_inputs": [],
      "matching_inputs": ["DRAFT_INIT_FILE"],
      "matching_outputs": ["WORKFLOW_SPEC_FILE"]
    }
  ],
  "chains": [
    {
      "description": "Chained workflows to reach target",
      "steps": [
        {"workflow": "codebase_to_meta_v1", "outputs": ["META_CONTENT_FILE"]},
        {"workflow": "meta_to_workflow_v1", "outputs": ["WORKFLOW_SPEC_FILE"]}
      ]
    }
  ]
}
```

**Tasks:**
1. **Backend: Discovery engine**
   - Match workflows by input/output overlap
   - Support exact, subset, superset matching modes
   - Calculate match score

2. **Backend: Chaining engine (MVP)**
   - Simple chain detection: A.output == B.input
   - Limit chain depth (max 3 for MVP)
   - Return chain as array of steps

3. **Runner: Add discovery client method**
   - `discover_workflows(have_inputs, want_outputs)`

**Verification:**
- Discover by single input → returns matching workflows
- Discover by output → returns workflows that produce it
- Discover with chain → returns multi-step chains

---

### Phase 4: Operator Console Integration

**Goal:** UI for contract discovery and selection.

**Files:**
- `operator-console-v2/src/pages/SubmitPage.tsx`

**Features:**
1. **Discovery mode toggle**
   - Switch from "manual workflow selection" to "discovery mode"

2. **Artifact selectors**
   - Dropdown of known artifact keys (from backend)
   - Multi-select for "I have"
   - Multi-select for "I want"

3. **Discovery results table**
   - List matching workflows with match score
   - Show missing inputs (what else is needed)
   - One-click select to populate submission form

4. **Chain visualization**
   - Show chained workflows as a flow diagram
   - Allow selecting chain vs single workflow

**Tasks:**
1. **Console: Add artifact key endpoint**
   - GET /api/artifacts/keys returns all known artifact keys

2. **Console: Discovery UI components**
   - Artifact selector component
   - Discovery results table
   - Chain visualizer (simple boxes/arrows)

3. **Console: Integration with submit flow**
   - Selecting a discovery result populates:
     - workflow_name
     - input artifacts (pre-filled based on match)
     - implementation (default selected)

**Verification:**
- User selects "I have DRAFT_INIT_FILE, want WORKFLOW_SPEC_FILE"
- System shows workflow_builder_v2 as match
- User clicks match → submit form pre-filled

---

### Phase 5: Workflow Chaining Foundation

**Goal:** Enable workflows to invoke other workflows via contract.

**Architecture:**

```
Parent Workflow
  └── Step: "invoke_child_workflow"
      └── Action: trigger_workflow_by_contract
          └── Input: {contract_input: value}
          └── Output: {contract_output: value} → available to parent
```

**New Action:**

```python
# agent_runner_v2/actions/trigger_workflow.py

def trigger_workflow_by_contract(
    input_artifacts: dict[str, str],
    target_contract: dict[str, Any],  # {inputs: [...], outputs: [...]}
    wait_for_completion: bool = True,
) -> dict[str, str]:
    """
    1. Discover workflows matching target_contract
    2. If multiple matches, raise/return list for user selection
    3. Submit run for selected workflow
    4. If wait_for_completion: poll until complete, return outputs
    5. If async: return run_id for later polling
    """
```

**Backend Support:**
- Child runs reference parent_run_id
- GET /api/runs/{id}/children lists child runs
- Cascading status (parent waits for children)

**Tasks:**
1. **Backend: Parent-child run relationship**
   - Add `parent_run_id` column to run table
   - Add `child_runs` relationship

2. **Backend: Cascading status**
   - Parent run status considers child runs
   - Option to block parent until children complete

3. **Runner: trigger_workflow action**
   - Implement `trigger_workflow_by_contract()`
   - Support sync and async modes

4. **Runner: Child run context injection**
   - Child receives parent context (artifacts, config)
   - Child outputs available to parent on completion

**Verification:**
- Parent workflow triggers child by contract
- Child runs, produces outputs
- Parent receives outputs and continues

---

## 5. Implementation Order

| Phase | Depends On | Effort | Priority |
|-------|------------|--------|----------|
| 1. Contract Storage | — | Small | P1 |
| 2. Contract Query | Phase 1 | Small | P1 |
| 3. Discovery API | Phase 2 | Medium | P2 |
| 4. Console Integration | Phase 2 | Medium | P2 |
| 5. Chaining | Phase 1-3 | Large | P3 |

**MVP Scope:** Phases 1-2 (backend storage and basic query)  
**Complete Scope:** All phases

---

## 6. Example: Updated workflow.toml

```toml
[workflow]
name = "workflow_builder_v2"
label = "Workflow Builder V2"
description = "Builds workflow packages from composition specs"
job_prefix = "AGB"
init_step = "analyze_spec"

[workflow.contract]
inputs = ["COMPOSITION_SPEC_FILE", "BASE_COMPOSITION_STANDARD_FILE"]
optional_inputs = ["REFERENCE_WORKFLOW_TOML"]
outputs = ["WORKFLOW_SPEC_FILE", "WORKFLOW_PACKAGE_DIR"]
input_output_description = "Transforms composition spec into executable workflow package"
category = "builder"
tags = ["codegen", "workflow", "sdlc"]

[[workflow.implementation]]
name = "standard"
label = "Standard Builder"
description = "Full 12-step builder pipeline"

[[workflow.implementation]]
name = "fast"
label = "Fast Builder"
description = "Skip validation steps for quick iteration"

[[workflow.step]]
name = "analyze_spec"
# ... step config
```

---

## 7. Database Schema (Backend)

```sql
-- Add to workflow table
ALTER TABLE workflow ADD COLUMN contract_definition JSONB DEFAULT NULL;

-- Parent-child relationship for chaining
ALTER TABLE workflow_run ADD COLUMN parent_run_id UUID REFERENCES workflow_run(id);
ALTER TABLE workflow_run ADD COLUMN child_run_ids UUID[] DEFAULT '{}';
```

---

## 8. API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/workflows/sync` | POST | Includes contract in definition |
| `/api/workflows` | GET | Add `has_input`, `has_output` filters |
| `/api/workflows/contracts` | GET | List all contracts (lightweight) |
| `/api/workflows/{name}/contract` | GET | Single contract |
| `/api/workflows/discover` | POST | Match by have/want artifacts |
| `/api/artifacts/keys` | GET | List known artifact keys |
| `/api/runs/{id}/children` | GET | List child runs (chaining) |

---

## 9. Success Criteria

- [ ] Backend stores and returns workflow contracts
- [ ] Sync includes contract from workflow.toml
- [ ] Query by input/output artifact works
- [ ] Discovery API returns matching workflows
- [ ] Console has discovery mode UI
- [ ] Workflows can trigger other workflows by contract (P3)

---

## 10. Open Questions

1. **Chain scoring:** How to rank chains when multiple paths exist?
2. **Artifact compatibility:** Exact key match or type-based matching?
3. **Circular chains:** Detect and prevent A→B→A?
4. **Async chaining:** Parent continues before child completes?
5. **Multi-impl chains:** Which impl to use in chained execution?
