---
title: "Operator Console SDLC Workflow Support Plan"
version: "1.0.0"
status: "draft"
created: "2026-07-22"
author: "human"
---

# Operator Console SDLC Workflow Support Plan

## Goal

Enable the operator console (Flet desktop GUI) to support SDLC workflow
job submission and monitoring, workflow by workflow. Each SDLC workflow
has specific input requirements that the console must handle.

## Strategy

- Implement support one workflow at a time, starting with sdlc_10.
- Each workflow gets its own draft initiative, fed through the SDLC
  pipeline to develop and test the feature.
- The SDLC workflow chain is used to implement the console app features
  (test-driving the SDLC process on a real internal tool).

## Feature List

### Phase 1: sdlc_10_requirement_v1 (Initiative Intake)

**Console requirements:**
- File picker for DRAFT_INIT_FILE (user selects a draft initiative file)
- Submit job with the selected file path as input artifact
- Display submission result

**Input:** DRAFT_INIT_FILE (file path selected by user)
**Output:** INIT_FILE (approved initiative document)

### Phase 2: sdlc_20_planning_v1 (Planning)

**Console requirements:**
- Dropdown or file picker to select an approved INIT_FILE
- Submit job with INIT_FILE as input
- Display generated REQ_FILE location

**Input:** INIT_FILE (approved, from sdlc_10 output)
**Output:** REQ_FILE (requirements document)

### Phase 3: sdlc_30_backlog_v1 (Backlog)

**Console requirements:**
- Dropdown or file picker to select an approved REQ_FILE
- Submit job with REQ_FILE as input
- Display generated PLAN_FILE location

**Input:** REQ_FILE (approved)
**Output:** PLAN_FILE (plan document)

### Phase 4: sdlc_40_task_v1 (Task)

**Console requirements:**
- Dropdown or file picker to select an approved PLAN_FILE
- Submit job with PLAN_FILE as input
- Display generated BACKLOG_FILE location

**Input:** PLAN_FILE (approved)
**Output:** BACKLOG_FILE (backlog document)

### Phase 5: sdlc_50_implementation_v1 (Implementation Planning)

**Console requirements:**
- Dropdown or file picker to select an approved BACKLOG_FILE
- Submit job with BACKLOG_FILE as input
- Display generated TASK_FILE location

**Input:** BACKLOG_FILE (approved)
**Output:** TASK_FILE (task specification)

### Phase 6: sdlc_60_execution_v1 (Execution)

**Console requirements:**
- Dropdown or file picker to select an approved TASK_FILE
- Submit job with TASK_FILE as input
- Display generated IMPL_FILE and code changes

**Input:** TASK_FILE (approved)
**Output:** IMPL_FILE (implementation record) + code changes

### Phase 7: sdlc_70_validation_v1 (Validation)

**Console requirements:**
- Dropdown or file picker to select an approved IMPL_FILE
- Submit job with IMPL_FILE as input
- Display generated VAL_FILE (validation report)

**Input:** IMPL_FILE (approved)
**Output:** VAL_FILE (validation report)

### Phase 8: sdlc_80_review_v1 (Review)

**Console requirements:**
- Dropdown or file picker to select an approved VAL_FILE
- Submit job with VAL_FILE as input
- Display generated REV_FILE, MEM_FILE, CLOSE_FILE

**Input:** VAL_FILE (approved)
**Output:** REV_FILE + MEM_FILE + CLOSE_FILE

## Common UI Components Needed

1. **File picker** -- Browse button + read-only text field showing selected path
2. **Artifact dropdown** -- List approved artifacts from previous workflow runs
3. **Output display** -- Show generated artifact locations after job completion
4. **Workflow-specific input panel** -- Dynamic UI that changes based on selected workflow

## Implementation Notes

- The file picker uses Flet's `ft.FilePicker` component.
- Input artifacts are passed to the backend via `--input KEY=VALUE` in the
  submit command.
- The daemon picks up the job and resolves input artifact paths from the
  `input_payload`.
- Each workflow's `context_extensions.py` resolves the artifact paths to
  absolute paths for prompt rendering.

## Current Status

| Phase | Workflow | Status |
|---|---|---|
| 1 | sdlc_10_requirement_v1 | In progress (draft init created) |
| 2 | sdlc_20_planning_v1 | Not started |
| 3 | sdlc_30_backlog_v1 | Not started |
| 4 | sdlc_40_task_v1 | Not started |
| 5 | sdlc_50_implementation_v1 | Not started |
| 6 | sdlc_60_execution_v1 | Not started |
| 7 | sdlc_70_validation_v1 | Not started |
| 8 | sdlc_80_review_v1 | Not started |
