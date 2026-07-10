---
template_id: "ENG-01-DG"
title: "Developer Guide - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide: agent-runner-v2

## Development Workflow

### 1. Local Setup

```bash
# Clone repository
git clone <repo-url>
cd agent-runner-v2

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Running Tests

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run all tests
pytest
```

### 3. Running Workflows

```bash
# Initialize runner
ukbe-run-agent init

# Run master docs bootstrap
run-00_master_docs_bootstrap_v2.bat

# Run execution scaffold
run-10_execution_scaffold_v2.bat

# Run initiative intake
run-20_initiative_intake_v1.bat
```

### 4. Code Changes

The daemon spawns fresh subprocesses for each step, so code changes are picked up automatically without daemon restart. Simply submit a new job or wait for the next step.

## Key Commands

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent init` | Initialize runner home |
| `ukbe-run-agent run --template-group <workflow>` | Run workflow locally |
| `ukbe-run-agent worker --backend-url <url>` | Run as backend worker |
| `ukbe-run-agent daemon <worker_id>` | Run supervisor daemon |
| `pytest tests/unit/` | Run unit tests |
| `run-*.bat` | Pre-configured workflow batch files |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `AGENT_RUNNER_ROOT` | Path to agent-runner-v2 installation |
| `TARGET_PROJECT_ROOT` | Project to run workflows against |
| `DRY_RUN` | Set to `true` for prompt rendering only |
| `NEW_JOB` | Set to `true` for fresh job creation |

## Documentation Responsibilities

### Code Scanning Entrypoint

**File**: `agent_runner_v2/actions/scan_repo_codebase.py`

**Purpose**: Repository scanning for documentation generation.

**Usage**:
```bash
# Scan is triggered by workflows
run-40_documentation_sync_v1.bat
```

**Output**: `docs/codebase/01_inventory/codebase_inventory.md`

### Documentation Generation Entrypoint

**File**: `agent_runner_v2/actions/generate_site.py`

**Purpose**: HTML site generation for architecture documentation.

**Usage**:
```bash
# Generate stakeholder site
run-51_stakeholder_docs_v1.bat

# Generate developer site
run-52_developer_docs_v1.bat
```

**Output**: `docs/system/00_governance/bootstrap/*.html`

### Workflow Execution Entrypoint

**File**: `agent_runner_v2/run_agent.py`

**Purpose**: CLI entry point for all workflow execution.

**Usage**:
```bash
# Local execution
ukbe-run-agent run --template-group <workflow>

# Worker mode
ukbe-run-agent worker --backend-url <url>

# Daemon mode
ukbe-run-agent daemon <worker_id>
```

### Bootstrap-to-Runtime Sync

**File**: `agent_runner_v2/sync_workflows.py`

**Purpose**: Synchronize bootstrap workflow files to global runtime bundles.

**Usage**:
```bash
# Sync workflows (called automatically)
python -m agent_runner_v2.sync_workflows
```

## Architecture Posture

### Current Profile: `provisional`

The repository follows a **provisional** architecture profile because:

1. **Active migration**: Plugin workflow system replacing monolithic TEMPLATE_GROUPS
2. **Bootstrap/runtime distinction**: Careful synchronization required
3. **Documentation establishment**: Bootstrap documents being generated
4. **Test coverage verification**: Ongoing

### Target Profile: `explicit`

The intended target is `explicit` - a fully documented, tested, and typed system with:

- All modules documented
- Architecture decisions recorded
- Operational procedures defined
- Validation automated

### Migration Mode: `in_progress`

The current migration is the plugin workflow system on branch `feat/plugin-workflow-system`:

| Aspect | Legacy | New |
|--------|--------|-----|
| Definition | `template_groups.py` dict | `workflow.toml` manifest |
| Prompts | Embedded strings | `prompts/*.txt` files |
| Hooks | Hardcoded | `context_extensions.py` |
| Loading | Dict lookup | Adapter pattern |

### Evidence Sources

1. **Plugin system migration**: Active branch `feat/plugin-workflow-system`
2. **Constants refactoring**: Recent migration to centralized `constants.py`
3. **Bootstrap/runtime distinction**: Two-tier source of truth documented
4. **v2 sidecar contract**: Strict meta.json enforcement
5. **Test infrastructure**: 45 unit tests passing

## Working with the Codebase

### Adding a New Action

1. Create file in `agent_runner_v2/actions/my_action.py`
2. Implement `my_action(*, context, state, step_cfg, project_root)`
3. Return `ActionResult(status="success", outputs={})`
4. Import in `agent_runner_v2/actions/__init__.py`

### Adding a New Workflow (Plugin)

1. Create directory `workflows/my_workflow_v1/`
2. Write `workflow.toml` manifest
3. Create `prompts/` directory with templates
4. Optional: Add `context_extensions.py` for hooks
5. No changes to core code required

### Modifying Core Execution

1. Edit relevant file (e.g., `step_runner.py`)
2. Add/update tests in `tests/unit/`
3. Run tests to verify
4. Changes picked up automatically (no daemon restart)

### Path Constants

All paths use centralized constants:

```python
from agent_runner_v2.constants import (
    ARTIFACT_KEY_PROJECT_ANALYSIS,
    FOLDER_KEY_SYSTEM_BOOTSTRAP,
    artifact_path,
)

# Get path for artifact
path = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
```

Never hardcode paths. Always use constants.

### Sidecar Contract

When writing coder steps, ensure meta.json compliance:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary",
    "artifacts": {
      "ARTIFACT_KEY": "relative/path/to/file.md"
    },
    "recorded_at": "2026-07-10T19:56:49+08:00"
  }
}
```

## Debugging

### Enable Verbose Logging

```python
# In code or config
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Job State

```bash
# Read job.json
cat ~/.ukbe-runner/jobs/<job_id>/job.json
```

### Check Step Sidecars

```bash
# List step directories
ls ~/.ukbe-runner/jobs/<job_id>/steps/

# Read meta.json
cat ~/.ukbe-runner/jobs/<job_id>/steps/01_<step>/meta.json
```

### Dry Run Mode

```bash
# Render prompts without execution
set DRY_RUN=true
run-00_master_docs_bootstrap_v2.bat
```

## Testing Philosophy

| Test Type | Location | Purpose |
|-----------|----------|---------|
| Unit | `tests/unit/` | Pure logic, isolated, no I/O |
| Integration | `tests/integration/` | Real files, subprocesses, external systems |

### Unit Test Requirements

- Mock external dependencies
- Test pure functions
- No filesystem operations
- Fast execution

### Integration Test Requirements

- Real file operations
- Subprocess execution
- Network where needed
- Slower but comprehensive

## Contributing

1. Follow existing code style
2. Use centralized constants for paths
3. Add tests for new functionality
4. Update documentation
5. Run full test suite before commit

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
