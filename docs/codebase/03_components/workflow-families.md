---
title: "Component Documentation: workflow families"
template_id: "CB-03"
status: "active"
component_id: "workflow-families"
created: "2026-07-04T13:29:07+08:00"
owner: "40_documentation_sync_v1"
last_verified_by_change: "40_documentation_sync_v1 / 40DOCSYNC-GEN-20260704-001 / 2026-07-04T13:29:07+08:00"
modules: ["00_master_docs_bootstrap_v1", "10_execution_scaffold_v1", "20_initiative_intake_v1", "21_bug_fix_intake_v1", "30_delivery_planning_v1", "31_task_execution_v1", "40_documentation_sync_v1", "50_architecture_site_v1", "image_csv_gen_v2", "videoxpress_gen_v1", "tiktok_video_pipeline_v1"]
---

# Component Documentation: workflow families

## 1. Component Overview

### 1.1 Purpose

Repository workflow families, their step sequences, and their current bootstrap/runtime contracts.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `00_master_docs_bootstrap_v1` | 00DOC / 10 steps |
| `10_execution_scaffold_v1` | 10SCAFFOLD / 13 steps |
| `20_initiative_intake_v1` | 20PREINIT / 5 steps |
| `21_bug_fix_intake_v1` | 21BUGFIX / 7 steps |
| `30_delivery_planning_v1` | 30PLAN / 10 steps |
| `31_task_execution_v1` | 31EXEC / 12 steps |
| `40_documentation_sync_v1` | 40DOCSYNC / 2 steps |
| `50_architecture_site_v1` | 50SITE / 2 steps |
| `image_csv_gen_v2` | IMGCSV / 3 steps |
| `videoxpress_gen_v1` | VIDEXP / 9 steps |
| `tiktok_video_pipeline_v1` | TIKTOK / 10 steps |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `00_master_docs_bootstrap_v1` | outbound | markdown | 00DOC / 10 steps |
| `10_execution_scaffold_v1` | outbound | markdown | 10SCAFFOLD / 13 steps |
| `20_initiative_intake_v1` | outbound | markdown | 20PREINIT / 5 steps |
| `21_bug_fix_intake_v1` | outbound | markdown | 21BUGFIX / 7 steps |
| `30_delivery_planning_v1` | outbound | markdown | 30PLAN / 10 steps |
| `31_task_execution_v1` | outbound | markdown | 31EXEC / 12 steps |
| `40_documentation_sync_v1` | outbound | markdown | 40DOCSYNC / 2 steps |
| `50_architecture_site_v1` | outbound | markdown | 50SITE / 2 steps |
| `image_csv_gen_v2` | outbound | markdown | IMGCSV / 3 steps |
| `videoxpress_gen_v1` | outbound | markdown | VIDEXP / 9 steps |
| `tiktok_video_pipeline_v1` | outbound | markdown | TIKTOK / 10 steps |

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
| 2026-07-04 | Initial baseline generated from repository scan | 11 modules/files | 40_documentation_sync_v1 |
