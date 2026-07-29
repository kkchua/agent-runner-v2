# Operator Console Refactoring Design

## Phase 4.2: Refactor Deep Nesting in operator_console/app.py

## Current State Analysis

### The Problem

The `operator_console/app.py` file is 1123 lines with significant nesting issues:

1. **Deeply Nested Function Definitions**: Callback functions defined inside other functions
   - `on_browse_click` (line 362) defined inside `build_dynamic_inputs`
   - `on_worker_id_changed` (line 482) defined inside `app`
   - `on_repo_changed` (line 516) defined inside `app`
   - `on_workflow_changed` (line 544) defined inside `app`

2. **God Function**: The `app` function contains:
   - UI initialization (~200 lines)
   - Event handlers (~300 lines)
   - Business logic mixed with UI code
   - All state as closure variables

3. **Tight Coupling**: Business logic is tightly coupled to Flet UI components

### Code Smells Identified

**Nested Closure Pattern** (Line 362):
```python
def build_dynamic_inputs(...):
    async def on_browse_click(e, k=key, f=tf, d=input_dir):
        # 15+ lines of async code with access to outer scope
        ...
```

**Mixed Concerns** (Lines 482-544):
```python
def app(page: ft.Page):
    # UI setup
    ...
    def on_worker_id_changed(_event=None):
        # Business logic mixed with UI updates
        ...
    def on_repo_changed(_event=None):
        # Business logic mixed with UI updates
        ...
```

**Deep Conditional Nesting** (Line 366-385):
```python
if _is_cross_os(...):
    file_picker.root_directory = ...
elif d and d != ".":
    resolved = ...
    if resolved.is_dir():
        file_picker.root_directory = ...
    else:
        file_picker.root_directory = ...
else:
    file_picker.root_directory = ...
```

## Proposed Solution

### Strategy: Extract Method Pattern + State Class

Convert the closure-based pattern to a class-based approach with explicit state management.

### Implementation Steps

#### Step 1: Create AppState Class

Create `operator_console/state.py`:

```python
@dataclass
class ConsoleState:
    """Holds all mutable console state, replacing closure variables."""
    page: ft.Page
    config: ConsoleConfig
    selected_worker_id: str = ""
    selected_repo: RepoEntry | None = None
    selected_workflow: WorkflowEntry | None = None
    input_fields: dict[str, ft.TextField] = field(default_factory=dict)
    dynamic_inputs: list[ft.Control] = field(default_factory=list)
```

#### Step 2: Extract Event Handlers to Methods

Create `operator_console/handlers.py`:

```python
class EventHandlers:
    """Extracted event handlers as methods instead of closures."""
    
    def __init__(self, state: ConsoleState):
        self.state = state
    
    async def on_browse_click(
        self,
        e: ft.ControlEvent,
        *,
        key: str,
        field: ft.TextField,
        input_dir: str | None,
    ) -> None:
        """Handle file browse button click."""
        # Implementation extracted from nested closure
        ...
    
    def on_worker_id_changed(self, _event=None) -> None:
        """Handle worker ID dropdown change."""
        ...
    
    def on_repo_changed(self, _event=None) -> None:
        """Handle repository dropdown change."""
        ...
    
    def on_workflow_changed(self, _event=None) -> None:
        """Handle workflow dropdown change."""
        ...
```

#### Step 3: Extract UI Builders

Create `operator_console/builders.py`:

```python
class UIBuilder:
    """Extracted UI building logic."""
    
    def __init__(self, state: ConsoleState, handlers: EventHandlers):
        self.state = state
        self.handlers = handlers
    
    def build_dynamic_inputs(self, workflow: WorkflowEntry) -> ft.Container:
        """Build dynamic input controls for workflow."""
        ...
    
    def build_main_layout(self) -> ft.Column:
        """Build main application layout."""
        ...
```

#### Step 4: Refactor File Picker Logic

Extract the deeply nested path resolution logic:

```python
def resolve_file_picker_root(
    repo_path: str,
    input_dir: str | None,
    os_type: str,
    is_cross_os: bool,
) -> str:
    """Determine file picker root directory.
    
    Extracted from nested if/elif/else in on_browse_click.
    """
    if is_cross_os:
        return str(Path.home())
    
    if input_dir and input_dir != ".":
        resolved = Path(repo_path) / input_dir
        if resolved.is_dir():
            return str(resolved)
    
    return repo_path
```

### Files to Modify

| File | Changes |
|------|---------|
| `operator_console/state.py` | **NEW** - ConsoleState dataclass |
| `operator_console/handlers.py` | **NEW** - EventHandlers class |
| `operator_console/builders.py` | **NEW** - UIBuilder class |
| `operator_console/app.py` | Refactor to use extracted classes |

### Success Criteria

1. `app.py` reduced from 1123 to <600 lines
2. No function definitions nested more than 2 levels deep
3. All event handlers are module-level or class methods
4. State is explicit in ConsoleState, not closures
5. All 367+ unit tests pass
6. Console functionality unchanged

## Implementation Plan

### Phase A: Create State Class

1. Create `state.py` with ConsoleState dataclass
2. Identify all closure variables in `app()` function
3. Map them to ConsoleState fields

### Phase B: Extract Handlers

1. Create `handlers.py` with EventHandlers class
2. Convert each nested function to a method
3. Update state references to use self.state

### Phase C: Extract Builders

1. Create `builders.py` with UIBuilder class
2. Move UI construction logic
3. Pass handlers to builder methods

### Phase D: Refactor app.py

1. Import new classes
2. Replace closures with class instances
3. Verify functionality

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking UI interactions | Comprehensive manual testing after refactor |
| State synchronization issues | Keep state centralized in ConsoleState |
| Event handler binding | Ensure handlers bound correctly to UI controls |
| Async function extraction | Test async/await patterns carefully |
