---
doc_type: "test_criteria"
lifecycle_status: "draft"
domain: "ar_meta_builder"
total_criteria_count: 117
---

# Test Criteria for AR Meta Builder v1 Meta-Meta Builder

## Introduction

### Scope

This document defines the acceptance criteria for the AR Meta Builder v1 meta-meta builder workflow. These criteria apply to every artifact produced during the 9-phase, 21-step execution of ar_meta_builder_v1. Each criterion is specific, verifiable, and traceable to the composition system specification provided as input (WORKFLOW_SPEC_FILE: codebase_to_meta_v1.md).

### Purpose

The criteria serve three purposes:

1. Gatekeep decisions at each phase boundary -- the gatekeeper reviews use these criteria to approve or reject artifacts.
2. Reviewer guidance -- the reviewer uses these criteria to produce actionable feedback.
3. Refinement targeting -- when an artifact is rejected, the refine step uses failed criteria to scope the correction.

### Applicability

All criteria in this document apply to the AR Meta Builder v1 workflow. The input specification (codebase_to_meta_v1.md) describes a composition system that transforms codebase documentation into audience-specific Rich Markdown meta content files. The criteria verify that ar_meta_builder_v1 correctly processes that specification into the required output artifacts.

### Structure

- TC-001 through TC-008: Foundation Phase (Phase 1)
- TC-009 through TC-021: Component Schema (Phase 2)
- TC-022 through TC-035: Composition Format (Phase 3)
- TC-036 through TC-047: Output Format (Phase 4)
- TC-048 through TC-062: Operational Workflow (Phase 5)
- TC-063 through TC-070: Composition Standard (Phase 6)
- TC-071 through TC-077: Meta Composition Spec (Phase 7)
- TC-078 through TC-099: Package Assembly (Phase 8)
- TC-100 through TC-106: Promotion (Phase 9)
- TC-107 through TC-114: Negative Criteria
- TC-115 through TC-117: Self-Validation

---

## Criteria for Foundation Phase (Phase 1)

This phase contains 3 steps: generate_test_criteria (01), review_test_criteria (02), and refine_test_criteria (03, conditional). The phase produces the acceptance criteria document that all subsequent phases are measured against.

TC-001: The generated TEST_CRITERIA_FILE exists at the path declared in workflow.toml for the TEST_CRITERIA_FILE artifact key.

TC-002: The TEST_CRITERIA_FILE contains YAML frontmatter with the following mandatory fields: doc_type set to "test_criteria", lifecycle_status, domain set to "ar_meta_builder", and total_criteria_count.

TC-003: The total_criteria_count value in the frontmatter matches the actual number of TC-NNN entries in the document body.

TC-004: The document contains exactly 12 top-level sections: Introduction, Criteria for Foundation Phase (Phase 1), Criteria for Component Schema (Phase 2), Criteria for Composition Format (Phase 3), Criteria for Output Format (Phase 4), Criteria for Operational Workflow (Phase 5), Criteria for Composition Standard (Phase 6), Criteria for Meta Composition Spec (Phase 7), Criteria for Package Assembly (Phase 8), Criteria for Promotion (Phase 9), Negative Criteria, and Self-Validation.

TC-005: Every criterion identifier (TC-NNN) is unique across the entire document -- no duplicates exist.

TC-006: Every criterion uses specific, verifiable language -- no criterion contains vague phrases such as "must work properly", "must be correct", "should be good", or "must be handled appropriately".

TC-007: Every criterion traces to a specific requirement in the input specification (WORKFLOW_SPEC_FILE: codebase_to_meta_v1.md) -- no criterion invents requirements absent from the spec.

TC-008: The REVIEW_TEST_CRITERIA_FILE produced by step 02 contains a structured review with explicit APPROVED or REJECTED verdict per criterion category, and REJECTED categories include specific failure reasons with criterion identifiers.

---

## Criteria for Component Schema (Phase 2)

This phase contains 2 steps: generate_component_schema (04) and gatekeep_component_schema (05). It defines the Layer 1 component schema based on the spec Section 2.

TC-009: The COMPONENT_SCHEMA_FILE defines all 5 component types present in the spec Section 2: step_definition, role_policy, routing_pattern, prompt_pattern, and artifact_contract.

TC-010: The step_definition component type section includes all 5 steps from spec Section 2.1: scan_audiences (action), generate_meta_content (prompt), review_meta_content (prompt), refine_meta_content (prompt), and publish_meta_content (action).

TC-011: Each step_definition includes the required properties: step_name, step_type (prompt or action), purpose, and produces array. The step_type values match the spec (scan_audiences and publish_meta_content are "action"; the other three are "prompt").

TC-012: The role_policy component type section defines role assignments matching spec Section 2.2: scan_audiences has no role (action), generate_meta_content uses architect_standard, review_meta_content uses reviewer_standard, refine_meta_content uses architect_standard, and publish_meta_content has no role (action).

TC-013: The routing_pattern component type section defines routing matching spec Section 2.3: scan_audiences routes to generate_meta_content on success; generate_meta_content routes to review_meta_content; review_meta_content routes to publish_meta_content on success and to refine_meta_content on rejection (max 2 iterations); refine_meta_content routes to review_meta_content; publish_meta_content routes to step_completion.

TC-014: The routing_pattern for review_meta_content includes the exhaustion code META_CONTENT_REVIEW_EXHAUSTED with classification HUMAN_RETRY_REQUIRED, matching spec Section 2.3.

TC-015: The prompt_pattern component type section defines the 6 prompt patterns from spec Section 2.4: reference_inputs, generation_tasks, self_critic, self_validation, forbidden_content, and output_instructions.

TC-016: The prompt_pattern section specifies which patterns apply to which steps, matching spec Section 2.4: reference_inputs applies to all 3 prompt steps; generation_tasks applies to generate and refine; self_critic applies to all 3; self_validation applies to all 3; forbidden_content applies to generate and refine; output_instructions applies to all 3.

TC-017: The artifact_contract component type section defines all 5 artifacts from spec Section 2.5: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, and META_MANIFEST_FILE.

TC-018: Each artifact_contract includes the artifact_key, filename_pattern, required flag, and produced_by step matching spec Section 2.5.

TC-019: The component schema includes validation rules corresponding to spec Section 2.7: audiences directory existence (CRITICAL), frontmatter validity (CRITICAL), unique audience_id (CRITICAL), codebase manifest existence (CRITICAL), self-contained output (HIGH), source attribution (HIGH), no hallucination (CRITICAL), audience fidelity (HIGH), and YAML frontmatter on output (HIGH).

TC-020: The component schema includes at least one example for each of the 5 component types showing a valid instance with all required properties populated.

TC-021: The GATEKEEP_COMPONENT_SCHEMA_FILE produced by step 05 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-009 through TC-020) that failed.

---

## Criteria for Composition Format (Phase 3)

This phase contains 2 steps: generate_composition_format (06) and gatekeep_composition_format (07). It defines the Layer 2 composition format based on spec Section 3.

TC-022: The COMPOSITION_FORMAT_FILE defines the 3 binding rules from spec Section 3.2: codebase_docs (Ordered set, required), codebase_manifest (Singleton, required), and audience_defs (Unordered set, required).

TC-023: Each binding rule specifies the binding name, source, cardinality, required flag, and description matching spec Section 3.2.

TC-024: The composition format defines the override mechanism from spec Section 3.3, covering all 4 audience definition fields: tone (overrides default writing style), focus_areas (overrides which sections to emphasize), exclude (overrides which content to omit), and section_structure (overrides output section order).

TC-025: The override mechanism clarifies that these are audience-specific configuration parameters that drive LLM content generation behavior, not traditional component-level overrides, matching spec Section 3.3.

TC-026: The composition format defines the placeholder resolution mechanism from spec Section 3.4 with 4 priority-ordered data sources: Runtime context (priority 1, provides CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR), Audience definition (priority 2, provides audience_id, label, tone, focus_areas, section_structure), Codebase manifest (priority 3, provides doc_inventory, section_list, total_doc_count), and Job runtime (priority 4, provides job_id, seq, workspace_root).

TC-027: The composition format defines the composition structure from spec Section 3.1 with the two required fields: CODEBASE_DOC_ROOT (directory, required, approximately 155 files) and audiences/ (directory, required, audience definition plugin files).

TC-028: The composition format includes the example composition from spec Section 3.5 showing the input directory structure (CODEBASE_DOC_ROOT with subdirectories and audiences/) and the expected output structure (docs/repo/meta_content/current/ with per-audience subdirectories and meta_manifest.json).

TC-029: The composition format is internally consistent: binding rules reference component types from Phase 2 output, and placeholder resolution references data sources available from the workflow's runtime context.

TC-030: The composition format correctly maps the 3 binding rules to the component types: codebase_docs binds to artifact_contract instances representing codebase documentation files; codebase_manifest binds to the codebase_manifest.json artifact; audience_defs binds to the audience plugin files.

TC-031: The composition format preserves the constraint from the spec that there are no user-provided input artifacts -- all paths are resolved from the repo structure at runtime via context variables.

TC-032: The composition format correctly represents the audience definition plugin format from spec Section 2.6, including the 6 frontmatter fields: audience_id (string, required), label (string, required), tone (string, required), focus_areas (array, required), exclude (array, optional), and section_structure (array, required).

TC-033: The composition format specifies the initial audience set of 3 files: developer.md, architect.md, and executive.md, matching spec Section 2.6.

TC-034: The composition format includes ordering rules for how steps are sequenced, consistent with the routing patterns from Phase 2.

TC-035: The GATEKEEP_COMPOSITION_FORMAT_FILE produced by step 07 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-022 through TC-034) that failed.

---

## Criteria for Output Format (Phase 4)

This phase contains 2 steps: generate_output_format (08) and gatekeep_output_format (09). It defines the Layer 3 output format based on spec Section 4.

TC-036: The OUTPUT_FORMAT_FILE defines the YAML frontmatter schema for meta content files from spec Section 4.1, including fields: title, audience, audience_label, generated_date, source_version, and section_count.

TC-037: The output format defines the 7 resolution rules from spec Section 4.2: RR-META-001 (one file per audience), RR-META-002 (filename uses audience_id prefix META-{AUD}-{date}-{seq}.md), RR-META-003 (subdirectory matches audience_id), RR-META-004 (section order follows section_structure), RR-META-005 (tone follows tone field), RR-META-006 (excluded topics must not appear), RR-META-007 (source attribution via inline references).

TC-038: Each resolution rule (RR-META-001 through RR-META-007) specifies a verifiable condition that can be checked against generated output.

TC-039: The output format defines the 7 quality requirements from spec Section 4.3: QR-META-001 (Completeness, CRITICAL), QR-META-002 (Audience fidelity, CRITICAL), QR-META-003 (Self-contained, HIGH), QR-META-004 (Source attribution, HIGH), QR-META-005 (No hallucination, CRITICAL), QR-META-006 (YAML frontmatter, HIGH), QR-META-007 (ASCII-only, HIGH).

TC-040: Each quality requirement specifies a verifiable condition and a severity level matching spec Section 4.3.

TC-041: The output format includes the meta content file format example from spec Section 4.4, showing the expected structure of generated output with YAML frontmatter, overview section, module catalog, API reference, dependency map, and developer guide sections.

TC-042: The output format specifies that each meta content file must be self-contained (readable without reference to source codebase docs), matching spec Section 1.1 and QR-META-003.

TC-043: The output format specifies that each output file must be audience-faithful: tone, focus, and section structure match the audience definition, matching spec Section 1.1.

TC-044: The output format specifies that claims must be source-attributed to specific codebase doc files, matching spec Section 1.1 and QR-META-004.

TC-045: The output format specifies that no hallucination is permitted -- no information beyond what codebase docs provide, matching spec Section 1.1 and QR-META-005.

TC-046: The output format includes the output directory structure showing per-audience subdirectories under docs/repo/meta_content/current/ and the meta_manifest.json file, matching spec Section 3.5.

TC-047: The GATEKEEP_OUTPUT_FORMAT_FILE produced by step 09 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-036 through TC-046) that failed.

---

## Criteria for Operational Workflow (Phase 5)

This phase contains 2 steps: generate_operational_workflow (10) and gatekeep_operational_workflow (11). It defines the complete operational workflow based on spec Section 5.

TC-048: The OPERATIONAL_WORKFLOW_FILE defines exactly 5 phases matching spec Section 5.1: Scan (scan_audiences), Generate (generate_meta_content), Review (review_meta_content), Refine (refine_meta_content), and Publish (publish_meta_content).

TC-049: The operational workflow defines all 5 steps matching spec Section 2.1: scan_audiences, generate_meta_content, review_meta_content, refine_meta_content, and publish_meta_content.

TC-050: Each step is classified as either prompt-type or action-type matching the spec: scan_audiences is action, generate_meta_content is prompt, review_meta_content is prompt, refine_meta_content is prompt, publish_meta_content is action.

TC-051: The scan_audiences action step includes the error handling from spec Section 5.4: REJECT with reject_code NO_AUDIENCES_FOUND if audiences/ directory is missing or contains no .md files; log warning and skip files with invalid YAML frontmatter; REJECT with reject_code DUPLICATE_AUDIENCE_ID if two files define the same audience_id.

TC-052: The publish_meta_content action step implements the 4-stage publish lifecycle from spec Section 5.4: (1) Backup -- copy current/ to backups/BACKUP-{timestamp}/; (2) History -- move old current/ to history/{job_id}/; (3) Publish -- copy generated files to current/{audience_id}/; (4) Manifest -- write current/meta_manifest.json listing all published files.

TC-053: The operational workflow specifies the routing from spec Section 2.3: scan_audiences onsuccess leads to generate_meta_content; generate_meta_content onsuccess leads to review_meta_content; review_meta_content onsuccess leads to publish_meta_content; review_meta_content on_reject_refine leads to refine_meta_content (max 2 iterations); refine_meta_content onsuccess leads to review_meta_content; publish_meta_content onsuccess leads to step_completion.

TC-054: The operational workflow specifies the 5 output artifacts from spec Section 5.3: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, and META_MANIFEST_FILE.

TC-055: The operational workflow includes the domain-specific requirements from spec Section 5.5: audiences/ directory is part of the workflow package; publish lifecycle follows staging pattern (stage, review, refine, backup, history, publish); output paths follow standard staging pattern (current/, runs/, history/, backups/); generate step reads codebase_manifest.json to understand full doc inventory.

TC-056: The operational workflow specifies that the generate step selectively reads docs from each section as guided by each audience's focus_areas, matching spec Section 5.5.

TC-057: The artifact flow is consistent: every artifact consumed by a step is either an input declared in the workflow or produced by a preceding step.

TC-058: The WORKFLOW_SPEC_FILE is declared as an input to the workflow and is available to all steps that reference it.

TC-059: Each phase's output artifacts are available as context to all subsequent phases.

TC-060: The operational workflow correctly represents the META_CONTENT_FILE naming convention: {audience_id}/META-{AUD}-{date}-{seq}_{slug}.md, where AUD is derived from audience_id at runtime (DEV, ARCH, EXEC), matching spec Section 2.5.

TC-061: The operational workflow includes the review step's exhaustion handling: review_meta_content has max 2 iterations with code META_CONTENT_REVIEW_EXHAUSTED and classification HUMAN_RETRY_REQUIRED, matching spec Section 2.3.

TC-062: The GATEKEEP_OPERATIONAL_WORKFLOW_FILE produced by step 11 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-048 through TC-061) that failed.

---

## Criteria for Composition Standard (Phase 6)

This phase contains 2 steps: generate_composition_standard (12) and gatekeep_composition_standard (13). This is a v3 innovation.

TC-063: The COMPOSITION_STANDARD_FILE defines a composition standard with YAML frontmatter containing: standard_name, standard_version, component_type_count, and a body with component type definitions.

TC-064: The composition standard includes a standard_name field that identifies the standard for the codebase_to_meta domain (e.g., "CODEBASE_TO_META_STANDARD" or similar).

TC-065: The composition standard includes a standard_version field with a semantic version string (e.g., "1.0.0").

TC-066: The composition standard defines all component types used by the generated workflow, with each type in a subsection using heading format "#### Type N: type_name".

TC-067: The composition standard includes a schema_sections field listing the sections that the generated workflow's schemas must contain.

TC-068: The composition standard includes an extensibility_model section that describes how new component types or audience definitions can be added without breaking existing compositions.

TC-069: The composition standard's component_type_count in frontmatter matches the actual number of type definitions in the body.

TC-070: The GATEKEEP_COMPOSITION_STANDARD_FILE produced by step 13 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-063 through TC-069) that failed.

---

## Criteria for Meta Composition Spec (Phase 7)

This phase contains 1 step: generate_meta_composition_spec (14). This is a v3 innovation.

TC-071: The META_COMPOSITION_SPEC_FILE defines a meta composition specification with the required sections covering: Domain Overview, Component Schema, Composition Format, Output Format, and Operational Requirements.

TC-072: Section 1 (Domain Overview) includes domain name, label, job prefix, description, purpose, and the audience-based output model from spec Section 1.

TC-073: Section 2 (Component Schema) covers the 5 component types and validation rules derived from spec Section 2, including step_definition, role_policy, routing_pattern, prompt_pattern, and artifact_contract.

TC-074: Section 3 (Composition Format) covers the binding rules, override mechanism, and placeholder resolution from spec Section 3.

TC-075: Section 4 (Output Format) covers the YAML frontmatter schema, resolution rules, and quality requirements from spec Section 4.

TC-076: Section 5 (Operational Requirements) covers the 5 phases, step sequence, action step definitions, audience definition plugin format, and artifact declarations from spec Section 5.

TC-077: The meta composition spec is self-contained: it contains enough information for a downstream consumer to understand the meta content format and audience structure without reference to the original bootstrap spec.

---

## Criteria for Package Assembly (Phase 8)

This phase contains 6 steps: generate_package (15), validate_package_deterministic (16), gatekeep_package (17), review_package (18), refine_package (19, conditional), and the deterministic validation action.

TC-078: The WORKFLOW_MANIFEST_FILE (workflow.toml) produced by step 15 is valid TOML and parses without errors.

TC-079: The workflow.toml declares all 5 steps in the correct order matching spec Section 2.1: scan_audiences, generate_meta_content, review_meta_content, refine_meta_content, publish_meta_content.

TC-080: The workflow.toml declares the correct step types for each step: scan_audiences is action, generate_meta_content is prompt, review_meta_content is prompt, refine_meta_content is prompt, publish_meta_content is action.

TC-081: The workflow.toml declares all 5 output artifacts from spec Section 2.5: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, META_MANIFEST_FILE.

TC-082: The workflow.toml declares the routing from spec Section 2.3 including the review-meta-content to refine-meta-content reject loop with max 2 iterations and exhaustion code META_CONTENT_REVIEW_EXHAUSTED.

TC-083: The WORKFLOW_EXTENSIONS_FILE (context_extensions.py) produced by step 15 is syntactically valid Python that parses without errors.

TC-084: The context_extensions.py registers all artifact keys from spec Section 2.5 with their corresponding path patterns.

TC-085: The context_extensions.py includes hardcoded paths for the 3 context variables from spec Section 1.3: CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR.

TC-086: The WORKFLOW_ACTIONS_FILE (actions.py) produced by step 15 is syntactically valid Python that parses without errors.

TC-087: The actions.py implements the scan_audiences action from spec Section 5.4, including: scanning AUDIENCE_DIR for .md files, parsing YAML frontmatter, building audience inventory, and error handling for missing directory (NO_AUDIENCES_FOUND), invalid frontmatter (log and skip), and duplicate audience_id (DUPLICATE_AUDIENCE_ID).

TC-088: The actions.py implements the publish_meta_content action from spec Section 5.4, including: backup stage (copy current/ to backups/BACKUP-{timestamp}/), history stage (move current/ to history/{job_id}/), publish stage (copy to current/{audience_id}/), and manifest stage (write meta_manifest.json).

TC-089: The validate_package_deterministic action validates the generated package, including: TOML validity, Python syntax validity, artifact key coverage, action step implementation completeness, prompt file existence, and placeholder consistency.

TC-090: The audiences/ directory contains exactly 3 audience definition files from spec Section 2.6: developer.md, architect.md, and executive.md.

TC-091: Each audience definition file has valid YAML frontmatter with the 6 fields from spec Section 2.6: audience_id, label, tone, focus_areas, exclude (optional), and section_structure.

TC-092: The developer.md audience definition has focus_areas covering: module APIs and signatures, dependency relationships, setup and contribution guides, code patterns and conventions, extension points (matching spec Section 2.6).

TC-093: The architect.md audience definition has focus_areas covering: design decisions and rationale, pattern analysis, component relationships, dependency graphs, technical debt assessment, architectural constraints (matching spec Section 2.6).

TC-094: The executive.md audience definition has focus_areas covering: project overview, key metrics (module count, test coverage, workflow count), risk summary, progress status, cost/effort indicators (matching spec Section 2.6).

TC-095: All prompt template files exist for every prompt-type step: generate_meta_content, review_meta_content, and refine_meta_content.

TC-096: Each {PLACEHOLDER} in each prompt template is declared in the corresponding step's required_inputs or produces in workflow.toml.

TC-097: The WORKFLOW_README_FILE (README.md) exists and describes the workflow's purpose, inputs, outputs, audience definitions, and how to invoke it.

TC-098: The Specs/codebase_to_meta_v1.md file is content-identical to the input WORKFLOW_SPEC_FILE, preserving bootstrap chain integrity.

TC-099: The VALIDATION_REPORT_FILE produced by validate_package_deterministic lists all validation checks performed and their pass/fail status.

---

## Criteria for Promotion (Phase 9)

This phase contains 2 steps: promote_workflow_package (20) and step_completion (21).

TC-100: The WORKFLOW_PACKAGE_DIR_FILE artifact records the absolute path to the promoted workflow package directory under workflows/.

TC-101: The step_completion action records the final outcome of the workflow execution, including success status and a summary of produced artifacts.

TC-102: The promoted directory contains workflow.toml at its root.

TC-103: The promoted directory contains context_extensions.py and actions.py at its root.

TC-104: The promoted directory contains a prompts/ subdirectory with all prompt template files for the 3 prompt-type steps.

TC-105: The promoted directory contains an audiences/ subdirectory with the 3 audience definition files (developer.md, architect.md, executive.md).

TC-106: The promoted directory contains a Specs/ subdirectory with the embedded codebase_to_meta_v1.md spec.

---

## Negative Criteria

These criteria define what MUST NOT appear in any output artifact. Violation of any negative criterion is an automatic rejection.

TC-107: No output file contains non-ASCII characters. All files must use ASCII-only content. No em-dashes, no curly quotes, no Unicode characters.

TC-108: No output file contains a dangling reference -- every artifact key reference ({ARTIFACT_KEY}) in a prompt template must correspond to a declared artifact in the step's required_inputs or produces in workflow.toml.

TC-109: No output file contains scope invention -- every requirement, component type, binding rule, or step in the output must trace back to the input specification (codebase_to_meta_v1.md). No new component types, patterns, or phases may be introduced beyond what the spec defines for the codebase_to_meta domain.

TC-110: No YAML frontmatter block is missing any mandatory field specified for that document type.

TC-111: No output file contains vague criteria or requirements such as "must work properly", "must be correct", "should handle edge cases", or "must be robust".

TC-112: No output file contains resolved filesystem paths to governance or platform documents. Only filenames (e.g., METADATA_STANDARD.md) are permitted, not full paths.

TC-113: No output file redefines, contradicts, or extends Layer 1 (governance) or Layer 2 (platform constitution) content. These layers are read-only.

TC-114: No generated meta content file contains information not present in the source codebase documentation (no hallucination), as verified by source attribution checks.

---

## Self-Validation

These criteria verify the completeness and internal consistency of the test criteria document itself.

TC-115: The test criteria document covers all 9 phases of the AR Meta Builder v1 workflow: Foundation (Phase 1), Component Schema (Phase 2), Composition Format (Phase 3), Output Format (Phase 4), Operational Workflow (Phase 5), Composition Standard (Phase 6), Meta Composition Spec (Phase 7), Package Assembly (Phase 8), and Promotion (Phase 9).

TC-116: Every criterion (TC-001 through TC-114) is independently verifiable -- a gatekeeper can check each criterion without needing additional context beyond the input spec and the produced artifact.

TC-117: The total_criteria_count in the YAML frontmatter equals the actual count of TC-NNN entries in the document body. This self-referential check ensures the metadata is consistent with content.

End of Test Criteria Document
