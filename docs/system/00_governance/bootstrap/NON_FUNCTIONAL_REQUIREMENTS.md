---
template_id: "SYS-00-NFR"
title: "Non-Functional Requirements - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Non-Functional Requirements

## Purpose

This document captures quality attributes and operational expectations for agent-runner-v2. It defines how the system should perform, not just what it should do.

**Why:** Non-functional requirements ensure the system is usable, reliable, maintainable, and performant in production environments.

## Quality Requirements

### Q1: Reliability

**Requirement:** The system must handle failures gracefully and maintain state integrity.

**Specifics:**
- State persisted after each step completion
- Recovery possible from any persisted state
- No silent failures — all errors logged and reported
- Retry logic for transient failures

**Metrics:**
- State persistence: 100% of completed steps
- Recovery success rate: >99% for valid states
- Silent failure rate: 0%

**Implementation:**
- JSON state files with schema versioning
- Migration functions for backward compatibility
- Atomic state writes (write to temp, then rename)
- Validation on state load

### Q2: Availability

**Requirement:** The system must be available for workflow execution during operational hours.

**Specifics:**
- Local execution: Available when workstation is running
- Worker mode: Available when worker process is running
- Daemon mode: Available when daemon is supervising
- Backend dependency: Graceful degradation if backend unavailable

**Metrics:**
- Local availability: Workstation uptime
- Worker availability: >99% during scheduled operation
- Daemon availability: >99.5% during scheduled operation

**Implementation:**
- Minimal external dependencies
- Automatic reconnection to backend
- Child process restart on failure
- Heartbeat monitoring

### Q3: Performance

**Requirement:** The system must execute workflows efficiently.

**Specifics:**
- Step startup time: <5 seconds (excluding LLM invocation)
- State save/load: <1 second
- Prompt rendering: <2 seconds for typical artifacts
- Memory usage: <500MB base, scales with artifact size

**Metrics:**
- P99 step startup: <5 seconds
- P99 state operation: <1 second
- Memory usage: Monitor via logs

**Implementation:**
- Efficient path resolution
- Caching of rendered prompts
- Streaming logs for long operations
- Configurable timeouts per step

### Q4: Scalability

**Requirement:** The system must handle increasing workloads via horizontal scaling.

**Specifics:**
- Multiple workers per backend
- Work distribution via backend queue
- No shared state between workers (stateless workers)
- Child process isolation in daemon mode

**Metrics:**
- Workers per backend: Unlimited (backend-limited)
- Concurrent child processes: Configurable (default 1)
- Throughput: Limited by LLM rate limits

**Implementation:**
- Worker pool pattern
- Backend-managed queue
- Process-per-work isolation
- Resource limits on children

### Q5: Usability

**Requirement:** The system must be easy to install, configure, and operate.

**Specifics:**
- Installation: Single pip command
- Initialization: Single init command
- Configuration: JSON files with clear structure
- CLI: Consistent commands with help text
- Logs: Readable, timestamped, structured

**Metrics:**
- Time to first workflow: <10 minutes (new user)
- CLI discoverability: All commands documented
- Log readability: Human-parseable

**Implementation:**
- `pip install -e .`
- `ukbe-run-agent init`
- Configuration templates
- Comprehensive help text
- Structured logging

### Q6: Maintainability

**Requirement:** The system must be easy to maintain and extend.

**Specifics:**
- Modular architecture (40+ modules)
- Clear module responsibilities
- Schema-driven validation
- Type hints throughout
- Documentation for all public APIs

**Metrics:**
- Module coupling: Low (clear boundaries)
- Test coverage: Target >80%
- Documentation coverage: All modules documented

**Implementation:**
- Separation of concerns (CLI, execution, state, adapters, actions)
- JSON schemas for contracts
- MyPy-compatible type hints
- Docstrings for public functions

### Q7: Portability

**Requirement:** The system must run on supported platforms.

**Specifics:**
- Python 3.11+ required
- Windows support (primary)
- Pathlib for cross-platform paths
- No hardcoded platform dependencies

**Metrics:**
- Supported platforms: Windows (primary), Linux (compatible)
- Python versions: 3.11, 3.12, 3.13

**Implementation:**
- pathlib for all paths
- Platform detection where needed
- Virtual environment support
- Standard library preference

### Q8: Security

**Requirement:** The system must handle credentials and sensitive data appropriately.

**Specifics:**
- API keys via environment variables (not committed)
- `.env.example` for template, `.env` for actual (gitignored)
- No logging of sensitive values
- Secure temporary file handling

**Metrics:**
- Credential exposure: 0
- Sensitive data in logs: 0
- Temporary file cleanup: 100%

**Implementation:**
- `python-dotenv` for environment loading
- Explicit `.env` in `.gitignore`
- Log filtering for sensitive patterns
- `tempfile` with automatic cleanup

## Operational Requirements

### O1: Observability

**Requirement:** System state and behavior must be observable.

**Specifics:**
- Job state: JSON files inspectable
- Logs: Written to `%USERPROFILE%\.ukbe-runner\logs\`
- Execution tracking: Usage data per step
- Heartbeats: Emitted by workers and daemon

**Implementation:**
- Structured logging with `runner_logger.py`
- Job state in human-readable JSON
- Usage tracking in job state
- Backend heartbeat API integration

### O2: Configuration

**Requirement:** System behavior must be configurable.

**Specifics:**
- Global config: `%USERPROFILE%\.ukbe-runner\config.json`
- Project config: `<project>\config.json`
- Environment variables: Override config
- CLI arguments: Override environment

**Configuration Scope:**
- Backend URL
- Worker ID
- Model preferences
- Timeout defaults
- Log levels

**Implementation:**
- Hierarchical configuration (CLI > env > project > global)
- JSON configuration files
- Validation on load

### O3: Backup and Recovery

**Requirement:** State must be recoverable.

**Specifics:**
- Job state: JSON files (backup via standard tools)
- Bundle state: Reproducible from package
- Config: User-managed backup
- No database to backup

**Recovery Scenarios:**
- Corrupt state: Migration or manual repair
- Lost job: Re-create from artifacts
- Lost bundles: Re-init from package

### O4: Resource Management

**Requirement:** System must manage resources efficiently.

**Specifics:**
- Disk: Rotate logs, clean old jobs
- Memory: Stream large artifacts, don't load entirely
- Processes: Clean up child processes
- Network: Retry with backoff

**Limits:**
- Job retention: Configurable (default indefinite)
- Log retention: Configurable rotation
- Child process timeout: Configurable per step
- Connection retries: Exponential backoff

## Documentation Requirements

### D1: Completeness

**Requirement:** All components must be documented.

**Specifics:**
- Public APIs: Docstrings
- Modules: Purpose and responsibility
- Workflows: Steps and artifacts
- Operations: Runbook procedures

**Coverage:**
- Code: All public functions
- System: Architecture, context, decisions
- Operations: Procedures, troubleshooting

### D2: Accuracy

**Requirement:** Documentation must match implementation.

**Specifics:**
- Sync with code changes
- Validate against schemas
- Review for accuracy
- Update triggers defined

**Validation:**
- Schema validation
- Link checking
- Content review

### D3: Accessibility

**Requirement:** Documentation must be discoverable.

**Specifics:**
- Index: README.md with navigation
- Cross-references: Links between docs
- Search: Standard tools (grep, IDE)
- Formats: Markdown (readable plain text)

## Compliance Requirements

### C1: Licensing

**Requirement:** Distribution must respect licenses.

**Specifics:**
- Runtime code: License TBD (check repo)
- Bootstrap content: License TBD
- Dependencies: Respect their licenses

### C2: Data Handling

**Requirement:** User data must be handled appropriately.

**Specifics:**
- Artifacts: User-controlled locations
- State: Local to workstation
- Logs: No PII without consent
- Backend: User-configurable endpoint

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
