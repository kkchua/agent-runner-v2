# Workflow Extension Interface — Architecture Plan

| Field | Value |
|-------|-------|
| Status | **Implemented** |
| Layer | Platform (cross-cutting) |
| Scope | All workflow packages |
| Date | 2026-07-22 |
| Implemented | 2026-08-04 |

---

## Problem Statement

The current workflow plugin system has four structural problems:

### 1. No Shared Artifact Key Mechanism

Each SDLC workflow independently defines its own artifact keys as raw
strings in both `workflow.toml` and `output_paths.py`. There is no
mechanism for keys shared across all SDLC workflows (e.g.
`REVIEW_FILE_SUGGESTED` appears in all 9 SDLC workflows with
duplicated path construction logic).

The global `artifact_keys.py` defines constants like
`ARTIFACT_KEY_REQ = "REQ_FILE"` but no workflow imports them — raw
strings are used everywhere.

### 2. Bootstrap Folder Searched at Runtime

`workflow_path_contracts.py:_output_paths_candidates()` searches two
locations for `output_paths.py`:

1. `workflows/<name>/output_paths.py` (repo-local)
2. `agent_runner_v2/bootstrap/workflows/default/<name>/output_paths.py` (bootstrap source)

At runtime, only the global path (`~/.ukbe-runner/workflows/`) should
be searched. The bootstrap source folder is a development-time concern.

### 3. Overly Complex Path Resolution Chain

The current chain has too many layers:

```
output_paths.py           → build_output_paths() returns relative paths
    ↓
context_extensions.py     → imports from output_paths.py, resolves to absolute
    ↓
workflow_path_contracts.py → dynamically loads output_paths.py via importlib
    ↓
step_runner.py            → calls context hook, merges into prompt context
```

Two separate mechanisms resolve paths: `context_extensions.py` for
prompt injection and `workflow_path_contracts.py` for frontmatter
generation. They load `output_paths.py` independently.

### 4. Broken Context Injection in SDLC Workflows

Only `sdlc_10_requirement_v1` imports from `output_paths.py` in its
`context_extensions.py`. The other 8 SDLC workflows hardcode directory
paths but never resolve artifact keys like `{INIT_FILE}`, `{REQ_FILE}`,
`{PLAN_FILE}` into the prompt context. Rendered prompts contain
unresolved placeholders.

---

## Architecture Decision

### Pattern: Plugin Lifecycle Interface

`context_extensions.py` becomes the **mandatory plugin interface** for
all workflows. A base class defines the contract. A scanner discovers
and invokes lifecycle hooks. CLI commands trigger the scanner.

```
context_extensions.py (MANDATORY per workflow)
├── class MyWorkflow(WorkflowExtensions)
│   ├── register_artifact_keys() → dict   → global ARTIFACT_PATHS
│   ├── build_context_extensions() → dict → prompt context
│   ├── init() → None                     → one-time setup
│   └── <future hooks>                    → extensible
```

### Key Design Principles

1. **Single interface file** — `context_extensions.py` is the only
   Python file a workflow developer must understand. No separate
   `output_paths.py`.

2. **Base class with defaults** — `WorkflowExtensions` provides
   no-op defaults. Workflows override only what they need. IDE
   autocompletion works. The contract is explicit.

3. **Scanner-driven discovery** — the runner scans all workflows for
   `WorkflowExtensions` subclasses and calls hooks by name. Adding a
   new global feature = adding one method to the base class + one
   scanner function.

4. **CLI-triggered** — hooks are invoked by CLI commands (`init`,
   `run`), not at import time. Explicit control over when things run.

5. **Global artifact registry** — `constants.ARTIFACT_PATHS` is the
   single dict that maps all artifact keys to paths. Populated by
   calling `register_artifact_keys()` on every workflow.

6. **Backward compatible** — existing workflows without the new class
   continue to work via fallback to the old free-function pattern.

---

## Interface Contract

### Base Class

Location: `agent_runner_v2/workflow_packages/extensions_base.py`

```python
class WorkflowExtensions:
    """Base class for workflow plugin lifecycle hooks.

    Every workflow package MUST have a context_extensions.py module.
    Subclass WorkflowExtensions and override the methods your workflow
    needs. Unoverridden methods are safe no-ops.
    """

    workflow_name: str = ""

    def register_artifact_keys(
        self, *, job_id: str, mode: str
    ) -> dict[str, str]:
        """Return artifact key → relative path mappings.

        Called during workflow startup to populate the global
        ARTIFACT_PATHS registry. Paths may contain {job_id} and
        {slug} placeholders resolved at runtime.

        Returns:
            Dict mapping artifact key strings to repo-relative
            path templates.
        """
        return {}

    def build_context_extensions(
        self,
        *,
        state: dict,
        step: str,
        step_cfg: dict,
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:
        """Return additional context variables for prompt rendering.

        Called before each step's prompt is rendered. Use this to
        inject absolute artifact paths, governance roots, and any
        other context the prompt templates need.

        Returns:
            Dict of context variable name → value strings.
        """
        return {}

    def init(
        self, *, workspace_root: Path, runner_home: Path
    ) -> None:
        """One-time initialization when `ukbe-run-agent init` runs.

        Use this to install workflow artifacts to the global runner
        home, seed configuration, or perform any setup that must
        happen once per environment.
        """
        pass
```

### Scanner Module

Location: `agent_runner_v2/workflow_packages/hooks.py`

```python
def scan_all(hook_name: str, **kwargs) -> dict[str, Any]:
    """Call *hook_name* on every discovered workflow's Extensions class.

    Returns:
        Dict mapping workflow_name → hook return value.
    """

def register_all_artifact_keys(*, job_id: str, mode: str) -> None:
    """Call register_artifact_keys() on all workflows.

    Merges results into constants.ARTIFACT_PATHS.
    """

def init_all(*, workspace_root: Path, runner_home: Path) -> None:
    """Call init() on all workflows."""

def get_extension(template_group: str) -> WorkflowExtensions | None:
    """Return the cached extension instance for a workflow.

    Returns None if the workflow has no WorkflowExtensions subclass.
    """
```

### Global Registry

Location: `agent_runner_v2/constants.py`

```python
ARTIFACT_PATHS: dict[str, str] = {}

def register_artifact_paths(paths: dict[str, str]) -> None:
    """Merge workflow-contributed paths into the global registry."""
    ARTIFACT_PATHS.update(paths)

def get_artifact_path(key: str, default: str = "") -> str:
    """Look up an artifact path from the global registry."""
    return ARTIFACT_PATHS.get(key, default)
```

---

## Lifecycle Sequence

### At `ukbe-run-agent init`

```
CLI init command
  → init_workspace()                    # copy bootstrap bundles
  → hooks.init_all(workspace_root, runner_home)
      → for each workflow:
          ext = get_extension(workflow_name)
          if ext: ext.init(...)
```

### At `ukbe-run-agent run`

```
CLI run command
  → _load_group()                       # load workflow config
  → hooks.register_all_artifact_keys(job_id, mode)
      → for each workflow:
          ext = get_extension(workflow_name)
          if ext: ARTIFACT_PATHS.update(ext.register_artifact_keys(...))
  → build_context()                     # build prompt context
      → _apply_workflow_package_context_hooks()
          → ext = get_extension(template_group)
          → ctx.update(ext.build_context_extensions(...))
  → render_prompt()                     # placeholders resolved
```

---

## Migration Plan

### Phase 1: SDLC Workflows (Focus)

Migrate all 9 SDLC workflows to the new interface. Delete their
`output_paths.py` files.

| Workflow | Artifact Keys |
|----------|---------------|
| `sdlc_00_delivery_scaffold_v1` | 21 scaffold template/agent paths |
| `sdlc_10_requirement_v1` | DRAFT_INIT_FILE, INIT_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_20_planning_v1` | REQ_FILE, PLAN_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_30_backlog_v1` | BACKLOG_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_40_task_v1` | TASK_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_50_implementation_v1` | IMPL_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_60_execution_v1` | EXEC_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_70_validation_v1` | VAL_FILE, REVIEW_FILE_SUGGESTED |
| `sdlc_80_review_v1` | REV_FILE, MEM_FILE, CLOSE_FILE, REVIEW_FILE_SUGGESTED |

### Phase 2: Existing Workflows (Backward Compatible)

Existing workflows (01_governance_foundation, 02_agent_runner_platform,
image_csv_gen_v3, etc.) continue to work unchanged. The scanner falls
back to the old free-function `build_context_extensions()` pattern and
`output_paths.py` loading when no `WorkflowExtensions` subclass is
found.

Migration to the new interface can happen incrementally when these
workflows are next modified.

### Phase 3: Consumer Simplification

Once all workflows use the new interface:

- Remove `workflow_path_contracts.py` dynamic loading entirely
- Remove `_load_context_extensions_module()` from `step_runner.py`
- All path resolution goes through `ARTIFACT_PATHS` + `get_extension()`

---

## Shared SDLC Constants

Common values used across all SDLC workflows:

```python
# In constants.py
SDLC_DELIVERY_BASE = "docs/repo/agent_runner/sdlc/delivery"
```

Each SDLC workflow's `register_artifact_keys()` uses this constant
instead of hardcoding the base path.

---

## Workflow Development SOP

### Mandatory Interface

Every new workflow package MUST have `context_extensions.py`
implementing `WorkflowExtensions`:

```python
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions

class MyWorkflowExtensions(WorkflowExtensions):
    workflow_name = "my_new_workflow_v1"

    def register_artifact_keys(self, *, job_id, mode):
        return {
            "MY_OUTPUT": f"path/to/output/{job_id}.md",
        }

    def build_context_extensions(self, *, state, step, step_cfg, ctx, project_root):
        # Resolve artifact paths to absolute, inject governance roots
        return { ... }
```

### Adding a New Global Hook

When a new cross-cutting feature is needed:

1. Add method to `WorkflowExtensions` base class (default no-op)
2. Add scanner function in `hooks.py`
3. Wire to CLI command in `run_agent.py`
4. Implement in workflows that need it

No new file types. No new discovery mechanisms. Just a method name.

### File Contract

| File | Required? | Purpose |
|------|-----------|---------|
| `workflow.toml` | Yes | Step definitions, routing, coder roles |
| `context_extensions.py` | Yes | WorkflowExtensions subclass (mandatory interface) |
| `prompts/` | Yes | Prompt templates |
| `actions.py` | No | Custom @action functions |
| `bundle_governance.toml` | Yes | Artifact registry for backend sync |
| `output_paths.py` | **DELETED** | Replaced by register_artifact_keys() |

---

## Verification

1. Unit tests pass: `.venv\Scripts\python -m pytest tests/unit/ -v`
2. sdlc_10 rendered prompt has `{INIT_FILE}` resolved to absolute path
3. Existing workflows (01_governance, 02_platform) still work unchanged
4. `ARTIFACT_PATHS` populated after `register_all_artifact_keys()` call
5. `workflow_path_contracts.py` no longer searches bootstrap folder
