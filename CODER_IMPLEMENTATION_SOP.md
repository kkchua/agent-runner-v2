# Coder Implementation SOP

Purpose

This document defines the mandatory working rules for any AI coder operating in this repository, including Claude Code, Qwen Code, Codex, OpenCode, or future coder backends.

Scope

This SOP applies before planning, before code changes, during implementation, and before returning completion status.

Mandatory Rules

1. Read the current source of truth first.
   - Read the task, implementation plan, review findings, validation findings, and any referenced workflow governance docs before changing logic.
   - Re-read the exact files from disk for the current step. Do not rely on memory from earlier runs.

2. Reconcile before assuming.
   - Inspect the actual repository state before assuming APIs, schemas, paths, side effects, status values, or workflow routing behavior.
   - If the codebase reality is uncertain, use inspect or reconcile language in planning artifacts and verify the code before implementation.

3. Preserve architecture unless the task explicitly changes it.
   - Reuse the existing execution path, data model, and state machine where possible.
   - Do not create parallel logic when an existing shared path can be extended.
   - Do not introduce a second source of truth for status, routing, notification, or artifact publication behavior.

4. Extend centralized modules instead of duplicating behavior.
   - If behavior already exists in a runner, router, state transition, notification, or artifact helper, refactor toward one shared function.
   - New entrypoints must call shared orchestration code rather than re-implementing completion, failure, or notification logic locally.

5. Prefer one state machine per concern.
   - Workflow state transitions must be decided in one authoritative place.
   - Notification emission must be derived from authoritative state transitions, not re-decided independently in multiple runtimes.
   - Backend, daemon, and manual execution modes must share the same transition contract.

6. Make enforcement executable, not only documented.
   - If a new rule matters operationally, enforce it in prompt injection, validation, tests, or code review gates.
   - Do not rely on a passive markdown document alone for important runtime behavior.

7. Write narrowly and verify immediately.
   - Change the smallest surface that achieves unification.
   - Add or update tests that prove manual mode and daemon or backend mode follow the same logic.
   - Prefer focused tests that assert shared helper usage and terminal state behavior.

8. Keep contracts explicit.
   - Artifact paths, status values, and sidecar or result structures must remain explicit and deterministic.
   - If a contract changes, update all participating execution modes together.

9. Fail closed on drift.
   - If you detect duplicated logic for the same concern, treat it as a design defect.
   - Refactor to a shared helper or shared transition function before adding more behavior to the duplicated paths.

10. Completion requires verification.
   - Before returning success, verify the intended files exist, tests relevant to the change pass, and the changed path is the shared path rather than a new fork.

11. Use the project .venv (Python 3.12) for all commands.
    - The default system Python on this machine is **3.14**, which has known
      compatibility issues (e.g. stdout buffering swallows print output).
    - Always invoke Python and pytest via the project virtual environment:
      ```batch
      .venv\Scripts\python -m pytest tests/unit/
      ```
    - Batch files (``run-*.bat``, ``run-tests.bat``) already activate ``.venv``
      automatically — prefer those for manual workflow runs.

Implementation Checklist

- Identify the authoritative module for the concern being changed.
- Identify all entrypoints that currently bypass that module.
- Refactor the concern behind one callable helper or state transition service.
- Update all entrypoints to use that shared path.
- Add regression tests for each execution mode affected.
- Only then add the new behavior itself.

Specific Guidance For This Repository

- Manual `run`, backend `worker`, and daemon supervisor flows must converge on the same post-step completion logic.
- Workflow completion, failure, waiting-for-human, artifact publication, and notifications should be emitted from shared transition code.
- Step-specific prompts may add role detail, but repository-wide safety and implementation rules should come from runner-injected instructions and shared validator expectations.

Non-Compliant Patterns

- Adding notification logic separately in manual, worker, and daemon paths.
- Recomputing terminal workflow status independently in each runtime.
- Creating new status values or event names in one path only.
- Implementing logic based on assumed repository structure without reading the current files.
- Returning success without adding tests for the shared path change.

Compliant Patterns

- Extract shared `finalize_*` or `transition_*` helpers and route every runtime through them.
- Add prompt injection for mandatory coder behavior across all coder backends.
- Add validator or reviewer checks for critical workflow invariants.
- Add tests that prove different execution modes reach the same terminal behavior.
