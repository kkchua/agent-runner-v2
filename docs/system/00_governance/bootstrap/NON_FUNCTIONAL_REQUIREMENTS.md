---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements: agent-runner-v2

## Quality Requirements

### Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Workflow startup time** | <5 seconds | Time from command to first step execution |
| **Step execution overhead** | <1 second | Time excluding LLM/action execution |
| **Artifact validation** | <100ms per file | Time to validate artifact existence |
| **Bundle loading** | <2 seconds | Time to load workflow definition |
| **Job state write** | <50ms | Time to persist job.json |

### Scalability

| Requirement | Target | Notes |
|-------------|--------|-------|
| **Concurrent jobs** | 10+ | Per worker instance |
| **Job history retention** | 90 days | Configurable |
| **Artifact storage** | 10GB | Per project, configurable cleanup |
| **Log retention** | 30 days | Rotated automatically |
| **Workflow bundle size** | <50MB | Total bundle size |

### Reliability

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Workflow success rate** | >95% | Jobs completing all steps |
| **Step retry success** | >90% | After automatic retries |
| **Daemon uptime** | >99% | Excluding planned maintenance |
| **Data durability** | 100% | Job state persistence |
| **Recovery time** | <5 minutes | From failure to resumed execution |

### Availability

| Component | Target | Notes |
|-----------|--------|-------|
| **Local execution** | 100% | No external dependencies |
| **Backend-connected** | 99.5% | With backend available |
| **Documentation sync** | 99% | Scheduled maintenance windows |

## Operational Requirements

### Deployability

| Requirement | Specification |
|-------------|---------------|
| **Installation** | `pip install -e .` |
| **Initialization** | `ukbe-run-agent init` |
| **Configuration** | JSON config file |
| **Updates** | pip upgrade, no migration scripts |
| **Rollback** | pip install specific version |

### Maintainability

| Requirement | Specification |
|-------------|---------------|
| **Code organization** | Modular, clear separation of concerns |
| **Configuration** | Centralized constants, no hardcoded values |
| **Logging** | Structured logs with rotation |
| **Documentation** | Generated docs with drift detection |
| **Test coverage** | Unit tests for pure logic, integration for workflows |

### Supportability

| Requirement | Specification |
|-------------|---------------|
| **Debuggability** | Verbose logging, job state inspection |
| **Troubleshooting** | Clear error messages, stack traces |
| **Monitoring** | Heartbeats, job status, notifications |
| **Diagnostics** | CLI commands for job inspection |

### Security

| Requirement | Specification |
|-------------|---------------|
| **Credential storage** | `.env` files, not committed |
| **API keys** | Environment variables or config.json |
| **Backend authentication** | Token-based with rotation |
| **File permissions** | Restricted access to job data |
| **Audit trail** | Job history, artifact checksums |

## Platform Requirements

### Supported Platforms

| Platform | Version | Status |
|----------|---------|--------|
| **Windows** | 10/11 | Primary development |
| **macOS** | 12+ | Supported |
| **Linux** | Ubuntu 20.04+ | Supported |

### Python Requirements

| Requirement | Specification |
|-------------|---------------|
| **Python version** | 3.10, 3.11, 3.12 |
| **Virtual environment** | Required (`.venv`) |
| **Dependencies** | Listed in `requirements.txt` |
| **Dev dependencies** | Listed in `pyproject.toml` |

### Runtime Dependencies

| Component | Purpose |
|-----------|---------|
| **Python standard library** | Core functionality |
| **pydantic** | Data validation |
| **requests** | HTTP client |
| **markdown** | HTML generation |
| **jinja2** | Template rendering |

### External Dependencies

| Component | Purpose | Required |
|-----------|---------|----------|
| **LLM API** | AI execution | Yes (for coder steps) |
| **Backend API** | Enterprise mode | No (optional) |
| **Pushover** | Notifications | No (optional) |
| **Git** | Version control | No (optional) |

## Usability Requirements

### CLI Usability

| Requirement | Specification |
|-------------|---------------|
| **Command discovery** | `--help` on all commands |
| **Error messages** | Clear, actionable guidance |
| **Progress indication** | Step progress, timing |
| **Configuration validation** | At startup, clear errors |
| **Batch files** | Pre-configured for common workflows |

### Documentation Usability

| Requirement | Specification |
|-------------|---------------|
| **Generated docs** | Auto-sync with code |
| **Audience-specific** | Stakeholder, developer, operator views |
| **Cross-references** | Working links, clear navigation |
| **Searchability** | Index, table of contents |
| **Versioning** | Change IDs, timestamps |

### Workflow Authoring

| Requirement | Specification |
|-------------|---------------|
| **Template syntax** | Clear placeholder convention |
| **Validation** | Schema enforcement |
| **Debugging** | Verbose mode, dry-run |
| **Examples** | Built-in example workflows |
| **Migration path** | From monolith to plugin |

## Compatibility Requirements

### Backward Compatibility

| Requirement | Specification |
|-------------|---------------|
| **API stability** | Semantic versioning |
| **Workflow compatibility** | Old workflows continue to work |
| **Config migration** | Auto-migration or clear errors |
| **Artifact format** | Versioned schemas |

### Forward Compatibility

| Requirement | Specification |
|-------------|---------------|
| **Plugin system** | New workflows without core changes |
| **Model support** | New LLM backends via adapters |
| **Action extensibility** | Custom actions supported |
| **Theme customization** | Custom HTML themes |

## Monitoring Requirements

### Metrics

| Metric | Type | Collection |
|--------|------|------------|
| **Workflow duration** | Timing | Automatic |
| **Step success rate** | Counter | Automatic |
| **LLM tokens** | Usage | Backend-provided |
| **Queue depth** | Gauge | Backend-provided |
| **Error rate** | Counter | Automatic |

### Logging

| Requirement | Specification |
|-------------|---------------|
| **Log levels** | DEBUG, INFO, WARNING, ERROR |
| **Log format** | Timestamp, level, message |
| **Log rotation** | Size-based, 10 files |
| **Log location** | `~/.ukbe-runner/logs/` |
| **Audit logging** | Job lifecycle events |

### Alerting

| Requirement | Specification |
|-------------|---------------|
| **Notification channels** | Pushover, console |
| **Alert conditions** | Failure, long-running, queue depth |
| **Rate limiting** | Configurable per channel |
| **Escalation** | Backend-driven |

## Constraints

### Technical Constraints

- **Python-only**: No compiled extensions required
- **Filesystem-based**: Local file system for state
- **Subprocess execution**: Fresh process per LLM call
- **Sequential execution**: No parallel step execution

### Business Constraints

- **Open source**: MIT license
- **Self-hosted**: No cloud dependency
- **Backend optional**: Local mode works standalone
- **Cost-conscious**: Supports multiple LLM backends

### Resource Constraints

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 2 cores | 4 cores |
| **Memory** | 4GB | 8GB |
| **Disk** | 10GB | 50GB |
| **Network** | 10 Mbps | 100 Mbps |

## Compliance Requirements

### Data Handling

| Requirement | Specification |
|-------------|---------------|
| **Data residency** | Local filesystem |
| **Retention** | Configurable |
| **Encryption** | Filesystem-level |
| **Backup** | User responsibility |

### Audit Requirements

| Requirement | Specification |
|-------------|---------------|
| **Job history** | Complete, immutable |
| **Artifact lineage** | Checksum tracked |
| **Approval records** | Timestamped, signed |
| **Change tracking** | Git integration |

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
