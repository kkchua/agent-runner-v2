# Core Governance Bundle Contract

This workflow bundle owns only ecosystem-level governance for the agent-runner documentation model.

## Scope

- Govern the universal documentation contract for the agent-runner ecosystem.
- Govern the three-layer documentation model:
  - ecosystem master docs define universal rules
  - workflow bundle master docs travel with each installed bundle in the global runner home
  - repo-local generated docs live under `docs/repo/*`
- Govern only the four canonical ecosystem master docs under `docs/system/00_governance/bootstrap/`.

## Non-Scope

- Do not classify repo-derived analysis as core governance.
- Do not treat codebase scans, system overviews, audience outputs, or delivery run state as canonical governance.
- Do not claim ownership of repo-local outputs under `docs/repo/*`.
- Do not mutate unrelated root guidance files as part of this bundle.

## Operational Rules

- The canonical source of truth for this bundle is its workflow-owned governance manifest plus this document.
- Bundle-local agent adapter files are generated from this canonical source and must not drift independently.
- During publish or install, the generated adapter files must travel with the bundle into the global runner home.
- When prompt instructions conflict with repo-local stale docs, this bundle contract wins.
