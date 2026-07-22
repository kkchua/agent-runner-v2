# UKBE Delivery Documentation — Migrated Structure

This folder is the migrated UKBE delivery documentation set, normalized into the new delivery layout.

## Structure
- `00_templates/` → canonical templates and registry
- `01_initiatives/` → high-level initiatives
- `02_plans/` → executable plans
- `02_plans/artifacts/` → supporting plan artifacts such as task graphs
- `03_tasks/` → tasks plan (what)
- `04_implementation_plans` → tasks implementation plan (how)
- `05_reviews/` → reviews, approvals, and validation records
- `06_memory/` → durable delivery memory
- `07_master_prompts/` → agent master prompt 
- `08_agents/` → agent contracts


## Migration Notes
- Legacy archived templates were preserved under `00_templates/_legacy/`.
- Old `04_decisions/` content was migrated into `05_reviews/` because approval decisions behave as review outputs in the new system.
- Old test plans were normalized into task documents.
- Old test results and outcomes were normalized into review documents.
- Existing IDs from legacy docs were preserved in notes where useful, while new delivery IDs were assigned for the new structure.

## Current Coverage
This migrated bundle includes:
- 1 initiative
- 1 main plan
- 1 plan artifact (task graph)
- 9 task documents
- 5 implementation plans
- 7 review documents
- 1 delivery memory document
- 7 agent master prompts
- 6 agent documents
