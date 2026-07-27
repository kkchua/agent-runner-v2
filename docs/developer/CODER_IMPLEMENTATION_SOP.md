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

If a task requires architecture or governance facts, obtain them from the active workflow bundle and current runner code, not from this file.
