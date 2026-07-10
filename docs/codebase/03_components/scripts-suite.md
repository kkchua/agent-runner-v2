---
title: "Component Documentation: scripts suite"
template_id: "CB-03"
status: "active"
component_id: "scripts-suite"
created: "2026-07-10T14:00:58+08:00"
owner: "00_master_docs_bootstrap_v2"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-GEN-20260710-004 / 2026-07-10T14:00:58+08:00"
modules: ["archive/batch/run-bug_fix_v1.bat", "archive/batch/run-codebase_bootstrap_v1.bat", "archive/batch/run-codebase_reconcile_v1.bat", "archive/batch/run-codebase_rescan_v1.bat", "archive/batch/run-codebase_sync_v1.bat", "archive/batch/run-documentation_bootstrap_v1.bat", "archive/batch/run-documentation_validation_v1.bat", "archive/batch/run-system_docs_bootstrap_v1.bat", "archive/batch/submit-bug_fix_v1.bat", "archive/batch/submit-codebase_bootstrap_v1.bat", "archive/batch/submit-codebase_reconcile_v1.bat", "archive/batch/submit-codebase_rescan_v1.bat", "archive/batch/submit-codebase_sync_v1.bat", "archive/batch/submit-documentation_bootstrap_v1.bat", "archive/batch/submit-documentation_validation_v1.bat", "run-00_master_docs_bootstrap_v1.bat", "run-00_master_docs_bootstrap_v2.bat", "run-10_execution_scaffold_v1.bat", "run-20_initiative_intake_v1.bat", "run-21_bug_fix_intake_v1.bat", "run-30_delivery_planning_v1.bat", "run-31_task_execution_v1.bat", "run-40_documentation_sync_v1.bat", "run-41_developer_doc_v1.bat", "run-41_operator_doc_v1.bat", "run-41_stakeholder_doc_v1.bat", "run-41_tester_doc_v1.bat", "run-41_user_doc_v1.bat", "run-50_architecture_site_v1.bat", "run-51_stakeholder_docs_v1.bat", "run-52_developer_docs_v1.bat", "run-53_operator_docs_v1.bat", "run-54_tester_docs_v1.bat", "run-55_user_docs_v1.bat", "run-all-tests.bat", "run-approve-step.bat", "run-bootstrap-publish.bat", "run-cleanup-generated-docs.bat", "run-daemon.bat", "run-integration-tests.bat", "run-reset-step.bat", "run-tests.bat", "sample-run-delivery.bat", "scripts/approve-run.sh", "scripts/examples/approve-run.sh", "scripts/examples/submit-delivery-planning.sh", "scripts/examples/submit-delivery-scaffold.sh", "scripts/examples/submit-image-csv-gen-v1.sh", "scripts/examples/submit-image-csv-gen-v2.sh", "scripts/examples/submit-initiative-intake.sh", "scripts/examples/submit-task-execution.sh", "scripts/README.md", "scripts/submit-delivery-planning.sh", "scripts/submit-delivery-scaffold.sh", "scripts/submit-initiative-intake.sh", "scripts/ukbe-daemon-wsl.sh", "scripts/ukbe-daemon.bat", "scripts/ukbe-run-delivery.bat", "scripts/ukbe-runner.sh", "submit-00_master_docs_bootstrap_v1.bat", "submit-10_execution_scaffold_v1.bat", "submit-40_documentation_sync_v1.bat", "submit-41_audience_doc_v1.bat", "sync-10_execution_scaffold_v1-workflow-spec.bat", "sync-workflows-to-backend.bat", "test-runner.bat"]
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
| `run-00_master_docs_bootstrap_v2.bat` | automation / entrypoint |
| `run-10_execution_scaffold_v1.bat` | automation / entrypoint |
| `run-20_initiative_intake_v1.bat` | automation / entrypoint |
| `run-21_bug_fix_intake_v1.bat` | automation / entrypoint |
| `run-30_delivery_planning_v1.bat` | automation / entrypoint |
| `run-31_task_execution_v1.bat` | automation / entrypoint |
| `run-40_documentation_sync_v1.bat` | automation / entrypoint |
| `run-41_developer_doc_v1.bat` | automation / entrypoint |
| `run-41_operator_doc_v1.bat` | automation / entrypoint |
| `run-41_stakeholder_doc_v1.bat` | automation / entrypoint |
| `run-41_tester_doc_v1.bat` | automation / entrypoint |
| `run-41_user_doc_v1.bat` | automation / entrypoint |
| `run-50_architecture_site_v1.bat` | automation / entrypoint |
| `run-51_stakeholder_docs_v1.bat` | automation / entrypoint |
| `run-52_developer_docs_v1.bat` | automation / entrypoint |
| `run-53_operator_docs_v1.bat` | automation / entrypoint |
| `run-54_tester_docs_v1.bat` | automation / entrypoint |
| `run-55_user_docs_v1.bat` | automation / entrypoint |
| `run-all-tests.bat` | automation / entrypoint |
| `run-approve-step.bat` | automation / entrypoint |
| `run-bootstrap-publish.bat` | automation / entrypoint |
| `run-cleanup-generated-docs.bat` | automation / entrypoint |
| `run-daemon.bat` | automation / entrypoint |
| `run-integration-tests.bat` | automation / entrypoint |
| `run-reset-step.bat` | automation / entrypoint |
| `run-tests.bat` | automation / entrypoint |
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
| `submit-40_documentation_sync_v1.bat` | automation / entrypoint |
| `submit-41_audience_doc_v1.bat` | automation / entrypoint |
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
| `run-00_master_docs_bootstrap_v2.bat` | outbound | markdown | automation / entrypoint |
| `run-10_execution_scaffold_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-20_initiative_intake_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-21_bug_fix_intake_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-30_delivery_planning_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-31_task_execution_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-40_documentation_sync_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-41_developer_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-41_operator_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-41_stakeholder_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-41_tester_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-41_user_doc_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-50_architecture_site_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-51_stakeholder_docs_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-52_developer_docs_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-53_operator_docs_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-54_tester_docs_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-55_user_docs_v1.bat` | outbound | markdown | automation / entrypoint |
| `run-all-tests.bat` | outbound | markdown | automation / entrypoint |
| `run-approve-step.bat` | outbound | markdown | automation / entrypoint |
| `run-bootstrap-publish.bat` | outbound | markdown | automation / entrypoint |
| `run-cleanup-generated-docs.bat` | outbound | markdown | automation / entrypoint |
| `run-daemon.bat` | outbound | markdown | automation / entrypoint |
| `run-integration-tests.bat` | outbound | markdown | automation / entrypoint |
| `run-reset-step.bat` | outbound | markdown | automation / entrypoint |
| `run-tests.bat` | outbound | markdown | automation / entrypoint |
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
| `submit-40_documentation_sync_v1.bat` | outbound | markdown | automation / entrypoint |
| `submit-41_audience_doc_v1.bat` | outbound | markdown | automation / entrypoint |
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
| 2026-07-10 | Initial baseline generated from repository scan | 66 modules/files | 00_master_docs_bootstrap_v2 |
