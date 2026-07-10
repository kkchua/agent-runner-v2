---
title: "Non-Functional Requirements"
template_id: "SYS-00-NFR"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Quality Attributes

### QA-01: Reliability

**Description**: The system shall operate without failure under expected conditions.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01.1 | Workflow execution completion rate | ≥ 99% of workflows complete without system failure |
| NFR-01.2 | Step retry success rate | ≥ 95% of retried steps succeed |
| NFR-01.3 | Daemon uptime | ≥ 99% availability during operational hours |
| NFR-01.4 | Job state persistence | 100% of job state changes persisted to disk |

**Rationale**: Users depend on workflows completing reliably. System failures should be rare and recoverable.

### QA-02: Determinism

**Description**: The system shall produce consistent results given the same inputs.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-02.1 | Deterministic routing | Same inputs → same routing decisions |
| NFR-02.2 | Artifact path stability | Artifact paths deterministic across runs |
| NFR-02.3 | Prompt reproducibility | Same artifacts → same rendered prompts |

**Rationale**: Determinism enables debugging, replay, and predictable behavior.

### QA-03: Traceability

**Description**: All operations shall be traceable through logs and artifacts.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-03.1 | Step execution logging | Every step execution logged |
| NFR-03.2 | Artifact provenance | All artifacts traceable to producing step |
| NFR-03.3 | Job history | Complete step history preserved |
| NFR-03.4 | Decision audit trail | All routing decisions auditable |

**Rationale**: Traceability supports debugging, compliance, and operational visibility.

### QA-04: Extensibility

**Description**: The system shall support extension without core modifications.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-04.1 | Action addition | New actions added without core changes |
| NFR-04.2 | Workflow addition | New workflows added via templates only |
| NFR-04.3 | Model addition | New LLM providers added via adapters |
| NFR-04.4 | Extension points | ≥ 5 documented extension mechanisms |

**Rationale**: Extensibility enables customization without forking.

### QA-05: Portability

**Description**: The system shall run on multiple platforms.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-05.1 | Python compatibility | Python 3.11+ support |
| NFR-05.2 | OS compatibility | Windows 10+, macOS 12+, Linux |
| NFR-05.3 | Path handling | Cross-platform path resolution |
| NFR-05.4 | Zero dependencies | No external runtime dependencies |

**Rationale**: Portability enables deployment flexibility.

### QA-06: Performance

**Description**: The system shall execute within acceptable time bounds.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-06.1 | Step startup time | ≤ 5 seconds (excluding LLM time) |
| NFR-06.2 | Prompt rendering | ≤ 1 second |
| NFR-06.3 | Artifact validation | ≤ 2 seconds per document |
| NFR-06.4 | Job state persistence | ≤ 100ms |

**Rationale**: Performance impacts user experience and throughput.

### QA-07: Security

**Description**: The system shall operate securely.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-07.1 | No credential exposure | API keys never logged or exposed |
| NFR-07.2 | Path traversal protection | Input paths validated |
| NFR-07.3 | Secure defaults | Safe default configurations |
| NFR-07.4 | Least privilege | Minimal permissions required |

**Rationale**: Security protects user data and credentials.

### QA-08: Observability

**Description**: The system shall be observable in production.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-08.1 | Structured logging | JSON log format |
| NFR-08.2 | Log levels | DEBUG, INFO, WARN, ERROR levels |
| NFR-08.3 | Metrics export | Key metrics extractable |
| NFR-08.4 | Health checks | Daemon health check endpoint |

**Rationale**: Observability enables monitoring and troubleshooting.

### QA-09: Maintainability

**Description**: The system shall be maintainable over time.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-09.1 | Code coverage | ≥ 80% test coverage |
| NFR-09.2 | Documentation coverage | All modules documented |
| NFR-09.3 | Backward compatibility | 2 major version support |
| NFR-09.4 | Dependency count | Zero runtime dependencies |

**Rationale**: Maintainability reduces long-term costs.

### QA-10: Compatibility

**Description**: The system shall integrate with existing infrastructure.

**Requirements**:
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-10.1 | Backend API compatibility | Compatible with backend v1 API |
| NFR-10.2 | LLM API compatibility | Support current API versions |
| NFR-10.3 | Job format compatibility | Forward/backward compatible state |
| NFR-10.4 | Workflow compatibility | Existing workflows continue working |

**Rationale**: Compatibility protects existing investments.

## Constraints

### Technical Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| C-01 | Python 3.11+ required | Type hints, modern features |
| C-02 | Zero runtime dependencies | Deployment simplicity |
| C-03 | File-based state only | No database required |
| C-04 | CLI-only interface | No GUI dependencies |
| C-05 | Single-threaded execution | Determinism, simplicity |

### Operational Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| C-06 | Requires filesystem access | Artifact storage |
| C-07 | Network required for LLM/backend | External dependencies |
| C-08 | Windows primary target | Current deployment |
| C-09 | UTF-8 encoding required | International text |

## Operational Characteristics

### Resource Usage

| Resource | Expected Usage | Limit |
|----------|---------------|-------|
| Memory | 50-200 MB | 500 MB |
| Disk (jobs) | 10 MB per job | 1 GB total |
| Disk (logs) | 100 MB per day | 30 days retention |
| Network | Varies by LLM | Unlimited |

### Scalability

| Aspect | Limit | Mitigation |
|--------|-------|------------|
| Concurrent workflows | 1 per process | Multiple processes |
| Job history | Unlimited | Archival |
| Artifact size | 10 MB | External storage |
| Workflow complexity | 100 steps | Sub-workflows |

### Availability

| Component | Target | Recovery |
|-----------|--------|----------|
| Local execution | On-demand | N/A |
| Worker mode | 95% | Restart |
| Daemon | 99% | Auto-restart |
| Backend connection | Best effort | Retry |

### Recovery

| Scenario | Recovery Time | Recovery Point |
|----------|---------------|----------------|
| Process crash | Immediate | Last step |
| System restart | 1 minute | Last persisted state |
| Backend outage | 5 minutes | Queue backlog |

## Compliance and Governance

### Documentation Standards

| Requirement | Standard |
|-------------|----------|
| Frontmatter format | YAML with required fields |
| Template ID stability | Immutable once assigned |
| Section requirements | Mandatory sections per doc type |
| Cross-reference validity | Links must resolve |

### Change Governance

| Requirement | Standard |
|-------------|----------|
| Workflow changes | Version bump |
| Schema changes | Migration path |
| Breaking changes | Major version |
| Documentation changes | Change ID |

## Related Documents

- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Functional requirements
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Architecture profile
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Documentation governance
