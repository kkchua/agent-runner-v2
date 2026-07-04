---
title: "Component Documentation: config and data"
template_id: "CB-03"
status: "active"
component_id: "config-and-data"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
modules: [".env.example", "agent_runner_v2/comfyui_config.json", "agent_runner_v2/job_schema.json", "agent_runner_v2/llm_response_schema.json", "agent_runner_v2/model_mapping.json", "agent_runner_v2/usage_schema.json", "docs/codebase/04_changes/00DOC-GEN-20260704-001-bootstrap-snapshot.json", "docs/codebase/04_changes/00DOC-GEN-20260704-002-bootstrap-snapshot.json", "docs/codebase/04_changes/DOCSYNC-20260704_codebase-doc-update.meta.json", "pyproject.toml"]
---

# Component Documentation: config and data

## 1. Component Overview

### 1.1 Purpose

Configuration and structured data files that define runtime and documentation behavior.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `.env.example` | configuration / structured data |
| `agent_runner_v2/comfyui_config.json` | configuration / structured data |
| `agent_runner_v2/job_schema.json` | configuration / structured data |
| `agent_runner_v2/llm_response_schema.json` | configuration / structured data |
| `agent_runner_v2/model_mapping.json` | configuration / structured data |
| `agent_runner_v2/usage_schema.json` | configuration / structured data |
| `docs/codebase/04_changes/00DOC-GEN-20260704-001-bootstrap-snapshot.json` | configuration / structured data |
| `docs/codebase/04_changes/00DOC-GEN-20260704-002-bootstrap-snapshot.json` | configuration / structured data |
| `docs/codebase/04_changes/DOCSYNC-20260704_codebase-doc-update.meta.json` | configuration / structured data |
| `pyproject.toml` | configuration / structured data |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `.env.example` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/comfyui_config.json` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/job_schema.json` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/llm_response_schema.json` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/model_mapping.json` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/usage_schema.json` | outbound | markdown | configuration / structured data |
| `docs/codebase/04_changes/00DOC-GEN-20260704-001-bootstrap-snapshot.json` | outbound | markdown | configuration / structured data |
| `docs/codebase/04_changes/00DOC-GEN-20260704-002-bootstrap-snapshot.json` | outbound | markdown | configuration / structured data |
| `docs/codebase/04_changes/DOCSYNC-20260704_codebase-doc-update.meta.json` | outbound | markdown | configuration / structured data |
| `pyproject.toml` | outbound | markdown | configuration / structured data |

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
| 2026-07-04 | Initial baseline generated from repository scan | 10 modules/files | 00_master_docs_bootstrap_v1 |
