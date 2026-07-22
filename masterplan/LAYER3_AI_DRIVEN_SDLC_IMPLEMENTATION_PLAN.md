---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "implementation plan for Layer 3 AI-Driven SDLC workflows; exclude from operational scans"
---

# Layer 3 AI-Driven SDLC Implementation Plan

## Status

**Draft** — This document defines the implementation sequence and strategy for the Layer 3 AI-Driven SDLC workflow bundles.

## Implementation Approach

We will follow the SDLC workflow sequence for implementation, building each workflow on top of the previous one:

```
Phase 0: Prerequisites (CLI + Folder Structure)
    ↓
Phase 0.4: sdlc_00_delivery_scaffold_v1 (Bootstrap Templates + Agents)
    ↓
Phase 1: sdlc_10_requirement_v1 (INIT/REQ)
    ↓
Phase 2: sdlc_20_planning_v1 (PLAN)
    ↓
Phase 3: sdlc_30_backlog_v1 (BACKLOG)
    ↓
Phase 4: sdlc_40_task_v1 (TASK)
    ↓
Phase 5: sdlc_50_implementation_v1 (IMPL)
    ↓
Phase 6: sdlc_60_execution_v1 (EXEC)
    ↓
Phase 7: sdlc_70_validation_v1 (VALIDATION)
    ↓
Phase 8: sdlc_80_review_v1 (REVIEW)
    ↓
Phase 9: sdlc_00_codebase_v1 (Maintenance Sync)
```

**Rationale:**
- Phase 0.4 generates the master templates and agent contracts that all SDLC workflows reference
- Each workflow can be tested end-to-end as it's implemented
- Early workflows (10, 20, 30) establish the approval gate pattern
- Middle workflows (40, 50, 60) test the task execution model
- Late workflows (70, 80) validate the complete flow
- sdlc_00_codebase_v1 is implemented last as it's a maintenance workflow, not part of the initiative flow

## Coding Standards

All code implemented for Layer 3 SDLC workflows must follow these standards:

### Docstrings
- **All modules** must have a module-level docstring explaining purpose
- **All classes** must have a class-level docstring explaining purpose and usage
- **All functions** must have a function-level docstring with:
  - Brief description of what the function does
  - Args section documenting each parameter
  - Returns section documenting return value
  - Raises section documenting exceptions (if any)
- Use Python standard docstring format (triple quotes)
- Follow PEP 257 docstring conventions
- Docstrings must be ASCII-only (no Unicode characters)

**Example:**
```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of what the function does.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param1 is invalid.
    """
    pass
```

### General Standards
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Keep functions focused and single-purpose
- Write unit tests for all new code

## Phase 0: Prerequisites

### 0.1 CLI Command: codebase-init

**Objective:** Create CLI command for initial codebase setup

**Deliverables:**
- `ukbe-run-agent codebase-init` command implementation
- Creates `docs/repo/codebase/` directory structure
- Generates initial codebase documentation

**Testing:**
- Run command on empty repository
- Verify folder structure created
- Verify initial docs generated

**Dependencies:** None

### 0.2 Folder Structure

**Objective:** Create SDLC folder structure

**Deliverables:**
- `docs/repo/sdlc/delivery/` subfolders
- `docs/repo/sdlc/00_governance/` baseline docs
- `docs/repo/codebase/` structure (from codebase-init)

**Testing:**
- Verify all folders exist
- Verify governance docs present

**Dependencies:** Phase 0.1

### 0.3 Shared Actions

**Objective:** Implement shared actions used by multiple workflows

**Deliverables:**
- `promote_artifact` action (single artifact promotion)
- `promote_to_requirement` action (two-file promotion)
- `promote_all` action (multi-artifact promotion)
- `aggregate_executions` action (for sdlc_70)
- `commit_changes` action (for sdlc_00)
- `create_backup` action (for sdlc_00)
- `generate_sync_log` action (for sdlc_00)

**Testing:**
- Unit tests for each action
- Integration tests with mock artifacts

**Dependencies:** Phase 0.2

### 0.4 sdlc_00_delivery_scaffold_v1

**Objective:** Create bootstrap workflow that generates master document templates and agent contracts

**Deliverables:**
- `workflows/sdlc_00_delivery_scaffold_v1/workflow.toml`
- `workflows/sdlc_00_delivery_scaffold_v1/prompts/01_generate_templates.txt`
- `workflows/sdlc_00_delivery_scaffold_v1/prompts/02_generate_agent_contracts.txt`
- `workflows/sdlc_00_delivery_scaffold_v1/prompts/03_review_scaffold.txt`
- `workflows/sdlc_00_delivery_scaffold_v1/prompts/04_refine_scaffold.txt`
- `workflows/sdlc_00_delivery_scaffold_v1/context_extensions.py`
- `workflows/sdlc_00_delivery_scaffold_v1/output_paths.py`
- `workflows/sdlc_00_delivery_scaffold_v1/bundle_governance/`
- `run-sdlc_00_delivery_scaffold_v1.bat`

**Output Model:** L2 platform pattern (stage → publish → init to global)
- Staging: `docs/system/00_governance/platform/agent_runner/sdlc/runs/<job_id>/`
- Publish: `docs/system/00_governance/platform/agent_runner/sdlc/current/`
- Global: `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/`

**Generated Outputs:**
- `00_governance/` — SDLC governance baseline
- `01_templates/` — 10 master document templates
- `02_agents/` — 8 agent contract files

**Testing:**
- Verify workflow.toml parses correctly
- Verify prompt templates render with context
- Verify output paths follow L2 platform pattern
- Dry-run to verify template and agent generation

**Dependencies:** Phase 0.2

---

## Phase 1: sdlc_10_requirement_v1 (INIT/REQ)

### 1.1 Workflow Package

**Objective:** Implement requirement intake workflow

**Deliverables:**
- `workflows/sdlc_10_requirement_v1/workflow.toml`
- `workflows/sdlc_10_requirement_v1/prompts/*.txt`
- `workflows/sdlc_10_requirement_v1/actions.py` (if needed)
- `workflows/sdlc_10_requirement_v1/context_extensions.py`
- `workflows/sdlc_10_requirement_v1/output_paths.py`
- `workflows/sdlc_10_requirement_v1/bundle_governance/`

**Testing:**
- Dry-run with mock DRAFT_INIT_FILE
- Verify PRE-REQ generation
- Verify REQ promotion
- Verify approval gate works

**Dependencies:** Phase 0

### 1.2 Batch File

**Objective:** Create batch file for manual execution

**Deliverables:**
- `run-sdlc_10_requirement_v1.bat`

**Testing:**
- Run batch file
- Verify workflow executes

**Dependencies:** Phase 1.1

### 1.3 Integration Test

**Objective:** End-to-end test of requirement workflow

**Testing:**
- Create sample DRAFT_INIT_FILE
- Run workflow
- Verify PRE-REQ and REQ generated
- Verify approval gate
- Verify artifacts in correct locations

**Dependencies:** Phase 1.2

---

## Phase 2: sdlc_20_planning_v1 (PLAN)

### 2.1 Workflow Package

**Objective:** Implement planning workflow

**Deliverables:**
- `workflows/sdlc_20_planning_v1/workflow.toml`
- `workflows/sdlc_20_planning_v1/prompts/*.txt`
- `workflows/sdlc_20_planning_v1/context_extensions.py`
- `workflows/sdlc_20_planning_v1/output_paths.py`
- `workflows/sdlc_20_planning_v1/bundle_governance/`

**Testing:**
- Dry-run with approved REQ
- Verify PLAN generation
- Verify approval gate

**Dependencies:** Phase 1 (approved REQ)

### 2.2 Batch File

**Deliverables:**
- `run-sdlc_20_planning_v1.bat`

**Dependencies:** Phase 2.1

### 2.3 Integration Test

**Testing:**
- Run sdlc_10 -> sdlc_20 flow
- Verify PLAN generated from REQ
- Verify approval gate

**Dependencies:** Phase 2.2

---

## Phase 3: sdlc_30_backlog_v1 (BACKLOG)

### 3.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_30_backlog_v1/workflow.toml`
- `workflows/sdlc_30_backlog_v1/prompts/*.txt`
- `workflows/sdlc_30_backlog_v1/context_extensions.py`
- `workflows/sdlc_30_backlog_v1/output_paths.py`
- `workflows/sdlc_30_backlog_v1/bundle_governance/`

**Testing:**
- Dry-run with approved PLAN
- Verify BACKLOG generation
- Verify approval gate

**Dependencies:** Phase 2 (approved PLAN)

### 3.2 Batch File

**Deliverables:**
- `run-sdlc_30_backlog_v1.bat`

**Dependencies:** Phase 3.1

### 3.3 Integration Test

**Testing:**
- Run sdlc_10 -> sdlc_20 -> sdlc_30 flow
- Verify BACKLOG generated from PLAN
- Verify approval gate

**Dependencies:** Phase 3.2

---

## Phase 4: sdlc_40_task_v1 (TASK)

### 4.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_40_task_v1/workflow.toml`
- `workflows/sdlc_40_task_v1/prompts/*.txt`
- `workflows/sdlc_40_task_v1/context_extensions.py`
- `workflows/sdlc_40_task_v1/output_paths.py`
- `workflows/sdlc_40_task_v1/bundle_governance/`

**Testing:**
- Dry-run with approved BACKLOG
- Verify TASK generation (one per backlog item)
- Verify approval gate

**Dependencies:** Phase 3 (approved BACKLOG)

### 4.2 Batch File

**Deliverables:**
- `run-sdlc_40_task_v1.bat`

**Dependencies:** Phase 4.1

### 4.3 Integration Test

**Testing:**
- Run sdlc_10 -> sdlc_20 -> sdlc_30 -> sdlc_40 flow
- Verify TASK docs generated from BACKLOG
- Verify multiple TASK docs for multiple backlog items
- Verify approval gate

**Dependencies:** Phase 4.2

---

## Phase 5: sdlc_50_implementation_v1 (IMPL)

### 5.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_50_implementation_v1/workflow.toml`
- `workflows/sdlc_50_implementation_v1/prompts/*.txt`
- `workflows/sdlc_50_implementation_v1/context_extensions.py`
- `workflows/sdlc_50_implementation_v1/output_paths.py`
- `workflows/sdlc_50_implementation_v1/bundle_governance/`

**Testing:**
- Dry-run with approved TASK
- Verify IMPL generation
- Verify IMPL contains all required sections
- Verify approval gate

**Dependencies:** Phase 4 (approved TASK)

### 5.2 Batch File

**Deliverables:**
- `run-sdlc_50_implementation_v1.bat`

**Dependencies:** Phase 5.1

### 5.3 Integration Test

**Testing:**
- Run sdlc_10 -> ... -> sdlc_50 flow
- Verify IMPL docs generated from TASK
- Verify IMPL contains detailed implementation plan
- Verify approval gate

**Dependencies:** Phase 5.2

---

## Phase 6: sdlc_60_execution_v1 (EXEC)

### 6.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_60_execution_v1/workflow.toml`
- `workflows/sdlc_60_execution_v1/prompts/*.txt`
- `workflows/sdlc_60_execution_v1/context_extensions.py`
- `workflows/sdlc_60_execution_v1/output_paths.py`
- `workflows/sdlc_60_execution_v1/bundle_governance/`

**Testing:**
- Dry-run with approved IMPL
- Verify EXEC generation
- Verify internal review/refine loop
- Verify human approval gate
- Verify actual code changes (mock)

**Dependencies:** Phase 5 (approved IMPL)

### 6.2 Batch File

**Deliverables:**
- `run-sdlc_60_execution_v1.bat`

**Dependencies:** Phase 6.1

### 6.3 Integration Test

**Testing:**
- Run sdlc_10 -> ... -> sdlc_60 flow
- Verify EXEC docs generated from IMPL
- Verify internal review/refine loop works
- Verify human approval gate
- Verify code changes made

**Dependencies:** Phase 6.2

---

## Phase 7: sdlc_70_validation_v1 (VALIDATION)

### 7.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_70_validation_v1/workflow.toml`
- `workflows/sdlc_70_validation_v1/prompts/*.txt`
- `workflows/sdlc_70_validation_v1/actions.py` (aggregate_executions)
- `workflows/sdlc_70_validation_v1/context_extensions.py`
- `workflows/sdlc_70_validation_v1/output_paths.py`
- `workflows/sdlc_70_validation_v1/bundle_governance/`

**Testing:**
- Dry-run with multiple approved EXEC docs
- Verify aggregation works
- Verify VAL generation
- Verify system-wide validation
- Verify approval gate

**Dependencies:** Phase 6 (all EXEC approved)

### 7.2 Batch File

**Deliverables:**
- `run-sdlc_70_validation_v1.bat`

**Dependencies:** Phase 7.1

### 7.3 Integration Test

**Testing:**
- Run sdlc_10 -> ... -> sdlc_70 flow
- Verify VAL doc generated from all EXEC docs
- Verify system-wide validation
- Verify approval gate

**Dependencies:** Phase 7.2

---

## Phase 8: sdlc_80_review_v1 (REVIEW)

### 8.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_80_review_v1/workflow.toml`
- `workflows/sdlc_80_review_v1/prompts/*.txt`
- `workflows/sdlc_80_review_v1/actions.py` (close_initiative)
- `workflows/sdlc_80_review_v1/context_extensions.py`
- `workflows/sdlc_80_review_v1/output_paths.py`
- `workflows/sdlc_80_review_v1/bundle_governance/`

**Testing:**
- Dry-run with approved VAL
- Verify REV, MEM, CLOSE generation
- Verify review/refine loop
- Verify human approval gate
- Verify codebase update
- Verify multi-artifact promotion

**Dependencies:** Phase 7 (approved VAL)

### 8.2 Batch File

**Deliverables:**
- `run-sdlc_80_review_v1.bat`

**Dependencies:** Phase 8.1

### 8.3 Integration Test

**Testing:**
- Run complete sdlc_10 -> ... -> sdlc_80 flow
- Verify REV, MEM, CLOSE docs generated
- Verify review/refine loop works
- Verify human approval gate
- Verify codebase updated
- Verify initiative closure

**Dependencies:** Phase 8.2

---

## Phase 9: sdlc_00_codebase_v1 (Maintenance Sync)

### 9.1 Workflow Package

**Deliverables:**
- `workflows/sdlc_00_codebase_v1/workflow.toml`
- `workflows/sdlc_00_codebase_v1/prompts/*.txt`
- `workflows/sdlc_00_codebase_v1/actions.py` (commit_changes, create_backup, generate_sync_log)
- `workflows/sdlc_00_codebase_v1/context_extensions.py`
- `workflows/sdlc_00_codebase_v1/output_paths.py`
- `workflows/sdlc_00_codebase_v1/bundle_governance/`

**Testing:**
- Dry-run on repository with codebase docs
- Verify sync log generation
- Verify backup creation
- Verify git commit
- Verify no approval gates

**Dependencies:** Phase 0 (codebase docs exist)

### 9.2 Batch File

**Deliverables:**
- `run-sdlc_00_codebase_v1.bat`

**Dependencies:** Phase 9.1

### 9.3 Integration Test

**Testing:**
- Make manual changes to repository
- Run sdlc_00
- Verify codebase docs updated
- Verify sync log created
- Verify backup created
- Verify git commit made

**Dependencies:** Phase 9.2

---

## Testing Strategy

### Unit Tests
- Each action has unit tests
- Each prompt template validated
- Workflow.toml validated

### Integration Tests
- Each phase has integration test
- Tests run full workflow with mock inputs
- Tests verify outputs in correct locations
- Tests verify approval gates work

### End-to-End Tests
- Complete initiative flow (sdlc_10 -> sdlc_80)
- Multiple tasks in one initiative
- Review/refine loops
- Human approval gates

### Regression Tests
- After each phase, run all previous phases
- Ensure no regressions introduced

## Migration Path

### Legacy Workflow Deprecation
- `00_repo_master_docs_bootstrap_v1` will be deprecated after Phase 9
- Users should migrate to `codebase-init` + `sdlc_00_codebase_v1`
- Legacy workflow will be moved to `archive/` folder

### Data Migration
- No data migration needed
- New workflows use different folder structure
- Legacy docs remain in place

## Success Criteria

### Phase Completion
Each phase is complete when:
- Workflow package created
- Batch file created
- Integration tests pass
- Documentation updated

### Overall Completion
Implementation is complete when:
- All 9 phases complete
- End-to-end test passes
- Legacy workflow deprecated
- User documentation updated

## Risk Mitigation

### Risk: Complex workflow interactions
**Mitigation:** Implement in sequence, test each phase before moving to next

### Risk: Approval gate failures
**Mitigation:** Test approval gates thoroughly in each phase

### Risk: Multi-task orchestration
**Mitigation:** Test with multiple tasks in Phase 4, 5, 6

### Risk: Codebase sync errors
**Mitigation:** Implement backup and sync log in Phase 9

## References

- Layer 3 AI-Driven SDLC Specification: `masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md`
- Layer 2 Platform Core Specification: `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md`
- Layer 1 Governance Specification: `masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md`
- Legacy workflow reference: `masterplan/00_repo_master_docs_bootstrap_v1/`
