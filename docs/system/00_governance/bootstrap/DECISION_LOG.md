---
title: "Decision Log: agent-runner-v2"
template_id: "SYS-03-DL"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Decision Log: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

This document records significant architectural and design decisions made during the development of agent-runner-v2.

## Architecture Decisions

### AD-001: V2 Sidecar-Only Contract

**Status:** Accepted

**Context:**
In v1, the runner relied on multiple communication channels between the runner and coder: stdout parsing, file existence checks, and sidecar JSON. This led to ambiguity in result interpretation and complex fallback logic.

**Decision:**
In v2, `meta.json` is the ONLY structured result channel. All artifacts, status, remarks, and usage data flow through this single sidecar file. The runner never parses coder stdout for results.

**Consequences:**
- **Positive:** Clear contract, unambiguous result interpretation
- **Positive:** Easier testing and validation
- **Negative:** Coder must always write valid `meta.json`
- **Negative:** Hard failures if sidecar missing (no graceful degradation)

### AD-002: No Markdown Write-Backs

**Status:** Accepted

**Context:**
In v1, the runner would write metadata back to markdown files (review stamps, created timestamps, status badges). This caused race conditions and violated single-responsibility principles.

**Decision:**
The runner never writes to markdown files. All metadata lives in `job.json` or `meta.json`. Markdown files are read-only inputs or coder-generated outputs.

**Consequences:**
- **Positive:** Clear separation of concerns
- **Positive:** No race conditions on file writes
- **Positive:** Markdown can be versioned without runner noise
- **Negative:** Documentation tools must read `job.json` for metadata

### AD-003: Bootstrap/Runtime Split

**Status:** Accepted

**Context:**
Workflow templates and prompts need to be customizable per-project but also updatable with the package.

**Decision:**
Maintain two distinct sources:
1. **Bootstrap source** in the package (`agent_runner_v2/bootstrap/`) — seeds new installations
2. **Runtime bundles** in user home (`~/.ukbe-runner/workflows/`) — actually loaded at runtime

**Consequences:**
- **Positive:** Safe customization without package modification
- **Positive:** Version isolation between projects
- **Positive:** Rollback capability
- **Negative:** Potential drift between bootstrap and runtime
- **Negative:** Additional complexity in bundle loading

### AD-004: Explicit Failure Routing

**Status:** Accepted

**Context:**
Silent failures and automatic recovery paths can mask issues and make debugging difficult.

**Decision:**
All failures route explicitly through `route_after_failure()`. No silent recovery. Failure classification (`AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, `FATAL`) determines next steps.

**Consequences:**
- **Positive:** Predictable failure handling
- **Positive:** Clear audit trail
- **Positive:** No hidden recovery masking root causes
- **Negative:** More intervention required for transient failures

### AD-005: Blocking Issues Owned by Coder

**Status:** Accepted

**Context:**
In v1, the runner extracted blocking issues from content and decided when to escalate. This duplicated the coder's content analysis.

**Decision:**
`blocking_issues` is always empty in runner context. The coder owns all content analysis and blocking determination. The runner trusts the coder's REJECTED status.

**Consequences:**
- **Positive:** Single responsibility for content decisions
- **Positive:** Simpler runner logic
- **Positive:** Coder can use any blocking criteria
- **Negative:** Less runner visibility into why blocks occur

### AD-006: Multi-Provider Coder Support

**Status:** Accepted

**Context:**
Different tasks may benefit from different LLM providers (Claude for reasoning, Codex for code, Qwen for local execution).

**Decision:**
Support multiple coder providers through a unified adapter interface. Each provider implements the same contract: prompt in, sidecar out.

**Consequences:**
- **Positive:** Flexibility to choose best tool for task
- **Positive:** Fallback options if one provider unavailable
- **Positive:** Local-first option with Qwen
- **Negative:** Provider-specific tuning required
- **Negative:** Testing matrix expansion

### AD-007: Deterministic Runner Actions

**Status:** Accepted

**Context:**
Workflow steps need reproducible, testable operations on the repository.

**Decision:**
All file/system operations go through deterministic action modules in `actions/`. Actions are pure functions with explicit inputs/outputs.

**Consequences:**
- **Positive:** Testable operations
- **Positive:** Reproducible executions
- **Positive:** Clear audit trail
- **Negative:** More boilerplate for new operations
- **Negative:** Limited to pre-defined actions

### AD-008: Backend Worker Mode

**Status:** Accepted

**Context:**
For team workflows and centralized job management, a backend-driven execution model is needed alongside local CLI.

**Decision:**
Implement worker mode where a backend service distributes work. Workers poll for steps, execute, and submit results. Daemon mode supervises workers.

**Consequences:**
- **Positive:** Scalable team workflows
- **Positive:** Centralized job management
- **Positive:** Workstation supervision via daemon
- **Negative:** Network dependency
- **Negative:** Additional infrastructure complexity

### AD-009: Schema Versioning for Job State

**Status:** Accepted

**Context:**
Job state format evolves over time. Need to support existing jobs while adding new fields.

**Decision:**
Use explicit schema versioning (`CURRENT_SCHEMA_VERSION = 6`). Include migration functions (`migrate_job_state()`) for backward compatibility.

**Consequences:**
- **Positive:** Safe evolution of job format
- **Positive:** Existing jobs remain usable
- **Positive:** Clear upgrade path
- **Negative:** Migration code accumulates
- **Negative:** Testing complexity for old versions

### AD-010: Template Groups as Python Modules

**Status:** Accepted

**Context:**
Workflow definitions need to be programmatically inspectable and importable.

**Decision:**
Define workflows in `template_groups.py` Python modules rather than JSON/YAML. This enables programmatic inspection, type hints, and complex logic.

**Consequences:**
- **Positive:** Full Python power in workflow definitions
- **Positive:** Import-time validation
- **Positive:** IDE support
- **Negative:** Python knowledge required for customization
- **Negative:** Security considerations with user code

## Technology Decisions

### TD-001: Python 3.11+ Requirement

**Status:** Accepted

**Context:**
Modern Python features improve code quality and maintainability.

**Decision:**
Require Python 3.11+ for features like `tomllib`, improved `typing`, and `asyncio` enhancements.

**Consequences:**
- **Positive:** Access to modern Python features
- **Positive:** Better type annotation support
- **Negative:** Older system compatibility

### TD-002: Jinja2 for Prompt Templating

**Status:** Accepted

**Context:**
Workflow prompts need dynamic content insertion with conditionals and loops.

**Decision:**
Use Jinja2 for prompt template rendering. Templates are plain text files with Jinja2 syntax.

**Consequences:**
- **Positive:** Powerful templating with conditionals, loops
- **Positive:** Familiar syntax
- **Positive:** Sandboxed execution
- **Negative:** Jinja2 dependency

### TD-003: JSON for State Storage

****Status:** Accepted

**Context:**
Job state needs to be human-readable, editable, and tool-processable.

**Decision:**
Use JSON for job state (`job.json`) and sidecars (`meta.json`). Avoid binary formats.

**Consequences:**
- **Positive:** Human-readable and editable
- **Positive:** Universal tooling support
- **Positive:** Line-oriented for version control
- **Negative:** No native datetime types
- **Negative:** Verbose for large states

### TD-004: Pathlib for Path Operations

**Status:** Accepted

**Context:**
Cross-platform path handling is error-prone with string manipulation.

**Decision:**
Use `pathlib.Path` for all path operations. No string path manipulation.

**Consequences:**
- **Positive:** Cross-platform compatibility
- **Positive:** Type safety
- **Positive:** Clear path semantics
- **Negative:** Slight performance overhead

## Deferred Decisions

### DD-001: Bundle Taxonomy Evolution

**Status:** Deferred

**Context:**
Bundle organization (core, domain, workflow) may need refinement as usage patterns emerge.

**Decision:**
Keep current flat structure under `workflows/`. Revisit if bundle count grows significantly.

**Trigger for Revisit:**
More than 20 workflow families or clear categorization needs.

### DD-002: Template Groups Splitting

**Status:** Deferred

**Context:**
`template_groups.py` may grow too large as workflow families are added.

**Decision:**
Keep single file per workflow bundle. Consider splitting if file exceeds 5,000 lines.

**Trigger for Revisit:**
Template groups file exceeds 5,000 lines or load time becomes noticeable.

### DD-003: ComfyUI Integration Depth

**Status:** Deferred

**Context:**
Current ComfyUI integration is via HTTP submission. Deeper integration may be beneficial.

**Decision:**
Keep current submission-only model. Revisit if workflow needs require more control.

**Trigger for Revisit:**
Need for progress polling, result retrieval, or workflow manipulation.

## Rejected Alternatives

### RA-001: SQLite for Job State

**Status:** Rejected

**Context:**
Considered SQLite for job state storage instead of JSON files.

**Reason for Rejection:**
JSON files provide better debuggability, easier manual intervention, and simpler backup. SQLite adds unnecessary complexity for the query patterns needed.

**Consequences of Rejection:**
- Job state remains file-based
- Manual editing and inspection remain easy
- No SQL dependency

### RA-002: Asyncio Throughout

**Status:** Rejected

**Context:**
Considered using `asyncio` for all I/O operations.

**Reason for Rejection:**
Most operations are sequential by nature. Asyncio adds complexity without clear benefit for the current use cases. Keep synchronous code with threading where needed (daemon).

**Consequences of Rejection:**
- Simpler code flow
- Easier debugging
- Threading used only in daemon mode

### RA-003: Protobuf for Sidecar

**Status:** Rejected

**Context:**
Considered Protocol Buffers for sidecar format instead of JSON.

**Reason for Rejection:**
JSON is human-readable, editable, and universally supported. Protobuf would require code generation and complicate debugging. Performance gains not needed for this use case.

**Consequences of Rejection:**
- Sidecar remains JSON
- Human inspection and editing possible
- No code generation step

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
