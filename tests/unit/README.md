# Unit Tests

Unit tests verify individual functions, classes, and logic in isolation without file I/O or external dependencies.

## Running Unit Tests

```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run all workflow-grouped unit tests
python tests/run_workflow_unit_tests.py all

# Run one workflow test group
python tests/run_workflow_unit_tests.py 00_core_governance_bootstrap_v1

# Run with coverage
python -m pytest tests/unit/ --cov=agent_runner_v2 --cov-report=term-missing

# Run specific test
python -m pytest tests/unit/test_bundle_loader.py -xvs
```

## Test Files

- `test_bundle_loader.py` - Bootstrap bundle loading logic
- `test_runtime_context_paths.py` - Path resolution logic
- `test_tool_instruction_block.py` - Prompt rendering logic
- `test_codebase_docs.py` - Documentation generation logic
- `test_documentation_governance.py` - Governance rules and validation
- `test_documentation_guardrails_cleanup.py` - Cleanup logic
- `test_run_agent_status.py` - Status formatting functions
- `test_backend_worker_mode.py` - Backend worker mode logic (mocked)
- `workflows/<workflow_name>/` - Workflow-specific unit tests grouped by bundle

## Workflow Test Groups

Workflow-owned tests now live under:

```text
tests/unit/workflows/
  00_core_governance_bootstrap_v1/
  00_repo_master_docs_bootstrap_v1/
  ...
```

Use `tests/run_workflow_unit_tests.py` to run one workflow group or all workflow groups together.
