---
doc_type: "deterministic_validation"
lifecycle_status: "final"
job_id: "WBUILD2-dpxcr3x1"
---

# Deterministic Package Validation Report

- **Valid:** YES
- **Errors:** 0
- **Warnings:** 8

## Findings

| Level | Code | Message |
|---|---|---|
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'scan_components' requires 'COMPONENT_LIBRARY_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'plan_compositions' requires 'COMPOSITIONS_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'plan_compositions' requires 'DATA_SOURCE_DIR' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'generate_output' requires 'COMPONENT_SCHEMA_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'generate_output' requires 'OUTPUT_FORMAT_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'review_output' requires 'COMPONENT_SCHEMA_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'review_output' requires 'COMPOSITION_FORMAT_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'review_output' requires 'OUTPUT_FORMAT_FILE' but no prior step produces it. It may be an input artifact or a binding error. |
