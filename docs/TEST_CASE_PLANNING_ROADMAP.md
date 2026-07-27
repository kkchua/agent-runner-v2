# Test Case Planning Roadmap

**Created:** 2026-07-27
**Status:** Draft

## Purpose

Document current test coverage gaps and plan for missing unit tests and integration tests.

---

## Current State Summary

| Category | Files | Tests | Status |
|----------|-------|-------|--------|
| Unit tests | 55 test files | ~250 tests | Moderate coverage, some gaps |
| Integration tests | 8 test files | ~25 tests | Light coverage, 2 files have import errors |
| Workflows tests | 2 workflows | 12 tests | Minimal coverage |

---

## Unit Test Gaps

### 1. Core Modules Without Tests

| Module | Purpose | Has Tests? | Priority |
|--------|---------|------------|----------|
| `artifact_keys.py` | Canonical artifact key literals | ❌ None | High |
| `artifact_paths.py` | Artifact path resolution | ❌ None | High |
| `path_primitives.py` | Stable filename/root constants | ❌ None | Medium |
| `exceptions.py` | Custom exception classes | ❌ None | Low |
| `action_result.py` | Action result dataclass | ❌ None | Medium |
| `state_defaults.py` | Default state values | ❌ None | Medium |
| `site_styles.py` | Site CSS styles | ❌ None | Low |
| `doc_text.py` | Document text utilities | ❌ None | Low |
| `system_docs.py` | System documentation helpers | ❌ None | Low |

### 2. Modules with Partial Coverage

| Module | Current Tests | Missing Coverage |
|--------|---------------|------------------|
| `daemon.py` | 0 tests (deleted) | Full coverage needed |
| `daemon_runtime.py` | 19 tests (sync payload) | `build_worker_request_payload()`, `resolve_worker_engine_root()` |
| `manual_runtime.py` | 0 tests | `resolve_manual_run()`, `_initialize_state_from_backend()` |
| `run_agent.py` | CLI tests only | `_sync_results_to_backend()`, `_worker_command()` |
| `backend_client.py` | Minimal | API error handling, retry logic |
| `coder_adapters.py` | Sidecar grace tests | OpenCode invocation, timeout handling |
| `step_runner.py` | Render tests | `run_step()`, `run_action()`, `build_context()` |
| `workflow_router.py` | Notification tests | `route_after_step()`, `route_after_failure()` |
| `job_state.py` | Various tests | State migration, artifact validation |

### 3. CLI Command Modules

| Module | Current Tests | Missing Coverage |
|--------|---------------|------------------|
| `submit_commands.py` | 1 test | Error handling, argument validation |
| `approve_commands.py` | 1 test | Resume flag, error cases |
| `stop_commands.py` | 1 test | Cancel logic |
| `list_runs_commands.py` | 1 test | Output formatting |
| `show_run_commands.py` | 1 test | JSON output |
| `reset_step_commands.py` | 1 test | Validation logic |
| `codebase_init_commands.py` | 1 test | Directory creation |

---

## Integration Test Gaps

### 1. Daemon Behavior Tests (HIGH PRIORITY)

**Current State:** `test_daemon.py` has 4 tests, `test_backend_worker_mode.py` has import errors

**Missing Tests:**

| Scenario | Description | Priority |
|----------|-------------|----------|
| Worker ID matching | Submit job with matching `worker_id` → daemon claims it | High |
| Worker ID filtering | Submit job with different `worker_id` → daemon ignores it | High |
| Worker label matching | Submit job with matching `worker_label` → daemon claims it | High |
| Job claim → execute → sync | Full cycle: claim → spawn CLI → execute → sync results | High |
| Cancel during execution | Cancel run while step executing → daemon skips sync | High |
| Backend unreachable | Backend down during claim → daemon retries gracefully | Medium |
| Child process timeout | Step exceeds timeout → daemon terminates child | Medium |
| Multi-step workflow | Complete workflow with 3+ steps sequentially | Medium |

### 2. Notification Tests

**Current State:** 5 test files, moderate coverage

**Missing Tests:**

| Scenario | Description | Priority |
|----------|-------------|----------|
| Pushover API failure | API returns error → graceful degradation | Medium |
| Rate limiting | Multiple notifications → rate limiting applied | Low |

### 3. End-to-End Workflow Tests

**Current State:** None

**Missing Tests:**

| Scenario | Description | Priority |
|----------|-------------|----------|
| Bootstrap workflow | Run `00_bootstrap_lifecycle_admin_v1` to completion | Medium |
| Governance workflow | Run `01_governance_foundation_v1` to completion | Medium |
| SDLC scaffold | Run `sdlc_00_delivery_scaffold_v1` to completion | Medium |

---

## Test Files with Issues

### Import Errors

| File | Error | Action |
|------|-------|--------|
| `tests/integration/test_architecture_site.py` | Module import error | Fix or delete |
| `tests/integration/test_backend_worker_mode.py` | Module import error | Fix imports |

### Recently Deleted

| File | Reason | Replacement |
|------|--------|-------------|
| `tests/unit/test_daemon_race_conditions.py` | Mock-based tests, no real coverage | Integration tests needed |

---

## Recommended Test Implementation Order

### Phase 1: Critical Unit Tests (Week 1)

1. `daemon_runtime.py` — Add tests for `build_worker_request_payload()`
2. `manual_runtime.py` — Add tests for `resolve_manual_run()` logic
3. `artifact_keys.py` — Add tests for key validation

### Phase 2: Daemon Integration Tests (Week 2-3)

1. Worker ID matching/filtering
2. Job claim → execute → sync cycle
3. Cancel during execution handling

### Phase 3: Workflow Integration Tests (Week 4)

1. Bootstrap workflow end-to-end
2. SDLC scaffold end-to-end

### Phase 4: Remaining Unit Test Gaps (Ongoing)

1. CLI command modules
2. Path/artifact modules
3. State management

---

## Test Philosophy

### Unit Tests

- **Test pure logic functions directly** — no mocks for the logic being tested
- **Mock only external dependencies** — subprocess, network, filesystem
- **Verify outputs, not mock interactions** — check return values, state changes
- **Avoid `assert_called()` patterns** — they test mocks, not code

### Integration Tests

- **Test real system behavior** — submit job → daemon picks up → verify state
- **Use real backend when possible** — or realistic test doubles
- **Test failure scenarios** — network down, timeout, crash
- **Verify end-to-end outcomes** — not intermediate API calls

---

## Metrics Targets

| Metric | Current | Target |
|--------|---------|--------|
| Unit test coverage (core modules) | ~60% | 80% |
| Integration test coverage (daemon) | ~10% | 70% |
| Workflow end-to-end tests | 0 | 3 workflows |
| Mock-based unit tests | 2 files | 0 files |

---

## Appendix: Source Module Inventory

### Core Runtime (68 modules)

```
agent_runner_v2/
├── run_agent.py              # CLI entry point
├── daemon.py                 # Backend polling supervisor
├── daemon_runtime.py         # Daemon payload construction
├── manual_runtime.py         # Manual mode resolution
├── step_runner.py            # Step execution
├── workflow_router.py        # Post-step routing
├── job_state.py              # Job state management
├── backend_client.py         # Backend API client
├── coder_adapters.py         # LLM invocation
├── execution_core.py         # Execution orchestration
├── runtime_context.py        # Runtime paths
├── constants.py              # Path constants
├── artifact_keys.py          # Artifact key literals
├── artifact_paths.py         # Artifact path resolution
├── path_primitives.py        # Path helpers
├── exceptions.py             # Custom exceptions
├── ... (53 more modules)
```

### Test Coverage Matrix

| Module | Unit Tests | Integration Tests | Coverage |
|--------|------------|-------------------|----------|
| daemon_runtime.py | ✅ 19 | ❌ | Medium |
| manual_runtime.py | ❌ | ❌ | None |
| run_agent.py | ✅ CLI | ❌ | Low |
| step_runner.py | ✅ Render | ❌ | Low |
| workflow_router.py | ✅ Notif | ❌ | Low |
| daemon.py | ❌ | ✅ 4 | Low |
| job_state.py | ✅ Various | ❌ | Medium |
| backend_client.py | ✅ Minimal | ❌ | Low |