---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures the runtime, quality, and operational expectations for `agent-runner-v2`. These requirements constrain how the system behaves, independent of specific features.

## Quality Requirements

### Performance

#### Response Time

| Metric | Target | Critical |
|--------|--------|----------|
| Step execution initiation | <5s | Yes |
| Prompt rendering | <1s | No |
| Artifact validation | <3s | Yes |
| Workflow routing | <1s | Yes |

#### Throughput

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent workflows | 10+ | Configurable |
| Steps per hour | 100+ | Depends on model latency |
| Jobs per day | 1000+ | Backend limited |

#### Resource Usage

| Resource | Target | Limit |
|----------|--------|-------|
| Memory per job | <100MB | Hard limit |
| Disk per job | <50MB | Artifact dependent |
| CPU usage | Moderate | Burst acceptable |

### Reliability

#### Availability

| Level | Target | Measurement |
|-------|--------|-------------|
| System uptime | 99.9% | Excluding planned maintenance |
| Job completion rate | >95% | Of started jobs |
| Step success rate | >98% | Of executed steps |

#### Fault Tolerance

| Scenario | Behavior |
|----------|----------|
| Model timeout | Mark step failed, trigger retry |
| Meta.json missing | Hard failure, explicit routing |
| Artifact missing | Validation failure, explicit error |
| Backend unavailable | Queue for retry, exponential backoff |

#### Recovery

| Capability | Requirement |
|------------|-------------|
| Job state recovery | Automatic on restart |
| Step retry | Configurable attempts |
| Manual intervention | Supported via approval gates |

### Maintainability

#### Code Quality

| Metric | Target |
|--------|--------|
| Test coverage | >80% (unit tests) |
| Type hints | Required for public APIs |
| Documentation | Required for modules |

#### Modularity

| Principle | Requirement |
|-----------|-------------|
| Single responsibility | One purpose per module |
| Loose coupling | Minimize inter-module dependencies |
| High cohesion | Related functions grouped |

### Portability

#### Platform Support

| Platform | Support Level |
|----------|---------------|
| Windows 10/11 | Primary |
| macOS | Compatible |
| Linux | Compatible |

#### Python Versions

| Version | Support |
|---------|---------|
| 3.12 | Recommended |
| 3.11 | Supported |
| 3.10 | Supported |
| <3.10 | Not supported |

### Security

#### Data Protection

| Requirement | Implementation |
|-------------|----------------|
| No secrets in code | Use .env files |
| Encrypted storage | Backend responsibility |
| Access control | Backend-enforced |

#### Execution Safety

| Requirement | Implementation |
|-------------|----------------|
| Sandboxed actions | Subprocess isolation |
| No arbitrary code execution | Deterministic actions only |
| Input validation | Schema validation |

## Operational Requirements

### Deployability

#### Installation

| Requirement | Details |
|-------------|---------|
| Package install | `pip install -e .` |
| Dependencies | Listed in pyproject.toml |
| Bootstrap | `ukbe-run-agent init` |

#### Configuration

| Requirement | Details |
|-------------|---------|
| Config file | `%USERPROFILE%\.ukbe-runner\config.json` |
| Environment | `.env` file support |
| Runtime override | Command-line arguments |

### Observability

#### Logging

| Requirement | Details |
|-------------|---------|
| Log location | `%USERPROFILE%\.ukbe-runner\logs\` |
| Log levels | DEBUG, INFO, WARNING, ERROR |
| Rotation | Daily rotation |

#### Metrics

| Metric | Collection |
|--------|------------|
| Step duration | Automatic |
| Model usage | Tracked in job state |
| Success/failure rates | Computed from job history |

#### Notifications

| Event | Notification |
|-------|--------------|
| Job complete | Pushover (configurable) |
| Step failure | Pushover (configurable) |
| Human approval needed | Pushover (configurable) |

### Scalability

#### Horizontal Scaling

| Aspect | Support |
|--------|---------|
| Multiple workers | Yes (backend-managed) |
| Load balancing | Backend responsibility |
| State distribution | Backend-managed |

#### Vertical Scaling

| Resource | Scaling |
|----------|---------|
| Memory | Per-process limits |
| Disk | Artifact retention policy |
| CPU | Model-dependent |

## Runtime Expectations

### Execution Environment

#### CLI Mode

| Aspect | Requirement |
|--------|-------------|
| Interactive | Support for manual execution |
| Batch | Support for scripted execution |
| Output | Structured logging |

#### Worker Mode

| Aspect | Requirement |
|--------|-------------|
| Backend poll | Configurable interval |
| Step execution | Single step per invocation |
| Isolation | Fresh subprocess per step |

#### Daemon Mode

| Aspect | Requirement |
|--------|-------------|
| Long-running | Continuous operation |
| Supervision | Worker process management |
| Recovery | Automatic restart on failure |

### Integration Points

#### Backend API

| Requirement | Details |
|-------------|---------|
| Protocol | REST over HTTPS |
| Authentication | Token-based |
| Retry | Exponential backoff |
| Timeout | Configurable |

#### Model APIs

| Requirement | Details |
|-------------|---------|
| Claude | Anthropic API |
| Codex | OpenAI API |
| Qwen | Local inference |
| Fallback | None (hard failure) |

## Constraints

### Technical Constraints

| Constraint | Implication |
|------------|-------------|
| Python 3.10+ | Modern language features available |
| No async/await | Synchronous execution model |
| File-based state | Simple but limited scalability |
| Subprocess model | Code changes picked up automatically |

### Business Constraints

| Constraint | Implication |
|------------|-------------|
| Single user per runner | No multi-tenancy |
| Local execution | No distributed steps |
| Manual workflow trigger | No scheduled execution |

### Compliance Constraints

| Constraint | Implication |
|------------|-------------|
| No PII in logs | Data sanitization required |
| Audit trail | All actions logged |
| Document versioning | Change tracking required |

## Validation and Verification

### Testing Requirements

| Type | Coverage | Target |
|------|----------|--------|
| Unit tests | Logic functions | >80% |
| Integration tests | End-to-end | Key paths |
| Validation tests | Document structure | All templates |

### Monitoring Requirements

| Aspect | Requirement |
|--------|-------------|
| Health checks | Backend poll success |
| Alerts | Failure rate threshold |
| Dashboards | Job status overview |

---

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — System explanation
- [BUSINESS_CAPABILITIES.md](BUSINESS_CAPABILITIES.md) — Business value
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional behaviors
- [RUNBOOK.md](RUNBOOK.md) — Operational procedures

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
