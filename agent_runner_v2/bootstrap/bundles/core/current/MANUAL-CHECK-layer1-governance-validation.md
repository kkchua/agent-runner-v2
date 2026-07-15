# Layer1 Governance Validation

- Job ID: `MANUAL-CHECK`
- Total checks: `50`
- Failed checks: `2`

## Failed Checks

- `bundle_taxonomy_scope` @ `docs\system\00_governance\bootstrap\BUNDLE_TAXONOMY.md`: BUNDLE_TAXONOMY must not present repo-analysis outputs or repo-local outputs as Layer 1 ownership.
- `runtime_governance_scope` @ `docs\system\00_governance\bootstrap\RUNTIME_GOVERNANCE.md`: RUNTIME_GOVERNANCE must define steady-state runtime governance, not repo-analysis ownership.
