---
title: "Component Documentation: scripts suite"
template_id: "CB-03"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
component_id: "scripts-suite"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
modules: ["run-bootstrap-publish.bat", "run-bootstrap-publish.sh", "run-cleanup-workflow.bat", "run-cleanup-workflow.sh", "run-cleanup.bat", "run-daemon.bat", "run-daemon.sh", "run-init.bat", "run-init.sh", "scripts/run-00_bootstrap_lifecycle_admin_v1.bat", "scripts/run-00_bootstrap_lifecycle_admin_v1.sh", "scripts/run-01_governance_foundation_v1.bat", "scripts/run-01_governance_foundation_v1.sh", "scripts/run-02_agent_runner_platform_v1.bat", "scripts/run-02_agent_runner_platform_v1.sh", "scripts/run-approve-step.bat", "scripts/run-approve-step.sh", "scripts/run-console.bat", "scripts/run-console.sh", "scripts/run-reset-step.bat", "scripts/run-reset-step.sh", "scripts/run-sdlc_00_codebase_v1.bat", "scripts/run-sdlc_00_codebase_v1.sh", "scripts/run-sdlc_00_delivery_scaffold_v1.bat", "scripts/run-sdlc_00_delivery_scaffold_v1.sh", "scripts/run-sdlc_00_init_doc_v1.bat", "scripts/run-sdlc_00_init_doc_v1.sh", "scripts/run-sdlc_10_requirement_v1.bat", "scripts/run-sdlc_10_requirement_v1.sh", "scripts/run-sdlc_20_planning_v1.bat", "scripts/run-sdlc_20_planning_v1.sh", "scripts/run-sdlc_30_backlog_v1.bat", "scripts/run-sdlc_30_backlog_v1.sh", "scripts/run-sdlc_40_task_v1.bat", "scripts/run-sdlc_40_task_v1.sh", "scripts/run-sdlc_50_implementation_v1.bat", "scripts/run-sdlc_50_implementation_v1.sh", "scripts/run-sdlc_60_execution_v1.bat", "scripts/run-sdlc_60_execution_v1.sh", "scripts/run-sdlc_70_validation_v1.bat", "scripts/run-sdlc_70_validation_v1.sh", "scripts/run-sdlc_80_review_v1.bat", "scripts/run-sdlc_80_review_v1.sh", "scripts/submit-00_bootstrap_lifecycle_admin_v1.bat", "scripts/submit-00_bootstrap_lifecycle_admin_v1.sh", "scripts/submit-01_governance_foundation_v1.bat", "scripts/submit-01_governance_foundation_v1.sh", "scripts/submit-02_agent_runner_platform_v1.bat", "scripts/submit-02_agent_runner_platform_v1.sh", "scripts/submit-sdlc_00_codebase_v1.bat", "scripts/submit-sdlc_00_codebase_v1.sh", "scripts/submit-sdlc_00_init_doc_v1.bat", "scripts/submit-sdlc_00_init_doc_v1.sh", "scripts/submit-sdlc_10_requirement_v1.bat", "scripts/submit-sdlc_10_requirement_v1.sh", "scripts/submit-sdlc_20_planning_v1.bat", "scripts/submit-sdlc_20_planning_v1.sh", "scripts/submit-sdlc_30_backlog_v1.bat", "scripts/submit-sdlc_30_backlog_v1.sh", "scripts/submit-sdlc_40_task_v1.bat", "scripts/submit-sdlc_40_task_v1.sh", "scripts/submit-sdlc_50_implementation_v1.bat", "scripts/submit-sdlc_50_implementation_v1.sh", "scripts/submit-sdlc_60_execution_v1.bat", "scripts/submit-sdlc_60_execution_v1.sh", "scripts/submit-sdlc_70_validation_v1.bat", "scripts/submit-sdlc_70_validation_v1.sh", "scripts/submit-sdlc_80_review_v1.bat", "scripts/submit-sdlc_80_review_v1.sh", "sync-workflows-to-backend.bat", "sync-workflows-to-backend.sh"]
---

# Component Documentation: scripts suite

## 1. Component Overview

### 1.1 Purpose

Shell and batch scripts used to run and operate the repository workflows.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `run-bootstrap-publish.bat` | automation / entrypoint |
| `run-bootstrap-publish.sh` | automation / entrypoint |
| `run-cleanup-workflow.bat` | automation / entrypoint |
| `run-cleanup-workflow.sh` | automation / entrypoint |
| `run-cleanup.bat` | automation / entrypoint |
| `run-daemon.bat` | automation / entrypoint |
| `run-daemon.sh` | automation / entrypoint |
| `run-init.bat` | automation / entrypoint |
| `run-init.sh` | automation / entrypoint |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.bat` | automation / entrypoint |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.sh` | automation / entrypoint |
| `scripts/run-01_governance_foundation_v1.bat` | automation / entrypoint |
| `scripts/run-01_governance_foundation_v1.sh` | automation / entrypoint |
| `scripts/run-02_agent_runner_platform_v1.bat` | automation / entrypoint |
| `scripts/run-02_agent_runner_platform_v1.sh` | automation / entrypoint |
| `scripts/run-approve-step.bat` | automation / entrypoint |
| `scripts/run-approve-step.sh` | automation / entrypoint |
| `scripts/run-console.bat` | automation / entrypoint |
| `scripts/run-console.sh` | automation / entrypoint |
| `scripts/run-reset-step.bat` | automation / entrypoint |
| `scripts/run-reset-step.sh` | automation / entrypoint |
| `scripts/run-sdlc_00_codebase_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_00_codebase_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_00_delivery_scaffold_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_00_delivery_scaffold_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_00_init_doc_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_00_init_doc_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_10_requirement_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_10_requirement_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_20_planning_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_20_planning_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_30_backlog_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_30_backlog_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_40_task_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_40_task_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_50_implementation_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_50_implementation_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_60_execution_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_60_execution_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_70_validation_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_70_validation_v1.sh` | automation / entrypoint |
| `scripts/run-sdlc_80_review_v1.bat` | automation / entrypoint |
| `scripts/run-sdlc_80_review_v1.sh` | automation / entrypoint |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.bat` | automation / entrypoint |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.sh` | automation / entrypoint |
| `scripts/submit-01_governance_foundation_v1.bat` | automation / entrypoint |
| `scripts/submit-01_governance_foundation_v1.sh` | automation / entrypoint |
| `scripts/submit-02_agent_runner_platform_v1.bat` | automation / entrypoint |
| `scripts/submit-02_agent_runner_platform_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_00_codebase_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_00_codebase_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_00_init_doc_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_00_init_doc_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_10_requirement_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_10_requirement_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_20_planning_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_20_planning_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_30_backlog_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_30_backlog_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_40_task_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_40_task_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_50_implementation_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_50_implementation_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_60_execution_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_60_execution_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_70_validation_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_70_validation_v1.sh` | automation / entrypoint |
| `scripts/submit-sdlc_80_review_v1.bat` | automation / entrypoint |
| `scripts/submit-sdlc_80_review_v1.sh` | automation / entrypoint |
| `sync-workflows-to-backend.bat` | automation / entrypoint |
| `sync-workflows-to-backend.sh` | automation / entrypoint |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `run-bootstrap-publish.bat` | outbound | markdown | automation / entrypoint |
| `run-bootstrap-publish.sh` | outbound | markdown | automation / entrypoint |
| `run-cleanup-workflow.bat` | outbound | markdown | automation / entrypoint |
| `run-cleanup-workflow.sh` | outbound | markdown | automation / entrypoint |
| `run-cleanup.bat` | outbound | markdown | automation / entrypoint |
| `run-daemon.bat` | outbound | markdown | automation / entrypoint |
| `run-daemon.sh` | outbound | markdown | automation / entrypoint |
| `run-init.bat` | outbound | markdown | automation / entrypoint |
| `run-init.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-01_governance_foundation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-01_governance_foundation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-02_agent_runner_platform_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-02_agent_runner_platform_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-approve-step.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-approve-step.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-console.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-console.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-reset-step.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-reset-step.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_codebase_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_codebase_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_delivery_scaffold_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_delivery_scaffold_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_init_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_00_init_doc_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_10_requirement_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_10_requirement_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_20_planning_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_20_planning_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_30_backlog_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_30_backlog_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_40_task_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_40_task_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_50_implementation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_50_implementation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_60_execution_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_60_execution_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_70_validation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_70_validation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_80_review_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/run-sdlc_80_review_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-01_governance_foundation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-01_governance_foundation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-02_agent_runner_platform_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-02_agent_runner_platform_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_00_codebase_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_00_codebase_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_00_init_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_00_init_doc_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_10_requirement_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_10_requirement_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_20_planning_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_20_planning_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_30_backlog_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_30_backlog_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_40_task_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_40_task_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_50_implementation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_50_implementation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_60_execution_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_60_execution_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_70_validation_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_70_validation_v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_80_review_v1.bat` | outbound | markdown | automation / entrypoint |
| `scripts/submit-sdlc_80_review_v1.sh` | outbound | markdown | automation / entrypoint |
| `sync-workflows-to-backend.bat` | outbound | markdown | automation / entrypoint |
| `sync-workflows-to-backend.sh` | outbound | markdown | automation / entrypoint |

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
| 2026-08-06 | Initial baseline generated from repository scan | 71 modules/files | sdlc_00_codebase_v1 |
