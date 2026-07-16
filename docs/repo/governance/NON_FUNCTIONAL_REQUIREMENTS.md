---
template_id: "SYS-00-NFR"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Non-Functional Requirements

This document captures the quality attributes, runtime expectations, and
operational constraints for `agent-runner-v2`.

## Quality Attributes

### Reliability

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| Job state persistence | After every step | `job_state.py` persists to disk |
| State recovery | Resume from last checkpoint | Recovery runtime reads job state |
| Graceful shutdown | Complete current step, persist state | Signal handling in daemon |
| Error handling | Catch exceptions, log context, fail step | Exception handling in step runner |

### Availability

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| Daemon uptime | 99%+ with auto-restart | Backend health monitoring |
| Job retry | Manual retry via CLI | Submit command with same job ID |
| Backend failover | Continue with local state | Job state in `.ukbe-runner/` |

### Performance

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| Job state write | < 100ms | JSON serialization to disk |
| Workflow loading | < 1s | TOML parsing and validation |
| Prompt rendering | < 500ms | Template string formatting |
| Notification dispatch | < 2s | Async Pushover API calls |

### Scalability

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| Parallel workflows | Unlimited (OS-limited) | Independent job directories |
| Concurrent daemon workers | Configurable per deployment | Subprocess spawning |
| Artifact size | No explicit limit | File system dependent |

## Operational Requirements

### Platform Support

| Platform | Support Level | Notes |
|----------|---------------|-------|
| Windows 10/11 | Primary | Batch scripts, `.venv` activation |
| Linux | Supported | WSL tested, native path pending |
| macOS | Untested | Path handling may need adjustment |

### Runtime Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Runtime environment |
| `tomli` | 2.0+ | TOML parsing |
| `requests` | 2.28+ | HTTP client for notifications |
| `markdown` | 3.5+ | Site generation |
| LLM coder | Configurable | OpenCode, Claude, etc. |

### Configuration Requirements

| Configuration | Required | Location |
|---------------|----------|----------|
| `config.json` | Yes | Runner home or project root |
| `.env` | Optional | Project root (credentials) |
| Workflow bundle | Yes | Global or local path |

### Credential Requirements

| Credential | Purpose | Resolution Order |
|------------|---------|------------------|
| Pushover token | Notifications | `.env`, config, environment |
| Pushover user | Notifications | `.env`, config, environment |
| Coder API keys | LLM invocation | Coder-specific config |

## Security Requirements

### Authentication

| Requirement | Implementation |
|-------------|----------------|
| Backend API | API key in config |
| Pushover API | Token/user in config or env |
| Coder backends | Configured per coder |

### Authorization

| Requirement | Implementation |
|-------------|----------------|
| Role-based policies | `role_policies.json` in registry |
| Workflow authorization | Coder role definitions |
| Action execution | No authorization (local execution) |

### Data Protection

| Requirement | Implementation |
|-------------|----------------|
| Credential storage | `.env` (gitignored), environment variables |
| Job state isolation | Per-job directories under `.ukbe-runner/` |
| Artifact protection | Declarative allow-list for deletion |

## Maintainability

### Code Quality

| Requirement | Target | Status |
|-------------|--------|--------|
| Unit test coverage | 80%+ | 45+ unit tests, pure logic focus |
| Integration test coverage | Critical paths | 10+ integration tests |
| Lint/type checking | Pass | Ruff, mypy compatible |

### Documentation

| Requirement | Target | Status |
|-------------|--------|--------|
| API documentation | Per-module | `docs/repo/codebase/02_modules/` |
| Workflow documentation | Per-workflow | `workflow.toml` descriptions |
| Architecture documentation | Layer 2 master docs | This document set |

### Extensibility

| Requirement | Implementation |
|-------------|----------------|
| New workflows | Plugin workflow packages |
| New actions | `@action()` decorator registration |
| New coders | Coder adapter pattern |
| Context extensions | Per-workflow hooks |

## Observability

### Logging

| Log Level | Content | Destination |
|-----------|---------|-------------|
| INFO | Workflow start/end, step completion | Console, file |
| DEBUG | Step details, routing decisions | File (if enabled) |
| ERROR | Failures, exceptions | Console, file |

### Metrics

| Metric | Collection | Purpose |
|--------|------------|---------|
| Step duration | Per-step | Performance monitoring |
| Token usage | Per-coder-step | Cost management |
| Job count | Cumulative | Capacity planning |

### Alerting

| Condition | Alert Method |
|-----------|--------------|
| Workflow failure | Pushover notification |
| Daemon crash | Backend health check |
| Coder timeout | Step timeout error |

## Compliance

### Audit Trail

| Requirement | Implementation |
|-------------|----------------|
| Job history | Persistent job state |
| Step results | Sidecar `meta.json` |
| Execution timestamps | Job state metadata |

### Data Retention

| Data Type | Retention | Cleanup |
|-----------|-----------|---------|
| Job state | Indefinite | Manual cleanup |
| Artifacts | Indefinite | Manual cleanup |
| Logs | Rotating | Log rotation |

### Change Control

| Requirement | Implementation |
|-------------|----------------|
| Workflow changes | Version in TOML manifest |
| Governance changes | Change ID in frontmatter |
| Code changes | Git version control |