"""[REMOVED] V2 daemon moved to agent_runner_v2/daemon_v2.py.

This file is kept as a redirect stub. All V2 daemon code now lives in
the self-contained daemon_v2.py module at the package root level.

The new module:
- Has zero imports from V1 daemon.py
- Implements pre-execution backend state sync (backend_state.json)
- Contains its own copies of shared utilities (ChildExecution, DaemonLogger, etc.)
"""
