# Circular Import Resolution Design

## Phase 4.1: Break Circular Imports in Runtime Dependencies

## Current State Analysis

### The Problem

The codebase uses a deferred import pattern to avoid circular dependencies:

```python
# shared_runtime_deps.py uses:
from . import backend_execution as _backend_execution
from . import daemon_runtime as _daemon_runtime
# ... etc
```

This pattern indicates circular dependency chains exist. The `_runtime_deps` modules act as:
1. **Deferred import containers** - Breaking import-time cycles
2. **Dependency injection hooks** - Passed as `hooks` parameter to functions
3. **God objects** - Centralizing access to many modules

### Identified Circular Chains

**Chain 1: Execution Flow**
```
shared_runtime_deps.py
  → imports step_runner
  → imports step_execution_runtime
  → imports step_runner (StepResult)
  → imports job_state
  → imports shared_runtime_deps (via run_agent hooks)
```

**Chain 2: Daemon Flow**
```
shared_runtime_deps.py
  → imports daemon_runtime
  → uses hooks._build_worker_request_payload
  → hooks come from shared_runtime_deps
```

**Chain 3: Backend Flow**
```
backend_execution.py
  → deferred import from workflow_runtime
  → workflow_runtime imports bundle_loader
  → bundle_loader may import runtime modules
```

### Why This Pattern Exists

1. **Late Binding**: The `hooks` parameter allows functions to call other functions without direct imports
2. **Testability**: Hooks can be mocked for testing
3. **Import Order Independence**: Modules can be imported in any order

### Problems with Current Pattern

1. **Hidden Dependencies** - Hard to trace what a function actually needs
2. **Type Checking Issues** - `hooks: Any` defeats type checking
3. **Refactoring Difficulty** - Moving functions requires updating hook usage
4. **God Object** - `_runtime_deps` knows about everything

## Proposed Solution

### Strategy: Interface Extraction + Explicit Dependencies

Instead of:
```python
def prepare_step_execution(..., hooks: Any):
    missing = hooks._missing_artifacts(...)
```

Use:
```python
from typing import Protocol

class StepHooks(Protocol):
    def missing_artifacts(self, keys: list[str], state: dict) -> list[str]: ...

def prepare_step_execution(..., hooks: StepHooks):
    missing = hooks.missing_artifacts(...)
```

### Implementation Steps

#### Step 1: Define Protocol Interfaces

Create `agent_runner_v2/hooks_protocols.py`:

```python
from typing import Protocol, Any
from pathlib import Path

class ArtifactHooks(Protocol):
    def missing_artifacts(self, keys: list[str], state: dict[str, Any]) -> list[str]: ...

class WorkflowHooks(Protocol):
    def build_group_cfg_from_execution_spec(
        self, spec: dict[str, Any], template_group: str, step_name: str
    ) -> tuple[dict[str, Any], dict[str, Any]]: ...

class StepHooks(ArtifactHooks, WorkflowHooks):
    """Combined protocol for step execution."""
    pass
```

#### Step 2: Create RuntimeHooks Class

Create `agent_runner_v2/runtime_hooks.py`:

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import workflow_runtime
    from . import step_execution_runtime
    # ... etc

class RuntimeHooks:
    """Explicit hook implementations with lazy module loading."""
    
    def __init__(self):
        self._workflow_runtime = None
        self._step_execution_runtime = None
        # ... etc
    
    @property
    def _workflow_rt(self):
        if self._workflow_runtime is None:
            from . import workflow_runtime
            self._workflow_runtime = workflow_runtime
        return self._workflow_runtime
    
    def missing_artifacts(self, keys: list[str], state: dict) -> list[str]:
        return self._workflow_rt.missing_artifacts(keys, state)
    
    # ... etc
```

#### Step 3: Migrate Functions Incrementally

For each function using `hooks: Any`:

1. Define a Protocol with only the methods it needs
2. Change type hint from `Any` to the Protocol
3. Update the RuntimeHooks class to implement the Protocol

#### Step 4: Deprecate _runtime_deps Pattern

1. Mark `_shared_runtime_deps` and `_manual_runtime_deps` as deprecated
2. Update run_agent.py to use RuntimeHooks class
3. Eventually remove the old modules

### Files to Modify

| File | Changes |
|------|---------|
| `hooks_protocols.py` | **NEW** - Protocol definitions |
| `runtime_hooks.py` | **NEW** - RuntimeHooks implementation |
| `step_execution_runtime.py` | Replace `hooks: Any` with `hooks: StepHooks` |
| `daemon_runtime.py` | Replace `hooks: Any` with specific protocols |
| `backend_execution.py` | Replace `hooks: Any` with specific protocols |
| `workflow_runtime.py` | No changes needed (leaf module) |
| `run_agent.py` | Use RuntimeHooks instead of _runtime_deps modules |
| `shared_runtime_deps.py` | Deprecate, delegate to RuntimeHooks |
| `manual_runtime_deps.py` | Deprecate, delegate to RuntimeHooks |

## Success Criteria

1. No `from . import module as _module` deferred imports remain
2. All `hooks: Any` parameters have specific Protocol types
3. All 367+ unit tests pass
4. No circular import errors on startup
5. Type checker (pyright/mypy) can validate hook usage

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing tests | Incremental migration, test after each file |
| Missing some hook methods | Comprehensive grep for `hooks\._` patterns |
| Runtime errors | Maintain backward compatibility during transition |
| Type checker errors | Use `TYPE_CHECKING` guards for imports |

## Implementation Order

1. Create `hooks_protocols.py` with core protocols
2. Create `runtime_hooks.py` with RuntimeHooks class
3. Update `step_execution_runtime.py` (most central)
4. Update `daemon_runtime.py`
5. Update `backend_execution.py`
6. Update `run_agent.py` to use new pattern
7. Deprecate old `_runtime_deps` modules
8. Run full test suite
