---
template_id: "SYS-00-BC"
title: "Business Capabilities - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Business Capabilities

## Purpose

This document maps the operational capabilities enabled by agent-runner-v2. It describes what the platform enables organizations to accomplish, not just its technical features.

**Why:** Understanding capabilities (rather than just features) helps stakeholders evaluate fit, plan adoption, and identify opportunities for value creation.

## Capability Map

### Capability: Workflow Orchestration

**Description:** Execute structured multi-step workflows with deterministic progression and state management.

**Enables:**
- Automating complex processes that require multiple steps
- Ensuring consistent execution regardless of operator
- Recovering from failures without losing progress
- Reviewing and approving intermediate results

**Operational Impact:**
- Reduces manual coordination overhead
- Increases process reliability
- Enables parallel execution of independent steps
- Provides audit trail of execution

**Workflow Families Supported:**

| Family | Steps | Use Case |
|--------|-------|----------|
| `00_master_docs_bootstrap_v1` | 10 | System documentation generation |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold setup |
| `20_initiative_intake_v1` | 5 | Initiative capture and refinement |
| `21_bug_fix_intake_v1` | 7 | Bug triage and resolution |
| `30_delivery_planning_v1` | 10 | Plan and task generation |
| `31_task_execution_v1` | 12 | Task implementation and validation |
| `40_documentation_sync_v1` | 4 | Documentation synchronization |
| `image_csv_gen_v2` | 5 | Image generation workflow |
| `videoxpress_gen_v1` | 9 | Video content generation |
| `tiktok_video_pipeline_v1` | 10 | TikTok content pipeline |

### Capability: LLM Integration

**Description:** Invoke multiple LLM providers (Claude, Codex, Qwen) with unified interfaces and result handling.

**Enables:**
- Using the best model for each task type
- Switching models without workflow changes
- Tracking usage and costs across providers
- Standardizing result validation

**Operational Impact:**
- Optimizes cost/quality tradeoffs per step
- Reduces vendor lock-in
- Simplifies model experimentation
- Centralizes usage tracking

**Model Support:**

| Provider | Models | Typical Use |
|----------|--------|-------------|
| Claude | Sonnet, Opus, Haiku | Complex reasoning, coding |
| Codex | o3, o4-mini | Code generation, review |
| Qwen | Qwen3 | Local/self-hosted execution |

### Capability: Quality Assurance

**Description:** Review loops, approval gates, and validation ensure output quality before progression.

**Enables:**
- Catching errors before they propagate
- Human oversight of critical steps
- Iterative refinement until standards met
- Explicit rejection codes for targeted fixes

**Operational Impact:**
- Improves output quality
- Reduces rework downstream
- Provides clear quality criteria
- Enables automated retry for fixable issues

**Review Patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| Auto-retry | Automatic retry on transient failures | Timeout recovery |
| Human review | Requires human approval to continue | Architecture decisions |
| Replan | Workflow adaptation based on findings | Scope changes |

### Capability: Distributed Execution

**Description:** Backend-connected worker and daemon modes enable distributed, scalable execution.

**Enables:**
- Scaling beyond single workstation
- Centralized queue management
- Work distribution across multiple workers
- Heartbeat monitoring and failure detection

**Operational Impact:**
- Increases throughput via parallel workers
- Improves reliability through redundancy
- Enables cloud deployment
- Centralizes operational visibility

**Execution Modes:**

| Mode | Use Case | Scaling |
|------|----------|---------|
| Local (`run`) | Development, testing | Single workstation |
| Worker (`worker`) | Backend-connected execution | Multi-worker pool |
| Daemon (`daemon`) | Continuous supervision | Per-workstation daemon |

### Capability: Content Generation

**Description:** Specialized workflows for image, video, and audio content generation.

**Enables:**
- Automated content pipelines
- Multi-modal asset creation
- Integration with generation services (ComfyUI)
- Asset assembly and composition

**Operational Impact:**
- Accelerates content production
- Ensures consistent asset organization
- Enables batch processing
- Tracks generation results

**Content Types:**

| Type | Workflow | Output |
|------|----------|--------|
| Images | `image_csv_gen_v2` | Image CSV + generated images |
| Videos | `videoxpress_gen_v1` | Composed video with voiceover |
| TikTok | `tiktok_video_pipeline_v1` | Platform-optimized content |

### Capability: Documentation Governance

**Description:** Automated generation, synchronization, and validation of codebase and system documentation.

**Enables:**
- Keeping documentation synchronized with code
- Generating documentation from code analysis
- Validating documentation completeness
- Protecting workflow-generated documents

**Operational Impact:**
- Reduces documentation drift
- Ensures consistent documentation structure
- Enforces documentation standards
- Tracks documentation changes

**Documentation Types:**

| Type | Location | Content |
|------|----------|---------|
| System docs | `docs/system/` | Governance, standards, guides |
| Codebase docs | `docs/codebase/` | Inventory, modules, components |
| Delivery docs | `docs/delivery/` | Initiatives, plans, tasks |

## Operational Interpretation

### For Development Teams

**Capability:** Accelerated Delivery
- Automated code generation and review
- Consistent implementation patterns
- Reduced boilerplate writing
- Faster onboarding via generated docs

**Metrics:**
- Time from initiative to implementation
- Code review cycle time
- Documentation coverage percentage

### For Content Teams

**Capability:** Scalable Content Production
- Automated asset generation
- Batch processing capabilities
- Consistent output organization
- Quality-controlled pipelines

**Metrics:**
- Assets generated per hour
- Revision cycles per asset
- Pipeline success rate

### For Operations Teams

**Capability:** Reliable Automation
- Monitored execution with heartbeats
- Automatic failure recovery
- Centralized logging and visibility
- Resource-efficient daemon mode

**Metrics:**
- Worker utilization
- Failure recovery rate
- Mean time to completion

### For Architecture Teams

**Capability:** Consistent Patterns
- Standardized workflow definitions
- Documented architectural decisions
- Enforced documentation standards
- Traceable change history

**Metrics:**
- ADR coverage
- Documentation standard compliance
- Workflow reuse across projects

## Capability Dependencies

```
Workflow Orchestration
    ↓
LLM Integration → Quality Assurance
    ↓
Content Generation ← Distributed Execution
    ↓
Documentation Governance
```

**Flow Explanation:**
1. **Workflow Orchestration** is foundational — all other capabilities build on it
2. **LLM Integration** and **Quality Assurance** are complementary — LLM outputs need quality control
3. **Distributed Execution** enables scale for both content and documentation
4. **Documentation Governance** captures patterns and decisions for reuse

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
