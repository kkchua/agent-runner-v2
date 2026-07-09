---
template_id: "ENG-01-DG"
title: "Developer Guide - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:26:47+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide: agent-runner-v2

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd agent-runner-v2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Initialize runner home**
   ```bash
   ukbe-run-agent init
   ```

### Development Cycle

| Phase | Command | Purpose |
|-------|---------|---------|
| **Code** | Edit source files | Implement changes |
| **Test** | `pytest tests/unit/` | Unit tests (pure logic) |
| **Integration** | `pytest tests/integration/` | Integration tests |
| **Validate** | `pytest` | Full test suite |
| **Manual** | `run-00_master_docs_bootstrap_v1.bat` | Workflow testing |

### Code Scanning Entrypoint

**Primary**: `agent_runner_v2/actions/scan_repo_codebase.py`

Purpose: Scans repository and generates codebase documentation baseline.

```bash
# Direct execution via action
python -m agent_runner_v2.actions.scan_repo_codebase

# Via workflow
run-40_documentation_sync_v1.bat  # Includes codebase sync
```

### Documentation Generation Entrypoint

**System Docs**: `agent_runner_v2/actions/sync_system_docs.py`
- Generates system documentation from bootstrap bundles

**Codebase Docs**: `agent_runner_v2/actions/sync_codebase_docs.py`
- Synchronizes codebase documentation with repository state

**Architecture Site**: `agent_runner_v2/actions/publish_architecture_site.py`
- Publishes HTML architecture site for human consumption

```bash
# System docs
run-00_master_docs_bootstrap_v1.bat

# Codebase docs
run-40_documentation_sync_v1.bat

# Architecture site
run-50_architecture_site_v1.bat
```

### Workflow Execution Entrypoint

**Primary**: `agent_runner_v2/run_agent.py`

CLI modes:
- `init`: Initialize runner home
- `run`: Local workflow execution
- `poll`/`worker`: Backend-connected execution
- `daemon`: Continuous operation
- `execute-step`: Direct step execution

```bash
# Run workflow
ukbe-run-agent run <workflow> --target-project-root <path>

# Daemon mode
ukbe-run-agent daemon
```

## Key Commands

### Workflow Launchers (Batch Files)

| Batch File | Workflow | Purpose |
|------------|----------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | 00_master_docs_bootstrap_v1 | Generate master system docs |
| `run-10_execution_scaffold_v1.bat` | 10_execution_scaffold_v1 | Setup delivery scaffold |
| `run-20_initiative_intake_v1.bat` | 20_initiative_intake_v1 | Initiative drafting |
| `run-21_bug_fix_intake_v1.bat` | 21_bug_fix_intake_v1 | Bug triage and patch |
| `run-30_delivery_planning_v1.bat` | 30_delivery_planning_v1 | Plan and task generation |
| `run-31_task_execution_v1.bat` | 31_task_execution_v1 | Task implementation |
| `run-40_documentation_sync_v1.bat` | 40_documentation_sync_v1 | Doc reconciliation |
| `run-50_architecture_site_v1.bat` | 50_architecture_site_v1 | HTML site generation |

### Testing Commands

| Command | Purpose |
|---------|---------|
| `pytest tests/unit/` | Pure unit tests (no filesystem) |
| `pytest tests/integration/` | Integration tests |
| `pytest` | All tests |
| `run-tests.bat` | Test runner batch |

### Development Utilities

| Command | Purpose |
|---------|---------|
| `run-cleanup-generated-docs.bat` | Clean generated docs |
| `run-bootstrap-publish.bat` | Publish bootstrap bundles |
| `run-reset-step.bat` | Reset step for retry |

## Documentation Responsibilities

### System Documentation

| Document | Owner | Update Trigger |
|----------|-------|----------------|
| `PROJECT_ANALYSIS.md` | Bootstrap workflow | Architecture changes |
| `SYSTEM_OVERVIEW.md` | Bootstrap workflow | Capability changes |
| `COMPONENT_ARCHITECTURE.md` | Bootstrap workflow | Structural changes |
| `DECISION_LOG.md` | Bootstrap workflow | New ADRs |
| `DEVELOPER_GUIDE.md` | Bootstrap workflow | Dev process changes |

### Codebase Documentation

| Document | Owner | Update Trigger |
|----------|-------|----------------|
| `codebase_inventory.md` | scan_repo_codebase | New/deleted modules |
| Module docs (02_modules/) | sync_codebase_docs | Module changes |
| Component docs (03_components/) | sync_codebase_docs | Component changes |
| Change impact docs (04_changes/) | sync_codebase_docs | Significant changes |

### Delivery Documentation

| Document | Owner | Update Trigger |
|----------|-------|----------------|
| `DELIVERY_SOP.md` | 10_execution_scaffold_v1 | SOP changes |
| `DELIVERY_STATUS_RULES.md` | 10_execution_scaffold_v1 | Status rule changes |
| `DELIVERY_AGENTS.md` | 10_execution_scaffold_v1 | Agent changes |
| `AGENT-*.md` | 10_execution_scaffold_v1 | Agent changes |

### Template Maintenance

**Location**: `agent_runner_v2/bootstrap/workflows/default/prompts/`

| Template Type | Edit Location |
|---------------|---------------|
| Workflow prompts | `prompts/<workflow>/<step>_<name>.txt` |
| Master templates | `bootstrap/bundles/core/current/templates/` |

**Rule**: When templates need changes, update the SOURCE prompt, not the generated document.

## Architecture Posture

### Current Profile

```yaml
current_profile: "explicit-v2-workflow-runner"
target_profile: "mature-multi-tenant-orchestrator"
migration_mode: "incremental"
repo_state: "explicit"
```

### What "Explicit" Means

The repository declares clear architecture standards:

1. **v2 Execution Contract**
   - Strict sidecar validation (meta.json is ONLY channel)
   - No markdown write-backs by runner
   - No silent recovery paths

2. **Centralized Constants**
   - All paths in `constants.py`
   - Zero hardcoded strings
   - ARTIFACT_KEY_* and FOLDER_KEY_* constants

3. **Deterministic Routing**
   - REVIEW_DECISIONS, HUMAN_DECISIONS, CONTROL_CLASSES
   - No implicit state transitions

4. **Schema Versioning**
   - Job state schema v6
   - Automatic migration on load

### When to Follow Ecosystem Baseline vs Repo-Selected

| Scenario | Approach |
|----------|----------|
| Path construction | Use repo's centralized constants.py |
| Step execution | Follow v2 sidecar-only contract |
| State transitions | Use repo's explicit decision enums |
| Documentation | Follow DOCUMENTATION_STANDARD.md |
| General Python | Follow ecosystem baseline |

### Extension Patterns

**Adding a New Runner Action**:

1. Create `agent_runner_v2/actions/my_action.py`
2. Implement `execute(state, config) -> ActionResult`
3. Register in `agent_runner_v2/actions/__init__.py`
4. Add to workflow template in `template_groups.py`

**Adding a New Workflow**:

1. Define in `template_groups.py` TEMPLATE_GROUPS
2. Create prompts in `prompts/<workflow_name>/`
3. Add batch launcher `run-<workflow>.bat`
4. Update `DOCUMENTATION_STANDARD.md`

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 04_generate_architecture_docs | Change: 00DOC-20260708-78fb419e*
