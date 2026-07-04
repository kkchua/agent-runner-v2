---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures the quality attributes and operational requirements for the `agent-runner-v2` platform. These requirements constrain how the system behaves while meeting its functional goals.

## Quality Attributes

### QA-1: Reliability

**Requirement**: The system must handle transient failures gracefully and maintain job state integrity.

**Metrics**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| Step success rate | > 95% | Successful steps / total steps |
| State persistence | 100% | Jobs recoverable after interruption |
| Data integrity | 100% | No corruption on graceful shutdown |

**Strategies**:
- Atomic job state writes
- Idempotent retry handling
- Clear failure classification

### QA-2: Performance

**Requirement**: Step execution must complete within acceptable time bounds.

**Metrics**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| Prompt rendering | < 100ms | Time to render template |
| Job state save | < 50ms | Time to persist state |
| Artifact validation | < 200ms | Time to check artifact existence |
| Step overhead | < 500ms | Non-LLM step processing time |

**Constraints**:
- LLM invocation time is provider-dependent and excluded
- Network latency to backend is excluded from worker metrics

### QA-3: Scalability

**Requirement**: The system must support concurrent execution patterns.

**Metrics**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| Concurrent jobs | 10+ | Jobs in flight per daemon |
| Workflow families | 20+ | Supported without degradation |
| Steps per workflow | 50+ | Steps without performance loss |

**Limitations**:
- Single daemon per workstation
- Job state is file-based (not distributed)
- Backend coordination required for multi-worker

### QA-4: Maintainability

**Requirement**: The codebase must support evolution and debugging.

**Standards**:
- Python 3.11+ type hints throughout
- Docstrings for public APIs
- Clear module separation of concerns
- Comprehensive logging

**Metrics**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | > 70% | Lines covered by tests |
| Cyclomatic complexity | < 10 | Per function |
| Module size | < 500 lines | Per module (preferable) |

### QA-5: Portability

**Requirement**: The system must run on supported platforms.

**Platforms**:
| Platform | Support Level | Notes |
|----------|---------------|-------|
| Windows | Primary | Development and production |
| macOS | Secondary | Development only |
| Linux | Community | May require adaptation |

**Dependencies**:
- Python 3.11+
- Standard library only (no external runtime deps)
- Dev dependencies: pytest, pytest-cov

### QA-6: Security

**Requirement**: The system must handle sensitive data appropriately.

**Requirements**:
- No credential storage in job state
- No logging of sensitive inputs
- Environment-based API key handling
- Protected document guards prevent unauthorized modification

**Excluded**:
- Encryption at rest (file system responsibility)
- Network security (backend responsibility)
- Authentication (backend responsibility)

## Operational Requirements

### OR-1: Deployment

**Requirement**: The system must be deployable with minimal configuration.

**Installation**:
```bash
pip install -e .
ukbe-run-agent init
```

**Configuration**:
- `%USERPROFILE%\.ukbe-runner\config.json` for runtime settings
- Environment variables for API keys
- `template_groups.py` for workflow definitions

### OR-2: Monitoring

**Requirement**: System health must be observable.

**Observability**:
| Component | Mechanism | Output |
|-----------|-----------|--------|
| Daemon | Log files | `%USERPROFILE%\.ukbe-runner\logs\` |
| Steps | Structured logs | Console and file |
| Heartbeats | Backend API | Worker status |
| Metrics | Backend API | Usage data per step |

### OR-3: Logging

**Requirement**: Operations must be auditable through logs.

**Log Levels**:
| Level | Use Case |
|-------|----------|
| DEBUG | Development troubleshooting |
| INFO | Normal operation events |
| WARNING | Recoverable issues |
| ERROR | Step failures |
| CRITICAL | System failures |

**Log Retention**:
- Daemon logs: Rolling retention (configurable)
- Job logs: Persist with job state
- Audit events: Backend persistence

### OR-4: Backup and Recovery

**Requirement**: Job state must be recoverable.

**Scope**:
- Job state directory (`%USERPROFILE%\.ukbe-runner\jobs\`)
- Runtime bundles (`%USERPROFILE%\.ukbe-runner\workflows\`)

**Excluded**:
- Package source (recoverable via pip/git)
- Backend data (backend responsibility)

### OR-5: Compatibility

**Requirement**: The system must maintain backward compatibility where possible.

**Version Compatibility**:
| Component | Compatibility Rule |
|-----------|-------------------|
| Job schema | Migration path for v1 → v2 |
| Workflow bundles | Family versioning for breaking changes |
| CLI interface | Semantic versioning for commands |

## Constraints

### Technical Constraints

| Constraint | Description |
|------------|-------------|
| Python 3.11+ | Minimum Python version |
| No async/await | Synchronous execution model |
| File-based state | No database dependency |
| CLI-only | No web interface |

### Business Constraints

| Constraint | Description |
|------------|-------------|
| Backend dependency | Distributed mode requires backend |
| LLM provider accounts | User must provide API credentials |
| Local filesystem | Runtime requires writable home directory |

## Quality Assurance

### Testing Requirements

| Test Type | Coverage | Tool |
|-----------|----------|------|
| Unit tests | Core modules | pytest |
| Integration tests | Step execution | pytest |
| Contract tests | Meta.json schema | JSON Schema validation |

### Validation Requirements

| Validation | Frequency | Owner |
|------------|-----------|-------|
| Schema conformance | Every build | CI/CD |
| Type checking | Every commit | Developer |
| Documentation sync | On code change | documentation_sync_v1 |

---

*These non-functional requirements constrain the implementation of agent-runner-v2. See `FUNCTIONAL_SPEC.md` for functional requirements and `RUNBOOK.md` for operational procedures.*
