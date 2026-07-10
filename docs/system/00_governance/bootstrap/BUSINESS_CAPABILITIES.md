---
template_id: "SYS-00-BC"
title: "Business Capabilities"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document describes the operational capabilities that `agent-runner-v2` enables. It maps technical functionality to business value, helping stakeholders understand what the platform makes possible.

## Capability Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    Business Outcomes                             │
├─────────────────────────────────────────────────────────────────┤
│  • Faster delivery          • Higher quality                     │
│  • Reduced risk             • Better compliance                  │
│  • Improved traceability    • Lower cognitive load               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Operational Capabilities                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Workflow    │  │   Quality    │  │    Scale     │          │
│  │  Automation  │  │   Assurance  │  │   & Speed    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Technical Capabilities                        │
├─────────────────────────────────────────────────────────────────┤
│  Multi-Model Execution │ Review Loops │ Artifact Management     │
│  Retry Logic          │ Approval Gates │ Deterministic Actions   │
│  Workflow Routing     │ Sidecar Validation │ Step Recovery       │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Automation

### Capability: Structured Multi-Step Execution

**What it enables**:
- Complex workflows decomposed into discrete steps
- Each step has clear inputs, outputs, and routing
- Steps can be manual (LLM) or automated (Python actions)

**Business Value**:
- **Consistency**: Same process every time
- **Visibility**: Clear progress tracking
- **Auditability**: Complete execution history

**Example Workflows**:
- Initiative intake and refinement
- Delivery planning with task graphs
- Task execution with implementation and validation
- Documentation synchronization
- Architecture site generation

### Capability: Review/Refine Loops

**What it enables**:
- Quality gates at key decision points
- Automatic refinement on rejection
- Convergence tracking with iteration limits

**Business Value**:
- **Quality**: Catches issues before they propagate
- **Learning**: Model improves through feedback
- **Control**: Human oversight where needed

**Example Patterns**:
```
Generate → Review → (Approve | Refine → Review)
```

## Quality Assurance

### Capability: Deterministic Actions

**What it enables**:
- Python functions for predictable operations
- Same input always produces same output
- No ambiguity in execution

**Business Value**:
- **Reliability**: Known behavior
- **Testability**: Can be unit tested
- **Maintainability**: Clear logic

**Example Actions**:
- `finalize_bootstrap.py`: Bundle finalization
- `validate_delivery_docs.py`: Document validation
- `sync_codebase_docs.py`: Documentation sync
- `promote_artifact.py`: Artifact promotion

### Capability: Artifact Validation

**What it enables**:
- Verify expected artifacts exist
- Check content conforms to standards
- Validate cross-references

**Business Value**:
- **Completeness**: Nothing missing
- **Correctness**: Standards compliance
- **Traceability**: Link validation

**Validation Types**:
- Existence checks (file exists)
- Structure checks (frontmatter, sections)
- Content checks (no placeholders)
- Cross-reference checks (links resolve)

## Scale and Speed

### Capability: Multi-Model Support

**What it enables**:
- Claude for complex reasoning
- Codex for code generation
- Qwen for general tasks
- Aliased models for specific purposes

**Business Value**:
- **Optimization**: Best model for each task
- **Resilience**: Fallback options
- **Cost control**: Cheaper models where appropriate

**Model Mapping**:
```json
{
  "default": "claude-opus-4",
  "fast": "claude-sonnet-4",
  "code": "codex",
  "local": "qwen"
}
```

### Capability: Retry with Backoff

**What it enables**:
- Automatic retry on transient failures
- Configurable retry limits
- Progress tracking across attempts

**Business Value**:
- **Resilience**: Handles temporary issues
- **Efficiency**: No manual restart needed
- **Reliability**: Eventually succeeds

**Retry Types**:
- Auto-retry: Automatic retry on rejection
- Human-retry: Retry after human intervention
- Replan: Alternative approach on failure

## Governance and Compliance

### Capability: Declarative Document Protection

**What it enables**:
- `produces` lists control write access
- No unauthorized document modifications
- Clear ownership and lifecycle

**Business Value**:
- **Security**: Controlled access
- **Compliance**: Audit trail
- **Stability**: Protected documents

**Protection Model**:
- Allow-list based (can write if in `produces`)
- Workflow-scoped (protection per workflow)
- Step-scoped (protection per step)

### Capability: Complete Execution History

**What it enables**:
- Every step recorded in job state
- Model usage tracked
- Decision rationale captured

**Business Value**:
- **Auditability**: Full traceability
- **Analysis**: Performance insights
- **Learning": Pattern identification

**Tracked Data**:
- Step completions and failures
- Retry history
- Model usage per step
- Decision rationale
- Artifact provenance

## Operational Interpretation

### For Development Teams

| Capability | How It Helps |
|------------|--------------|
| Workflow Automation | Standardized delivery process |
| Review Loops | Quality gates prevent defects |
| Multi-Model Support | Right tool for each job |
| Artifact Validation | Nothing slips through |

### For Operations Teams

| Capability | How It Helps |
|------------|--------------|
| Deterministic Actions | Predictable behavior |
| Retry Logic | Self-healing workflows |
| Execution History | Full observability |
| Document Protection | Controlled environment |

### For Management

| Capability | How It Helps |
|------------|--------------|
| Complete History | Compliance and audit |
| Quality Gates | Risk reduction |
| Standardized Process | Consistent outcomes |
| Multi-Model | Cost optimization |

## Capability Dependencies

```
Workflow Automation
    ├── Requires: Step Runner
    ├── Requires: Workflow Router
    └── Enables: Review Loops

Review Loops
    ├── Requires: Workflow Automation
    ├── Requires: Artifact Validation
    └── Enables: Quality Gates

Quality Gates
    ├── Requires: Review Loops
    ├── Requires: Document Protection
    └── Enables: Compliance

Multi-Model Support
    ├── Requires: Coder Adapters
    └── Enables: Optimization
```

## Metrics and KPIs

### Efficiency Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow completion rate | >95% | Jobs completing successfully |
| Average retry count | <2 | Retries per step |
| Review convergence rate | >80% | Reviews approved on first try |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Artifact validation pass rate | >98% | Documents passing validation |
| Cross-reference accuracy | >99% | Links that resolve |
| Document freshness | <7 days | Time since last update |

### Scale Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Concurrent workflows | >10 | Parallel executions |
| Step execution time | <30s | Average step duration |
| Model availability | >99% | Successful model calls |

---

## Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — System explanation
- [FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md) — Technical behaviors
- [NON_FUNCTIONAL_REQUIREMENTS.md](NON_FUNCTIONAL_REQUIREMENTS.md) — Quality requirements

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
