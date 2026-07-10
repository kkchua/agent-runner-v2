---
title: "Developer Guide"
template_id: "ENG-01-DG"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide: agent-runner-v2

## Development Workflow

### 1. Code Scanning Entrypoint

**File**: `agent_runner_v2/actions/scan_repo_codebase.py`

**Purpose**: Automated codebase inventory generation

**Invocation**:
```bash
# Via workflow
run-40_documentation_sync_v1.bat

# Or directly
ukbe-run-agent run scan_repo_codebase --workflow documentation_sync_v1
```

**What it does**:
- Scans repository Python files
- Generates `docs/codebase/01_inventory/codebase_inventory.md`
- Creates/updates module documentation stubs
- Identifies component relationships

**When to run**:
- After adding new modules
- After significant refactoring
- Before documentation sync workflow

### 2. Documentation Generation Entrypoint

**Files**:
- `agent_runner_v2/actions/generate_site.py` - HTML architecture site
- `agent_runner_v2/actions/prepare_delivery_scaffold.py` - Delivery governance
- `agent_runner_v2/actions/finalize_bootstrap.py` - Bootstrap completion

**Purpose**: Generate structured documentation from code

**Invocation**:
```bash
# Master system docs
run-00_master_docs_bootstrap_v1.bat

# Delivery scaffold
run-10_execution_scaffold_v1.bat

# Architecture site
run-50_architecture_site_v1.bat
```

**What they do**:
- Generate markdown from templates and analysis
- Validate against section requirements
- Create HTML sites for multi-audience consumption
- Update bootstrap bundles

**When to run**:
- `00_master_docs_bootstrap_v1` - New repo or major structural changes
- `10_execution_scaffold_v1` - Setting up delivery governance
- `50_architecture_site_v1` - Publishing docs to stakeholders

### 3. Workflow Execution Entrypoint

**File**: `agent_runner_v2/run_agent.py` (CLI)

**Purpose**: Primary workflow execution interface

**Invocation**:
```bash
# Manual execution
ukbe-run-agent run <workflow> --project-root <path>

# Backend worker
ukbe-run-agent worker --worker-id <id>

# Execute single step
ukbe-run-agent execute-step --job-id <id> --step <step>

# Daemon mode
ukbe-run-agent daemon --worker-id <id>
```

**Key Commands**:
| Command | Purpose |
|---------|---------|
| `init` | Initialize runner home and seed workflows |
| `run` | Execute workflow manually |
| `worker` | Run as backend-connected worker |
| `poll` | Poll backend for work |
| `execute-step` | Execute single step (daemon subprocess) |
| `daemon` | Start workstation supervisor |

### 4. Architecture Posture Management

**Entrypoints**:
- `docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md` - Read-only, generated
- `agent_runner_v2/constants.py` - Centralized path constants

**Purpose**: Maintain repository architectural posture

**Current Posture**:
| Attribute | Value |
|-----------|-------|
| **Current Profile** | `provisional` |
| **Target Profile** | `structured_delivery` |
| **Migration Mode** | `incremental` |
| **Repo State** | `explicit` |

**What this means**:
- Repository has existing documentation (67+ module docs)
- Documentation actively being reconciled
- Targeting structured delivery workflow governance
- Following incremental migration, not big-bang

## Key Commands

### Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Initialize runner home
ukbe-run-agent init --project-root .
```

### Testing

```bash
# Run all tests
run-all-tests.bat

# Run only unit tests
run-tests.bat
# or
pytest tests/unit -v

# Run only integration tests
run-integration-tests.bat
# or
pytest tests/integration -v
```

### Workflow Execution

```bash
# Bootstrap system docs for current repo
run-00_master_docs_bootstrap_v1.bat

# Scaffold delivery governance
run-10_execution_scaffold_v1.bat

# Intake a new initiative
run-20_initiative_intake_v1.bat

# Execute a task
run-31_task_execution_v1.bat

# Sync documentation after code changes
run-40_documentation_sync_v1.bat

# Generate architecture site
run-50_architecture_site_v1.bat
```

### Daemon Operations

```bash
# Start daemon
run-daemon.bat

# Or directly
ukbe-run-agent daemon --worker-id <id>
```

**Note**: Code changes are picked up automatically; no daemon restart required.

### Utility Scripts

| Script | Purpose |
|----------|---------|
| `run-approve-step.bat` | Approve waiting step |
| `run-reset-step.bat` | Reset step for retry |
| `run-cleanup-generated-docs.bat` | Clean generated docs |

## Documentation Responsibilities

### Code to Documentation Mapping

| Code Change | Documentation Impact | Required Action |
|-------------|---------------------|-----------------|
| New module added | Module doc in `docs/codebase/02_modules/` | Run `40_documentation_sync_v1` |
| New action added | Action doc, component doc update | Run `40_documentation_sync_v1` |
| API change | Functional spec update | Manual update + sync |
| New workflow | Template group doc, prompts doc | Run bootstrap workflows |
| Path constant change | All dependent docs | Update constants, run sync |

### Documentation Generation Flow

```
Code Change → Scan Repo → Generate Inventory → Update Module Docs → Validate → Commit
```

### Who Updates What

| Document Type | Generated By | Manual Updates |
|---------------|--------------|----------------|
| `codebase_inventory.md` | `scan_repo_codebase.py` | Never (regenerate) |
| Module docs (`02_modules/`) | Bootstrap/reconcile | Never (regenerate) |
| Component docs (`03_components/`) | Bootstrap/reconcile | Never (regenerate) |
| System docs (`system/`) | Master bootstrap | Governance rules only |
| Delivery docs (`delivery/`) | Delivery workflows | Initiative-specific content |

### Critical Files

**Never modify manually** (workflow-generated):
- `docs/codebase/01_inventory/codebase_inventory.md`
- `docs/codebase/02_modules/*.md`
- `docs/codebase/03_components/*.md`
- `docs/system/00_governance/bootstrap/*.md` (except via workflows)

**Modify with care** (centralized constants):
- `agent_runner_v2/constants.py` - Changes affect all paths
- `agent_runner_v2/bootstrap/workflows/default/template_groups.py` - Step definitions

## Architecture Posture

### Repository State

**Explicit** - The repository contains:
- 67+ module documentation files
- Structured workflow definitions (8+ families)
- Comprehensive test suite (45 unit tests)
- Active documentation governance (`docs/delivery/`, `docs/codebase/`)

### Posture Attributes

| Attribute | Current | Target | Migration Path |
|-----------|---------|--------|----------------|
| **Profile** | provisional | structured_delivery | Incremental refinement |
| **Documentation** | 67 module docs | Full coverage | Reconcile gaps |
| **Test Coverage** | 45 unit tests | 100+ tests | Add as needed |
| **Governance** | Bootstrap active | Stable | Stabilize over time |

### Development Guidelines

1. **Follow CODER_IMPLEMENTATION_SOP.md** - All code changes must adhere to SOP
2. **Use centralized constants** - No hardcoded paths; use `constants.py`
3. **Add tests for logic** - Unit tests for pure functions
4. **Run sync after changes** - Documentation sync keeps docs current
5. **Preserve contracts** - Sidecar-only results, explicit routing

### Extension Points

| Extension | Entrypoint | Pattern |
|-----------|------------|---------|
| New action | `actions/<name>.py` | Implement `run_action()` |
| New workflow | `bootstrap/workflows/default/template_groups.py` | Define step sequence |
| New coder | `coder_adapters.py` | Add adapter function |
| New validation | `actions/validate_*.py` | Implement validator |

### Common Tasks

**Adding a new runner action**:
1. Create `agent_runner_v2/actions/my_action.py`
2. Implement `run_action(*, action_name, action_cfg, state, step_dir, ...)`
3. Import in `actions/__init__.py`
4. Add test in `tests/unit/test_actions.py`
5. Run `40_documentation_sync_v1` to generate docs

**Adding a new workflow step**:
1. Edit `template_groups.py` to add step definition
2. Create prompt template in `bootstrap/workflows/default/prompts/<wf>/`
3. Run `ukbe-run-agent init` to sync runtime bundle
4. Test with `--dry-run` first

**Modifying artifact paths**:
1. Update constants in `constants.py`
2. Update `REFERENCE_FILES` dict if prompt placeholders affected
3. Run `40_documentation_sync_v1` to validate
4. Run `00_master_docs_bootstrap_v1` to regenerate affected docs
