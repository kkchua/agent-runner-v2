---
title: "Developer Guide: agent-runner-v2"
template_id: "ENG-01-DG"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Developer Guide: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. Getting Started

### 1.1 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime |
| pip | Latest | Package management |
| Git | Latest | Version control |

### 1.2 Installation

```bash
# Clone the repository
git clone <repository-url>
cd agent-runner-v2

# Install in development mode
pip install -e ".[dev]"

# Initialize the runner
ukbe-run-agent init
```

### 1.3 Verify Installation

```bash
# Check CLI is available
ukbe-run-agent --help

# Run tests
pytest
```

## 2. Development Workflow

### 2.1 Code Scanning Location

Code scanning and analysis functionality lives in:

| File | Path | Purpose |
|------|------|---------|
| Repository Scanner | `agent_runner_v2/actions/scan_repo_codebase.py` | Scans repo and generates baseline |
| Codebase Docs | `agent_runner_v2/codebase_docs.py` | Codebase documentation helpers |
| Module Templates | `agent_runner_v2/actions/prepare_delivery_scaffold.py` | Generates module doc templates |

### 2.2 Documentation Generation Location

Documentation generation happens across these modules:

| Document Type | Location | Generated Output |
|---------------|----------|------------------|
| Project Analysis | `agent_runner_v2/actions/scan_repo_codebase.py` | `project_analysis.md` |
| Codebase Inventory | `agent_runner_v2/actions/scan_repo_codebase.py` | `codebase_inventory.md` |
| Module Docs | `agent_runner_v2/actions/sync_codebase_docs.py` | `docs/codebase/02_modules/*.md` |
| System Docs | `agent_runner_v2/actions/sync_system_docs.py` | `docs/system/**/*.md` |
| Validation | `agent_runner_v2/actions/validate_*.py` | Validation reports |

### 2.3 Workflow Execution Location

Workflow execution is orchestrated by:

| Component | File | Purpose |
|-----------|------|---------|
| CLI Entry | `agent_runner_v2/run_agent.py` | Command parsing, top-level orchestration |
| Step Runner | `agent_runner_v2/step_runner.py` | Prompt rendering, coder invocation, validation |
| Router | `agent_runner_v2/workflow_router.py` | Post-step routing, loop management |
| Job State | `agent_runner_v2/job_state.py` | State machine, lifecycle management |

## 3. Project Structure

### 3.1 Where to Find Things

| What | Where | Notes |
|------|-------|-------|
| Core execution | `agent_runner_v2/run_agent.py` | CLI and orchestration |
| Step execution | `agent_runner_v2/step_runner.py` | Prompt → Coder → Sidecar |
| Routing | `agent_runner_v2/workflow_router.py` | Post-step decisions |
| Job state | `agent_runner_v2/job_state.py` | JSON state machine |
| LLM adapters | `agent_runner_v2/coder_adapters.py` | Claude/Codex/Qwen |
| Actions | `agent_runner_v2/actions/*.py` | 16 deterministic actions |
| Tests | `tests/*.py` | Pytest test suite |
| Prompts | `agent_runner_v2/bootstrap/workflows/default/prompts/` | 100+ templates |

### 3.2 Adding a New Feature

#### 3.2.1 Adding a New Action

1. Create file: `agent_runner_v2/actions/my_action.py`
2. Implement action function:
```python
def run_my_action(*, artifact_root: Path, context: dict, **kwargs) -> dict:
    """Run my custom action."""
    # Implementation
    return {"status": "ok", "result_path": str(output_path)}
```
3. Export in `agent_runner_v2/actions/__init__.py`:
```python
from .my_action import run_my_action
__all__ = [..., "run_my_action"]
```
4. Register in `agent_runner_v2/runner_actions.py`
5. Add tests in `tests/test_my_action.py`

#### 3.2.2 Adding a New Workflow Family

1. Define workflow in `template_groups.py`:
```python
MY_WORKFLOW = {
    "steps": {
        "01_step": {...},
    },
    "transitions": [...],
}
TEMPLATE_GROUPS["my_workflow_v1"] = MY_WORKFLOW
```
2. Create prompts in `prompts/my_workflow_v1/*.txt`
3. Update `ARTIFACT_KEYS` if new artifact types
4. Test workflow: `ukbe-run-agent run my_workflow_v1`

#### 3.2.3 Adding a New Coder Provider

1. Extend `coder_adapters.py`:
```python
def invoke_new_coder(prompt_text: str, **kwargs) -> InvocationResult:
    # Implementation
    pass
```
2. Add to `CODER_ADAPTERS` mapping
3. Add to `model_mapping.json`
4. Update documentation

## 4. Testing

### 4.1 Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_runner_v2

# Run specific test
pytest tests/test_job_state.py -v

# Run with debug output
pytest -s --tb=short
```

### 4.2 Test Structure

| Test File | Coverage |
|-----------|----------|
| `test_backend_worker_mode.py` | Backend integration |
| `test_bundle_loader.py` | Bundle loading |
| `test_codebase_docs.py` | Documentation sync |
| `test_daemon.py` | Daemon supervisor |
| `test_run_agent_status.py` | CLI status handling |
| `test_runtime_context_paths.py` | Path resolution |
| `test_tool_instruction_block.py` | Tool instructions |
| `test_ukbe_runner_wrapper.py` | Wrapper functionality |

### 4.3 Writing Tests

Tests use pytest with fixtures in `conftest.py`:

```python
def test_my_feature(tmp_path, mock_context):
    # Arrange
    job_id = "test-job"
    
    # Act
    result = my_function(job_id=job_id, path=tmp_path)
    
    # Assert
    assert result.status == "ok"
```

## 5. Debugging

### 5.1 Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export AGENT_RUNNER_LOG_LEVEL=debug
```

### 5.2 Inspect Job State

```bash
# Read job state
cat %USERPROFILE%\.ukbe-runner\jobs\default\<job-id>\job.json | jq .

# Check step result
cat %USERPROFILE%\.ukbe-runner\jobs\default\<job-id>\<step>\meta.json | jq .
```

### 5.3 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Meta.json not found | Coder didn't write sidecar | Check coder timeout, review logs |
| Artifact validation fail | Path doesn't exist | Check `artifact_root` resolution |
| Workflow not found | Bundle not initialized | Run `ukbe-run-agent init` |
| Step routing error | Invalid transition | Check `template_groups.py` transitions |

## 6. Code Style

### 6.1 Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Docstrings: Google style

### 6.2 Imports

```python
# Standard library
import datetime
from pathlib import Path

# Third party
import jinja2

# Local
from .runtime_context import PROJECT_ROOT
from .job_state import load_job
```

### 6.3 Type Hints

```python
def process_step(
    step_name: str,
    config: dict[str, Any],
    *,
    timeout: int | None = None,
) -> StepResult:
    ...
```

## 7. Contribution Workflow

### 7.1 Before Committing

1. Run tests: `pytest`
2. Check type hints: `mypy agent_runner_v2/`
3. Check style: `ruff check agent_runner_v2/`
4. Update documentation if needed

### 7.2 Protected Documents

The following documents are workflow-generated and should not be manually edited:

| Document | Path |
|----------|------|
| Codebase Inventory | `docs/codebase/01_inventory/codebase_inventory.md` |
| Module Docs | `docs/codebase/02_modules/*.md` |
| System Docs (Governance) | `docs/system/00_governance/bootstrap/*.md` |
| Change Impact | `docs/codebase/04_changes/*.md` |

## 8. Key Patterns

### 8.1 Adding Context to Prompts

```python
context = build_context(
    state=job_state,
    step_cfg=step_config,
    project_root=PROJECT_ROOT,
)
prompt = render_prompt(template_path, context)
```

### 8.2 Handling Step Results

```python
result = run_step(...)
if result.status == "APPROVED":
    # Advance to next step
    pass
elif result.status == "REJECTED":
    # Handle rejection
    pass
```

### 8.3 State Transitions

```python
# Valid transitions
CREATED → IN_PROGRESS
IN_PROGRESS → WAITING_FOR_AUTO_RETRY
IN_PROGRESS → WAITING_FOR_HUMAN_INTERVENTION
IN_PROGRESS → WAITING_FOR_HUMAN_APPROVAL
IN_PROGRESS → COMPLETED
IN_PROGRESS → FAILED
```

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
