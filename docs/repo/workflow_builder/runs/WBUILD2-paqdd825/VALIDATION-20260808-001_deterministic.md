---
doc_type: "deterministic_validation"
lifecycle_status: "final"
job_id: "WBUILD2-paqdd825"
---

# Deterministic Package Validation Report

- **Valid:** YES
- **Errors:** 0
- **Warnings:** 9

## Findings

| Level | Code | Message |
|---|---|---|
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'scan_components' requires 'COMPONENT_LIBRARY_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'scan_components' requires 'COMPONENT_SCHEMA_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'validate_components' requires 'COMPONENT_SCHEMA_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'plan_compositions' requires 'COMPOSITIONS_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'plan_compositions' requires 'DATA_SOURCE_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'generate_output' requires 'DATA_SOURCE_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'generate_output' requires 'OUTPUT_FORMAT_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'review_output' requires 'OUTPUT_FORMAT_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'refine_output' requires 'DATA_SOURCE_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
