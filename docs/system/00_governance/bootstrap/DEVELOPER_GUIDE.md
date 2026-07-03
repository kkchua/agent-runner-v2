---
template_id: "ENG-01-DG"
title: "Developer Guide - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Developer Guide: agent-runner-v2

## Development Workflow

### Setup

1. **Clone the repository**
   ```bash
   cd D:\MyProjectSpace\01_Workflows
   git clone <repo-url> agent-runner-v2
   cd agent-runner-v2
   ```

2. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Initialize the runner**
   ```bash
   ukbe-run-agent init
   ```
   This seeds `%USERPROFILE%\.ukbe-runner\` with workflow bundles.

4. **Verify installation**
   ```bash
   ukbe-run-agent --help
   ```

### Making Changes

1. **Edit source files** in `agent_runner_v2/`
2. **Run tests** to verify changes
   ```bash
   pytest
   ```
3. **Test locally** with a workflow
   ```bash
   ukbe-run-agent run --template-group initiative_intake_v1 --dry-run
   ```

### Committing Changes

Follow the existing commit message style observed in `git log`:
- Concise summary line
- Reference issue/PR numbers where applicable

## Key Commands

### Installation and Setup

| Command | Purpose |
|---------|---------|
| `pip install -e ".[dev]"` | Install package with development dependencies |
| `ukbe-run-agent init` | Initialize global runner home |
| `ukbe-run-agent --help` | Show CLI help |

### Local Workflow Execution

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent run --template-group <group>` | Run workflow from template group |
| `ukbe-run-agent run --job-id <id>` | Resume existing job |
| `ukbe-run-agent run --dry-run` | Render prompts without invocation |
| `ukbe-run-agent run --show-job` | Display job state |
| `ukbe-run-agent run --check-job-status` | Check job status |

### Worker Mode

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent worker --backend-url <url> --worker-id <id>` | Start worker loop |
| `ukbe-run-agent worker --once` | Execute single poll cycle |
| `ukbe-run-agent poll --backend-url <url> --worker-id <id>` | Poll and execute one step |
| `ukbe-run-agent execute-step --request-file <file> --result-file <file>` | Execute single step |

### Daemon Mode

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent daemon <worker-id>` | Start daemon supervisor |
| `ukbe-run-agent daemon <worker-id> --backend-url <url>` | Start with backend |

### Batch File Shortcuts

| File | Purpose |
|------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | Run documentation bootstrap workflow |
| `run-10_execution_scaffold_v1.bat` | Run execution scaffold workflow |
| `run-approve-step.bat` | Approve pending step |
| `run-reset-step.bat` | Reset step for retry |
| `run-daemon.bat` | Launch daemon mode |

## Documentation Responsibilities

### Entry Points

| Functionality | Entry Point | Module |
|---------------|-------------|--------|
| **Code Scanning** | `scan_repo_codebase.py` action | `agent_runner_v2/actions/scan_repo_codebase.py` |
| **Documentation Generation** | `sync_codebase_docs.py`, `sync_system_docs.py` actions | `agent_runner_v2/actions/sync_*.py` |
| **Workflow Execution** | `ukbe-run-agent` CLI | `agent_runner_v2/run_agent.py:main()` |

### Code Scanning

The code scanning entry point is `actions/scan_repo_codebase.py`:

```python
# From actions/scan_repo_codebase.py
def scan_repository(project_root: Path) -> dict:
    """Analyze repository structure and return codebase inventory."""
    ...
```

**Triggered by:**
- `00_master_docs_bootstrap_v1` workflow step `01_generate_codebase_baseline`
- Manual execution via `ukbe-run-agent run` with appropriate template group

### Documentation Generation

The documentation generation entry points are:

| Generator | Module | Output |
|-----------|--------|--------|
| Codebase docs | `actions/sync_codebase_docs.py` | `docs/codebase/01_inventory/`, `docs/codebase/02_modules/`, `docs/codebase/03_components/` |
| System docs | `actions/sync_system_docs.py` | `docs/system/00_governance/bootstrap/` |

**Triggered by:**
- Bootstrap workflow steps
- Documentation sync workflow (`40_documentation_sync_v1`)

### Workflow Execution

The workflow execution entry point is:

```python
# agent_runner_v2/run_agent.py
def main():
    """CLI entry point for ukbe-run-agent."""
    ...
```

**Command:** `ukbe-run-agent`

**Modes:**
- `init` — Initialize runner home
- `run` — Local workflow execution
- `worker` — Backend-connected worker loop
- `poll` — Single poll and execute
- `execute-step` — Single step execution
- `daemon` — Workstation supervisor

## Architecture Posture

### Current Posture

| Attribute | Value |
|-----------|-------|
| **Current Profile** | `explicit` |
| **Target Profile** | `standard` |
| **Migration Mode** | `in_progress` |

### Profile Explanation

**Explicit Profile Characteristics:**
- Architecture decisions are documented but not enforced by tooling
- Module boundaries exist but rely on convention
- Documentation is generated and protected by guardrails
- Test coverage exists but gaps remain

**Standard Profile Target:**
- Fully documented component boundaries
- Comprehensive test coverage
- Clear public API contracts
- Cross-platform support

### Migration Path

The repository is actively migrating toward the `standard` profile:

1. **Documentation** (In Progress)
   - System documentation bootstrap (this workflow)
   - Codebase documentation reconciliation
   - Operational manual refresh

2. **Testing** (Pending)
   - Expand test coverage
   - Add integration tests for workflow families

3. **Platform Support** (Pending)
   - Cross-platform path handling
   - Linux/macOS testing

### Repository vs Ecosystem Baseline

This repository uses a **repo-selected profile**:

| Aspect | Universal Baseline | This Repository |
|--------|-------------------|-----------------|
| **Organization** | Technical layers | Workflow families |
| **Documentation** | Manual maintenance | Generated + protected |
| **Deployment** | Package installation | Bootstrap + runtime split |
| **Communication** | Varied patterns | Strict sidecar-only |

### When to Follow vs Diverge

**Follow ecosystem baseline when:**
- Adding new technical components
- Implementing standard patterns (logging, configuration)
- Writing utility modules

**Diverge intentionally when:**
- Workflow execution semantics require specific patterns
- Bootstrap/runtime split provides necessary flexibility
- Sidecar-only communication ensures validation

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
