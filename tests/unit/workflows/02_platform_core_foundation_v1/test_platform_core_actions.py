"""Unit tests for ``02_platform_core_foundation_v1/actions.py``.

Covers the L1 path discipline and cross-reference validation gate.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_actions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "02_platform_core_foundation_v1"
        / "actions.py"
    )
    spec = importlib.util.spec_from_file_location("tests.platform_core_actions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load actions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# L1 path discipline
# ---------------------------------------------------------------------------
def test_build_context_inventory_uses_global_l1_path(tmp_path: Path) -> None:
    """The context inventory artifact must reference L1 from the global path, not a repo-local path."""
    actions = _load_actions_module()

    (tmp_path / "workflows").mkdir()
    (tmp_path / "masterplan").mkdir()
    (tmp_path / "masterplan" / "LAYER_ARCHITECTURE_MASTERPLAN.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "masterplan" / "LAYER2_PLATFORM_CORE_SPECIFICATION.md").write_text("# x\n", encoding="utf-8")

    inventory = actions._build_context_inventory(
        project_root=tmp_path, job_id="02PC-TEST", step="collect_platform_context",
    )

    # Must NOT reference the repo-local L1 path
    assert "docs/system/00_governance/foundation/current" not in inventory, (
        "context inventory must not reference repo-local L1 path"
    )
    # MUST reference the global runtime root
    global_root = str(actions.GLOBAL_RUNNER_HOME / "bundles" / "core" / "current")
    assert global_root in inventory, (
        f"context inventory must reference global L1 path; expected {global_root!r} in text"
    )


# ---------------------------------------------------------------------------
# Cross-reference validation gate
# ---------------------------------------------------------------------------
SHARED_SERVICES_BAD = """\
---
template_id: "SYS-02-SS"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Shared Services

## Artifact Resolution

### Function

`resolve_repo_or_runtime_path()` resolves a path.

### Resolution Order

1. Check the repository working tree first.
2. Fall back to the runtime artifact root.
3. Return the resolved absolute path.

## Meta Sidecar

The `meta.json` sidecar is the sole communication channel between a coder
(LLM) and the runner. No stdout JSON parsing, no pre-invocation sidecar
writes, no disk recovery functions.

## Path Contracts

```python
def build_context_extensions(context: dict) -> dict:
    return {"CUSTOM_PATH": "/some/path"}
```

```python
def build_output_paths(job_id: str, run_root: Path) -> dict:
    return {"MY_ARTIFACT": run_root / "my_artifact.md"}
```

## Backend Sync Protocol

No BackendClient section here.
"""

SHARED_SERVICES_GOOD = """\
---
template_id: "SYS-02-SS"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Shared Services

## Artifact Resolution

### Function

`resolve_repo_or_runtime_path()` resolves a path.

### Resolution Order

The function dispatches by path prefix (namespace routing):
- absolute paths are returned unchanged
- `docs/`, `archive/`, `scripts/`, `temp/` resolve under the project root
- `.ukbe-runner/` resolves under the runner home
- everything else resolves under the jobs root

## Meta Sidecar

The `meta.json` sidecar is the primary communication channel between a coder
(LLM) and the runner. When the sidecar is missing or invalid, the runner
repairs it via `_repair_or_validate_meta_json` in `step_runner.py`.

## Path Contracts

```python
def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
    return {"CUSTOM_PATH": "/some/path"}
```

```python
def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    return {"MY_ARTIFACT": "docs/my_artifact.md"}
```

```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
    pass
```

## Backend Sync Protocol

### BackendClient

- `submit_run()`
- `claim_step()`
- `approve_run()`
"""


def test_check_shared_services_catches_bad_prose_and_signatures() -> None:
    """The aggressive cross-reference checks must flag all known defects on a bad SHARED_SERVICES doc."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_shared_services(checks, SHARED_SERVICES_BAD, "SHARED_SERVICES.md")
    failed = {c["check"] for c in checks if not c["ok"]}

    assert "hook_signature_match" in failed, "must catch wrong signature for build_context_extensions"
    assert "resolution_order_forbidden_prose" in failed, "must catch 'check the repository working tree first'"
    assert "resolution_order_has_dispatch_keyword" in failed, "must fail when dispatch-by-prefix keyword is missing"
    assert "meta_sidecar_forbidden_prose" in failed, "must catch 'no disk recovery functions'"
    assert "meta_sidecar_sole_channel_ban" in failed, "must catch 'sole communication channel' when repair exists"
    assert "backend_client_section_missing" in failed, "must flag missing BackendClient section"


def test_check_shared_services_passes_good_doc() -> None:
    """The cross-reference checks should pass on a corrected SHARED_SERVICES doc."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_shared_services(checks, SHARED_SERVICES_GOOD, "SHARED_SERVICES.md")
    failed = [c for c in checks if not c["ok"]]
    # BackendClient method verification may have false negatives if backend_client.py has methods not
    # listed in our sample doc — only assert that signature/resolution/meta checks pass.
    sig_failures = [c for c in failed if c["check"] in (
        "hook_signature_match",
        "resolution_order_forbidden_prose",
        "resolution_order_has_dispatch_keyword",
        "meta_sidecar_forbidden_prose",
        "meta_sidecar_sole_channel_ban",
        "backend_client_section_missing",
    )]
    assert not sig_failures, f"expected cross-reference checks to pass on corrected doc; failures: {sig_failures}"


RUNTIME_MODEL_BAD = """\
---
template_id: "SYS-02-RM"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Runtime Model

## Coder Integration

### Invocation Contract

The `meta.json` sidecar is the sole communication channel between coder
and runner. No stdout JSON parsing, no disk recovery functions.

Some modules referenced: `step_runner.py`, `coder_adapters.py`,
`backend_client.py`, `nonexistent_module.py`.
"""

RUNTIME_MODEL_GOOD = """\
---
template_id: "SYS-02-RM"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Runtime Model

## Coder Integration

### Invocation Contract

The `meta.json` sidecar is the primary communication channel between coder
and runner. When the sidecar is missing or invalid, the runner repairs it
via `_repair_or_validate_meta_json` in `step_runner.py`.

Some modules referenced: `step_runner.py`, `coder_adapters.py`,
`backend_client.py`.
"""


def test_check_runtime_model_catches_bad_prose_and_missing_modules() -> None:
    """The RUNTIME_MODEL check must catch banned meta sidecar prose and non-existent source modules."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_runtime_model(checks, RUNTIME_MODEL_BAD, "RUNTIME_MODEL.md")
    failed = {c["check"] for c in checks if not c["ok"]}

    assert "meta_sidecar_forbidden_prose" in failed
    assert "meta_sidecar_sole_channel_ban" in failed
    # nonexistent_module.py should fail source_module_exists
    nonexistent_fails = [
        c for c in checks
        if not c["ok"] and c["check"] == "source_module_exists" and c.get("field") == "nonexistent_module.py"
    ]
    assert nonexistent_fails, "must flag non-existent source module"


def test_check_runtime_model_passes_good_doc() -> None:
    """The RUNTIME_MODEL check should pass on a corrected doc."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_runtime_model(checks, RUNTIME_MODEL_GOOD, "RUNTIME_MODEL.md")
    failed = [c for c in checks if not c["ok"]]
    assert not failed, f"expected all checks to pass on corrected doc; failures: {failed}"


METADATA_CONTRACT_BAD = """\
---
template_id: "SYS-02-MC"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Metadata Contract

## Platform authority Values

### Usage Rules

- Permanent Layer 2 documents use `authority: "workflow-generated"` when
  produced by the platform constitution workflow.
- No generated document may claim `authority: "human-authored"`.
"""

METADATA_CONTRACT_GOOD = """\
---
template_id: "SYS-02-MC"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "test"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "test"
---

# Metadata Contract

## Platform authority Values

### Usage Rules

- `authority` and `managed_by` are orthogonal axes: `authority` defines
  content ownership, while `managed_by` identifies the mechanical
  producer or maintainer. A document may carry
  `authority: "platform-owned"` with `managed_by: workflow-generated`.
- No generated document may claim `authority: "human-authored"`.
"""


def test_check_metadata_contract_catches_missing_orthogonality() -> None:
    """The METADATA_CONTRACT check must flag missing authority/managed_by orthogonality statement."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_metadata_contract(checks, METADATA_CONTRACT_BAD, "METADATA_CONTRACT.md")
    failed = {c["check"] for c in checks if not c["ok"]}

    assert "authority_managed_by_orthogonality" in failed


def test_check_metadata_contract_passes_good_doc() -> None:
    """The METADATA_CONTRACT check should pass when orthogonality is explicitly stated."""
    actions = _load_actions_module()
    checks: list[dict[str, object]] = []
    actions._check_metadata_contract(checks, METADATA_CONTRACT_GOOD, "METADATA_CONTRACT.md")
    failed = [c for c in checks if not c["ok"]]
    assert not failed, f"expected all checks to pass; failures: {failed}"


# ---------------------------------------------------------------------------
# Signature extraction
# ---------------------------------------------------------------------------
def test_extract_source_signatures_handles_multiline_def() -> None:
    """The signature extractor must handle multi-line function definitions."""
    actions = _load_actions_module()
    ctx_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "02_platform_core_foundation_v1"
        / "context_extensions.py"
    )
    sigs = actions._extract_source_signatures(ctx_path)

    assert "build_context_extensions" in sigs
    sig = sigs["build_context_extensions"]
    # The multi-line signature must contain all keyword-only params
    assert "state" in sig
    assert "step_cfg" in sig
    assert "project_root" in sig


def test_installed_platform_root_resolves() -> None:
    """The installed platform root must resolve to a valid directory."""
    actions = _load_actions_module()
    root = actions._installed_platform_root()
    assert root.exists()
    assert root.is_dir()
    assert root.name == "agent_runner_v2"


def test_resolve_source_module_finds_backend_client() -> None:
    """Source resolution must find backend_client.py via the installed package."""
    actions = _load_actions_module()
    bc_path = actions._resolve_source_module("agent_runner_v2/backend_client.py")
    assert bc_path is not None
    assert bc_path.exists()
    assert "backend_client.py" in bc_path.name