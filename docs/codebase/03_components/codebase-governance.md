---
title: "Component Documentation: codebase governance"
template_id: "CB-03"
status: "active"
component_id: "codebase-governance"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
modules: [".qwen/skills/auto-skill-agent-system-review/SKILL.md", ".qwen/skills/auto-skill-generate-agents/SKILL.md", ".qwen/skills/auto-skill-generate-architecture-docs/SKILL.md", ".qwen/skills/auto-skill-generate-master-system-docs/SKILL.md", ".qwen/skills/auto-skill-generate-sop/SKILL.md", ".qwen/skills/auto-skill-generate-templates/SKILL.md", ".qwen/skills/auto-skill-project-analysis/SKILL.md", ".qwen/skills/auto-skill-review-master-system-docs/SKILL.md", "agent_runner_v2/image_csv_generation.md", "agent_runner_v2/QWEN.md", "archive/batch/README.md", "docs/codebase/01_inventory/codebase_inventory.md", "HOW_TO_GUIDE.md", "QWEN.md", "README.md", "WINDOWS_COMPATIBILITY.md"]
---

# Component Documentation: codebase governance

## 1. Component Overview

### 1.1 Purpose

The codebase documentation standards, templates, inventory, and validation rules that govern `/docs/codebase`.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `.qwen/skills/auto-skill-agent-system-review/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-agents/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-architecture-docs/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-master-system-docs/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-sop/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-templates/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-project-analysis/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-review-master-system-docs/SKILL.md` | documentation artifact |
| `agent_runner_v2/image_csv_generation.md` | documentation artifact |
| `agent_runner_v2/QWEN.md` | documentation artifact |
| `archive/batch/README.md` | documentation artifact |
| `docs/codebase/01_inventory/codebase_inventory.md` | documentation artifact |
| `HOW_TO_GUIDE.md` | documentation artifact |
| `QWEN.md` | documentation artifact |
| `README.md` | documentation artifact |
| `WINDOWS_COMPATIBILITY.md` | documentation artifact |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `.qwen/skills/auto-skill-agent-system-review/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-agents/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-architecture-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-master-system-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-sop/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-templates/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-project-analysis/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-review-master-system-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/image_csv_generation.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/QWEN.md` | outbound | markdown | documentation artifact |
| `archive/batch/README.md` | outbound | markdown | documentation artifact |
| `docs/codebase/01_inventory/codebase_inventory.md` | outbound | markdown | documentation artifact |
| `HOW_TO_GUIDE.md` | outbound | markdown | documentation artifact |
| `QWEN.md` | outbound | markdown | documentation artifact |
| `README.md` | outbound | markdown | documentation artifact |
| `WINDOWS_COMPATIBILITY.md` | outbound | markdown | documentation artifact |

## 3. Behavior

### 3.1 Lifecycle

Created during codebase bootstrap or reconcile runs and refreshed when repository structure changes.

### 3.2 State Management

State is represented by the generated inventory and per-module/component documents.

### 3.3 Error Propagation

Documentation drift is treated as a validation failure and reraised to the workflow runner.

## 4. Configuration

| Parameter | Source | Default | Description |
|-----------|--------|---------|-------------|
| | | | |

## 5. Constraints

| Constraint | Rationale | Enforcement |
|------------|-----------|-------------|
| Zero mutation of source code | Documentation bootstrap must not alter code | Workflow writes docs only |

## 6. Testing

### 6.1 Integration Tests

| Test | Coverage |
|------|----------|
| | |

### 6.2 Known Gaps

Auto-generated baseline; extend with component-specific checks as needed.

## 7. Change Log

| Date | Change | Modules Affected | Verified By |
|------|--------|-----------------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 16 modules/files | 00_master_docs_bootstrap_v1 |
