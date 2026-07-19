# Action Policy

Allowed action intents:

- `collect_context`
- `validate`
- `publish`
- `step_completion`

Allowed action behavior:

- gather read-only context inventories
- run deterministic validation against staged artifacts
- publish approved staged artifacts into the active Layer 1 location
- write meta sidecars and manifests required by the runner

Forbidden action intents:

- mutate runtime implementation code during governance generation
- perform repository bootstrap setup
- generate Layer 2 platform constitutions
- generate Layer 3 bundle-local prompts or artifact mappings
- rewrite `masterplan/` documents
- hide draft and active artifacts behind the same path without manifest tracking
