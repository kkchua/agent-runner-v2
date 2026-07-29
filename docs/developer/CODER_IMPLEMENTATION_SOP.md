# Coder Implementation SOP

This file defines execution discipline only. It is not an architecture specification.

Mandatory rules:

1. Re-read the current task inputs and referenced files from disk before making changes.
2. Verify current code behavior before assuming APIs, paths, workflow names, or status contracts.
3. Prefer extending shared modules instead of adding duplicate logic.
4. Keep changes narrow and update the closest relevant tests.
5. When docs and code disagree, prefer the active workflow files and current code over old markdown.
6. Before returning success, verify the intended files exist and the relevant tests pass.
7. Use `.venv\Scripts\python` for Python and pytest commands in this repository.
8. All code must include docstrings for modules, classes, and functions following PEP 257 conventions.

## Pattern Compliance Rules (v0.3.0+)

When modifying code, you MUST follow the established patterns introduced in the v0.3.0 refactoring:

| Module | Required Pattern | Forbidden Pattern |
|--------|------------------|-------------------|
| `coder_adapters.py` | Use `CODER_REGISTRY` dispatch table | `if/elif` coder chains |
| `daemon.py` | Use `SupervisorConfig` dataclass | Functions with 10+ parameters |
| `exceptions.py` | Raise `ConfigurationError`, `NotFoundError` | Return `None` for error conditions |
| `config/*.py` | Exception-based error handling | `Optional[Path]` returns on errors |
| `hooks_protocols.py` | Protocol-based hooks | Deferred imports (`from . import x as _x`) |
| New config functions | `SupervisorConfig` pattern with dataclass | Long parameter lists |
| Error handling | Explicit exception types | Silent `None` returns |

### Pattern Quick Reference

**Adding a new coder:**
```python
# coder_adapters.py - Add to CODER_REGISTRY dict
CODER_REGISTRY["new_coder"] = _invoke_new_coder
# No if/elif chain modifications needed
```

**Adding daemon options:**
```python
# daemon.py - Extend SupervisorConfig dataclass
@dataclass
class SupervisorConfig:
    existing: str
    new_option: str = "default"  # Add with default

def _run_supervisor(cfg: SupervisorConfig) -> None:
    value = cfg.new_option  # Access via cfg object
```

**Adding error conditions:**
```python
# exceptions.py
class NewError(ConfigurationError):
    """Specific error for this condition."""

# Your code - raise, don't return None
raise NewError(f"Context: {details}")
```

**Adding hooks:**
```python
# hooks_protocols.py - Define Protocol first
class NewHooks(Protocol):
    def new_operation(self, arg: str) -> Result: ...

# runtime_hooks.py - Implement lazy loading
@property
def new_hooks(self) -> NewHooks:
    if self._new_hooks is None:
        from . import new_module
        self._new_hooks = new_module
    return self._new_hooks
```

### Verification Checklist

Before submitting changes, verify:
- [ ] No `if/elif` chains for dispatch logic (use registry pattern)
- [ ] Config objects use dataclasses with sensible defaults
- [ ] Error conditions raise explicit exceptions, don't return `None`
- [ ] New hooks use Protocol definitions in `hooks_protocols.py`
- [ ] Docstrings use raw strings (`r"""`) when containing backslashes (Windows paths, regex)

If a task requires architecture or governance facts, obtain them from the active workflow bundle and current runner code, not from this file.
