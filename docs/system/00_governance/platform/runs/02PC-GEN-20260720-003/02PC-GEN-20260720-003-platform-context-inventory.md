---
doc_type: "validation_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped platform context inventory"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-003"
generated_at: "2026-07-20T15:16:34+08:00"
---

# Platform Context Inventory

## Reference Files

- `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`
- `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md`
- Layer 1 governance set: `docs/system/00_governance/foundation/current/`

## Source Code Modules (read-only reference)

- `agent_runner_v2/runtime_context.py` (present)
- `agent_runner_v2/step_runner.py` (present)
- `agent_runner_v2/daemon.py` (present)
- `agent_runner_v2/coder_adapters.py` (present)
- `agent_runner_v2/coder_registry.py` (present)
- `agent_runner_v2/constants.py` (present)
- `agent_runner_v2/bundle_loader.py` (present)
- `agent_runner_v2/backend_client.py` (present)
- `agent_runner_v2/backend_execution.py` (present)
- `agent_runner_v2/action_result.py` (present)
- `agent_runner_v2/notification_manager.py` (present)
- `agent_runner_v2/workflow_packages/base.py` (present)
- `agent_runner_v2/workflow_packages/loader.py` (present)
- `agent_runner_v2/workflow_packages/actions.py` (missing)
- `agent_runner_v2/workflow_packages/registry.py` (present)
- `agent_runner_v2/actions/documentation_validation_core.py` (present)
- `agent_runner_v2/workflow_bundle_validator.py` (present)

## Known Workflow Bundles

- `00_bootstrap_lifecycle_admin_v1`
- `00_repo_master_docs_bootstrap_v1`
- `01_governance_foundation_v1`
- `_registry`

## Notes

- This artifact is comparison context only.
- It is not part of the permanent Layer 2 platform set.
- Source code modules are read-only reference for the runtime model.
- The curated reference list is fixed in the action implementation, not discovered at runtime.
