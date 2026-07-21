---
doc_type: "audit_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped final semantic audit of platform core; temporary evidence artifact"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260721-009"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `audit_platform_core_docs`
> This file is a temporary evidence artifact. It is not part of the permanent platform constitution.

# Platform Core Semantic Audit

## Decision

APPROVED

The staged Layer 2 platform core constitution set passes all semantic
audit checks. Every claim in every document exactly matches the platform
source code. Zero findings. The set is ready for human approval and
publish.

Documents audited:

| # | Document | File | Template ID |
|---|---|---|---|
| 1 | Platform Index | `README.md` | `SYS-02-IDX` |
| 2 | Runtime Model | `RUNTIME_MODEL.md` | `SYS-02-RM` |
| 3 | Bundle Authoring Contract | `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` |
| 4 | Shared Services | `SHARED_SERVICES.md` | `SYS-02-SS` |
| 5 | Metadata Contract | `METADATA_CONTRACT.md` | `SYS-02-MC` |
| 6 | Validation Contract | `VALIDATION_CONTRACT.md` | `SYS-02-VC` |

## Layer Boundary Audit

### Layer 1 Governance Boundary

No Layer 1 redefinition or contradiction detected.

- README.md line 62-84: Explicitly declares Layer 1 inheritance and
  states "No document in this set may contradict or redefine Layer 1."
- METADATA_CONTRACT.md: All doc_type and authority values are inherited
  verbatim from Layer 1 (verified against
  `C:\Users\kengk\.ukbe-runner\bundles\core\current\foundation\METADATA_STANDARD.md`
  lines 81-105). Platform-specific semantics are added as extensions,
  not as redefinitions.
- VALIDATION_CONTRACT.md: Inherits Layer 1 metadata standard for
  frontmatter enforcement (line 134-147). No Layer 1 values are
  redefined.
- RUNTIME_MODEL.md: Defines platform-specific runtime mechanics
  (step model, daemon, coder integration) without claiming ecosystem-wide
  governance authority.
- BUNDLE_AUTHORING_CONTRACT.md: Defines platform-level bundle contract
  without redefining Layer 1 bundle taxonomy or authority model.

### Layer 3 Drift Boundary

No Layer 3 bundle-specific drift detected.

- No document contains bundle-specific content normalized into platform
  standards.
- BUNDLE_AUTHORING_CONTRACT.md defines the generic platform contract
  using placeholder names (`my_bundle_name`, `my_bundle`) that are
  clearly illustrative.
- Code examples in SHARED_SERVICES.md and VALIDATION_CONTRACT.md are
  platform-level interface patterns, not bundle-specific outputs.
- No Layer 3 bundle name or job-specific content appears in any
  permanent document.

### Out-of-Scope Content

No operational bootstrap mechanics, installation guides, or repository
setup instructions detected.

- README.md line 100-113 explicitly excludes operational procedures
  from scope.
- No document contains install, deploy, or registry procedures.

### Lifecycle Status

All six staged permanent documents carry `lifecycle_status: "draft"`.
None are in `published` or `active` state. This is correct for staged
content awaiting human approval.

## Authority Audit

### authority / managed_by Orthogonality

METADATA_CONTRACT.md lines 102-120 (under `### Usage Rules`) explicitly
state:

- `authority` answers: "Who owns the canonical truth of this document?"
  This is a content ownership question.
- `managed_by` answers: "What mechanism produced and maintains this
  file?" This is a mechanical production question.
- "A document carrying `authority: 'platform-owned'` and
  `managed_by: workflow-generated` is consistent."

This is correct and consistent with Layer 1 definitions:
- Layer 1 `authority` field: "Who owns the truth of the document"
  (METADATA_STANDARD.md line 62)
- Layer 1 `managed_by` field: "Declares that the document is
  workflow-managed and protected from manual edits"
  (METADATA_STANDARD.md line 72-73)

The staged documents carry `authority: "workflow-generated"` and
`managed_by: workflow-generated`, which is consistent -- the workflow
is both the content owner (at draft stage) and the mechanical producer.

### Authority Values Accuracy

All authority values listed in METADATA_CONTRACT.md match Layer 1:

| Value | Layer 1 Source | Staged Doc |
|---|---|---|
| `human-authored` | METADATA_STANDARD.md line 101 | METADATA_CONTRACT.md line 79 |
| `workflow-generated` | METADATA_STANDARD.md line 102 | METADATA_CONTRACT.md line 80 |
| `bundle-owned` | METADATA_STANDARD.md line 103 | METADATA_CONTRACT.md line 81 |
| `platform-owned` | METADATA_STANDARD.md line 104 | METADATA_CONTRACT.md line 82 |
| `derived` | METADATA_STANDARD.md line 105 | METADATA_CONTRACT.md line 83 |

All values match exactly. No redefinitions.

### doc_type Values Accuracy

All doc_type values listed in METADATA_CONTRACT.md match Layer 1:

| Value | Layer 1 Source | Staged Doc |
|---|---|---|
| `masterplan` | METADATA_STANDARD.md line 85 | METADATA_CONTRACT.md line 37 |
| `system` | METADATA_STANDARD.md line 86 | METADATA_CONTRACT.md line 38 |
| `workflow_output` | METADATA_STANDARD.md line 87 | METADATA_CONTRACT.md line 39 |
| `review_artifact` | METADATA_STANDARD.md line 88 | METADATA_CONTRACT.md line 40 |
| `validation_artifact` | METADATA_STANDARD.md line 89 | METADATA_CONTRACT.md line 41 |
| `audit_artifact` | METADATA_STANDARD.md line 90 | METADATA_CONTRACT.md line 42 |
| `bundle_definition` | METADATA_STANDARD.md line 91 | METADATA_CONTRACT.md line 43 |
| `platform_standard` | METADATA_STANDARD.md line 92 | METADATA_CONTRACT.md line 44 |

All values match exactly. No redefinitions.

## Metadata Audit

### Frontmatter Compliance

All six permanent documents carry the required frontmatter fields:

| Field | README | RUNTIME_MODEL | BUNDLE_AUTHORING | SHARED_SERVICES | METADATA_CONTRACT | VALIDATION_CONTRACT |
|---|---|---|---|---|---|---|
| `template_id` | SYS-02-IDX | SYS-02-RM | SYS-02-BAC | SYS-02-SS | SYS-02-MC | SYS-02-VC |
| `version` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| `doc_type` | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard |
| `authority` | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |
| `scan_policy` | include | include | include | include | include | include |
| `scan_reason` | present | present | present | present | present | present |
| `layer` | layer2 | layer2 | layer2 | layer2 | layer2 | layer2 |
| `platform` | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 |
| `lifecycle_status` | draft | draft | draft | draft | draft | draft |
| `effective_version` | 02PC-GEN-20260721-009 | 02PC-GEN-20260721-009 | 02PC-GEN-20260721-009 | 02PC-GEN-20260721-009 | 02PC-GEN-20260721-009 | 02PC-GEN-20260721-009 |
| `managed_by` | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |

All fields present and valid across all six documents.

### Inheritance Rules Accuracy

METADATA_CONTRACT.md lines 177-201 correctly describe the inheritance
model:
- Layer 1 baseline fields are inherited verbatim.
- Layer 2 extensions add `platform`, `template_id`, `managed_by`,
  `lifecycle_status`, `effective_version`.
- Layer 3 inherits both Layer 1 and Layer 2.
- No lower layer may redefine Layer 1 values.

This is consistent with Layer 1 METADATA_STANDARD.md line 94-95:
"Layer 2 may extend this vocabulary for platform needs, but it must not
change the meaning of Layer 1 values."

### Scan Policy Expectations

METADATA_CONTRACT.md scan policy tables correctly map:
- Permanent platform standards -> `scan_policy: "include"`
- Temporary evidence -> `scan_policy: "conditional"` or `"exclude"`
- Platform context inventories -> `scan_policy: "exclude"`

This matches the Layer 1 scanner compliance rules (METADATA_STANDARD.md
lines 164-190).

### Canonical Path Usage

All file references use full canonical paths:
- `docs/system/00_governance/platform/current/README.md`
- `docs/system/00_governance/platform/current/RUNTIME_MODEL.md`
- `docs/system/00_governance/platform/current/BUNDLE_AUTHORING_CONTRACT.md`
- `docs/system/00_governance/platform/current/SHARED_SERVICES.md`
- `docs/system/00_governance/platform/current/METADATA_CONTRACT.md`
- `docs/system/00_governance/platform/current/VALIDATION_CONTRACT.md`

No shortened or schematic paths (e.g., `docs/platform/README.md`) found.

## Platform Identity Audit

### Platform Name

Every permanent document carries `platform: "agent-runner-v2"` in
frontmatter. The README.md clearly identifies the platform as
"agent-runner-v2" throughout.

### Platform Scope

README.md lines 34-48 correctly position agent-runner-v2 as one of
several possible Layer 2 cores that operationalize Layer 1 governance.
This matches the Layer Architecture Masterplan's "Replaceable Layer 2s"
principle (LAYER_ARCHITECTURE_MASTERPLAN.md lines 51-62).

### Layer 2 Identity

All documents carry `layer: "layer2"`. The README.md explicitly states
the dependency direction: Layer 1 -> Layer 2 -> Layer 3. This matches
the Layer Model (LAYER_MODEL.md lines 25-27).

### No Overclaimed Promotion Authority

No document claims promotion authority above Layer 2. The README.md
explicitly states that the document set "inherits from Layer 1
governance without redefining it" and "No document in this set may
contradict or redefine Layer 1."

## Signature Accuracy Audit

### build_context_extensions()

Documented in SHARED_SERVICES.md lines 38-46:
```python
def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
```

Actual source (workflows/02_platform_core_foundation_v1/context_extensions.py
lines 35-42):
```python
def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
```

MATCH: Exact. All parameter names, types, and return type match.

### resolve_repo_or_runtime_path()

Documented in SHARED_SERVICES.md lines 94-99:
```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

Actual source (agent_runner_v2/runtime_context.py lines 158-163):
```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

MATCH: Exact. All parameter names, types, and return type match.

### build_output_paths()

Documented in SHARED_SERVICES.md line 142:
```python
def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
```

Actual source (workflows/02_platform_core_foundation_v1/output_paths.py
line 4):
```python
def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
```

MATCH: Exact. The document explicitly cites "any bundled output_paths.py"
and this matches the output_paths.py module signature.

### write_meta_sidecar()

Documented in SHARED_SERVICES.md lines 244-253:
```python
def write_meta_sidecar(
    meta_path_like: str | Path,
    *,
    status: str,
    remark: str,
    artifacts: dict,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
```

Actual source (agent_runner_v2/runtime_context.py lines 273-282):
```python
def write_meta_sidecar(
    meta_path_like: str | Path,
    *,
    status: str,
    remark: str,
    artifacts: dict,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
```

MATCH: Exact. All parameter names, types, and return type match.

## Resolution Order Accuracy

SHARED_SERVICES.md lines 102-119 describe the resolution order as
prefix-based dispatch:

1. Absolute paths returned unchanged.
2. Repo-owned prefixes (`docs/`, `archive/`, `scripts/`, `temp/`)
   resolved under project root.
3. Runner-home paths (`.ukbe-runner/`) resolved under runner home.
4. Default resolved under jobs root.

Actual source (agent_runner_v2/runtime_context.py lines 158-187):
```python
path = Path(path_str)
if path.is_absolute():
    return path

normalized = path_str.replace("\\", "/")
repo_prefixes = ("docs/", "archive/", "scripts/", "temp/")
if normalized.startswith(repo_prefixes):
    base = project_root.resolve() if project_root is not None else get_workspace_root()
    return base / path

if normalized.startswith(".ukbe-runner/"):
    runtime_root = runtime_root or get_runner_home()
    suffix = normalized[len(".ukbe-runner/"):]
    return runtime_root / Path(suffix)

runtime_root = runtime_root or get_jobs_root()
return runtime_root / path
```

MATCH: The source confirms prefix-based dispatch. There is no
existence-based fallback. The document accurately states: "The function
dispatches by path prefix. It does not check the filesystem for
existence before resolving."

## Meta Sidecar Accuracy

### Primary Channel

RUNTIME_MODEL.md lines 187-193:
"The meta.json sidecar is the primary communication channel between the
coder and the runner."

SHARED_SERVICES.md lines 169-171:
"The meta.json sidecar is the primary communication channel between the
coding agent (coder) and the runner."

Both documents correctly identify the sidecar as the primary channel.

### Repair Fallback

RUNTIME_MODEL.md lines 189-193:
"The runner also implements a repair fallback in step_runner.py via
`_repair_or_validate_meta_json()`. If the coder fails to write a valid
meta.json sidecar, the runner attempts to construct one from the coder's
direct stdout output (parsed JSON)."

SHARED_SERVICES.md lines 216-236:
Describes both missing-sidecar repair and invalid-sidecar repair via
`_repair_or_validate_meta_json()`.

Actual source (agent_runner_v2/step_runner.py lines 637-677):
The function handles `MetaJsonMissingError` by inspecting parsed_result
from coder stdout, and handles `MetaJsonInvalidError` by attempting
coercion from existing content or parsed_result.

MATCH: Both documents accurately describe the primary channel AND the
repair fallback. Neither denies the repair mechanism. Neither uses the
forbidden phrases "no disk recovery functions", "no stdout JSON parsing",
or "sole communication channel" in a denial context.

## BackendClient Method Accuracy

SHARED_SERVICES.md lines 325-343 list 14 public methods. Verification
against agent_runner_v2/backend_client.py:

| Documented Method | Source Line | Present |
|---|---|---|
| `submit_run()` | Line 40 | YES |
| `approve_run()` | Line 85 | YES |
| `get_run()` | Line 93 | YES |
| `list_runs()` | Line 96 | YES |
| `stop_run()` | Line 115 | YES |
| `reset_run_step()` | Line 121 | YES |
| `register_worker()` | Line 124 | YES |
| `heartbeat()` | Line 132 | YES |
| `claim_step()` | Line 170 | YES |
| `complete_step_run()` | Line 173 | YES |
| `sync_job_state()` | Line 176 | YES |
| `create_artifact()` | Line 179 | YES |
| `create_event()` | Line 182 | YES |
| `cleanup_execution()` | Line 185 | YES |

MATCH: All 14 methods exist with correct names. No extra or missing
methods.

### BackendClient Dataclass

Documented in SHARED_SERVICES.md lines 317-321:
```python
@dataclass
class BackendClient:
    base_url: str
    timeout_seconds: int = 30
```

Actual source (agent_runner_v2/backend_client.py lines 9-12):
```python
@dataclass
class BackendClient:
    base_url: str
    timeout_seconds: int = 30
```

MATCH: Exact.

## Action Registration Accuracy

### @action() Decorator

SHARED_SERVICES.md line 378:
```python
from agent_runner_v2.workflow_packages.actions import action
```

Actual source (agent_runner_v2/workflow_packages/actions/__init__.py):
The module is a package, so the import resolves to the __init__.py which
exports `action`.

MATCH: The import path is correct.

### Action Function Signature

SHARED_SERVICES.md lines 381-388:
```python
@action("validate_docs")
def validate_docs(*, context, state, step_cfg, project_root):
```

Actual source (agent_runner_v2/workflow_packages/actions/__init__.py
lines 6-10) uses the same signature pattern:
```python
@action("my_custom_action")
def my_custom_action(*, context, state, step_cfg, project_root):
```

MATCH: Correct keyword-argument signature.

### ActionResult Dataclass

SHARED_SERVICES.md lines 400-407:
```python
@dataclass
class ActionResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict
    reject_code: str | None = None
```

Actual source (agent_runner_v2/action_result.py lines 10-15):
```python
@dataclass
class ActionResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict
    reject_code: str | None = None
```

MATCH: Exact.

## StepResult Accuracy

RUNTIME_MODEL.md lines 68-76 describes StepResult fields:

| Field | Documented | Source (step_runner.py lines 106-112) |
|---|---|---|
| `status` | "APPROVED" or "REJECTED" | `str  # "APPROVED" \| "REJECTED"` |
| `remark` | Human-readable summary | `str` |
| `artifacts` | Dict of artifact key to file path | `dict[str, str]` |
| `reject_code` | Optional categorized rejection reason | `str \| None` |
| `meta_json_path` | Path to the communication sidecar | `str` |
| `usage_data` | Token usage and duration metrics | `dict` |

MATCH: All fields present and correctly described.

## Forbidden Content Check

| Forbidden Phrase | RUNTIME_MODEL.md | SHARED_SERVICES.md | Result |
|---|---|---|---|
| "no disk recovery functions" | NOT FOUND | NOT FOUND | PASS |
| "no stdout JSON parsing" | NOT FOUND | NOT FOUND | PASS |
| "sole communication channel" (with denial) | NOT FOUND | NOT FOUND | PASS |

### Shortened Path Check

No shortened or schematic paths found. All path examples use the full
canonical form:
- `docs/system/00_governance/platform/current/...`
- `docs/system/00_governance/platform/runs/{job_id}/...`
- `docs/system/00_governance/platform/history/{job_id}/...`

## Runtime Model Accuracy

### Execution Paths

RUNTIME_MODEL.md describes daemon and manual modes. Verification:

- Daemon mode: References `daemon.py`, `BackendClient.claim_step()`,
  `BackendClient.sync_job_state()`, heartbeat, watchdog. All verified
  in source code (daemon.py, backend_client.py).
- Manual mode: References `python -m agent_runner_v2.run_agent run`.
  The `run_agent.py` module exists and supports this invocation.
- Shared core: References `run_step()` and `run_action()`. Both exist
  in step_runner.py (lines 119 and 324 respectively).

### Coder Integration

RUNTIME_MODEL.md references:
- `coder_adapters.py`: Exists. Contains `invoke_coder()` (line 554) and
  `_run_with_sidecar_poll()` (line 307).
- `coder_registry.py`: Exists. Configures coder backends.
- Sidecar-based early exit: Matches `_run_with_sidecar_poll()` behavior.
- Supported coders (codex, claude, qwen, opencode): Matches the adapter
  implementations.

## Cited Evidence

### Source Code References

| Reference | File | Lines |
|---|---|---|
| `resolve_repo_or_runtime_path()` | `agent_runner_v2/runtime_context.py` | 158-187 |
| `write_meta_sidecar()` | `agent_runner_v2/runtime_context.py` | 273-316 |
| `_resolve_meta_json_path()` | `agent_runner_v2/step_runner.py` | 422-467 |
| `_repair_or_validate_meta_json()` | `agent_runner_v2/step_runner.py` | 637-677 |
| `run_step()` | `agent_runner_v2/step_runner.py` | 119-133 |
| `run_action()` | `agent_runner_v2/step_runner.py` | 324 |
| `StepResult` | `agent_runner_v2/step_runner.py` | 106-112 |
| `invoke_coder()` | `agent_runner_v2/coder_adapters.py` | 554 |
| `_run_with_sidecar_poll()` | `agent_runner_v2/coder_adapters.py` | 307 |
| `BackendClient` | `agent_runner_v2/backend_client.py` | 9-190 |
| `ActionResult` | `agent_runner_v2/action_result.py` | 10-15 |
| `@action()` decorator | `agent_runner_v2/workflow_packages/actions/__init__.py` | 31-50 |
| `send_notification()` | `agent_runner_v2/notifications.py` | 394 |
| `DocumentationValidationPlan` | `agent_runner_v2/actions/documentation_validation_core.py` | 18 |
| `build_context_extensions()` | `workflows/02_platform_core_foundation_v1/context_extensions.py` | 35-42 |
| `build_output_paths()` | `workflows/02_platform_core_foundation_v1/output_paths.py` | 4 |
| `_validate_artifact_files_exist()` | `agent_runner_v2/step_runner.py` | 680-698 |
| `_validate_declared_produced_artifacts_exist()` | `agent_runner_v2/step_runner.py` | 701 |

### Layer 1 Governance References

| Reference | File | Lines |
|---|---|---|
| doc_type values | `METADATA_STANDARD.md` (Layer 1) | 81-92 |
| authority values | `METADATA_STANDARD.md` (Layer 1) | 97-105 |
| scan_policy values | `METADATA_STANDARD.md` (Layer 1) | 110-116 |
| layer values | `METADATA_STANDARD.md` (Layer 1) | 118-124 |
| lifecycle_status values | `METADATA_STANDARD.md` (Layer 1) | 126-136 |
| authority semantics | `DOCUMENT_AUTHORITY.md` (Layer 1) | 27-98 |
| layer model | `LAYER_MODEL.md` (Layer 1) | 1-247 |
| managed_by field | `METADATA_STANDARD.md` (Layer 1) | 57, 72-73 |

## Publish Recommendation

The staged Layer 2 platform core constitution set is ready for human
approval and publish.

Summary of why the set is ready:

1. Zero factual errors: Every function signature, class name, method
   name, module path, and behavioral claim exactly matches the platform
   source code.

2. Clean Layer 2 boundary: No Layer 1 redefinition, no Layer 3 drift,
   no out-of-scope content.

3. Correct metadata: All six documents carry compliant frontmatter with
   proper template IDs, doc_type, authority, layer, platform,
   lifecycle_status (draft), and managed_by values.

4. Accurate authority model: The orthogonality of authority and
   managed_by is correctly documented and applied.

5. Accurate runtime model: Execution paths, coder integration, sidecar
   protocol, repair fallback, daemon behavior, and action registration
   all match source code.

6. Accurate shared services: All BackendClient methods, function
   signatures, resolution orders, and path contracts verified against
   actual source.

7. No forbidden content: No denial of repair mechanisms, no shortened
   paths, no contradictory claims.

8. Consistent internal references: All cross-document references are
   coherent and non-contradictory.

Recommended next step: Human approval, followed by publish to
`docs/system/00_governance/platform/current/`.
