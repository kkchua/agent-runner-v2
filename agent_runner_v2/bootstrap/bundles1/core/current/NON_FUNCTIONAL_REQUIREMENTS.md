---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures runtime, quality, and operational requirements already implied by the `agent-runner-v2` repository.

## Performance Requirements

### Execution Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Step startup time** | < 5 seconds | Time from trigger to prompt render |
| **Coder invocation overhead** | < 2 seconds | Subprocess spawn + initial setup |
| **Polling interval** | 2-5 seconds | Interval between completion checks |
| **Job state save** | < 100ms | Time to persist job.json |
| **Documentation sync** | < 60 seconds | Full codebase scan and update |

### Throughput

| Scenario | Expected Throughput | Notes |
|----------|---------------------|-------|
| **Sequential steps** | 1 step per coder invocation | Serial execution per job |
| **Parallel jobs** | Limited by worker processes | Daemon manages concurrency |
| **Documentation generation** | 10-50 modules per minute | Depends on LLM response time |

### Resource Utilization

| Resource | Expected Usage | Limits |
|----------|----------------|--------|
| **Memory** | 50-200MB base + job state | Scales with job history size |
| **Disk** | 10MB per job + artifacts | Rotated via cleanup |
| **CPU** | Low (I/O bound) | Spikes during prompt render |
| **Network** | LLM API calls, optional backend | Configurable timeouts |

## Reliability Requirements

### Availability

| Aspect | Requirement |
|--------|-------------|
| **Local execution** | 99.9% (workstation dependent) |
| **Daemon mode** | 99.5% (excluding planned restarts) |
| **Backend connectivity** | Graceful degradation on disconnect |

### Fault Tolerance

| Failure Scenario | Required Behavior |
|------------------|-------------------|
| **LLM API unavailable** | Retry with exponential backoff; explicit failure |
| **Backend disconnect** | Queue locally; retry connection |
| **Job state corruption** | Detect on load; attempt migration |
| **Subprocess crash** | Detect via polling; record failure |
| **Disk full** | Detect pre-flight; fail with clear message |

### Recovery

| Recovery Type | Requirement |
|---------------|-------------|
| **Automatic retry** | 3 attempts default, configurable per step |
| **State recovery** | Resume from last completed step |
| **Daemon recovery** | Restart child processes on failure |
| **Backend reconnection** | Exponential backoff, max 5 minutes |

## Maintainability Requirements

### Code Organization

| Aspect | Requirement |
|--------|-------------|
| **Modularity** | Single responsibility per module |
| **Testability** | Pure functions unit tested; I/O in integration tests |
| **Documentation** | Docstrings for public APIs |
| **Type hints** | Full type coverage for public interfaces |

### Testing Requirements

| Test Type | Coverage Target |
|-----------|-----------------|
| **Unit tests** | Core logic without filesystem dependencies |
| **Integration tests** | End-to-end with temporary directories |
| **Schema validation** | All JSON schemas have test cases |
| **Path resolution** | All artifact paths tested |

### Documentation Requirements

| Aspect | Requirement |
|--------|-------------|
| **Freshness** | Documentation sync runs on significant changes |
| **Completeness** | All modules have documentation entries |
| **Accuracy** | Validation gates check for drift |
| **Accessibility** | Generated sites browsable by all audiences |

## Portability Requirements

### Platform Support

| Platform | Support Level |
|----------|---------------|
| **Windows** | Primary development platform |
| **macOS** | Supported, tested in CI |
| **Linux** | Supported, tested in CI |

### Python Versions

| Version | Support |
|---------|---------|
| **3.11** | Minimum supported |
| **3.12** | Recommended |
| **3.13** | Supported |
| **3.14** | Not yet validated |

### Dependencies

| Category | Requirements |
|----------|--------------|
| **Core** | Minimal standard library + click, jinja2, pyyaml |
| **Optional** | requests (backend), pushover (notifications) |
| **Development** | pytest, pytest-asyncio, ruff, mypy |

## Security Requirements

### Credential Handling

| Requirement | Implementation |
|-------------|----------------|
| **No hardcoded secrets** | Credentials via .env or config.json |
| **Environment isolation** | Subprocess execution isolates LLM context |
| **File permissions** | Job state readable only by owner |

### Data Protection

| Requirement | Implementation |
|-------------|----------------|
| **Local-only by default** | No external transmission in local mode |
| **Backend opt-in** | Worker mode requires explicit backend URL |
| **Audit trail** | Job state records execution history |

### Execution Isolation

| Requirement | Implementation |
|-------------|----------------|
| **Subprocess per step** | Fresh Python process for each invocation |
| **No shared state** | Communication via files only |
| **Sandboxed actions** | Actions operate within project directory |

## Scalability Requirements

### Current Scope

| Aspect | Current Limit |
|--------|---------------|
| **Jobs** | Unbounded (filesystem limited) |
| **Steps per job** | Unbounded (memory limited) |
| **Workers** | Single daemon per workstation |
| **Concurrent jobs** | 1 per daemon (worker model) |

### Future Scope

| Aspect | Target |
|--------|--------|
| **Distributed workers** | Multiple daemon instances |
| **Concurrent execution** | Configurable parallelism |
| **Backend coordination** | Multi-tenant job distribution |
| **State backend** | Optional backend state store |

## Usability Requirements

### CLI Usability

| Requirement | Implementation |
|-------------|----------------|
| **Consistent commands** | Verb-noun pattern (run, init, poll) |
| **Clear error messages** | Structured error types with context |
| **Progress indication** | Step-level status in job state |
| **Help documentation** | `--help` for all commands |

### Configuration Usability

| Requirement | Implementation |
|-------------|----------------|
| **Sensible defaults** | Works without config for basic usage |
| **Environment overrides** | .env file support |
| **Validation** | Config validation on load |
| **Documentation** | Config options documented |

### Observability

| Requirement | Implementation |
|-------------|----------------|
| **Job inspection** | `--show-job`, `--check-job-status` |
| **Log access** | Structured logs per job |
| **State visibility** | job.json human-readable |
| **Notifications** | Optional Pushover integration |

## Compatibility Requirements

### Backward Compatibility

| Aspect | Requirement |
|--------|-------------|
| **Job state** | Auto-migration from schema v1-v6 |
| **Config** | Preserve unknown keys |
| **API** | Stable CLI interface |
| **Workflows** | Legacy workflows continue to function |

### Forward Compatibility

| Aspect | Requirement |
|--------|-------------|
| **Schema versioning** | Forward-compatible field additions |
| **Unknown fields** | Preserve fields not in current schema |
| **Feature flags** | New features behind flags |

## Operational Requirements

### Deployment

| Requirement | Implementation |
|-------------|----------------|
| **Package install** | pip install -e . |
| **Runtime init** | ukbe-run-agent init |
| **No external deps** | Self-contained Python package |

### Monitoring

| Requirement | Implementation |
|-------------|----------------|
| **Health check** | Daemon heartbeat to backend |
| **Job status** | Query via CLI or inspect job.json |
| **Log aggregation** | Per-job log files |
| **Error alerting** | Pushover notifications |

### Maintenance

| Requirement | Implementation |
|-------------|----------------|
| **Cleanup** | Automated old job removal |
| **Backup** | Job directory archivable |
| **Update** | pip install for updates |
| **Re-init** | Safe re-initialization |

## Quality Attributes

| Attribute | Requirement | Verification |
|-----------|-------------|--------------|
| **Correctness** | Deterministic execution | Unit + integration tests |
| **Robustness** | Graceful failure handling | Failure injection tests |
| **Maintainability** | Clear code structure | Code review, linting |
| **Testability** | Pure functions isolated | Test coverage metrics |
| **Observability** | Execution traceability | Job state inspection |
| **Usability** | Clear CLI interface | Documentation, help |
| **Portability** | Cross-platform | CI on multiple platforms |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
