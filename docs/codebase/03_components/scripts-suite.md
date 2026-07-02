---
title: "Component Documentation: scripts suite"
template_id: "CB-03"
status: "active"
component_id: "scripts-suite"
created: "2026-07-02T18:00:53+08:00"
owner: "00_master_docs_bootstrap_v1"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260702-005 / 2026-07-02T18:00:53+08:00"
modules: ["archive/batch/run-bug_fix_v1.bat", "archive/batch/run-codebase_bootstrap_v1.bat", "archive/batch/run-codebase_reconcile_v1.bat", "archive/batch/run-codebase_rescan_v1.bat", "archive/batch/run-codebase_sync_v1.bat", "archive/batch/run-documentation_bootstrap_v1.bat", "archive/batch/run-documentation_validation_v1.bat", "archive/batch/run-system_docs_bootstrap_v1.bat", "archive/batch/submit-bug_fix_v1.bat", "archive/batch/submit-codebase_bootstrap_v1.bat", "archive/batch/submit-codebase_reconcile_v1.bat", "archive/batch/submit-codebase_rescan_v1.bat", "archive/batch/submit-codebase_sync_v1.bat", "archive/batch/submit-documentation_bootstrap_v1.bat", "archive/batch/submit-documentation_validation_v1.bat", "run-00_master_docs_bootstrap_v1.bat", "run-10_execution_scaffold_v1.bat", "run-approve-step.bat", "run-daemon.bat", "run-reset-step.bat", "sample-run-delivery.bat", "scripts/approve-run.sh", "scripts/examples/approve-run.sh", "scripts/examples/submit-delivery-planning.sh", "scripts/examples/submit-delivery-scaffold.sh", "scripts/examples/submit-image-csv-gen-v1.sh", "scripts/examples/submit-image-csv-gen-v2.sh", "scripts/examples/submit-initiative-intake.sh", "scripts/examples/submit-task-execution.sh", "scripts/README.md", "scripts/submit-delivery-planning.sh", "scripts/submit-delivery-scaffold.sh", "scripts/submit-initiative-intake.sh", "scripts/ukbe-daemon-wsl.sh", "scripts/ukbe-daemon.bat", "scripts/ukbe-run-delivery.bat", "scripts/ukbe-runner.sh", "submit-00_master_docs_bootstrap_v1.bat", "submit-10_execution_scaffold_v1.bat", "sync-10_execution_scaffold_v1-workflow-spec.bat", "sync-workflows-to-backend.bat", "test-runner.bat"]
---

# Component Documentation: scripts suite

## 1. Component Overview

### 1.1 Purpose

Shell and batch scripts used to run and operate the repository workflows.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `archive/batch/run-bug_fix_v1.bat` | automation / entrypoint |
| `archive/batch/run-codebase_bootstrap_v1.bat` | automation / entrypoint |
| `archive/batch/run-codebase_reconcile_v1.bat` | automation / entrypoint |
| `archive/batch/run-codebase_rescan_v1.bat` | automation / entrypoint |
| `archive/batch/run-codebase_sync_v1.bat` | automation / entrypoint |
| `archive/batch/run-documentation_bootstrap_v1.bat` | automation / entrypoint |
| `archive/batch/run-documentation_validation_v1.bat` | automation / entrypoint |
| `archive/batch/run-system_docs_bootstrap_v1.bat` | automation / entrypoint |
| `archive/batch/submit-bug_fix_v1.bat` | automation / entrypoint |
| `archive/batch/submit-codebase_bootstrap_v1.bat` | automation / entrypoint |
| `archive/batch/submit-codebase_reconcile_v1.bat` | automation / entrypoint |
| `archive/batch/submit-codebase_rescan_v1.bat` | automation / entrypoint |
| `archive/batch/submit-codebase_sync_v1.bat` | automation / entrypoint |
| `archive/batch/submit-documentation_bootstrap_v1.bat` | automation / entrypoint |
| `archive/batch/submit-documentation_validation_v1.bat` | automation / entrypoint |
| `run-00_master_docs_bootstrap_v1.bat` | automation / entrypoint |
| `run-10_execution_scaffold_v1.bat` | automation / entrypoint |
| `run-approve-step.bat` | automation / entrypoint |
| `run-daemon.bat` | automation / entrypoint |
| `run-reset-step.bat` | automation / entrypoint |
| `sample-run-delivery.bat` | automation / entrypoint |
| `scripts/approve-run.sh` | automation / entrypoint |
| `scripts/examples/approve-run.sh` | automation / entrypoint |
| `scripts/examples/submit-delivery-planning.sh` | automation / entrypoint |
| `scripts/examples/submit-delivery-scaffold.sh` | automation / entrypoint |
| `scripts/examples/submit-image-csv-gen-v1.sh` | automation / entrypoint |
| `scripts/examples/submit-image-csv-gen-v2.sh` | automation / entrypoint |
| `scripts/examples/submit-initiative-intake.sh` | automation / entrypoint |
| `scripts/examples/submit-task-execution.sh` | automation / entrypoint |
| `scripts/README.md` | automation / entrypoint |
| `scripts/submit-delivery-planning.sh` | automation / entrypoint |
| `scripts/submit-delivery-scaffold.sh` | automation / entrypoint |
| `scripts/submit-initiative-intake.sh` | automation / entrypoint |
| `scripts/ukbe-daemon-wsl.sh` | automation / entrypoint |
| `scripts/ukbe-daemon.bat` | automation / entrypoint |
| `scripts/ukbe-run-delivery.bat` | automation / entrypoint |
| `scripts/ukbe-runner.sh` | automation / entrypoint |
| `submit-00_master_docs_bootstrap_v1.bat` | automation / entrypoint |
| `submit-10_execution_scaffold_v1.bat` | automation / entrypoint |
| `sync-10_execution_scaffold_v1-workflow-spec.bat` | automation / entrypoint |
| `sync-workflows-to-backend.bat` | automation / entrypoint |
| `test-runner.bat` | automation / entrypoint |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `archive/batch/run-bug_fix_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-codebase_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-codebase_reconcile_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-codebase_rescan_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-codebase_sync_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-documentation_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-documentation_validation_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/run-system_docs_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-bug_fix_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-codebase_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-codebase_reconcile_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-codebase_rescan_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-codebase_sync_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-documentation_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `archive/batch/submit-documentation_validation_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-00_master_docs_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-10_execution_scaffold_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-approve-step.bat` | outbound | markdown | automation / entrypoint |
| `run-daemon.bat` | outbound | markdown | automation / entrypoint |
| `run-reset-step.bat` | outbound | markdown | automation / entrypoint |
| `sample-run-delivery.bat` | outbound | markdown | automation / entrypoint |
| `scripts/approve-run.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/approve-run.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-delivery-planning.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-delivery-scaffold.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-image-csv-gen-v1.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-image-csv-gen-v2.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-initiative-intake.sh` | outbound | markdown | automation / entrypoint |
| `scripts/examples/submit-task-execution.sh` | outbound | markdown | automation / entrypoint |
| `scripts/README.md` | outbound | markdown | automation / entrypoint |
| `scripts/submit-delivery-planning.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-delivery-scaffold.sh` | outbound | markdown | automation / entrypoint |
| `scripts/submit-initiative-intake.sh` | outbound | markdown | automation / entrypoint |
| `scripts/ukbe-daemon-wsl.sh` | outbound | markdown | automation / entrypoint |
| `scripts/ukbe-daemon.bat` | outbound | markdown | automation / entrypoint |
| `scripts/ukbe-run-delivery.bat` | outbound | markdown | automation / entrypoint |
| `scripts/ukbe-runner.sh` | outbound | markdown | automation / entrypoint |
| `submit-00_master_docs_bootstrap_v1.bat` | outbound | markdown | automation / entrypoint |
| `submit-10_execution_scaffold_v1.bat` | outbound | markdown | automation / entrypoint |
| `sync-10_execution_scaffold_v1-workflow-spec.bat` | outbound | markdown | automation / entrypoint |
| `sync-workflows-to-backend.bat` | outbound | markdown | automation / entrypoint |
| `test-runner.bat` | outbound | markdown | automation / entrypoint |

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
| 2026-07-02 | Initial baseline generated from repository scan | 42 modules/files | 00_master_docs_bootstrap_v1 |
