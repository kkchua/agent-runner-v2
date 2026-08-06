# Workflow Creation Guide

> **Purpose:** Step-by-step reference for creating a new agent-runner-v2 workflow
> package. Covers architecture, required files, common patterns, and pitfalls.
>
> **Audience:** Human developers and AI coders.

---

## Table of Contents

- [Part A: Quick-Start Checklist](#part-a-quick-start-checklist)
- [Part B: Architecture Overview](#part-b-architecture-overview)
- [Part C: File-by-File Reference](#part-c-file-by-file-reference)
- [Part D: Workflow Patterns](#part-d-workflow-patterns)
- [Part E: Common Pitfalls](#part-e-common-pitfalls)
- [Part F: Verification and Deployment](#part-f-verification-and-deployment)
- [Part G: Engine Management and Deployment](#part-g-engine-management-and-deployment)

---

## Part A: Quick-Start Checklist

Follow these steps in order to create a new workflow package.

### Step 1: Create the directory

```
workflows/<your_workflow_name>/
```

The directory name IS the workflow identifier. It must match the `name` field
in `workflow.toml` and the `workflow_name` attribute in `context_extensions.py`.

### Step 2: Create `workflow.toml`

Minimum viable manifest:

```toml
[workflow]
name = "your_workflow_name"
version = "1.0.0"
label = "Your Workflow Label"
job_prefix = "YRWF"
description = "What this workflow does."
visibility = "canonical"
default_max_rejects = 3
init_step = "first_step_name"

[[step]]
name = "first_step_name"
prompt = "prompts/01_first_step.txt"
enable_notifications = true
onsuccess = "stepCompletion"

[step.artifacts]
produces = ["YOUR_OUTPUT_ARTIFACT"]
result_meta_key = "YOUR_OUTPUT_ARTIFACT"

[step.coder]
role_policy = "architect_standard"

[[step]]
name = "stepCompletion"
action = "step_completion"
```

See [Part C: workflow.toml](#c1-workflowtoml) for the full reference.

### Step 3: Create `context_extensions.py`

This file is **mandatory**. It implements the `WorkflowExtensions` interface.

```python
"""Context extensions for your_workflow_name."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.runtime_context import get_runner_home, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class YourWorkflowExtensions(WorkflowExtensions):
    """Workflow extension hooks for your_workflow_name."""

    workflow_name = "your_workflow_name"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings."""
        date_str = dt.datetime.now().strftime("%Y%m%d")
        run_root = f"docs/repo/your_area/runs/{job_id}"
        return {
            "YOUR_OUTPUT_ARTIFACT": f"{run_root}/OUTPUT-{date_str}.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-review.md",
        }

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        """Inject absolute paths into prompt context."""
        result: dict[str, str] = {}
        workspace_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))

        # Governance roots
        runner_home = get_runner_home()
        if runner_home:
            result["GOVERNANCE_RUNTIME_ROOT"] = str(
                Path(runner_home) / "bundles" / "core" / "current" / "foundation"
            )

        # Resolve artifact paths to absolute
        for key, rel_path in self.register_artifact_keys(job_id=job_id).items():
            result[key] = str(workspace_root / rel_path)

        return result
```

See [Part C: context_extensions.py](#c2-context_extensionspy) for the full reference.

### Step 4: Create prompt templates

Create the `prompts/` directory and add `.txt` files referenced by `workflow.toml`:

```
workflows/your_workflow_name/prompts/01_first_step.txt
```

**Critical rules:**
- Use bare `{ARTIFACT_KEY}` placeholders — never wrap in backticks.
- Reference absolute paths via placeholders, never hardcode.

See [Part C: Prompt Templates](#c4-prompts) for the full reference.

### Step 5: (Optional) Create `actions.py`

Only needed if your workflow has action-driven steps.

```python
from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action

@action("your_custom_action")
def your_custom_action(*, context, state, step_cfg, project_root):
    # ... your logic ...
    return ActionResult(
        status="APPROVED",
        remark="Action completed.",
        artifacts={"YOUR_OUTPUT": output_path},
    )
```

See [Part C: actions.py](#c3-actionspy) for the full reference.

### Step 6: (Optional) Create `bundle_governance.toml`

Only needed if you want centralized artifact registry for backend sync
validation. See [Part C: bundle_governance.toml](#c5-bundle_governancetoml).

### Step 7: (Optional) Create `install.py`

Only needed if your workflow must install files to the global runner home
during `ukbe-run-agent init`. See
[WORKFLOW_PLUGIN_INSTALLATION.md](WORKFLOW_PLUGIN_INSTALLATION.md).

### Step 8: Create batch files

Create `run-<workflow_name>.bat` and optionally `submit-<workflow_name>.bat`
at the project root. These activate `.venv` and invoke `ukbe-run-agent`.

### Step 9: Verify and sync

```bash
# Validate locally
.venv\Scripts\python -c "from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir; from pathlib import Path; print(validate_workflow_bundle_dir(Path('workflows/your_workflow_name')).to_dict())"

# Sync to backend
ukbe-run-agent sync-workflows your_workflow_name
```

---

## Part B: Architecture Overview

### How the Plugin System Works

```
workflows/<name>/workflow.toml
        │
        ▼
  load_workflow_package()          ← loader.py
        │
        ▼
  WorkflowBundle (dataclass)       ← base.py
        │
        ▼
  bundle_to_template_group_dict()  ← loader.py (adapter)
        │
        ▼
  dict shaped like TEMPLATE_GROUPS ← existing runner pipeline
        │
        ▼
  step_runner.py → workflow_router.py → coder_adapters.py
```

The plugin system is a **configuration source adapter**. It converts
`workflow.toml` into the same dict format the runner already consumes.
No changes to the execution pipeline are needed.

### Runtime Discovery

Workflows are discovered from two locations:

1. **Repo-local:** `workflows/<name>/` — primary development copy
2. **Global (bootstrap):** `agent_runner_v2/bootstrap/workflows/default/<name>/`
   — packaged bundle seeded by `ukbe-run-agent init`

The loader uses **dual-path discovery**: global first, local fallback.

### Three Deployment Copies

After creating or modifying a workflow, keep all three in sync:

| Copy | Path | Purpose |
|---|---|---|
| Development | `workflows/<name>/` | Primary edit location |
| Bootstrap | `agent_runner_v2/bootstrap/workflows/default/<name>/` | Packaged for `init` |
| Published | `docs/system/00_governance/bootstrap/workflows/<name>/` | Governance source |

### Key Runtime Concepts

**Artifacts** — Named outputs tracked through workflow state. Each artifact
has a key (e.g., `REQ_FILE`) and a filesystem path. Keys are declared in
`workflow.toml` step fields and resolved to paths via `context_extensions.py`.

**Steps** — Either prompt-driven (LLM invocation) or action-driven (Python
function). After execution, the coder writes a `meta.json` sidecar — the
sole communication channel.

**Routing** — After each step, the runner decides the next step:
- `onsuccess` → advance to next step after approval
- `on_reject_refine` → refinement loop when rejected
- `requires_human_approval_after` → gate on human decision

**Coder Roles** — Role policies (e.g., `architect_standard`,
`reviewer_standard`) map to coder configurations resolved by
`coder_registry.py`. Available policies are defined in
`workflows/_registry/role_policies.json`.

---

## Part C: File-by-File Reference

### C.1: `workflow.toml`

The workflow manifest. Defines steps, routing, artifact contracts, and
coder roles.

#### Top-level metadata

```toml
[workflow]
name = "your_workflow_name"       # Required. Must match directory name.
version = "1.0.0"                 # Required. Semantic version string.
label = "Your Workflow Label"     # Required. Human-readable display name.
job_prefix = "YRWF"              # Required. Used for job ID generation.
description = "Brief description" # Optional.
visibility = "canonical"          # Optional. "canonical" or "hidden".
default_max_rejects = 3           # Optional. Default 3.
```

#### Init step declaration

Two equivalent styles are supported. **Pick one per workflow:**

**Style A — flat key (preferred for new workflows):**
```toml
[workflow]
init_step = "first_step_name"
```

**Style B — sub-table (used by legacy bootstrap workflows):**
```toml
[workflow.init]
step = "first_step_name"
inputs = []
```

Both are parsed by the loader. Style A is simpler and preferred.

#### Prompt-driven step

```toml
[[step]]
name = "generate_docs"
prompt = "prompts/01_generate_docs.txt"   # Relative to workflow dir
enable_notifications = true
onsuccess = "review_docs"                  # Next step on success

[step.artifacts]
required_inputs = ["INPUT_ARTIFACT"]       # Must exist before step runs
optional_inputs = ["OPTIONAL_INPUT"]       # Used if present, not required
produces = ["OUTPUT_ARTIFACT"]             # Step declares it produces this
result_meta_key = "OUTPUT_ARTIFACT"        # Key for meta.json sidecar
target_artifact = "OUTPUT_ARTIFACT"        # For in-place edits
edit_mode = "in_place"                     # "in_place" for refine steps

[step.coder]
role_policy = "architect_standard"         # From role_policies.json
```

**Important:** `onsuccess` is NOT a first-class field on `StepConfig`. It
flows through the `extra` passthrough dict in the TOML parser and reaches
the routing runtime via the adapted dict. This is intentional — it works
correctly. Do NOT try to add it to `[step.artifacts]`.

#### Action-driven step

```toml
[[step]]
name = "validate_docs"
action = "validate_docs"                   # Function name from @action()
enable_notifications = true
onsuccess = "publish_docs"

[step.artifacts]
required_inputs = ["INPUT_ARTIFACT"]
produces = ["VALIDATION_REPORT"]
result_meta_key = "VALIDATION_REPORT"
```

#### Promote step

Updates an artifact's `Status:` field to `Approved` in-place.

```toml
[[step]]
name = "promote_plan"
action = "promote_artifact"
promotes = "PLAN_FILE"                     # MUST be top-level, NOT under [step.artifacts]
enable_notifications = true
onsuccess = "stepCompletion"

[step.artifacts]
required_inputs = ["PLAN_FILE"]
result_meta_key = "PLAN_FILE"
```

For multiple artifacts:
```toml
[[step]]
name = "promote_all"
action = "promote_all"
promotes = ["REV_FILE", "MEM_FILE", "CLOSE_FILE"]
```

**CRITICAL:** The `promotes` key MUST be at the `[[step]]` top level.
The TOML loader silently drops unknown fields from `[step.artifacts]` —
only top-level unknown keys are captured by the `extra` passthrough.

#### Terminal step

Every workflow MUST end with:

```toml
[[step]]
name = "stepCompletion"
action = "step_completion"
```

#### Refinement loop

```toml
[step.on_reject_refine]
step = "refine_docs"                       # Step to run for refinement
artifact = "OUTPUT_ARTIFACT"               # Artifact being refined
max_iterations = 2                         # Max refine attempts
exhausted_failure_code = "REFINE_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

The refine step should use `onsuccess` to route back to the review step:

```toml
[[step]]
name = "refine_docs"
prompt = "prompts/04_refine.txt"
onsuccess = "review_docs"                  # After refine, go back to review

[step.artifacts]
required_inputs = ["OUTPUT_ARTIFACT", "REVIEW_FILE_SUGGESTED"]
produces = ["OUTPUT_ARTIFACT"]
target_artifact = "OUTPUT_ARTIFACT"
edit_mode = "in_place"
result_meta_key = "OUTPUT_ARTIFACT"
```

#### Available role policies

Defined in `workflows/_registry/role_policies.json`:

| Policy | Default Role | Typical Use |
|---|---|---|
| `architect_standard` | bailian_qwen3.7-plus | Generation steps |
| `reviewer_standard` | bailian_glm-5 | Review/critique steps |
| `refine_standard` | bailian_qwen3.7-plus | Refinement steps |
| `validation_standard` | bailian_qwen3.7-plus | Validation/audit steps |
| `implement_standard` | bailian_qwen3-coder-next | Code implementation |
| `execution_standard` | bailian_qwen3-coder-next | Code execution |
| `plan_standard` | bailian_glm-5 | Planning steps |
| `backlog_standard` | bailian_kimi-k2.5 | Backlog management |
| `task_standard` | bailian_MiniMax-M2.5 | Task decomposition |
| `code_fix_standard` | bailian_MiniMax-M2.5 | Bug fixes |
| `documentation_standard` | bailian_kimi-k2.5 | Documentation |

---

### C.2: `context_extensions.py`

**This file is mandatory** for every workflow package.

#### Required structure

```python
"""Context extensions for <workflow_name>."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class MyWorkflowExtensions(WorkflowExtensions):
    """Workflow extension hooks for <workflow_name>."""

    workflow_name = "<workflow_name>"  # Must match directory name

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key → relative-path mappings."""
        ...

    def build_context_extensions(
        self, *, state, step, step_cfg, ctx, project_root=None,
    ) -> dict[str, str]:
        """Return prompt context variables (absolute paths)."""
        ...
```

#### `register_artifact_keys()` rules

1. Returns **relative** paths (relative to project root).
2. Use `{job_id}` and `{slug}` placeholders — resolved at runtime.
3. Use `SDLC_DELIVERY_BASE` from `constants.py` for SDLC delivery paths.
4. Use `resolve_next_seq()` from `constants.py` for auto-incrementing
   sequence numbers in filenames.

#### `build_context_extensions()` rules

1. Must resolve ALL paths to **absolute** — the daemon runs from a
   different working directory.
2. Use `get_workspace_root()` and `get_runner_home()` from
   `runtime_context.py`.
3. The `project_root` parameter may be `None` — always provide a fallback:
   ```python
   workspace_root = Path(project_root or get_workspace_root() or Path.cwd())
   ```

#### Common imports

```python
from agent_runner_v2.constants import SDLC_DELIVERY_BASE, resolve_next_seq
from agent_runner_v2.runtime_context import (
    get_runner_home,
    get_workspace_root,
    resolve_repo_or_runtime_path,
    GLOBAL_RUNNER_HOME,
    JOBS_ROOT,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions
```

#### Slug extraction pattern

Many SDLC workflows extract a slug from an input artifact filename for
consistent naming. The pattern:

```python
import re

def _extract_slug_from_path(file_path: str) -> str:
    """Extract slug from SDLC artifact filename."""
    if not file_path:
        return "unknown"
    filename = Path(file_path).stem
    match = re.search(r"_(.+)$", filename)
    if match:
        return match.group(1)
    return "unknown"
```

#### Sequence auto-increment pattern

To prevent overwrites when multiple runs produce the same artifact type:

```python
from agent_runner_v2.constants import resolve_next_seq

# In build_context_extensions():
if "{seq}" in resolved:
    path_dir, path_file = resolved.rsplit("/", 1)
    target_dir = workspace_root / path_dir
    prefix = path_file.split("{seq}")[0]
    seq = resolve_next_seq(target_dir, prefix)
    resolved = resolved.replace("{seq}", seq)
```

---

### C.3: `actions.py`

**Optional.** Only needed for action-driven steps.

```python
"""Custom actions for your_workflow_name."""
from __future__ import annotations

from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("your_action_name")
def your_action_name(*, context, state, step_cfg, project_root):
    """Brief docstring of what this action does."""
    # Access step configuration
    artifacts = state.get("artifacts", {})

    # Your logic here
    success = True

    if success:
        return ActionResult(
            status="APPROVED",
            remark="Action completed successfully.",
            artifacts={"OUTPUT_KEY": "/absolute/path/to/output"},
        )
    else:
        return ActionResult(
            status="REJECTED",
            remark="Action failed: reason.",
            artifacts={"OUTPUT_KEY": "/absolute/path/to/output"},
            reject_code="ACTION_FAILED",
        )
```

**Returning REJECTED** triggers `on_reject_refine` routing.
**Returning APPROVED** advances to `onsuccess`.

---

### C.4: Prompts

Prompt files are plain `.txt` files in `prompts/`.

#### Placeholder rules

```
CORRECT:   Write output to {YOUR_OUTPUT_ARTIFACT}.
WRONG:     Write output to `{YOUR_OUTPUT_ARTIFACT}`.
```

Backtick-wrapped placeholders are literal text — the runner will NOT
resolve them. The coder will see the key name instead of the file path.

#### Required sections

Every prompt should include:

1. **Objective** — what the coder should do
2. **Reference Inputs** — what to read (use `{ARTIFACT_KEY}` placeholders)
3. **Artifacts** — what to write (use `{ARTIFACT_KEY}` placeholders)
4. **Output Instructions** — format, encoding, structure requirements

#### Example

```text
Objective

Generate the requirements document from the approved initiative.

Reference Inputs

- Read the approved initiative: {INIT_FILE}
- Read Layer 1 governance: {GOVERNANCE_RUNTIME_ROOT}

Artifacts

Write the requirements document to: {REQ_FILE}

Output Instructions

- Complete markdown with YAML frontmatter.
- Include traceability matrix linking requirements to initiative goals.
```

---

### C.5: `bundle_governance.toml`

**Optional.** Provides a centralized artifact registry for backend sync
validation. Currently only 3 of 14 workflows have this file.

When to use it:
- Your workflow produces artifacts that must be registered with the backend
- You want validation that all artifact keys are declared before sync
- You need governance adapter generation (AGENTS.md, QWEN.md, CLAUDE.md)

```toml
[governance]
canonical_source = "bundle_governance/core_governance.md"
generated_dir = "bundle_governance/generated"
adapter_targets = ["AGENTS.md", "QWEN.md", "CLAUDE.md"]
include_in_prompts = true
prompt_targets = ["all"]

[[artifact]]
key = "YOUR_OUTPUT"
path = "docs/repo/your_area/runs/<job_id>/OUTPUT.md"
description = "Main output document."
required = true

[[artifact]]
key = "REVIEW_FILE_SUGGESTED"
path = "docs/repo/your_area/runs/<job_id>/REVIEW.md"
description = "Review document."
required = false
```

**Note:** Even without this file, artifact keys are auto-accepted by the
runner if they appear in `workflow.toml` step fields. The governance file
adds an extra validation layer but is not required for basic operation.

---

### C.6: Self-Validation

**Recommended for:** All prompt-driven producer steps (generate, define,
design, analyze).

Self-Validation is a pattern where the LLM checks its own output against
criteria BEFORE reporting APPROVED. This catches errors early and improves
quality without waiting for external review.

#### When to use

- Steps that produce design documents (REQUIREMENTS, ARTIFACTS, STEPS)
- Steps where downstream steps will fail if the output is incomplete
- Complex workflows where reviewer time is limited

#### How to implement

Add a "Self-Validation" section to the prompt:

```text
## Self-Validation

Before reporting APPROVED, validate your output against these criteria:

1. Completeness Check: Does the output include ALL required elements?
2. Consistency Check: Are there internal contradictions?
3. Traceability Check: Can every element be traced to the input spec?
4. Feasibility Check: Is the design implementable?

If any check fails:
- Revise the output to fix the issue
- Re-run the validation
- Only report APPROVED when all checks pass

Include a "Self-Validation Results" section in the output documenting
which checks passed/failed and any revisions made.
```

#### Benefits

- Catches errors before they propagate downstream
- Reduces reviewer burden (catches obvious issues)
- Encourages higher quality output through self-correction
- Provides transparency via documented validation results

---

### C.7: Principles-Based Generation

**Recommended for:** Complex generation steps where the exact file list
cannot be known in advance.

Principles-based generation is an alternative to fixed task lists. Instead
of listing "generate these 6 files", the prompt instructs the LLM to
"infer the required files from the design documents."

#### Fixed task list (traditional)

```text
Generate these 6 files:
1. workflow.toml
2. context_extensions.py
3. prompts/index.txt
4. README.md
5. .env.sample
6. config.json.sample
```

**Problem:** If the design changes (e.g., needs actions.py), the prompt
must be updated.

#### Principles-based (recommended)

```text
Generate ALL files the design requires. From the STEP_ARCHITECTURE and
ARTIFACT_CONTRACT, determine:

- workflow.toml (always required)
- context_extensions.py (always required)
- prompts/ (if prompt-driven steps exist)
- actions.py (if action-driven steps exist)
- README.md (always required)
- .env.sample (if environment variables needed)
- config.json.sample (if runtime config needed)

Principle: Include a file ONLY if the design calls for it.
```

**Benefits:**
- Adapts to design changes without prompt updates
- Prevents missing files (e.g., actions.py for action steps)
- Prevents unnecessary files (e.g., empty .env.sample)
- Aligns with the Single Responsibility Principle

#### When to use each approach

| Approach | Use When |
|----------|----------|
| Fixed list | Simple workflows with predictable structure |
| Principles-based | Complex workflows where design determines files |

---

## Part D: Workflow Patterns

### Pattern 1: Action-Only Pipeline

**Used by:** `00_bootstrap_lifecycle_admin_v1`

All steps are Python actions. No prompts, no LLM invocations.

```
validate → publish → init → sync → write_summary → stepCompletion
```

**Characteristics:**
- No `prompts/` directory
- No `[step.coder]` sections
- No `bundle_governance.toml`
- Fast execution, deterministic results
- Each step has minimal or no `[step.artifacts]`

### Pattern 2: Prompt-Driven with Review/Refine Loop

**Used by:** `sdlc_10` through `sdlc_80` (the SDLC chain)

The standard pattern for LLM-generated documents with quality gates.

```
generate → technical_critique → review → [refine → review] → promote → stepCompletion
```

**Characteristics:**
- 4 prompt files: generate, critique, review, refine
- 2 role policies: `architect_standard` (generate/refine), `reviewer_standard` (critique/review)
- Refinement loop: review rejects → refine → back to review
- Refine step uses `onsuccess` to return to review
- `requires_human_approval_after = true` on review step
- Promote step at the end with `promotes` at `[[step]]` top level
- `target_artifact` + `edit_mode = "in_place"` on refine step

**Typical step flow:**

| Step | Type | Role Policy | Routing |
|---|---|---|---|
| generate | prompt | architect_standard | onsuccess → technical_critique |
| technical_critique | prompt | reviewer_standard | onsuccess → review; on_reject_refine → generate |
| review | prompt | reviewer_standard | onsuccess → promote; on_reject_refine → refine; requires_human_approval |
| refine | prompt | architect_standard | onsuccess → review |
| promote | action (promote_artifact) | — | onsuccess → stepCompletion |
| stepCompletion | action (step_completion) | — | terminal |

### Pattern 3: Mixed with Generate + Review + Refine + Audit

**Used by:** `01_governance_foundation_v1`, `02_agent_runner_platform_v1`

Extended pattern with an additional audit/validation step.

```
generate → review → refine → validate → audit → promote → stepCompletion
```

**Characteristics:**
- Has `bundle_governance.toml` with artifact registry
- Has `bundle_governance/` directory with governance adapters
- Uses `result_meta_key_from_context` instead of `result_meta_key` on
  review/audit steps
- Has legacy `output_paths.py` (should be migrated to `context_extensions.py`)
- Uses `[workflow.init]` sub-table style

---

### Pattern 4: Gatekeeper QC Pipeline

**Used by:** `workflow_builder_v1`

Quality control pattern with validation checkpoints between each major
phase. Gatekeepers validate the output of the preceding step before
downstream steps consume it.

```
generate_test_criteria → review_test_criteria → analyze_spec → gatekeep_requirements
  → resolve_questions → define_artifacts → gatekeep_artifacts → design_steps
  → gatekeep_steps → generate_package → gatekeep_package → validate_bundle
  → review_package → [refine_package → review_package] → promote_package → stepCompletion
```

**Full 8-step sequence with 4 gatekeepers:**

| Phase | Step | Type | Purpose |
|-------|------|------|---------|
| 1 | analyze_spec | prompt | Generate requirements from spec |
| 1a | gatekeep_requirements | prompt | QC: Validate requirements completeness |
| 2 | resolve_questions | prompt | Fill gaps, resolve ambiguities |
| 3 | define_artifacts | prompt | Define artifact contract |
| 3a | gatekeep_artifacts | prompt | QC: Validate artifact coverage |
| 4 | design_steps | prompt | Design step sequence and routing |
| 4a | gatekeep_steps | prompt | QC: Validate step flow and data chains |
| 5 | generate_package | prompt | Generate ALL workflow files |
| 5a | gatekeep_package | prompt | QC: Validate files match design |
| 6 | validate_bundle | action | Structural + semantic validation |
| 7 | review_package | prompt | Final quality review |
| 8 | promote_package | action | Copy to workflows/{slug}/ |

**Characteristics:**
- Every producer step (analyze, define, design, generate) followed by QC
- Gatekeepers ask: "Will this solution actually work? Are there gaps?"
- Gatekeepers have `on_reject_refine` routing back to producer step
- Uses `validation_standard` role policy for gatekeepers
- Producer steps include **Self-Validation** section in prompts
- Uses **principles-based generation** (infers files from design, not fixed list)
- Validates that action-driven steps have corresponding `actions.py`

#### Gatekeeper step syntax

```toml
[[step]]
name = "gatekeep_requirements"
prompt = "prompts/01c_gatekeep_requirements.txt"
onsuccess = "resolve_questions"

[step.artifacts]
required_inputs = ["WORKFLOW_REQUIREMENTS", "WORKFLOW_SPEC"]
produces = ["GATEKEEP_REQUIREMENTS"]
result_meta_key = "GATEKEEP_REQUIREMENTS"

[step.coder]
role_policy = "validation_standard"

[step.on_reject_refine]
step = "analyze_spec"
artifact = "WORKFLOW_REQUIREMENTS"
max_iterations = 2
```

#### Gatekeeper prompt template (adaptable)

Gatekeeper prompts follow a standard structure:

```text
Objective

Validate that the [ARTIFACT] is complete, technically sound, and will
achieve all objectives. This is a QC checkpoint before downstream steps
consume this artifact.

Reference Inputs

- Read {ORIGINAL_SPEC} for the source requirements.
- Read {GENERATED_ARTIFACT} for the artifact to validate.

Validation Questions

Answer each question with specific evidence:

1. Completeness: Does the artifact define ALL elements needed?
2. Technical Soundness: Is the approach technically valid?
3. Downstream Feasibility: Can the next step consume this output?
4. Constraint Satisfaction: Does it respect all declared constraints?

Decision Rules

- APPROVED: The artifact is complete and will achieve objectives.
- REJECTED: The artifact has gaps or needs significant revision.

Output Instructions

- Write the gatekeeper report to {GATEKEEP_ARTIFACT}.
- Include YAML frontmatter with doc_type: "gatekeep_report".
- Structure: Summary, Validation Results table, Issues, Recommendations, Verdict.
- Verdict: APPROVED or REJECTED on its own line.
- The result field in meta.json must match the verdict exactly.
```

---

## Part E: Common Pitfalls

### E.1: `onsuccess` placement

`onsuccess` goes at the `[[step]]` top level, NOT under `[step.artifacts]`
or `[step.routing]`. It flows through the `extra` passthrough dict.

```toml
# CORRECT
[[step]]
name = "generate"
prompt = "prompts/01_generate.txt"
onsuccess = "review"

# WRONG — will be silently ignored
[step.artifacts]
onsuccess = "review"
```

### E.2: `promotes` placement

`promotes` MUST be at the `[[step]]` top level. The TOML loader silently
drops unknown fields from `[step.artifacts]`.

```toml
# CORRECT
[[step]]
name = "promote_plan"
action = "promote_artifact"
promotes = "PLAN_FILE"

# WRONG — silently dropped, promote action sees no target
[step.artifacts]
promotes = "PLAN_FILE"
```

### E.3: Undefined variables in `context_extensions.py`

Always import what you use. A common bug:

```python
# BUG — workspace_root is not defined
effective_root = Path(project_root or workspace_root or Path.cwd())

# CORRECT — import and use get_workspace_root()
from agent_runner_v2.runtime_context import get_workspace_root
effective_root = Path(project_root or get_workspace_root() or Path.cwd())
```

### E.4: Relative paths in `build_context_extensions()`

The daemon runs from a different working directory. All paths injected
into prompt context MUST be absolute.

```python
# WRONG — relative path
result["MY_OUTPUT"] = "docs/repo/output/file.md"

# CORRECT — absolute path
result["MY_OUTPUT"] = str(workspace_root / "docs/repo/output/file.md")
```

### E.5: Backtick-wrapped placeholders in prompts

Backticks make placeholders literal. The coder sees the key name, not
the file path.

```
# WRONG — coder sees literal "{REQ_FILE}" text
Write to `{REQ_FILE}`.

# CORRECT — coder sees the actual file path
Write to {REQ_FILE}.
```

### E.6: Forgetting `stepCompletion`

Every workflow MUST end with a terminal step:

```toml
[[step]]
name = "stepCompletion"
action = "step_completion"
```

Without it, the workflow never reaches `COMPLETED` status.

### E.7: Missing `workflow_name` attribute

The `WorkflowExtensions` subclass MUST set `workflow_name` to match the
directory name exactly:

```python
class MyExtensions(WorkflowExtensions):
    workflow_name = "my_workflow_v1"  # Must match workflows/my_workflow_v1/
```

### E.8: Artifact key mismatch

Keys in `register_artifact_keys()` must match keys in `workflow.toml`
step `produces`/`required_inputs`. Case-sensitive.

```python
# context_extensions.py
return {"REQ_FILE": "..."}

# workflow.toml — must use exactly "REQ_FILE", not "REQ_DOC" or "req_file"
[step.artifacts]
produces = ["REQ_FILE"]
```

### E.9: `bundle_governance.toml` is optional

Despite the DEVELOPER_GUIDE calling it "required", the runtime does NOT
enforce its presence. `load_bundle_governance()` returns `None` when the
file is missing, and the workflow still functions. The file adds
validation and backend sync benefits but is not a hard requirement.

### E.10: Duplicated helper functions

The `_extract_slug_from_path()` function is currently copy-pasted across
8 workflow files. When creating a new workflow, consider whether a shared
utility would be more appropriate than another copy.

### E.11: Missing gatekeeper after producer steps

When using the gatekeeper pattern, EVERY producer step must be followed
by a gatekeeper. Missing a gatekeeper allows bad output to propagate.

```toml
# WRONG — no gatekeeper between analyze and define
[[step]]
name = "analyze"
onsuccess = "define"     # ❌ Missing gatekeeper!

[[step]]
name = "define"

# CORRECT — gatekeeper validates output before downstream consumption
[[step]]
name = "analyze"
onsuccess = "gatekeep_analyze"

[[step]]
name = "gatekeep_analyze"
onsuccess = "define"
[step.on_reject_refine]
step = "analyze"          # ❌ Routes back if validation fails

[[step]]
name = "define"
```

### E.12: Gatekeeper without on_reject_refine

A gatekeeper that REJECTS must route back to the producer step for
refinement. Without `on_reject_refine`, a rejection has nowhere to go.

```toml
# WRONG — rejection leads to failure, not refinement
[[step]]
name = "gatekeep_requirements"
onsuccess = "next_step"
# ❌ Missing [step.on_reject_refine] — rejections fail the workflow

# CORRECT — rejections route back for refinement
[[step]]
name = "gatekeep_requirements"
onsuccess = "next_step"

[step.on_reject_refine]
step = "analyze_spec"     # ✅ Back to producer step
artifact = "WORKFLOW_REQUIREMENTS"
max_iterations = 2
```

### E.13: Self-Validation declared but not implemented

Declaring "This step includes Self-Validation" in the prompt header
is not enough. The LLM must actually perform the validation.

```text
# WRONG — just mentions Self-Validation exists
## Self-Validation
This step includes Self-Validation.

# WRONG — criteria listed but not applied
## Self-Validation
Validate against these criteria:
1. Completeness
2. Consistency

# CORRECT — explicit instruction to validate AND revise
## Self-Validation

Before reporting APPROVED, validate your output:

1. Completeness: Does it include ALL required elements?
2. Consistency: Are there contradictions?

If ANY check fails:
- Revise the output to fix the issue
- Re-run validation
- Only report APPROVED when all checks pass

Include "Self-Validation Results" section showing which checks passed.
```

---

## Part F: Verification and Deployment

### Local validation

```bash
# Validate a single workflow bundle
.venv\Scripts\python -c ^
    "from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir; ^
     from pathlib import Path; ^
     r = validate_workflow_bundle_dir(Path('workflows/your_workflow_name')); ^
     print('VALID' if r.valid else 'INVALID'); ^
     [print(f'  {f.level}: {f.code} — {f.message}') for f in r.findings]"
```

### Dry run

```bash
# Render prompts without invoking a coder
ukbe-run-agent run --template-group your_workflow_name --dry-run --new-job
```

### Backend sync

```bash
# Sync workflow definition to backend
ukbe-run-agent sync-workflows your_workflow_name
```

This validates locally, POSTs the definition, and registers artifact types.

### Unit tests

```bash
.venv\Scripts\python -m pytest tests/unit/ -v
```

### Deployment checklist

After creating the workflow:

1. [ ] `workflows/<name>/` — development copy complete
2. [ ] `agent_runner_v2/bootstrap/workflows/default/<name>/` — bootstrap copy synced
3. [ ] `docs/system/00_governance/bootstrap/workflows/<name>/` — published copy synced
4. [ ] `run-<name>.bat` — batch file at project root
5. [ ] Backend sync completed
6. [ ] Unit tests pass
7. [ ] Dry run succeeds

---

## Part G: Engine Management and Deployment

agent-runner-v2 runs in two modes: **development** (from repo source) and
**production** (installed as a CLI package with a versioned engine).

### Config File

The global config at `~/.ukbe-runner/config.json` controls the runtime:

```json
{
  "engine_version": "SNAPSHOT",
  "repo_root": "D:/MyProjectSpace/01_Workflows/agent-runner-v2",
  "backend_url": "http://127.0.0.1:8100",
  "worker_id": "my-worker-01",
  "worker_label": "live"
}
```

| Field | Purpose |
|---|---|
| `engine_version` | `"SNAPSHOT"` for dev mode, or a version tag like `"1.0.1"` for production |
| `repo_root` | Path to the agent-runner-v2 repo root. Used in SNAPSHOT mode to find `workflows/` when running from an arbitrary directory |
| `backend_url` | Backend API URL for daemon/worker mode |
| `worker_id` | Unique worker identifier |
| `worker_label` | Worker queue label (e.g., `"live"` or `"dev"`) |

### Engine Commands

```bash
# Show installed engine versions
ukbe-run-agent engine list

# Install from GitHub (public releases)
ukbe-run-agent engine install v1.0.1

# Install from local repo (private repos)
ukbe-run-agent engine install v1.0.1 --from-path D:/path/to/agent-runner-v2

# Switch to SNAPSHOT dev mode (auto-sets repo_root from cwd)
ukbe-run-agent engine use SNAPSHOT

# Switch to SNAPSHOT with explicit repo root
ukbe-run-agent engine use SNAPSHOT --repo-root D:/path/to/agent-runner-v2

# Switch to a versioned engine
ukbe-run-agent engine use v1.0.1
```

### Deployment Modes

**Development (SNAPSHOT):**
- `engine_version: "SNAPSHOT"` + `repo_root` pointing to the repo
- Workflows loaded from `workflows/` in the repo
- Code changes picked up immediately (daemon spawns fresh subprocesses)
- Only `daemon_v2.py` changes require a daemon restart

**Production (versioned):**
- `engine install <tag>` copies the package to `~/.ukbe-runner/engine/versions/<tag>/`
- `engine use <tag>` sets the active version
- Workflows loaded from `~/.ukbe-runner/workflows/default/` (seeded by `init`)
- Daemon resolves engine path from config, prepends to PYTHONPATH

### Per-Workflow Install Hooks

Each workflow implements `install_to_global()` and `sync_to_backend()` via
the `WorkflowExtensions` interface:

```bash
# Install all workflows (copy to global + sync)
ukbe-run-agent install

# Install a specific workflow
ukbe-run-agent install sdlc_00_delivery_scaffold_v1
```

The `init` command also calls these hooks automatically after seeding.

---

## Appendix: File Reference Matrix

| File | Required? | Purpose |
|---|---|---|
| `workflow.toml` | **Yes** | Step definitions, routing, artifact contracts |
| `context_extensions.py` | **Yes** | WorkflowExtensions interface (artifact paths, context injection) |
| `prompts/` | If prompt steps exist | Prompt template `.txt` files |
| `actions.py` | If action steps exist | Custom `@action()` functions |
| `bundle_governance.toml` | Optional | Artifact registry for backend sync validation |
| `bundle_governance/` | Optional | Governance adapters (AGENTS.md, etc.) |
| `install.py` | Optional | Global installation hook for `ukbe-run-agent init` |
| `README.md` | Optional | Package documentation |
