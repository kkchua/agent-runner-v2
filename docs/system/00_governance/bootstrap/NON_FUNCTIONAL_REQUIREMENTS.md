---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures the runtime, quality, and operational expectations for the `agent-runner-v2` platform. These requirements are implicit in the current implementation and must be maintained.

## Quality Requirements

### NFR-1: Performance

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-1.1 | Step startup time SHALL be under 5 seconds | < 5s | ✅ Met |
| NFR-1.2 | Prompt rendering SHALL be under 1 second | < 1s | ✅ Met |
| NFR-1.3 | State save/load SHALL be under 500ms | < 500ms | ✅ Met |
| NFR-1.4 | Backend polling interval SHALL be configurable | 5-60s | ✅ Met |
| NFR-1.5 | Memory usage SHALL remain under 512MB for daemon | < 512MB | ✅ Met |

**Rationale**: Responsiveness for interactive use, efficiency for long-running daemons.

**Validation**: Performance benchmarks in test suite.

### NFR-2: Reliability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-2.1 | Job state SHALL be persisted after each step | 100% | ✅ Met |
| NFR-2.2 | State corruption SHALL be detectable | N/A | ✅ Met |
| NFR-2.3 | Retry logic SHALL handle transient failures | > 95% | ✅ Met |
| NFR-2.4 | Daemon SHALL recover from child process failures | > 99% | ✅ Met |
| NFR-2.5 | Network failures SHALL be handled gracefully | N/A | ✅ Met |

**Rationale**: Workflow execution must be resilient to failures.

**Validation**: Integration tests with failure injection.

### NFR-3: Availability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-3.1 | Daemon uptime SHALL be 99% during operation | 99% | ✅ Met |
| NFR-3.2 | Worker SHALL reconnect after backend outage | < 60s | ✅ Met |
| NFR-3.3 | No single point of failure for local execution | N/A | ✅ Met |

**Rationale**: Production use requires reliable operation.

**Validation**: Long-running tests, chaos engineering.

### NFR-4: Scalability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-4.1 | Multiple workers SHALL share workload | N/A | ✅ Met |
| NFR-4.2 | Job state SHALL support 1000+ active jobs | 1000+ | ✅ Met |
| NFR-4.3 | Artifact storage SHALL scale to 10GB per job | 10GB | ✅ Met |

**Rationale**: Support team-scale usage.

**Validation**: Load testing, storage benchmarks.

## Operational Requirements

### NFR-5: Deployability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-5.1 | Installation SHALL be via pip | pip | ✅ Met |
| NFR-5.2 | Initialization SHALL be single command | 1 command | ✅ Met |
| NFR-5.3 | Configuration SHALL be file-based | JSON | ✅ Met |
| NFR-5.4 | Secrets SHALL be environment-based | .env | ✅ Met |

**Rationale**: Easy deployment across environments.

**Validation**: CI/CD pipelines.

### NFR-6: Observability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-6.1 | All steps SHALL be logged | 100% | ✅ Met |
| NFR-6.2 | Job state SHALL be queryable | N/A | ✅ Met |
| NFR-6.3 | Notifications SHALL be configurable | N/A | ✅ Met |
| NFR-6.4 | Usage SHALL be trackable | N/A | ✅ Met |

**Rationale**: Operational visibility and debugging.

**Validation**: Log analysis, monitoring integration.

### NFR-7: Maintainability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-7.1 | Code SHALL have > 70% test coverage | > 70% | 🔄 In Progress |
| NFR-7.2 | Documentation SHALL be workflow-generated | N/A | 🔄 In Progress |
| NFR-7.3 | Dependencies SHALL be minimal | < 50 | ✅ Met |
| NFR-7.4 | Configuration SHALL be centralized | N/A | ✅ Met |

**Rationale**: Sustainable development.

**Validation**: Coverage reports, dependency analysis.

### NFR-8: Portability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-8.1 | Python 3.12+ SHALL be supported | 3.12+ | ✅ Met |
| NFR-8.2 | Windows SHALL be primary platform | Win | ✅ Met |
| NFR-8.3 | Unix/WSL SHALL be supported | Unix | ⚠️ Secondary |
| NFR-8.4 | Path handling SHALL be cross-platform | N/A | ✅ Met |

**Rationale**: Support developer environments.

**Validation**: Cross-platform test suite.

## Security Requirements

### NFR-9: Authentication

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-9.1 | Backend access SHALL require authentication | Yes | ✅ Met |
| NFR-9.2 | API keys SHALL be stored securely | .env | ✅ Met |
| NFR-9.3 | Credentials SHALL NOT be logged | No | ✅ Met |

**Rationale**: Protect sensitive credentials.

**Validation**: Security audit, log review.

### NFR-10: Isolation

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-10.1 | Job executions SHALL be isolated | Process | ✅ Met |
| NFR-10.2 | Artifact access SHALL be job-scoped | N/A | ✅ Met |
| NFR-10.3 | Secrets SHALL be step-scoped | N/A | ✅ Met |

**Rationale**: Prevent cross-job interference.

**Validation**: Process isolation tests.

## Compatibility Requirements

### NFR-11: Backward Compatibility

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-11.1 | Job state SHALL migrate forward | v6 | ✅ Met |
| NFR-11.2 | Workflow definitions SHALL remain valid | Yes | ✅ Met |
| NFR-11.3 | CLI interface SHALL remain stable | Deprecation | ✅ Met |

**Rationale**: Protect existing jobs and workflows.

**Validation**: Migration tests, CLI compatibility tests.

### NFR-12: Interoperability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-12.1 | Backend API SHALL be REST-compatible | Yes | ✅ Met |
| NFR-12.2 | LLM backends SHALL be pluggable | Yes | ✅ Met |
| NFR-12.3 | Notification services SHALL be pluggable | Pushover | ⚠️ Limited |

**Rationale**: Integration with existing infrastructure.

**Validation**: Integration tests.

## Quality Attributes

### QA-1: Testability

The system is designed for testability:

- Unit tests for pure logic (45+ tests)
- Integration tests for end-to-end flows
- Mock backends for offline testing
- Temp paths for test isolation

### QA-2: Configurability

The system supports extensive configuration:

- `config.json` for runner settings
- `.env` for secrets
- CLI arguments for overrides
- Workflow-specific settings

### QA-3: Extensibility

The system supports extension:

- Custom actions in `actions/` package
- Workflow definitions in template groups
- Plugin system (migration in progress)
- Context extensions for workflows

### QA-4: Usability

The system emphasizes usability:

- Single CLI entry point
- Clear error messages
- Progress tracking
- Human-readable output

## Operational Expectations

### Runtime Environment

| Component | Requirement |
|-----------|-------------|
| Python | 3.12 or higher |
| Memory | 512MB minimum, 1GB recommended |
| Disk | 1GB free space minimum |
| Network | Required for worker/daemon modes |

### Resource Consumption

| Resource | Typical | Peak |
|----------|---------|------|
| CPU | Low | Medium during coder calls |
| Memory | 100MB | 256MB |
| Disk | 10MB/job | 1GB/video workflows |
| Network | Minimal | During uploads/downloads |

### Monitoring

| Metric | Collection | Alert Threshold |
|--------|------------|-----------------|
| Job failures | Per-step | > 5% failure rate |
| Retry rate | Per-step | > 20% retry rate |
| Queue depth | Worker mode | > 100 queued |
| Daemon health | Heartbeat | > 60s missing |

## Limitations

| Limitation | Reason | Mitigation |
|------------|--------|------------|
| Windows primary | Development focus | Unix support secondary |
| Local filesystem | Simplicity | Network storage via mount |
| JSON state | Human-readable | Schema evolution managed |
| Single daemon per workstation | Port conflicts | Multiple workers supported |

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional capabilities
- [RUNBOOK.md](RUNBOOK.md) — Operational procedures
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
