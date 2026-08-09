---
doc_type: "deterministic_validation"
lifecycle_status: "final"
job_id: "WBUILD3-rcmznh0q"
---

# Deterministic Package Validation Report

- **Valid:** NO
- **Errors:** 18
- **Warnings:** 2

## Findings

| Level | Code | Message |
|---|---|---|
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'validate_package_deterministic' requires 'SPECS_BUILDER_SPEC_FILE' but no prior step produces it. |
| warning | UNRESOLVABLE_INPUT_ARTIFACT | Step 'promote_workflow_package' requires 'SPECS_BUILDER_SPEC_FILE' but no prior step produces it. |
| error | MISSING_PROMPT_FILE | Step 'generate_test_criteria' references prompt 'prompts/01_generate_test_criteria.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'review_test_criteria' references prompt 'prompts/02_review_test_criteria.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'refine_test_criteria' references prompt 'prompts/03_refine_test_criteria.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_component_schema' references prompt 'prompts/04_generate_component_schema.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_component_schema' references prompt 'prompts/05_gatekeep_component_schema.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_composition_format' references prompt 'prompts/06_generate_composition_format.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_composition_format' references prompt 'prompts/07_gatekeep_composition_format.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_output_format' references prompt 'prompts/08_generate_output_format.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_output_format' references prompt 'prompts/09_gatekeep_output_format.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_operational_workflow' references prompt 'prompts/10_generate_operational_workflow.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_operational_workflow' references prompt 'prompts/11_gatekeep_operational_workflow.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_composition_standard' references prompt 'prompts/12_generate_composition_standard.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_composition_standard' references prompt 'prompts/13_gatekeep_composition_standard.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_meta_composition_spec' references prompt 'prompts/14_generate_meta_composition_spec.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'generate_package' references prompt 'prompts/15_generate_package.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'gatekeep_package' references prompt 'prompts/17_gatekeep_package.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'review_package' references prompt 'prompts/18_review_package.txt' but file does not exist |
| error | MISSING_PROMPT_FILE | Step 'refine_package' references prompt 'prompts/19_refine_package.txt' but file does not exist |
