---
title: "Non-Functional Requirements"
template_id: "SYS-00-NFR"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T00:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Non-Functional Requirements

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

## Overview

This document captures the non-functional requirements for agent-runner-v2 — the quality attributes, operational characteristics, and constraints that guide the system's design and implementation.

## Quality Attributes

### 1. Reliability

#### 1.1 Availability

| Requirement | Target |
|-------------|--------|
| Uptime (local mode) | N/A (user-controlled) |
| Uptime (daemon mode) | 99% |
| Uptime (worker mode) | 95% (accounting for backend dependencies) |

#### 1.2 Fault Tolerance

- **Auto-retry**: Steps classified as `AUTO_RETRYABLE` must retry automatically
- **State recovery**: Job state must be recoverable after process restart
- **Graceful degradation**: Backend unavailability must not crash local execution

#### 1.3 Data Integrity

- Job state must be atomic (write to temp, then rename)
- Sidecar validation must fail closed (reject on invalid)
- Artifact paths must be canonical

### 2. Performance

#### 2.1 Response Times

| Operation | Target | Maximum |
|-----------|--------|---------|
| Step initiation | < 1s | 5s |
| Prompt rendering | < 100ms | 500ms |
| State save | < 50ms | 200ms |
| CLI command | < 500ms | 2s |

#### 2.2 Throughput

- Support concurrent job execution
- Worker mode: process 1 step per poll cycle minimum
- Local mode: no artificial throttling

#### 2.3 Resource Usage

| Resource | Typical | Maximum |
|----------|---------|---------|
| Memory | 50 MB | 200 MB |
| Disk (per job) | 10 KB | 1 MB |
| CPU | Low | Burst during coder invocation |

### 3. Scalability

#### 3.1 Horizontal Scaling

- Worker instances can scale independently
- No shared state between workers (except backend)
- Stateless step execution

#### 3.2 Vertical Scaling

- Single workflow can have unlimited steps
- Job artifacts limited only by disk space
- Step output size limited by LLM context

### 4. Security

#### 4.1 Authentication

- API keys must not be logged
- API keys must not be committed to version control
- Support for environment-based key injection

#### 4.2 Authorization

- No multi-user support in v1
- Job isolation via directory structure
- No cross-job access

#### 4.3 Data Protection

- No sensitive data in job state (unless explicitly passed)
- Prompt templates are public
- Execution logs may contain sensitive data (user responsibility)

### 5. Maintainability

#### 5.1 Code Organization

| Module | Lines | Responsibility |
|--------|-------|--------------|
| run_agent.py | ~2000 | CLI entry |
| step_runner.py | ~2000 | Step execution |
| job_state.py | ~1800 | State management |
| workflow_router.py | ~800 | Routing |
| coder_adapters.py | ~1000 | LLM integration |

#### 5.2 Testability

- Unit tests for state management
- Integration tests for workflows
- Mock adapters for coder testing

#### 5.3 Documentation

- All public functions must have docstrings
- Complex logic must have inline comments
- Architecture decisions recorded in DECISION_LOG.md

### 6. Portability

#### 6.1 Platform Support

| Platform | Support Level |
|----------|---------------|
| Windows 10/11 | Primary |
| macOS | Secondary |
| Linux (WSL) | Secondary |

#### 6.2 Python Version

- Minimum: Python 3.11
- Recommended: Python 3.12
- Not supported: < 3.11

### 7. Usability

#### 7.1 CLI Interface

- Commands follow Unix conventions
- Consistent flag naming (`--kebab-case`)
- Help text for all commands
- Sensible defaults

#### 7.2 Error Messages

- Actionable error messages
- Include remediation steps
- Reference relevant documentation

#### 7.3 Configuration

- Sensible defaults for all options
- Environment variable support
- JSON configuration file

### 8. Interoperability

#### 8.1 LLM Providers

| Provider | Integration |
|----------|-------------|
| Anthropic (Claude) | Native |
| OpenAI (Codex) | Native |
| Alibaba (Qwen) | Native |

#### 8.2 External Systems

| System | Interface |
|--------|-----------|
| Backend API | HTTP REST |
| ComfyUI | HTTP REST |
| File System | Native Python |

#### 8.3 Data Formats

- JSON for structured data (schemas provided)
- Markdown for human-readable content
- YAML not used (JSON only)

## Operational Requirements

### 1. Deployment

#### 1.1 Package Installation

```bash
pip install agent-runner-v2
```

#### 1.2 Initialization

```bash
ukbe-run-agent init
```

Creates:
- `%USERPROFILE%\.ukbe-runner\config.json`
- `%USERPROFILE%\.ukbe-runner\jobs\`
- `%USERPROFILE%\.ukbe-runner\workflows\`
- `%USERPROFILE%\.ukbe-runner\logs\`

### 2. Monitoring

#### 2.1 Logging

- Structured JSON logs
- Rotation and cleanup
- Log levels: DEBUG, INFO, WARNING, ERROR

#### 2.2 Metrics

| Metric | Source |
|--------|--------|
| Steps executed | Job state |
| Success rate | Job state |
| Retry count | Job state |
| LLM usage | Sidecar data |
| Execution time | Sidecar data |

### 3. Backup and Recovery

#### 3.1 Job State Backup

- Job state is file-based (backup via file copy)
- No database to backup
- Archive completed jobs periodically

#### 3.2 Recovery

- Resume from any saved job state
- Retry failed steps
- Reset and restart workflows

## Design Constraints

### 1. Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| Python 3.11+ | Matchline operators, improved typing |
| No async/await | Simpler debugging, sufficient for use case |
| File-based state | Simplicity, portability |
| JSON only | Consistency, schema validation |

### 2. Business Constraints

| Constraint | Rationale |
|------------|-----------|
| MIT License | Extracted from UKBE |
| Self-hosted | No SaaS dependency |
| Offline capable | Local execution without backend |

### 3. Regulatory Constraints

- None currently identified
- User responsible for LLM provider compliance
- User responsible for data handling compliance

## Quality Assurance

### 1. Testing Requirements

| Type | Coverage Target |
|------|-----------------|
| Unit tests | Core modules |
| Integration tests | Workflow execution |
| End-to-end | Critical paths |

### 2. Code Quality

- Type hints on all public APIs
- Linting with ruff
- No circular dependencies

### 3. Documentation Quality

- Accurate and current
- Example commands tested
- Cross-references valid

## Compliance Requirements

### 1. Open Source

- License: MIT
- Attribution preserved
- Third-party licenses tracked

### 2. Security

- No hardcoded secrets
- No executable uploads
- Input validation on all boundaries

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs`*
