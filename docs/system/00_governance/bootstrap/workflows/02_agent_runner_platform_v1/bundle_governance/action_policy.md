# Action Policy

Allowed action intents:

- `collect_context`
- `validate`
- `publish`
- `step_completion`

Allowed action behavior:

- gather read-only context inventories from curated reference paths (not automated discovery)
- run deterministic validation against staged platform core artifacts
- publish approved staged artifacts into the active Layer 2 platform location
- write meta sidecars and manifests required by the runner

Forbidden action intents:

- mutate platform runtime code during constitution generation
- perform automated codebase scanning or repo analysis
- generate Layer 3 bundle definitions, prompts, or artifact mappings
- rewrite `masterplan/` documents
- perform repository bootstrap or installation operations
- hide draft and active artifacts behind the same path without manifest tracking
