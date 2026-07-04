---
template_id: "ENG-01-DG"
title: "Developer Guide"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide

## Development Workflow

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd agent-runner-v2
   ```

2. **Install with development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Initialize the runner**
   ```bash
   ukbe-run-agent init
   ```
   This seeds the global runner home at `%USERPROFILE%\.ukbe-runner\`.

4. **Verify installation**
   ```bash
   ukbe-run-agent --help
   ```

### Development Cycle

1. **Make changes** to source files in `agent_runner_v2/`

2. **Run tests**
   ```bash
   pytest
   ```

3. **Test locally**
   ```bash
   ukbe-run-agent run <workflow> --local
   ```

4. **Sync workflow changes** (if editing bootstrap workflows)
   ```bash
   sync-workflows-to-backend.bat
   ```

## Key Commands

### Local Execution

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent run <workflow>` | Execute a workflow locally |
| `ukbe-run-agent show-job <workflow> <job-id>` | Inspect job state |
| `ukbe-run-agent retry <workflow> <job-id>` | Retry failed steps |
| `ukbe-run-agent approve-step <workflow> <job-id> <step>` | Force approve a step |
| `ukbe-run-agent reset-step <workflow> <job-id> <step>` | Reset a step for retry |

### Backend Mode

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent worker` | Run as backend worker |
| `ukbe-run-agent poll` | Poll for available work |
| `ukbe-run-agent execute-step <workflow> <job-id> <step>` | Execute single step |

### Daemon Mode

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent daemon` | Start supervision daemon |

### Workflow Management

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent init` | Initialize runner home |
| `ukbe-run-agent list-workflows` | List available workflows |
| `ukbe-run-agent list-jobs <workflow>` | List workflow jobs |

### Development Utilities

| Script | Purpose |
|---------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | Run bootstrap workflow |
| `run-10_execution_scaffold_v1.bat` | Run scaffold workflow |
| `run-cleanup-generated-docs.bat` | Clean generated docs |
| `sync-workflows-to-backend.bat` | Sync workflows to backend |
| `test-runner.bat` | Run test suite |

## Documentation Responsibilities

### Code Scanning Entrypoint

**Location**: `agent_runner_v2/actions/scan_repo_codebase.py`

**Purpose**: Analyzes repository structure and generates codebase documentation baseline.

**When to use**:
- Repository initialization
- After significant code changes
- Documentation drift detection

**Invocation**:
```bash
ukbe-run-agent run 00_master_docs_bootstrap_v1 --init
```

### Documentation Generation Entrypoint

**Location**: `agent_runner_v2/actions/sync_codebase_docs.py`

**Purpose**: Synchronizes codebase documentation with current source state.

**When to use**:
- After code changes
- During bootstrap workflows
- Documentation reconciliation

### Workflow Execution Entrypoint

**Location**: `agent_runner_v2/run_agent.py`

**Purpose**: Main CLI entry point for all workflow operations.

**Key function**: `main(argv)` — Dispatches to subcommands.

### Architecture Posture Management

**Location**: `docs/system/00_governance/bootstrap/project_analysis.md`

**Purpose**: Records current architecture posture and migration state.

**Current posture**:
- `current_profile`: `provisional`
- `target_profile`: `explicit`
- `migration_mode`: `in-progress`

**When posture changes**:
- Update `project_analysis.md`
- Regenerate architecture docs via `00_master_docs_bootstrap_v1`
- Review `COMPONENT_ARCHITECTURE.md` for accuracy

## Architecture Posture

### Profile Separation

The repository follows a **repo-selected profile** approach:

| Concern | Universal Baseline | Repo-Specific |
|---------|-------------------|---------------|
| Execution contract | v2 sidecar rules | Workflow definitions in `template_groups.py` |
| Artifact model | Key classification | 40+ artifact keys defined in code |
| Routing behavior | APPROVED/REJECTED/FAILURE | Per-step routing config |
| Documentation structure | Required documents | Optional depth per module |

### Migration Path

The repository is transitioning from `provisional` to `explicit`:

1. **Current** (`provisional`): Substantial implementation, codebase docs exist
2. **In Progress**: System docs being generated via bootstrap workflow
3. **Target** (`explicit`): Full architecture documentation following standards

### Profile/DDD/EDA Status

| Pattern | Status | Application |
|---------|--------|-------------|
| **DDD** | Conditional | Applied to workflow domain modeling |
| **EDA** | Conditional | Event loop in daemon; explicit routing preferred |

## Extension Points

### Adding a New Coder Adapter

1. Add model configuration to `model_config.py`
2. Implement adapter in `coder_adapters.py`
3. Update `model_mapping.json`
4. Add tests in `tests/test_coder_adapters.py`

### Adding a New Runner Action

1. Create module in `agent_runner_v2/actions/`
2. Implement action function
3. Register in `actions/__init__.py`
4. Reference from `template_groups.py` step config
5. Add tests

### Adding a New Workflow

1. Define steps in `template_groups.py:TEMPLATE_GROUPS`
2. Create prompts in `bootstrap/workflows/default/prompts/<workflow>/`
3. Test with `ukbe-run-agent run <workflow> --local`
4. Sync with `sync-workflows-to-backend.bat`

### Adding Artifact Keys

1. Add to `ARTIFACT_KEYS` list in `template_groups.py`
2. Update `REFERENCE_FILES` if needed
3. Document in workflow prompts

## Debugging

### Job State Inspection

```bash
ukbe-run-agent show-job <workflow> <job-id>
```

Shows:
- Completed/failed steps
- Current artifacts
- Reject counts
- Loop context

### Log Locations

| Log Type | Location |
|----------|----------|
| Runner logs | `%USERPROFILE%\.ukbe-runner\logs\` |
| Job logs | Job directory `logs/` subfolder |
| Step output | Step directory in job folder |

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| "Workflow not found" | Runtime bundle missing | Run `ukbe-run-agent init` |
| "Schema validation failed" | Invalid meta.json | Check sidecar format |
| "Artifact not found" | Missing output file | Verify step produced declared artifacts |
| "Bundle version mismatch" | Outdated runtime bundle | Re-run `init` or sync workflows |

---

*This developer guide provides practical guidance for working with agent-runner-v2. See RUNBOOK.md for operational procedures and SYSTEM_FILE_STRUCTURE.md for directory organization.*
