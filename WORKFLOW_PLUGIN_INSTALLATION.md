# Workflow Plugin Installation System

## Overview

The agent-runner-v2 now supports a plugin-based workflow installation system where each workflow can provide its own `install.py` script to handle global path installation. This eliminates the need to hardcode workflow-specific logic in the core `bundle_loader.py`.

## How It Works

### 1. Discovery Phase

When `ukbe-run-agent init` is executed, the `init_workspace()` function in `bundle_loader.py` performs three installation phases:

1. **Bootstrap Installation** (`install_bootstrap_bundle()`)
   - Copies Layer 1 governance foundation docs
   - Source: `docs/system/00_governance/foundation/current/`
   - Destination: `~/.ukbe-runner/bundles/core/current/foundation/`

2. **Platform Installation** (`install_platform_bundle()`)
   - Copies Layer 2 platform-specific docs
   - Source: `docs/system/00_governance/platform/<platform>/current/`
   - Destination: `~/.ukbe-runner/bundles/core/current/platform/<platform>/`

3. **Workflow Plugin Installation** (`install_workflow_plugins()`) ← NEW
   - Scans `agent_runner_v2/bootstrap/workflows/default/` for workflow packages
   - For each workflow with an `install.py` file, executes the `install_workflow()` function
   - Each workflow controls its own installation logic

### 2. Installation Phase

For each workflow with `install.py`:

```python
# bundle_loader.py dynamically imports and calls:
module = importlib.import_module(f"bootstrap.workflows.default.{workflow_name}.install")
result = module.install_workflow(
    project_root=workspace_root,
    runner_home=runner_home
)
```

### 3. Workflow Implementation

Each workflow that needs global installation provides an `install.py` file:

```python
# workflows/sdlc_00_delivery_scaffold_v1/install.py
from pathlib import Path
import shutil

def install_workflow(*, project_root: Path, runner_home: Path) -> dict:
    """Install workflow artifacts to global path."""
    source = project_root / "docs/system/00_governance/platform/agent_runner/sdlc/current"
    dest = runner_home / "bundles/core/current/platform/agent_runner/sdlc"
    
    if not source.exists():
        return {"status": "SKIPPED", "reason": "Source not found"}
    
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    
    return {
        "status": "INSTALLED",
        "source": str(source),
        "destination": str(dest),
        "files_copied": 22
    }
```

## Benefits

1. **Separation of Concerns**: Core `bundle_loader.py` doesn't need to know about workflow-specific paths
2. **Extensibility**: New workflows can add global installation by simply creating `install.py`
3. **Maintainability**: Each workflow owns its installation logic
4. **Flexibility**: Workflows can implement custom installation logic (conditional copies, transformations, etc.)

## Current Implementations

### SDLC Scaffold Workflow

**Workflow**: `sdlc_00_delivery_scaffold_v1`  
**Purpose**: Installs SDLC templates and agent contracts to global path  
**Source**: `docs/system/00_governance/platform/agent_runner/sdlc/current/`  
**Destination**: `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/`  
**Files**: 22 files (13 templates + 8 agent contracts + 1 manifest)

## Adding a New Workflow Plugin

To add global installation for a new workflow:

1. Create `install.py` in your workflow directory:
   ```
   workflows/<workflow_name>/install.py
   ```

2. Implement the `install_workflow()` function:
   ```python
   def install_workflow(*, project_root: Path, runner_home: Path) -> dict:
       # Your installation logic here
       return {"status": "INSTALLED", ...}
   ```

3. Copy `install.py` to the bootstrap directory:
   ```
   agent_runner_v2/bootstrap/workflows/default/<workflow_name>/install.py
   ```

4. Run `ukbe-run-agent init` to test

## Example Output

```json
{
  "workflow_plugins_install": {
    "workflows_scanned": 13,
    "workflows_installed": 1,
    "installed": [
      {
        "workflow": "sdlc_00_delivery_scaffold_v1",
        "result": {
          "status": "INSTALLED",
          "source": "D:\\...\\sdlc\\current",
          "destination": "C:\\Users\\kengk\\.ukbe-runner\\bundles\\core\\current\\platform\\agent_runner\\sdlc",
          "files_copied": 22
        }
      }
    ]
  }
}
```

## Testing

To verify the system is working:

```bash
# Run init command
ukbe-run-agent init

# Check the output for "workflow_plugins_install" section
# Verify files were copied to ~/.ukbe-runner/bundles/core/current/...
```

## Future Enhancements

Potential improvements:
- Support for uninstall hooks (`uninstall_workflow()`)
- Pre/post installation hooks
- Dependency management between workflow plugins
- Installation status tracking and rollback
