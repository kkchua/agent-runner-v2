---
template_id: "ENG-01-DG"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide

## Development Workflow

### Getting Started

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd agent-runner-v2
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Initialize the runner**:
   ```bash
   ukbe-run-agent init
   ```

5. **Verify installation**:
   ```bash
   ukbe-run-agent --help
   pytest tests/unit/ -v
   ```

### Development Cycle

**Typical development flow**:

1. Make code changes in `agent_runner_v2/`
2. Run unit tests: `run-tests.bat` or `pytest tests/unit/ -v`
3. Run integration tests (if needed): `run-integration-tests.bat`
4. Test workflow execution: `run-00_master_docs_bootstrap_v1.bat`
5. Submit to backend (if applicable): `submit-*.bat`

**Important**: The daemon spawns fresh subprocesses, so code changes are picked up automatically without restart.

### Code Organization

| Area | Location | Responsibility |
|------|----------|--------------|
| CLI Entry | `run_agent.py` | Command parsing and orchestration |
| Step Execution | `step_runner.py` | Prompt rendering, coder invocation |
| Routing | `workflow_router.py` | Post-step routing decisions |
| State | `job_state.py` | Job persistence |
| Actions | `actions/*.py` | Deterministic runner actions |
| Constants | `constants.py` | All path constants |

## Key Commands

### Local Development Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `ukbe-run-agent init` | Initialize runner home | `ukbe-run-agent init --project-root .` |
| `ukbe-run-agent run` | Execute workflow locally | `ukbe-run-agent run --workflow default` |
| `ukbe-run-agent status` | Check job status | `ukbe-run-agent status <job-id>` |
| `ukbe-run-agent approve` | Approve a step | `ukbe-run-agent approve <job-id>` |

### Backend-Connected Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `ukbe-run-agent worker` | Start worker polling | `ukbe-run-agent worker --backend-url http://localhost:8100 --worker-id my-worker` |
| `ukbe-run-agent poll` | Single poll operation | `ukbe-run-agent poll` |
| `ukbe-run-agent execute-step` | Execute single step | `ukbe-run-agent execute-step --request-file req.json` |
| `ukbe-run-agent daemon` | Start daemon | `ukbe-run-agent daemon my-daemon` |

### Testing Commands

| Command | Purpose |
|---------|---------|
| `pytest tests/unit/ -v` | Run unit tests |
| `pytest tests/integration/ -v` | Run integration tests |
| `run-tests.bat` | Windows unit test runner |
| `run-integration-tests.bat` | Windows integration test runner |
| `run-all-tests.bat` | Run all tests |

### Workflow Commands (Batch Files)

| Batch File | Purpose |
|------------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | Bootstrap system docs |
| `run-10_execution_scaffold_v1.bat` | Scaffold delivery framework |
| `run-20_initiative_intake_v1.bat` | New initiative workflow |
| `run-30_delivery_planning_v1.bat` | Delivery planning workflow |
| `run-31_task_execution_v1.bat` | Task execution workflow |
| `run-40_documentation_sync_v1.bat` | Sync documentation |
| `run-50_architecture_site_v1.bat` | Generate architecture site |

### Documentation Commands

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent bootstrap-publish` | Publish repo docs to bootstrap bundle |
| `run-cleanup-generated-docs.bat` | Clean generated docs for regeneration |

## Documentation Responsibilities

### Code Scanning Entrypoint

**File**: `agent_runner_v2/actions/scan_repo_codebase.py`

**Purpose**: Discovers and catalogs all source files in the repository.

**Usage**: Called by `00_master_docs_bootstrap_v1` step 01 or manually via workflow execution.

**Output**: `docs/codebase/01_inventory/codebase_inventory.md`

### Documentation Generation Entrypoint

**File**: `agent_runner_v2/actions/sync_system_docs.py` and `sync_codebase_docs.py`

**Purpose**: Synchronizes generated documentation with repository state.

**Usage**: 
- Automatically called by bootstrap workflows
- Manual execution via `run-40_documentation_sync_v1.bat`

**Output**: Refreshed system and codebase documentation.

### Workflow Execution Entrypoint

**File**: `agent_runner_v2/run_agent.py`

**Purpose**: Main CLI entry point for all workflow execution.

**Key Functions**:
- `run_workflow_group()` — Execute a workflow group
- `run_step()` — Execute a single step
- `execute_step_mode()` — Backend step execution

### Architecture Posture Management

**Current Profile**: `explicit`
**Target Profile**: `universal-bootstrap`
**Migration Mode**: `maintenance`

**What this means**:
- Architecture decisions are explicitly documented (this file)
- Contracts are strictly enforced in code
- Generated documents are protected from manual edits
- Changes follow the migration mode (refresh vs recreate)

**Profile Decision Sources**:
- Profile declared in `PROJECT_ANALYSIS.md`
- Evidence from code patterns
- Migration path in `BUNDLE_MIGRATION_PLAN.md`

## Architecture Posture

### Where Code Scanning Lives

**Primary**: `agent_runner_v2/actions/scan_repo_codebase.py`

Scans repository and generates:
- Module inventory
- Component inventory
- Change impact tracking

**Called by**: `00_master_docs_bootstrap_v1` step 01.

### Where Documentation Generation Lives

**System Docs**: `agent_runner_v2/actions/sync_system_docs.py`
**Codebase Docs**: `agent_runner_v2/actions/sync_codebase_docs.py`

These actions:
- Read codebase inventory
- Generate/refresh documentation
- Apply protection banners
- Update manifest

**Called by**: Bootstrap and sync workflows.

### Where Workflow Execution Lives

**Core**: `agent_runner_v2/run_agent.py` (CLI)
**Step Logic**: `agent_runner_v2/step_runner.py`
**Routing**: `agent_runner_v2/workflow_router.py`

### Where Architecture Decisions Live

**Constants**: `agent_runner_v2/constants.py` (all path decisions)
**Workflows**: `agent_runner_v2/bootstrap/workflows/default/template_groups.py`
**Decisions**: `docs/system/00_governance/bootstrap/DECISION_LOG.md`

### Entrypoint Summary

| Purpose | Entrypoint | Location |
|---------|------------|----------|
| Code scanning | `scan_repo_codebase.py` | `agent_runner_v2/actions/` |
| Documentation generation | `sync_system_docs.py`, `sync_codebase_docs.py` | `agent_runner_v2/actions/` |
| Workflow execution | `run_agent.py` (CLI) | `agent_runner_v2/` |
| Architecture posture | Profile declared in `PROJECT_ANALYSIS.md` | `docs/system/00_governance/bootstrap/` |

## Development Guidelines

### Adding a New Action

1. Create file in `agent_runner_v2/actions/my_action.py`
2. Implement action function with signature: `def my_action(context: dict) -> dict`
3. Register in `agent_runner_v2/actions/__init__.py`
4. Add tests in `tests/unit/actions/`

### Adding a New Workflow

1. Define workflow in `agent_runner_v2/bootstrap/workflows/default/template_groups.py`
2. Create prompt templates in `prompts/<workflow_name>/`
3. Sync to runtime: `sync-workflows-to-backend.bat`
4. Create launcher: `run-<workflow>.bat`

### Modifying Constants

1. Edit `agent_runner_v2/constants.py`
2. Run tests: `pytest tests/unit/ -v`
3. Sync workflows if template_groups.py affected
4. Run bootstrap to regenerate affected docs

### Windows Path Handling

Always use the `_safe_relative_to()` helper for path operations:

```python
from pathlib import Path
import os

def _safe_relative_to(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return os.path.relpath(path, base)
```

Windows `pathlib.Path.relative_to()` can fail even for valid subpaths.

## Testing Guidelines

### Unit Tests

- Location: `tests/unit/`
- Scope: Pure logic, isolated, no filesystem dependencies
- Run: `pytest tests/unit/ -v`

**Guidelines**:
- Mock all external dependencies
- Test edge cases and error conditions
- Keep tests fast (< 100ms per test)

### Integration Tests

- Location: `tests/integration/`
- Scope: Real files, external systems, subprocesses
- Run: `pytest tests/integration/ -v`

**Guidelines**:
- May use `tmp_path` fixture (with Windows permission awareness)
- Test full workflow paths
- May require environment variables

### Test Markers

```python
# In pyproject.toml:
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (isolated, no filesystem)",
    "integration: Integration tests (real files, external systems)",
]
```

## Common Tasks

### Debug a Failing Step

1. Find job ID from output or `ukbe-run-agent list`
2. Check `~/.ukbe-runner/jobs/<workflow>/<job-id>/job.json`
3. Review step directory: `~/.ukbe-runner/jobs/<workflow>/<job-id>/<step>/`
4. Check `meta.json` for error details
5. Check `~/.ukbe-runner/logs/` for execution logs

### Update Workflow Prompts

1. Edit files in `agent_runner_v2/bootstrap/workflows/default/prompts/<workflow>/`
2. Run `sync-workflows-to-backend.bat` or `ukbe-run-agent init`
3. Test with `run-<workflow>.bat`

### Regenerate Documentation

1. Run `run-cleanup-generated-docs.bat` (optional, to force full regeneration)
2. Run `run-00_master_docs_bootstrap_v1.bat`
3. Review changes in `docs/system/00_governance/bootstrap/`

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
