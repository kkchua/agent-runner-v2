---
title: "Operator Console — Universal Workflow Launcher"
version: "2.0.0"
status: "draft"
created: "2026-07-23"
author: "human + agent"
supersedes: "1.0.0 (phase-per-workflow approach)"
---

# Operator Console — Universal Workflow Launcher

## 1. Problem Statement

The project has **34 per-workflow batch files** (21 `run-*.bat` + 13 `submit-*.bat`)
at the repository root. Each batch file is a near-identical copy-paste that differs
only in:

| What varies | Example |
|---|---|
| Workflow name | `sdlc_10_requirement_v1` |
| Input artifact keys | `INIT_FILE`, `PLAN_FILE`, `BACKLOG_FILE` + `WORK_ITEM`, … |
| Input file source directory | `delivery/00_initiatives/`, `delivery/20_plans/`, … |
| Run-specific settings | `JOB_ID`, `MODE`, `NEW_JOB`, `DRY_RUN` |
| Submit-specific settings | `WORKER_LABEL`, `CODER`, `INITIATIVE_ID` |

**Pain points:**
- Every repo that uses agent-runner-v2 must duplicate all 34 batch files.
- Adding a new workflow requires creating 2 new batch files + copying the template.
- Input artifact paths are hardcoded in each batch file — changing the directory
  structure means editing 20+ files.
- No validation feedback beyond "file not found" — the user must manually check
  that the correct file is selected for the correct workflow.

## 2. Goal

Replace all per-workflow batch files with the **Operator Console** (Flet desktop GUI)
as the single universal launcher. The console will:

1. **Dynamically detect** each workflow's input requirements from `workflow.toml`.
2. **Generate input fields** on the fly — file pickers for file artifacts, text
   fields for scalar values.
3. **Support both submit** (backend queue) **and run** (local execution) modes.
4. **Work from any repo** — no per-repo batch file duplication needed.

## 3. Current Architecture

### 3.1 Operator Console (existing)

```
operator_console/
├── app.py                 # Flet UI: repo/workflow dropdowns, action execution
├── config.py              # ConsoleConfig loader (repos + workflows)
├── models.py              # RepoEntry, WorkflowEntry, GlobalSettings
└── services/
    ├── backend_service.py # Backend API calls (list/stop/approve runs)
    └── runner_service.py  # Local runner invocations (submit, approve, init, sync)
```

**Existing actions:** submit job, approval, cancel job, reset step, bootstrap, init,
sync, cleanup.

**New actions (simplified):** Run, Submit, Approve, Reject, Reset, Cancel.

**Current `submit_job()` in `runner_service.py`:**
```python
def submit_job(self, *, repo_path, workflow, initiative_id="", coder=""):
    args = ["--workflow-name", workflow.workflow_name]
    if initiative_id:
        args.extend(["--initiative-id", initiative_id])
    if coder:
        args.extend(["--coder", coder])
    # ... backend-url, worker-id, worker-label
    return self._invoke(repo_path=repo_path, func=submit_commands.main, argv=args)
```

**Missing:** No `--input KEY=VALUE` flags are passed. The existing file picker
(`ft.FilePicker`) is in the UI but not wired to the submit flow.

### 3.2 Workflow Input Declarations (existing)

Each workflow's `workflow.toml` already declares its input requirements in the
init step's `[step.artifacts] required_inputs`:

| Workflow | Init Step | required_inputs |
|---|---|---|
| sdlc_00_init_doc_v1 | generate_initiative | `DRAFT_INIT_FILE` |
| sdlc_10_requirement_v1 | generate_requirements | `INIT_FILE` |
| sdlc_20_planning_v1 | generate_plan | `REQ_FILE` |
| sdlc_30_backlog_v1 | generate_backlog | `PLAN_FILE` |
| sdlc_40_task_v1 | generate_task | `BACKLOG_FILE` |
| sdlc_50_implementation_v1 | generate_implementation | `TASK_FILE` |
| sdlc_60_execution_v1 | execute_task | `IMPL_FILE` |
| sdlc_70_validation_v1 | generate_validation | `EXEC_FILE` |
| sdlc_80_review_v1 | generate_review | `VAL_FILE` |
| sdlc_00_codebase_v1 | create_backup | *(none — self-contained)* |
| 00_bootstrap_lifecycle_admin_v1 | *(no init_step)* | *(none)* |

**Additional non-file inputs:**
- `sdlc_40_task_v1` also accepts `WORK_ITEM` (a string ID, not a file path).

### 3.3 Batch File Input Pattern (what we're replacing)

Each submit batch file follows this pattern:
```batch
REM User edits filename only:
set "INIT_FILE=INIT-20260722-001_console-sdlc10-support.md"

REM Batch resolves to full path using hardcoded directory:
set "INIT_PATH=%~dp0docs\repo\agent_runner\sdlc\delivery\00_initiatives\!INIT_FILE!"

REM Validates existence:
if not exist "!INIT_PATH!" ( echo ERROR ... & exit /b 1 )

REM Passes as --input flag:
ukbe-run-agent submit --workflow-name sdlc_10_requirement_v1 --input INIT_FILE=!INIT_PATH!
```

Each run batch file follows the same pattern but uses `--set` instead of `--input`:
```batch
ukbe-run-agent run --template-group sdlc_10_requirement_v1 --set INIT_FILE=!INIT_PATH!
```

### 3.4 SDLC Delivery Directory Structure

All SDLC input artifacts live under a known base path:
```
SDLC_DELIVERY_BASE = "docs/repo/agent_runner/sdlc/delivery"
```

| Artifact Key | Subdirectory |
|---|---|
| DRAFT_INIT_FILE | `00_draft_initiatives/` |
| INIT_FILE | `00_initiatives/` |
| REQ_FILE | `10_requirements/` |
| PLAN_FILE | `20_plans/` |
| BACKLOG_FILE | `30_backlogs/` |
| TASK_FILE | `40_tasks/` |
| IMPL_FILE | `50_implementations/` |
| EXEC_FILE | `60_executions/` |
| VAL_FILE | `70_validations/` |

This mapping is already defined in `sdlc_00_delivery_scaffold_v1/context_extensions.py`
(lines 60-72) and `constants.py` (`SDLC_DELIVERY_BASE`).

## 4. Solution Design

### 4.1 Dynamic Input Detection

When the user selects a workflow in the console, the app will:

1. Load the workflow's `workflow.toml` using the existing
   `load_workflow_package(bundle_dir)` function (from `workflow_packages/loader.py`).
2. Find the init step (declared in `[workflow] init_step = "..."`).
3. Read that step's `[step.artifacts] required_inputs` list.
4. For each required input key, determine the field type:
   - Key ends with `_FILE` → **File input** (TextField + Browse button)
   - Otherwise → **Text input** (plain TextField)
5. Rebuild the dynamic input panel in the UI.

**Reuse:** `load_workflow_package()` is already used by `refresh_step_options()` in
the existing `app.py` (line ~330). Same pattern.

### 4.2 Dynamic Input Panel — UI Component Design

The dynamic input panel is a `ft.Container` with a `ft.Column` inside, placed
between the Active Runs section and the Submit Options section. It is rebuilt
from scratch every time the workflow selection changes.

#### 4.2.1 Panel Structure

```
┌─ Workflow Inputs ──────────────────────────────────────────────┐
│                                                                 │
│  DRAFT_INIT_FILE:                                               │
│  [                                    ] [Browse]               │
│                                                                 │
│  INIT_FILE:                                                     │
│  [INIT-20260722-001_console-sdlc10.md ] [Browse]               │
│                                                                 │
│  WORK_ITEM:                                                     │
│  [WI-20260723-001_console-sdlc10-support-02           ]        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Each input key gets its own row:
- **Label** — the artifact key name (e.g. `INIT_FILE`) rendered as a `ft.Text`
  above the input control.
- **File input** (`_FILE` keys) — a `ft.Row` containing:
  - `ft.TextField` (read-only, expand=True) — shows the selected file path or
    a manually typed filename.
  - `ft.ElevatedButton("Browse")` — opens the shared `ft.FilePicker`.
- **Text input** (non-`_FILE` keys) — a `ft.TextField` (editable, expand=True)
  for free-form text entry.

#### 4.2.2 Shared File Picker

The app already has a single `ft.FilePicker` instance (`file_picker` in `app.py`).
This is reused for all dynamic file inputs. The browse callback uses a closure
to track which TextField to update:

```python
# State: maps artifact key → its TextField control
_input_fields: dict[str, ft.TextField] = {}
_active_browse_key: str = ""   # which key the file picker is browsing for

async def on_browse(key: str, target_tf: ft.TextField):
    """Browse button clicked — open file picker for the given key."""
    _active_browse_key = key
    files = await file_picker.pick_files(
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["md"],
    )
    if files:
        target_tf.value = files[0].path or ""
        page.update()

def on_file_picked(e: ft.FilePickerResultEvent):
    """Fallback handler if using on_result instead of pick_files await."""
    if e.files and _active_browse_key in _input_fields:
        _input_fields[_active_browse_key].value = e.files[0].path
        page.update()
```

#### 4.2.3 Rebuild Logic

```python
def rebuild_input_fields(workflow_entry: WorkflowEntry) -> None:
    """Rebuild the dynamic input panel for the selected workflow."""
    _input_fields.clear()
    dynamic_inputs_column.controls.clear()

    repo_path = Path(selected_repo_path())
    bundle_dir = repo_path / "workflows" / workflow_entry.workflow_name

    if not bundle_dir.exists():
        dynamic_inputs_column.controls.append(
            ft.Text(f"Workflow directory not found: {bundle_dir}", color="red")
        )
        page.update()
        return

    try:
        bundle = load_workflow_package(bundle_dir)
    except Exception as exc:
        dynamic_inputs_column.controls.append(
            ft.Text(f"Failed to load workflow: {exc}", color="red")
        )
        page.update()
        return

    # Find init step's required_inputs
    init_step_name = bundle.init_step
    if not init_step_name or init_step_name not in bundle.steps:
        dynamic_inputs_column.controls.append(
            ft.Text("No input artifacts required.", italic=True, color="grey")
        )
        page.update()
        return

    init_step = bundle.steps[init_step_name]
    required_inputs = init_step.artifacts.get("required_inputs", [])

    if not required_inputs:
        dynamic_inputs_column.controls.append(
            ft.Text("No input artifacts required.", italic=True, color="grey")
        )
        page.update()
        return

    for key in required_inputs:
        if key.endswith("_FILE"):
            tf = ft.TextField(
                label=key,
                read_only=False,   # allow manual filename entry
                expand=True,
                hint_text=f"Filename or browse for {key}",
            )
            btn = ft.ElevatedButton(
                "Browse",
                on_click=lambda e, k=key, f=tf: on_browse(k, f),
            )
            _input_fields[key] = tf
            dynamic_inputs_column.controls.append(
                ft.Column([
                    ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                    ft.Row([tf, btn], spacing=8),
                ], spacing=4)
            )
        else:
            tf = ft.TextField(
                label=key,
                expand=True,
                hint_text=f"Enter {key}",
            )
            _input_fields[key] = tf
            dynamic_inputs_column.controls.append(
                ft.Column([
                    ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                    ft.Row([tf], spacing=8),
                ], spacing=4)
            )

    page.update()
```

**Key design decisions:**
- File input TextFields are **not** read-only — the user can type a filename
  directly (for auto-resolve) or use Browse to pick a file (sets full path).
- The `_input_fields` dict is the single source of truth for collecting values
  at submit/run time.
- The panel is fully rebuilt on workflow change — old controls are discarded,
  new ones created. No stale state.

#### 4.2.4 Empty State

When a workflow has no `init_step`, no `required_inputs`, or the workflow
directory doesn't exist, the panel shows a grey italic message:
*"No input artifacts required."* or an error in red. The panel container
remains visible (to avoid layout jumps) but contains no interactive controls.

### 4.3 File Resolution Strategy

When the user clicks "Run Action", the console collects values from
`_input_fields` and resolves each to an absolute path before passing to
the CLI.

#### 4.3.1 Resolution Logic

```python
def resolve_input_path(key: str, value: str, repo_path: Path) -> str:
    """Resolve an input value to an absolute path.

    - If value is an existing absolute path → return as-is.
    - If value is a filename and key is in SDLC_INPUT_DIRS → resolve against
      the known delivery subdirectory.
    - If resolved path doesn't exist → raise ActionExecutionError.
    """
    value = value.strip()
    if not value:
        return ""

    # Already an absolute path?
    p = Path(value)
    if p.is_absolute() and p.exists():
        return str(p)

    # Try auto-resolve from known SDLC directory
    if key in SDLC_INPUT_DIRS:
        resolved = repo_path / SDLC_INPUT_DIRS[key] / value
        if resolved.exists():
            return str(resolved)
        raise ActionExecutionError(
            f"File not found for {key}: {value}\n"
            f"  Tried: {resolved}\n"
            f"  Expected in: {SDLC_INPUT_DIRS[key]}/"
        )

    # Non-file input or unknown key — return as-is (text value)
    if not key.endswith("_FILE"):
        return value

    # File input but can't resolve
    raise ActionExecutionError(
        f"Cannot resolve file path for {key}: {value}\n"
        f"  Provide a full path or browse for the file."
    )
```

#### 4.3.2 Collection at Submit/Run Time

```python
def collect_input_artifacts(repo_path: Path) -> dict[str, str]:
    """Collect and resolve all dynamic input field values."""
    result = {}
    for key, tf in _input_fields.items():
        value = (tf.value or "").strip()
        if not value:
            continue   # skip empty fields
        resolved = resolve_input_path(key, value, repo_path)
        result[key] = resolved
    return result
```

#### 4.3.3 SDLC Input Directory Mapping

```python
SDLC_INPUT_DIRS = {
    "DRAFT_INIT_FILE": "docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives",
    "INIT_FILE":       "docs/repo/agent_runner/sdlc/delivery/00_initiatives",
    "REQ_FILE":        "docs/repo/agent_runner/sdlc/delivery/10_requirements",
    "PLAN_FILE":       "docs/repo/agent_runner/sdlc/delivery/20_plans",
    "BACKLOG_FILE":    "docs/repo/agent_runner/sdlc/delivery/30_backlogs",
    "TASK_FILE":       "docs/repo/agent_runner/sdlc/delivery/40_tasks",
    "IMPL_FILE":       "docs/repo/agent_runner/sdlc/delivery/50_implementations",
    "EXEC_FILE":       "docs/repo/agent_runner/sdlc/delivery/60_executions",
    "VAL_FILE":        "docs/repo/agent_runner/sdlc/delivery/70_validations",
}
```

This is the same mapping already used by all batch files and
`context_extensions.py`. Sourced from `SDLC_DELIVERY_BASE` in `constants.py`.

### 4.3 Actions: Run and Submit

Add a new action `"Run"` to the actions dropdown. This executes the
workflow locally (same as the `run-*.bat` files), as opposed to `"Submit"`
which sends it to the backend queue.

**Run-specific UI controls:** None. All run parameters use fixed defaults:
`MODE=manual`, `JOB_NO=` (empty), `NEW_JOB=false`, `DRY_RUN=false`.
The user only fills in the dynamic input fields from workflow.toml.

**Shared controls** (visible for both submit and run):

| Control | Type | Maps to |
|---|---|---|
| Dynamic input fields | File/Text | `--input` (submit) or `--set` (run) |

### 4.4 Data Flow

#### Submit Flow (action = "Submit", backend queue)
```
User selects workflow → dynamic fields appear
User fills in inputs (browse or type filename)
User clicks "Run Action" (action = "Submit")
    ↓
Console resolves filenames → absolute paths
Console calls runner_service.submit_job(
    workflow=...,
    input_artifacts={"INIT_FILE": "/abs/path/to/INIT.md"},
)
    ↓
runner_service builds argv:
    --workflow-name sdlc_10_requirement_v1
    --input INIT_FILE=/abs/path/to/INIT.md
    --backend-url ... --worker-label ...
    ↓
submit_commands.main(argv) → POST to backend
    ↓
Backend queues job → daemon picks up → daemon converts --input to --set
    → spawns run_agent subprocess
```

#### Run Flow (action = "Run", local execution)
```
User selects workflow → dynamic fields appear
User fills in input artifacts
User clicks "Run Action" (action = "Run")
    ↓
Console resolves filenames → absolute paths
Console calls runner_service.run_workflow(
    workflow=...,
    input_artifacts={"INIT_FILE": "/abs/path/to/INIT.md"},
)
    ↓
runner_service builds argv (with fixed defaults):
    run --template-group sdlc_10_requirement_v1
    --mode manual
    --set INIT_FILE=/abs/path/to/INIT.md
    ↓
run_agent.main(argv) → local execution
```

## 5. UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Agent Runner Operator Console                                   │
│  Choose a repository and its workflow.                           │
├─────────────────────────────────────────────────────────────────┤
│  [Repo: agent-runner-v2 ▼]   [Workflow: SDLC Requirement ▼]    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Selected: agent-runner-v2 / SDLC Requirement            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Backend: http://... | Worker: worker-1                         │
│                                                                  │
│  [Action: Run ▼]                                              │
│  [Refresh Active Runs] [Run Action]                              │
│                                                                  │
│  ┌─ Active Runs ────────────────────────────────────────────┐   │
│  │ [SDLC10REQ-20260723-abc | RUNNING | generate_requirements]│  │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─ Workflow Inputs ────────────────────────────────────────┐   │
│  │ INIT_FILE: [INIT-20260722-001_console-sdlc10.md] [Browse]│  │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [Reset Target Step ▼]                                          │
│  Feedback/Reason: [________________________________]            │
│                                                                  │
│  ┌─ Output ─────────────────────────────────────────────────┐   │
│  │ {"status": "submitted", "run_id": "...", ...}             │  │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Visibility Rules

| UI Section | Visible When |
|---|---|
| Workflow Inputs (dynamic) | A workflow is selected (any action) |
| Active Runs + Feedback | Action = "Approve", "Reject", "Reset", or "Cancel" |
| Reset Target Step | Action = "Reset" |

## 6. Implementation Plan

### 6.1 Files to Modify

| File | Change |
|---|---|
| `operator_console/app.py` | Dynamic input panel, "run workflow" action, visibility logic |
| `operator_console/services/runner_service.py` | Extend `submit_job()`, add `run_workflow()` |

No changes to `models.py`, `config.py`, `backend_service.py`, or any core runner
modules.

### 6.2 Step-by-Step

#### Step 1: Add artifact-to-directory mapping constant

Add a constant dict in `app.py` (or a new `console_constants.py`) mapping artifact
keys to their SDLC delivery subdirectories:

```python
SDLC_INPUT_DIRS = {
    "DRAFT_INIT_FILE": "docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives",
    "INIT_FILE":       "docs/repo/agent_runner/sdlc/delivery/00_initiatives",
    "REQ_FILE":        "docs/repo/agent_runner/sdlc/delivery/10_requirements",
    "PLAN_FILE":       "docs/repo/agent_runner/sdlc/delivery/20_plans",
    "BACKLOG_FILE":    "docs/repo/agent_runner/sdlc/delivery/30_backlogs",
    "TASK_FILE":       "docs/repo/agent_runner/sdlc/delivery/40_tasks",
    "IMPL_FILE":       "docs/repo/agent_runner/sdlc/delivery/50_implementations",
    "EXEC_FILE":       "docs/repo/agent_runner/sdlc/delivery/60_executions",
    "VAL_FILE":        "docs/repo/agent_runner/sdlc/delivery/70_validations",
}
```

#### Step 2: Dynamic input field generation

Add `rebuild_input_fields()` function that:
1. Loads the selected workflow's bundle via `load_workflow_package()`.
2. Reads `init_step` → `required_inputs`.
3. Creates `TextField` + optional `Browse` button per input key.
4. Clears and repopulates `dynamic_inputs_container`.

Wire into `on_workflow_changed()` so fields rebuild on workflow selection.

#### Step 3: File resolution helper

Add `resolve_input_path(key, value, repo_path)` function:
- If `value` is an existing absolute path → return as-is.
- If `value` is a filename and `key` is in `SDLC_INPUT_DIRS` → resolve against
  `repo_path / SDLC_INPUT_DIRS[key] / value`.
- If resolved path doesn't exist → raise error with helpful message.

#### Step 4: Extend `RunnerActionService`

**Modify `submit_job()`:**
```python
def submit_job(self, *, repo_path, workflow, input_artifacts=None):
    args = ["--workflow-name", workflow.workflow_name]
    args.extend(["--backend-url", self._settings.backend_url])
    if self._settings.worker_id:
        args.extend(["--worker-id", self._settings.worker_id])
    if self._settings.worker_label:
        args.extend(["--worker-label", self._settings.worker_label])
    if input_artifacts:
        for key, value in input_artifacts.items():
            args.extend(["--input", f"{key}={value}"])
    return self._invoke(...)
```

**Add `run_workflow()`:**
```python
def run_workflow(self, *, repo_path, workflow, input_artifacts=None):
    args = ["run", "--template-group", workflow.workflow_name,
            "--mode", "manual"]
    if input_artifacts:
        for key, value in input_artifacts.items():
            args.extend(["--set", f"{key}={value}"])
    return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)
```

#### Step 5: Wire "Run" and update action handlers in `execute_action()`

Update the `execute_action()` function:
- Rename `"submit job"` → `"Submit"` — calls `runner_service.submit_job()`.
- Add `"Run"` — calls `runner_service.run_workflow()`.
- Split `"approval"` → `"Approve"` and `"Reject"`:
  - `"Approve"` — same as old approval without reject flag.
  - `"Reject"` — same as old approval with reject flag + feedback.
- Rename `"reset step"` → `"Reset"`.
- Rename `"cancel job"` → `"Cancel"`.
- Remove `"bootstrap"`, `"init"`, `"sync"`, `"cleanup"`.

#### Step 6: Update visibility logic

Update `update_visibility()` for the 6 new actions:
- **Run, Submit** — show workflow inputs only.
- **Approve, Reject** — show active runs + feedback field.
- **Reset** — show active runs + feedback + reset target step dropdown.
- **Cancel** — show active runs + feedback (reason for cancellation).

## 7. Non-SDLC Workflow Support

The dynamic input detection works for **any** workflow, not just SDLC:

- **No required_inputs** (e.g. `sdlc_00_codebase_v1`, bootstrap workflows) →
  the input panel shows "No input artifacts required" or is hidden.
- **Workflows with non-file inputs** → text fields are shown.
- **Workflows with custom input keys** → fields are generated from whatever
  `required_inputs` declares.

## 8. Migration Plan

### Phase 1: Console parity (this plan)
- Implement dynamic inputs + run action in the console.
- Test with all SDLC workflows.
- Keep batch files as fallback.

### Phase 2: Batch file deprecation
- Once the console is verified, mark batch files as deprecated.
- Add a note in each batch file pointing to the console.
- Do NOT delete batch files immediately — they serve as documentation and
  fallback for headless/CI usage.

### Phase 3: Cleanup (future)
- Remove batch files from new repo setups.
- Update documentation to reference the console as the primary launcher.
- Keep `ukbe-run-agent run` and `ukbe-run-agent submit` CLI commands as the
  programmatic interface (for CI/CD, scripts, daemon).

## 9. Verification

### Manual Testing Checklist

1. **Launch console:** `ukbe-run-agent console`
2. **Dynamic fields — SDLC workflow:**
   - Select `sdlc_10_requirement_v1` → verify `INIT_FILE` field appears with Browse.
   - Select `sdlc_40_task_v1` → verify `BACKLOG_FILE` (file) + `WORK_ITEM` (text) appear.
   - Select `sdlc_00_codebase_v1` → verify no input fields (or "none required" message).
3. **File browse:**
   - Click Browse on INIT_FILE → select a .md file → verify full path appears.
4. **Filename auto-resolve:**
   - Type a filename in INIT_FILE → submit → verify it resolves to the correct directory.
5. **Submit:**
   - Select "Submit" action → fill in INIT_FILE → click Run Action → verify
     `--input INIT_FILE=...` appears in the output.
6. **Run:**
   - Select "Run" action → fill INIT_FILE → click Run Action → verify
     `--mode manual` and `--set INIT_FILE=...` in the output.
7. **Approve / Reject:**
   - Select "Approve" → verify active runs listed → select a run → click Run Action.
   - Select "Reject" → enter feedback → click Run Action → verify rejection.
8. **Reset:**
   - Select "Reset" → verify reset target step dropdown populated → select step → click Run Action.
9. **Cancel:**
   - Select "Cancel" → verify active runs listed → select a run → enter reason → click Run Action.
10. **Switch workflows:**
   - Change workflow selection → verify old fields are cleared and new fields appear.
11. **Non-SDLC workflow:**
    - Select `00_bootstrap_lifecycle_admin_v1` → verify no input fields needed.

### Edge Cases

- Workflow has no `init_step` → no input fields shown.
- Init step has no `required_inputs` → no input fields shown.
- User submits without filling required file inputs → validation error.
- File path doesn't exist → error message with the attempted path.
- Workflow not found in `workflows/` directory → error loading bundle.
