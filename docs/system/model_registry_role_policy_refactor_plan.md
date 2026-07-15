# Coder Connection And Role Policy Refactor Plan

## Purpose

This document defines the target design for:

- centralized coder connection routing
- centralized semantic role binding
- centralized step role policy binding
- adapter-specific command translation

This plan is intentionally separate from `backend_execution_refactor_plan.md` so the coder-routing refactor can be reviewed and executed independently.

## Core Decision

The runner must not manage authentication.

The runner should not store or resolve:

- API keys
- browser/session login state
- provider auth flows
- provider endpoint credentials

Instead, the runner should only resolve:

- `coder`
- `connection`
- `model_id`

Each coder installation is assumed to already be configured locally to use the intended provider/account.

## Scope Constraints

Current target coders:

- `qwen`
- `claude`
- `opencode`
- `codex`

Current target external connections:

- `bailian`
- `deepseek`
- `opencode_go`

Special rule:

- `codex` is standalone
- `codex` must not participate in provider connection routing
- `codex` roles should not define a `connection`

## Goals

1. Remove the flat `model_mapping.json` alias structure
2. Remove per-step hardcoded `default_role` and `allowed_roles`
3. Replace per-step coder selection with a single `role_policy` reference
4. Keep the runner fully auth-free
5. Let adapters translate either `coder + connection + model_id` or `codex + model_id` into the correct CLI form
6. Keep `codex + model_id` independent from external provider routing

## Current Problems

The current implementation has these issues:

- `model_mapping.json` mixes alias, coder, model, and occasional auth-related fields
- model strings are overloaded and interpreted differently by different adapters
- `opencode` already needs a provider-prefixed model string, while `qwen` largely wants only model id
- workflow steps repeat `default_role` and `allowed_roles` inline
- the current design pressure pushes the runner toward handling auth concerns, which is explicitly unwanted

## Canonical File Layout

The shared registries should live in the repo workflow root:

```text
workflows/
  _registry/
    coder_connections.json
    coder_roles.json
    role_policies.json

  00_core_governance_bootstrap_v1/
    workflow.toml
    prompts/
    docs/
```

Rationale:

- `workflows/_registry/` is easier to reason about than `agent_runner_v2/bootstrap/workflows/default/`
- the data is runtime configuration, not bootstrap-only implementation detail
- migrated workflows should read from one shared control plane

## Registry Responsibilities

### `coder_connections.json`

Owns:

- named runner-visible connections
- the list of coders supported by each connection
- the formatting rule for how the adapter should pass model selection
- optional provider prefix used only for command composition

Does not own:

- auth credentials
- auth environment variable names
- base URLs
- semantic roles
- step role policies

Example:

```json
{
  "connections": {
    "bailian": {
      "provider": "bailian",
      "supported_coders": ["qwen", "claude", "opencode"],
      "model_format": "model_id"
    },
    "deepseek": {
      "provider": "deepseek",
      "supported_coders": ["qwen", "claude", "opencode"],
      "model_format": "model_id"
    },
    "opencode_go": {
      "provider": "opencode_go",
      "supported_coders": ["opencode"],
      "model_format": "provider/model_id",
      "provider_prefix": "opencode-go"
    }
  }
}
```

Meaning:

- `qwen` and `claude` can be assigned to `bailian` or `deepseek`
- `opencode` can be assigned to `opencode_go`
- `codex` does not appear here because it is standalone

### `coder_roles.json`

Owns:

- semantic role to executable coder binding
- semantic role type classification
- selected connection for connection-routed coders
- selected model id

Example:

```json
{
  "roles": {
    "architect_primary": {
      "coder": "opencode",
      "connection": "opencode_go",
      "model_id": "deepseek-v4-flash",
      "role_type": "architect"
    },
    "architect_secondary": {
      "coder": "qwen",
      "connection": "bailian",
      "model_id": "qwen3.7-plus",
      "role_type": "architect"
    },
    "reviewer_primary": {
      "coder": "qwen",
      "connection": "deepseek",
      "model_id": "deepseek-chat",
      "role_type": "reviewer"
    },
    "reviewer_secondary": {
      "coder": "codex",
      "model_id": "gpt-5.4-nano",
      "role_type": "reviewer"
    }
  }
}
```

Rules:

- if `coder != "codex"`, then `connection` is required
- if `coder == "codex"`, then `connection` must be absent

### `role_policies.json`

Owns:

- step-usable named policies
- `default_role`
- `allowed_roles`

Example:

```json
{
  "role_policies": {
    "architect_standard": {
      "default_role": "architect_primary",
      "allowed_roles": [
        "architect_primary",
        "architect_secondary"
      ]
    },
    "reviewer_standard": {
      "default_role": "reviewer_primary",
      "allowed_roles": [
        "reviewer_primary",
        "reviewer_secondary"
      ]
    }
  }
}
```

## Workflow Contract

Per-step inline `default_role` and `allowed_roles` should be removed.

Target step shape:

```toml
[step.coder]
role_policy = "architect_standard"
```

And for review-type steps:

```toml
[step.coder]
role_policy = "reviewer_standard"
must_differ = false
```

Resolution chain:

```text
workflow step
-> role_policy
-> default_role / allowed_roles
-> semantic role
-> either:
   - coder + connection + model_id
   - codex + model_id
-> adapter-specific command translation
```

## Resolved Coder Contract

Every resolved role should produce one normalized payload.

Example for a connection-routed coder:

```json
{
  "coder": "qwen",
  "connection": "deepseek",
  "connection_profile": {
    "provider": "deepseek",
    "supported_coders": ["qwen", "claude", "opencode"],
    "model_format": "model_id"
  },
  "model_id": "deepseek-chat"
}
```

Example for standalone `codex`:

```json
{
  "coder": "codex",
  "connection": null,
  "connection_profile": null,
  "model_id": "gpt-5.4-nano"
}
```

Rules:

- the runner resolves either:
  - `coder`, `connection`, and `model_id`
  - or `codex` and `model_id`
- the runner does not resolve auth settings
- adapters consume structured fields rather than inferring behavior from overloaded model strings

## Resolver API Target

The resolver surface in `agent_runner_v2/model_config.py` should move toward this contract:

```python
def load_coder_connections(path: Path | str | None = None) -> dict[str, Any]
def load_coder_roles(path: Path | str | None = None) -> dict[str, Any]
def load_role_policies(path: Path | str | None = None) -> dict[str, Any]

def resolve_connection(connection_name: str) -> dict[str, Any] | None
def resolve_role(role_name: str) -> dict[str, Any] | None
def resolve_role_policy(policy_name: str) -> dict[str, Any] | None

def resolve_effective_coder(
    *,
    role_name: str,
) -> dict[str, Any]
```

`resolve_effective_coder()` should return:

- `coder`
- `connection`
- `connection_profile`
- `model_id`

Constraints:

- for `codex`, `connection` is `None`
- for non-`codex`, `connection` is required

## Adapter Translation Contract

The adapter layer must receive normalized fields and translate them explicitly.

### Shared expectations

Each adapter should receive:

- `coder`
- `connection`
- `connection_profile`
- `model_id`

Each adapter must decide:

- whether it needs only `model_id`
- whether it needs `provider_prefix/model_id`
- whether it ignores `connection` entirely

The runner should not inject auth flags, keys, or login/session details.

### `qwen`

Input contract:

- `connection`
- `model_id`

Translation rule:

- use `model_id` as the CLI model argument
- rely on the local `qwen` installation/config to already be wired to the intended provider/account

Example commands:

```text
qwen -y -m deepseek-chat --prompt
qwen -y -m qwen3.7-plus --prompt
```

If `qwen` later supports a non-secret local profile selector, that can be added explicitly, but auth still stays outside runner ownership.

### `claude`

Input contract:

- `connection`
- `model_id`

Translation rule:

- use only locally supported non-secret CLI switching behavior
- if local `claude` config already targets the intended connection, pass `model_id`
- do not add runner-owned auth handling

### `opencode`

Input contract:

- `connection`
- `connection_profile.provider_prefix`
- `model_id`

Translation rule:

- for `opencode_go`, compose:

```text
opencode run --model {provider_prefix}/{model_id}
```

Example:

```text
opencode run --model opencode-go/deepseek-v4-flash
```

Rule:

- `opencode` is the main case where the adapter should compose a provider-prefixed model string from connection metadata

### `codex`

Input contract:

- `coder`
- `model_id`

Translation rule:

- `codex` is standalone
- `codex` should ignore connection routing entirely
- role records for `codex` should not define a `connection`
- `codex + model_id` is a first-class supported resolution shape

Example:

```text
codex ... model=gpt-5.4-nano
```

## Prompt Resolution Contract

Prompt-resolution logic must use `model_id`, not connection names and not provider-prefixed composed values.

Reason:

- prompt file resolution is based on filename suffixes
- `model_id` is the stable prompt-selection token
- composed values like `opencode-go/deepseek-v4-flash` should not leak into file path resolution

## Logging Contract

Manual mode and daemon mode should log:

- coder backend
- semantic role
- connection, when present
- model id

Target log examples:

```text
[generate_core_governance_docs] invoking coder=qwen role=reviewer_primary connection=deepseek model_id=deepseek-chat
```

```text
[generate_core_governance_docs] invoking coder=opencode role=architect_primary connection=opencode_go model_id=deepseek-v4-flash
```

```text
[review_core_governance_docs] invoking coder=codex role=reviewer_secondary model_id=gpt-5.4-nano
```

## Validation Rules

These invariants should be enforced at load time:

1. every non-codex role defines:
   - `coder`
   - `connection`
   - `model_id`
2. every codex role defines:
   - `coder`
   - `model_id`
   and does not define `connection`
3. every referenced connection exists in `coder_connections.json`
4. every connection lists the assigned coder in `supported_coders`
5. every role policy references existing role names
6. `model_id` must be trimmed and non-empty
7. `opencode_go` must define `provider_prefix`
8. prompt resolution must use only `model_id`

## Migration Plan

### Phase 1: Registry introduction

1. create:
   - `workflows/_registry/coder_connections.json`
   - `workflows/_registry/coder_roles.json`
   - `workflows/_registry/role_policies.json`
2. populate them with current migrated workflow equivalents
3. remove dependency on bootstrap `model_mapping.json` for migrated workflow resolution

### Phase 2: Resolver rewrite

1. replace flat alias loading with connection/profile loading
2. add connection validation
3. add standalone `codex` validation rules
4. add role-policy resolution as a first-class loader concern

### Phase 3: Workflow contract cleanup

1. update migrated `workflow.toml`
2. remove per-step:
   - `default_role`
   - `allowed_roles`
3. replace them with:
   - `role_policy`

### Phase 4: Adapter rewrite

1. update `qwen` adapter to consume:
   - `connection`
   - `model_id`
2. update `claude` adapter to consume:
   - `connection`
   - `model_id`
3. keep `opencode` on explicit `provider_prefix/model_id` composition using connection metadata
4. keep `codex` standalone

### Phase 5: Prompt/runtime cleanup

1. ensure prompt resolution uses `model_id`
2. ensure daemon/provider summary uses structured coder/connection fields
3. ensure logs include:
   - role
   - coder
   - connection when present
   - model id

### Phase 6: Validation and tests

Add or update tests for:

- connection load validation
- unsupported coder/connection pair rejection
- codex-with-connection rejection
- non-codex-without-connection rejection
- unknown role rejection
- unknown role policy rejection
- `opencode_go` provider-prefix composition
- prompt lookup using `model_id`
- workflow role-policy resolution

## Acceptance Criteria

This refactor is complete when:

1. the migrated workflow no longer uses inline `default_role` or `allowed_roles`
2. the migrated workflow resolves coder choice through `role_policy`
3. all non-codex roles resolve through `coder + connection + model_id`
4. all codex roles resolve through `coder + model_id` without connection routing
5. `qwen` and `claude` run without runner-owned auth logic
6. `opencode` composes `provider_prefix/model_id` from connection metadata
7. prompt suffix lookup uses only `model_id`
8. manual and daemon logs show:
   - coder
   - role
   - connection when present
   - model id
9. the migrated workflow runs successfully end-to-end with the new registry structure

## Explicit Non-Goals

This plan does not require:

- runner-owned auth management
- provider profile definitions containing API keys or auth env vars
- backward compatibility with the old flat `model_mapping.json` shape for the migrated workflow
- backward compatibility with the old inline `default_role` / `allowed_roles` workflow format
- forcing `codex` into the external provider connection abstraction

Those compatibility layers are intentionally excluded because the migrated scope is currently narrow and the refactor should simplify, not preserve drift.
