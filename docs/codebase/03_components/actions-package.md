---
title: "Component Documentation: actions package"
template_id: "CB-03"
status: "active"
component_id: "actions-package"
created: "2026-07-04T06:01:39+08:00"
owner: "00_master_docs_bootstrap_v1"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-001 / 2026-07-04T06:01:39+08:00"
modules: ["agent_runner_v2/actions/__init__.py", "agent_runner_v2/actions/assemble_video.py", "agent_runner_v2/actions/copy_artifact.py", "agent_runner_v2/actions/documentation_validation_core.py", "agent_runner_v2/actions/execute_i2v.py", "agent_runner_v2/actions/execute_t2i.py", "agent_runner_v2/actions/execute_voiceover.py", "agent_runner_v2/actions/finalize_bootstrap.py", "agent_runner_v2/actions/prepare_delivery_scaffold.py", "agent_runner_v2/actions/promote_artifact.py", "agent_runner_v2/actions/promote_init.py", "agent_runner_v2/actions/scan_repo_codebase.py", "agent_runner_v2/actions/submit_comfyui.py", "agent_runner_v2/actions/sync_codebase_docs.py", "agent_runner_v2/actions/sync_system_docs.py", "agent_runner_v2/actions/validate_codebase_docs.py", "agent_runner_v2/actions/validate_delivery_docs.py", "agent_runner_v2/actions/validate_system_docs.py"]
---

# Component Documentation: actions package

## 1. Component Overview

### 1.1 Purpose

Deterministic action modules that implement non-coder steps and their I/O contracts.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `agent_runner_v2/actions/__init__.py` | deterministic runner action |
| `agent_runner_v2/actions/assemble_video.py` | deterministic runner action |
| `agent_runner_v2/actions/copy_artifact.py` | deterministic runner action |
| `agent_runner_v2/actions/documentation_validation_core.py` | deterministic runner action |
| `agent_runner_v2/actions/execute_i2v.py` | deterministic runner action |
| `agent_runner_v2/actions/execute_t2i.py` | deterministic runner action |
| `agent_runner_v2/actions/execute_voiceover.py` | deterministic runner action |
| `agent_runner_v2/actions/finalize_bootstrap.py` | deterministic runner action |
| `agent_runner_v2/actions/prepare_delivery_scaffold.py` | deterministic runner action |
| `agent_runner_v2/actions/promote_artifact.py` | deterministic runner action |
| `agent_runner_v2/actions/promote_init.py` | deterministic runner action |
| `agent_runner_v2/actions/scan_repo_codebase.py` | deterministic runner action |
| `agent_runner_v2/actions/submit_comfyui.py` | deterministic runner action |
| `agent_runner_v2/actions/sync_codebase_docs.py` | deterministic runner action |
| `agent_runner_v2/actions/sync_system_docs.py` | deterministic runner action |
| `agent_runner_v2/actions/validate_codebase_docs.py` | deterministic runner action |
| `agent_runner_v2/actions/validate_delivery_docs.py` | deterministic runner action |
| `agent_runner_v2/actions/validate_system_docs.py` | deterministic runner action |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `agent_runner_v2/actions/__init__.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/assemble_video.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/copy_artifact.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/documentation_validation_core.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/execute_i2v.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/execute_t2i.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/execute_voiceover.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/finalize_bootstrap.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/prepare_delivery_scaffold.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/promote_artifact.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/promote_init.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/scan_repo_codebase.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/submit_comfyui.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/sync_codebase_docs.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/sync_system_docs.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/validate_codebase_docs.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/validate_delivery_docs.py` | outbound | markdown | deterministic runner action |
| `agent_runner_v2/actions/validate_system_docs.py` | outbound | markdown | deterministic runner action |

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
| 2026-07-04 | Initial baseline generated from repository scan | 18 modules/files | 00_master_docs_bootstrap_v1 |
