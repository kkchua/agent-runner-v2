# agent-runner-v2 Specialist Agent Instructions

Use [README.md](../../README.md) as the first lookup source for this repository — it is the master documentation index.

## Purpose

This instruction file defines how a specialized coding or review agent should navigate `agent-runner-v2` without rediscovering the repository from scratch on each task.

The goal is to reduce wasted repo scans and avoid human interruption for path-finding tasks such as:

- where Layer 1 governance lives
- where the active platform constitution lives
- where workflow bundle contracts live
- where job evidence and job history live
- where daemon and worker runtime behavior is defined
- where coder integration, metadata, validation, and routing are implemented

## Default Operating Model

Follow this lookup order unless the user explicitly asks for something else:

1. Read `README.md` at the project root (master documentation index).
2. Start from the README's curated document links for the topic.
3. Prefer published governance and platform docs before source code.
4. Use source code only to answer implementation details or verify behavior.
5. Use targeted searches only inside the relevant path group.
6. Do not begin with a repo-wide scan.

## Path Priorities

When the question is about governance or platform rules:

- Start with `docs/system/00_governance/foundation/current/` for Layer 1.
- Start with `docs/system/00_governance/platform/agent_runner/current/` for Layer 2 platform constitution.
- Use `masterplan/` only for design intent, layer boundaries, and workflow specifications.

When the question is about workflow bundles:

- Start with `workflows/<workflow_name>/workflow.toml`.
- Then inspect `bundle_governance.toml`, `bundle_governance/`, and bundle-local `actions.py`.
- Use `docs/system/00_governance/platform/agent_runner/current/BUNDLE_AUTHORING_CONTRACT.md` for platform-wide bundle rules.

When the question is about runtime implementation:

- Start with `docs/system/00_governance/platform/agent_runner/current/RUNTIME_MODEL.md`.
- Then inspect the smallest relevant module set, usually one of:
  - `agent_runner_v2/run_agent.py`
  - `agent_runner_v2/step_runner.py`
  - `agent_runner_v2/workflow_router.py`
  - `agent_runner_v2/job_state.py`
  - `agent_runner_v2/daemon.py`
  - `agent_runner_v2/daemon_runtime.py`
  - `agent_runner_v2/coder_adapters.py`
  - `agent_runner_v2/coder_registry.py`

When the question is about job history or evidence:

- Use `docs/system/00_governance/*/runs/` and `docs/system/00_governance/*/history/` for governance or platform-document generation evidence.
- Use `~/.ukbe-runner/jobs/<workflow_name>/<job_id>/` for runtime job state outside the repository.

## Behavior Rules

- Treat `masterplan/` and published governance/platform docs as authoritative reference, not as implementation scratch space.
- Prefer `current/` over `history/` unless the user asks for prior versions or audit trails.
- Prefer exact file paths in answers.
- If a question maps cleanly to a manifest topic, do not broaden the search.
- If implementation details conflict with published docs, surface the conflict explicitly instead of silently choosing one.

## When To Search

Search is a fallback, not the default.

Use `rg` only after:

1. checking the README.md
2. checking the curated starting path for the topic
3. narrowing the search to the smallest relevant subtree

Good examples:

- search only `docs/system/00_governance/platform/agent_runner/current/` for metadata rules
- search only `agent_runner_v2/` for daemon or router implementation
- search only `workflows/02_agent_runner_platform_v1/` for bundle-local behavior

Bad examples:

- scanning the whole repository to locate Layer 1 governance
- scanning the whole repository to find runtime model docs
- scanning unrelated workflow bundles before checking the platform constitution

## Answering Style

When answering a repository navigation question:

- name the authoritative location first
- name the secondary verification location second
- state whether the answer came from docs, code, or both
- include exact paths

Example pattern:

`Layer 1 governance is in docs/system/00_governance/foundation/current/. If you need the active published version record, also check docs/system/00_governance/foundation/current/governance_set_manifest.json.`

## Pattern Quick Reference

When modifying code in these modules, follow the established patterns (v0.3.0+):

| Module | Pattern | Implementation |
|--------|---------|----------------|
| `coder_adapters.py` | Registry dispatch | Add to `CODER_REGISTRY` dict, no if/elif |
| `daemon.py` | Config dataclass | Extend `SupervisorConfig` with defaults |
| `exceptions.py` | Exception-based errors | Raise `ConfigurationError`/`NotFoundError` |
| `hooks_protocols.py` | Protocol hooks | Define Protocol → lazy-load in `runtime_hooks.py` |

**Reference:** `docs/developer/CODER_IMPLEMENTATION_SOP.md` — Pattern Compliance Rules section has copy-paste examples and verification checklist.

## Maintenance

If repository structure changes:

1. update `README.md` at the project root
2. keep this instruction file aligned with the README
3. preserve topic-based routing so future agents do not regress to repo-wide scanning
