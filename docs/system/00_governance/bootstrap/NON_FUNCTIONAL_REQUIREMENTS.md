---
template_id: "SYS-00-NFR"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures the runtime, quality, and operational expectations for agent-runner-v2. It defines how the system should perform, behave, and operate under various conditions, independent of specific functional requirements.

## Quality Requirements

### Reliability

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Availability** | 99.5% for daemon mode | Uptime percentage over 30 days |
| **Step Success Rate** | >95% | Successful completions vs total attempts |
| **Recovery Success** | >90% | Successful recoveries after failure |
| **State Consistency** | 100% | Job state corruption incidents |

### Fault Tolerance

| Scenario | Requirement |
|----------|-------------|
| **Coder Timeout** | Retry with exponential backoff, max 3 attempts |
| **Backend Unavailable** | Retry with 30s intervals, queue locally |
| **Sidecar Corruption** | Reject step, route to failure handling |
| **State Corruption** | Detect via schema validation, attempt migration |
| **Child Process Failure** | Terminate, report failure, claim next work |

### Data Integrity

| Requirement | Implementation |
|-------------|----------------|
| **Job State Persistence** | Atomic writes with checksum validation |
| **Artifact Verification** | Path existence check before routing |
| **Sidecar Validation** | JSON schema validation, required field check |
| **Path Resolution** | Absolute path normalization, traversal protection |

## Performance Requirements

### Response Time

| Operation | Target | Maximum |
|-----------|--------|---------|
| **Prompt Rendering** | <100ms | 500ms |
| **Preflight Check** | <50ms | 200ms |
| **Job State Load** | <100ms | 500ms |
| **Job State Save** | <200ms | 1s |
| **Sidecar Read** | <50ms | 200ms |

### Throughput

| Metric | Target | Notes |
|--------|--------|-------|
| **Steps per Hour (Local)** | 10-20 | Depends on coder response time |
| **Steps per Hour (Worker)** | 30-60 | Parallel execution across workers |
| **Concurrent Jobs** | 10 | Per daemon instance |
| **Poll Interval** | 10s | Worker poll frequency |

### Resource Usage

| Resource | Target | Maximum |
|----------|--------|---------|
| **Memory (Daemon)** | <100MB | 500MB |
| **Memory (Step)** | <500MB | 2GB |
| **Disk (Job State)** | <10KB per job | 50KB |
| **Disk (Logs)** | <100MB per day | Rotated |
| **CPU (Idle)** | <1% | 5% |

## Operational Requirements

### Deployment

| Requirement | Specification |
|-------------|-------------|
| **Installation** | pip install -e . |
| **Initialization** | ukbe-run-agent init |
| **Configuration** | config.json in runner home |
| **Upgrade** | pip install --upgrade + init |

### Monitoring

| Requirement | Implementation |
|-------------|----------------|
| **Heartbeat** | Every 30s in daemon mode |
| **Log Rotation** | Daily rotation, 7 day retention |
| **Metrics Exposure** | Job state queryable via CLI |
| **Health Check** | Backend ping endpoint |

### Maintenance

| Task | Frequency | Automation |
|------|-----------|------------|
| **Log Cleanup** | Daily | Automatic |
| **Job Archive** | Weekly | Manual script |
| **Bundle Sync** | As needed | Manual trigger |
| **Schema Migration** | On version change | Automatic with confirmation |

## Security Requirements

### Authentication

| Requirement | Implementation |
|-------------|----------------|
| **Backend Auth** | API key in config.json |
| **Coder Access** | System-level coder authentication |
| **Local Access** | File system permissions |

### Authorization

| Requirement | Implementation |
|-------------|----------------|
| **Job Ownership** | User-scoped job directories |
| **Artifact Access** | Path-based access control |
| **Workflow Access** | No restriction (local execution) |

### Data Protection

| Requirement | Implementation |
|-------------|----------------|
| **Sensitive Data** | .env files excluded from git |
| **Credentials** | Stored in config.json, not code |
| **Job Data** | Local storage only (unless backend-connected) |

## Compatibility Requirements

### Platform Support

| Platform | Support Level | Notes |
|----------|---------------|-------|
| **Windows** | Primary | Development and deployment platform |
| **macOS** | Supported | Via compatibility layer |
| **Linux** | Supported | CI/CD, server deployment |

### Python Version

| Version | Support | Notes |
|---------|---------|-------|
| **3.12** | Primary | Recommended version |
| **3.11** | Supported | Minimum supported |
| **3.13+** | Testing | Compatibility testing |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **Claude Code** | Latest | Coder invocation |
| **Codex CLI** | Latest | Coder invocation |
| **Qwen Code** | Latest | Coder invocation |
| **Python** | 3.11+ | Runtime |

## Scalability Requirements

### Horizontal Scaling

| Aspect | Requirement |
|--------|-------------|
| **Worker Distribution** | Multiple workstations claim work from backend |
| **Concurrent Execution** | Daemon spawns child processes per step |
| **Backend Coordination** | Backend manages work queue, tracks state |

### Vertical Scaling

| Aspect | Requirement |
|--------|-------------|
| **Resource Isolation** | Child processes isolated from daemon |
| **Resource Limits** | Configurable timeouts and memory limits |
| **Cleanup** | Automatic temp file cleanup post-step |

## Usability Requirements

### CLI Interface

| Requirement | Implementation |
|-------------|----------------|
| **Command Discovery** | --help on all commands |
| **Consistent Interface** | Common flags across modes |
| **Progress Visibility** | Step status in job state |
| **Error Clarity** | Descriptive error messages |

### Documentation

| Requirement | Implementation |
|-------------|----------------|
| **Usage Examples** | README.md with common commands |
| **Troubleshooting** | HOW_TO_GUIDE.md |
| **API Reference** | Function docstrings |
| **Architecture** | System documentation set |

## Portability Requirements

### Configuration Portability

| Aspect | Requirement |
|--------|-------------|
| **Config Location** | %USERPROFILE%\.ukbe-runner\config.json |
| **Relative Paths** | Job state uses relative paths |
| **Cross-Platform** | Pathlib for cross-platform paths |

### Workflow Portability

| Aspect | Requirement |
|--------|-------------|
| **Bundle Seeding** | Bootstrap seeds runtime bundles |
| **Version Pinning** | Workflows can pin to bundle versions |
| **Export/Import** | Jobs can be archived and restored |

## Maintainability Requirements

### Code Organization

| Requirement | Implementation |
|-------------|----------------|
| **Module Size** | No module >2,500 lines |
| **Separation of Concerns** | Narrow module responsibilities |
| **Constants Centralization** | All paths in constants.py |
| **Test Separation** | Unit vs integration split |

### Documentation

| Requirement | Implementation |
|-------------|----------------|
| **Doc Coverage** | All public functions documented |
| **Generated Docs** | Workflow-generated, protected |
| **Change Tracking** | Change impact documentation |

### Testing

| Requirement | Implementation |
|-------------|----------------|
| **Unit Test Coverage** | Pure logic isolated from filesystem |
| **Integration Test Coverage** | Real files, external systems |
| **Test Markers** | pytest markers for selection |

## Constraints

### Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| **No Markdown Write-Backs** | v2 contract — sidecar only |
| **No Pre-Invocation Sidecar Writes** | Coder owns sidecar |
| **No Recovery Functions** | Explicit failure routing |
| **Meta.json Only** | Single structured communication channel |

### Operational Constraints

| Constraint | Rationale |
|------------|-----------|
| **Bootstrap/Runtime Distinction** | Runtime loads from user home, not repo |
| **External Coder Dependency** | Runtime requires installed coders |
| **Windows Path Handling** | Special handling for pathlib edge cases |
| **Daemon Child Processes** | Fresh subprocess per step for code reload |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
