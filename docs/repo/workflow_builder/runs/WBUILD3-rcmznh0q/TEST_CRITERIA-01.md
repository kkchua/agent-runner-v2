---
doc_type: "test_criteria"
lifecycle_status: "draft"
domain: "workflow_builder"
total_criteria_count: 64
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_test_criteria"
---

# Test Criteria: Workflow Builder v3

## 1. Introduction

### 1.1 Scope

This document defines the acceptance criteria for the Workflow Builder v3
meta-meta builder. The criteria apply to every artifact produced during the
Workflow Builder workflow execution (job prefix WBUILD3). Each criterion is
specific, verifiable, and traceable to a section of the composition system
specification (WORKFLOW_SPEC_FILE).

### 1.2 Purpose

The acceptance criteria serve three roles:

1. Gate inputs for the gatekeep steps -- each gatekeeper checks the
   generated artifact against the criteria defined here for the
   corresponding phase.
2. Review inputs for the review steps -- reviewers evaluate whether the
   artifact satisfies the criteria before APPROVED status.
3. Validation inputs for the deterministic validation step -- the
   validate_package_deterministic action checks structural criteria
   programmatically.

### 1.3 Applicability

These criteria apply to the Workflow Builder v3 workflow only. They cover
all 9 phases, all 22 steps, and all output artifacts declared in the
specification. Criteria are numbered sequentially (TC-001 through TC-052)
for traceability.

---

## 2. Criteria for Foundation Phase (Phase 1)

Phase 1 contains steps 01 (generate_test_criteria), 02
(review_test_criteria), and 03 (refine_test_criteria).

TC-001: The TEST_CRITERIA_FILE artifact must exist at the declared output
path after step 01 completes with APPROVED status.

TC-002: The TEST_CRITERIA_FILE must include YAML frontmatter containing
the fields doc_type, lifecycle_status, domain, and total_criteria_count.

TC-003: The total_criteria_count value in the frontmatter must equal the
actual number of TC-NNN entries present in the document body.

TC-004: Each criterion in the TEST_CRITERIA_FILE must contain a verifiable
condition -- it must specify a concrete artifact property, file existence
check, field presence requirement, or structural constraint. Criteria
containing only subjective language such as "must be correct" or
"must work properly" are rejected.

TC-005: The review_test_criteria step must produce a
REVIEW_TEST_CRITERIA_FILE artifact with status APPROVED or REJECTED.

TC-006: If review_test_criteria returns REJECTED, the refine_test_criteria
step must execute and produce an updated TEST_CRITERIA_FILE. If review
returns APPROVED, refine_test_criteria must not execute.

TC-007: Every criterion in the TEST_CRITERIA_FILE must trace to at least
one section of the WORKFLOW_SPEC_FILE. Untraceable criteria are rejected
as scope invention.

---

## 3. Criteria for Component Schema (Phase 2)

Phase 2 contains steps 04 (generate_component_schema) and 05
(gatekeep_component_schema).

TC-008: The COMPONENT_SCHEMA_FILE must define exactly 8 component types:
step_definition, role_policy, routing_pattern, prompt_pattern,
artifact_contract, composition_standard, output_variance, and domain_spec.

TC-009: Each of the 8 component types must include the following 5
required common properties: component_id, component_type, name, version,
and description.

TC-010: Each component type that declares optional properties must list
them from the set: duration_range, platforms, tags. No other optional
properties are permitted unless explicitly specified in the spec.

TC-011: The COMPONENT_SCHEMA_FILE must define all validation rules
VR-001 through VR-016. Each rule must have a unique rule ID, a
machine-readable description, and a severity level.

TC-012: Validation rule VR-015 must enforce that every step referencing
WORKFLOW_SPEC_FILE in its prompt declares WORKFLOW_SPEC_FILE in
required_inputs.

TC-013: Validation rule VR-016 must enforce that both generate_package
and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE in their
produces lists.

TC-014: The COMPONENT_SCHEMA_FILE must include the dynamic discovery
mechanism specification: a function discover_component_types that accepts
a standard file path and returns a list of component type names parsed
from YAML frontmatter and section headings.

TC-015: The COMPONENT_SCHEMA_FILE must include at least one example for
each of the 8 component types demonstrating valid instantiation.

TC-016: The gatekeep_component_schema step must produce a
GATEKEEP_COMPONENT_SCHEMA_FILE artifact. Its status must be APPROVED only
if all criteria TC-008 through TC-015 pass.

---

## 4. Criteria for Composition Format (Phase 3)

Phase 3 contains steps 06 (generate_composition_format) and 07
(gatekeep_composition_format).

TC-017: The COMPOSITION_FORMAT_FILE must define exactly 9 binding rules:
the 8 base bindings (step_bindings, artifact_bindings,
composition_standard_binding, output_variances, and 4 others from the
spec's composition structure table) plus the self_bootstrap binding.

TC-018: The self_bootstrap binding must specify 4 required fields:
bootstrap_spec_key, bootstrap_spec_target, bootstrap_version, and
next_version_pattern.

TC-019: The COMPOSITION_FORMAT_FILE must define exactly 6 workflow
patterns. One of these patterns must be named meta_meta_builder.

TC-020: The COMPOSITION_FORMAT_FILE must define an override mechanism
that allows composition-level values to override component defaults.

TC-021: The COMPOSITION_FORMAT_FILE must define placeholder resolution
rules covering at least 4 data sources: user input, workflow context,
composition bindings, and discovery.

TC-022: The COMPOSITION_FORMAT_FILE must define ordering rules for
step_bindings that enforce sequential execution with explicit routing.

TC-023: The gatekeep_composition_format step must produce a
GATEKEEP_COMPOSITION_FORMAT_FILE artifact. Its status must be APPROVED
only if all criteria TC-017 through TC-022 pass.

---

## 5. Criteria for Output Format (Phase 4)

Phase 4 contains steps 08 (generate_output_format) and 09
(gatekeep_output_format).

TC-024: The OUTPUT_FORMAT_FILE must define a 3-part output structure:
Part 1 is Standards/COMPOSITION_STANDARD.md, Part 2 is
Specs/{builder_name}.md, Part 3 is the workflow package directory
containing workflow.toml, context_extensions.py, actions.py, prompts/,
and README.md.

TC-025: The OUTPUT_FORMAT_FILE must define exactly 9 resolution rules
(RR-001 through RR-009). Each rule must specify a source and a target.

TC-026: Resolution rule RR-008 must map the self_bootstrap_binding to
the file path Specs/{builder_name}.md as a copy of WORKFLOW_SPEC_FILE.

TC-027: Resolution rule RR-009 must map DISCOVERED_COMPONENT_TYPES to
all prompt templates for dynamic type list injection.

TC-028: The OUTPUT_FORMAT_FILE must define exactly 12 quality
requirements (QR-001 through QR-012). Each requirement must have a
severity level (CRITICAL, HIGH, or MEDIUM).

TC-029: Quality requirement QR-009 must enforce that the Standards/
directory exists and contains COMPOSITION_STANDARD.md at severity
CRITICAL.

TC-030: Quality requirement QR-010 must enforce that the Specs/
directory exists and contains at least one .md file at severity CRITICAL.

TC-031: Quality requirement QR-011 must enforce that all prompt
{PLACEHOLDERS} are declared in their step's required_inputs or produces
at severity CRITICAL.

TC-032: Quality requirement QR-012 must enforce that both
generate_package and refine_package declare
STANDARDS_COMPOSITION_STANDARD_FILE at severity CRITICAL.

TC-033: The OUTPUT_FORMAT_FILE must define the promotion contract
specifying source-to-target mappings for all 9 file/directory types
(workflow.toml, context_extensions.py, actions.py, README.md, prompts/,
Standards/, Specs/, .env.sample, config.json.sample).

TC-034: The gatekeep_output_format step must produce a
GATEKEEP_OUTPUT_FORMAT_FILE artifact. Its status must be APPROVED only
if all criteria TC-024 through TC-033 pass.

---

## 6. Criteria for Operational Workflow (Phase 5)

Phase 5 contains steps 10 (generate_operational_workflow) and 11
(gatekeep_operational_workflow).

TC-035: The OPERATIONAL_WORKFLOW_FILE must define exactly 9 phases:
Foundation, Component Schema, Composition Format, Output Format,
Operational Workflow, Composition Standard, Meta Composition Spec,
Package Assembly, and Promotion.

TC-036: The OPERATIONAL_WORKFLOW_FILE must define exactly 22 steps
across the 9 phases, numbered 01 through 22 in sequential order.

TC-037: Each step in the OPERATIONAL_WORKFLOW_FILE must declare a step
type of either "prompt" (LLM-driven) or "action" (Python-driven).

TC-038: The OPERATIONAL_WORKFLOW_FILE must define routing for each step:
onsuccess routes to the next step, on_reject_refine routes to the
corresponding refine step where applicable.

TC-039: Phase 1 must contain steps 01 (generate_test_criteria), 02
(review_test_criteria), and 03 (refine_test_criteria) with a reject
refine loop between 02 and 03.

TC-040: Phase 8 must contain steps 15 (generate_package), 16
(embed_builder_spec), 17 (validate_package_deterministic), 18
(gatekeep_package), 19 (review_package), and 20 (refine_package). The
embed_builder_spec step must be positioned after generate_package and
before validate_package_deterministic.

TC-041: Phase 9 must contain steps 21 (promote_workflow_package) and 22
(step_completion).

TC-042: The OPERATIONAL_WORKFLOW_FILE must declare all input and output
artifacts for each step, matching the artifact key names specified in
the spec (Section 5.6 and 5.7).

TC-043: The artifact flow must be internally consistent -- every
artifact consumed by a step must be produced by a preceding step or
declared as a workflow input.

---

## 7. Criteria for Composition Standard (Phase 6)

Phase 6 contains steps 12 (generate_composition_standard) and 13
(gatekeep_composition_standard). This phase represents a v3 innovation.

TC-044: The COMPOSITION_STANDARD_FILE must include a standard_name
field in its YAML frontmatter identifying the composition standard by
name.

TC-045: The COMPOSITION_STANDARD_FILE must include a standard_version
field in its YAML frontmatter with a semantic version string.

TC-046: The COMPOSITION_STANDARD_FILE must include a
component_types_defined section listing all 8 component types with their
schemas.

TC-047: The COMPOSITION_STANDARD_FILE must include a component_type_count
field in its YAML frontmatter that equals the number of component type
definitions in the body.

TC-048: The COMPOSITION_STANDARD_FILE must include schema_sections that
define the structure and properties for each component type.

TC-049: The COMPOSITION_STANDARD_FILE must include an
extensibility_model section describing how new component types can be
added without breaking existing compositions.

TC-050: The gatekeep_composition_standard step must produce a
GATEKEEP_COMPOSITION_STANDARD_FILE artifact. Its status must be APPROVED
only if all criteria TC-044 through TC-049 pass.

---

## 8. Criteria for Meta Composition Spec (Phase 7)

Phase 7 contains step 14 (generate_meta_composition_spec). This phase
represents a v3 innovation.

TC-051: The META_COMPOSITION_SPEC_FILE must contain exactly 5 sections:
(1) domain overview, (2) component schema, (3) composition format,
(4) output format, and (5) operational requirements.

TC-052: The META_COMPOSITION_SPEC_FILE must include a self-bootstrapping
capability description that explains how the generated builder can
process its own spec to produce the next version, including the
bootstrap chain invariant.

---

## 9. Criteria for Package Assembly (Phase 8)

Phase 8 contains steps 15 (generate_package), 16 (embed_builder_spec),
17 (validate_package_deterministic), 18 (gatekeep_package), 19
(review_package), and 20 (refine_package).

TC-053: The generate_package step must produce the following artifacts:
WORKFLOW_MANIFEST_FILE (workflow.toml), WORKFLOW_EXTENSIONS_FILE
(context_extensions.py), WORKFLOW_ACTIONS_FILE (actions.py),
WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, and
STANDARDS_COMPOSITION_STANDARD_FILE.

TC-054: The embed_builder_spec step must copy the input WORKFLOW_SPEC_FILE
to the output Specs/{builder_name}.md path. It must produce the
SPECS_BUILDER_SPEC_FILE artifact. The embedded file content must be
identical to the source WORKFLOW_SPEC_FILE.

TC-055: The validate_package_deterministic step must execute exactly 11
validation checks: (1) TOML parse validity, (2) Python syntax check,
(3) TYPE_CHECKING runtime import detection, (4) artifact binding
consistency, (5) action step implementation completeness, (6) prompt file
existence, (7) prompt placeholder vs required_inputs consistency,
(8) context_extensions.py artifact key coverage, (9)
Standards/COMPOSITION_STANDARD.md existence, (10) Specs/ directory
existence with at least one .md file, (11) bidirectional prompt
placeholder vs artifact declaration consistency.

TC-056: The VALIDATION_REPORT_FILE must list the pass/fail status of
each of the 11 checks with specific failure messages for any check that
does not pass.

TC-057: The gatekeep_package step must produce a GATEKEEP_PACKAGE_FILE
artifact. Its status must be APPROVED only if the VALIDATION_REPORT_FILE
shows all 11 checks passing and all criteria TC-053 through TC-056 pass.

TC-058: The review_package step must produce a REVIEW_FILE_SUGGESTED
artifact with status APPROVED or REJECTED.

TC-059: If review_package returns REJECTED, the refine_package step must
execute and produce an updated package. Both generate_package and
refine_package must declare STANDARDS_COMPOSITION_STANDARD_FILE in their
produces lists.

TC-060: The prompts/ directory must contain one .txt file per prompt-type
step, named with a two-digit prefix and step name (e.g.,
01_generate_test_criteria.txt).

---

## 10. Criteria for Promotion (Phase 9)

Phase 9 contains steps 21 (promote_workflow_package) and 22
(step_completion).

TC-061: The promote_workflow_package action must copy all required files
to workflows/{slug}/ including: workflow.toml, context_extensions.py,
actions.py (if exists), README.md, prompts/ directory, Standards/
directory, and Specs/ directory.

TC-062: The promote action must reject with status REJECTED and error
code MISSING_REQUIRED_OUTPUT_DIR if either Standards/ or Specs/ directory
is missing from the output.

TC-063: The WORKFLOW_PACKAGE_DIR_FILE artifact must be produced after
successful promotion, pointing to the deployed workflow directory path.

TC-064: The step_completion step must execute only after
promote_workflow_package returns APPROVED status.

---

## 11. Negative Criteria

The following conditions MUST NOT appear in any generated artifact.

NC-001: No generated artifact may contain non-ASCII characters. All files
must use plain ASCII encoding. Em-dashes, curly quotes, and other
Unicode characters are forbidden.

NC-002: No generated artifact may contain dangling references -- every
artifact key referenced in any file must correspond to a declared input
or output in the workflow manifest.

NC-003: No generated artifact may contain scope invention -- every
requirement, component type, binding rule, or phase must trace back to
the WORKFLOW_SPEC_FILE. New requirements not present in the spec are
forbidden.

NC-004: No section heading in any generated artifact may use backticks,
bold, italics, or other inline formatting. Section headings must be
plain text only.

NC-005: No generated artifact may use filesystem paths as governance
references. Governance documents must be referenced by filename only
(e.g., METADATA_STANDARD.md, not a full path).

NC-006: No workflow.toml may declare a step that references an artifact
key not registered in the workflow's artifact declarations.

---

## 12. Self-Validation

### 12.1 Spec Section Coverage

This section verifies that the criteria cover all sections of the
WORKFLOW_SPEC_FILE.

| Spec Section | Criteria Coverage |
|---|---|
| Section 1: Domain Overview | Introduction (Section 1), scope definition |
| Section 2: Component Schema | Phase 2 criteria (TC-008 to TC-016) |
| Section 3: Composition Format | Phase 3 criteria (TC-017 to TC-023) |
| Section 4: Output Format | Phase 4 criteria (TC-024 to TC-034) |
| Section 5: Operational Requirements | Phase 5 criteria (TC-035 to TC-043) |
| Section 6: Step Sequence | Phase 5 criteria (TC-036, TC-040 to TC-043) |
| Section 7: Self-Bootstrapping | Phase 7 criteria (TC-052), Phase 8 (TC-054) |
| Composition Standard (v3 innovation) | Phase 6 criteria (TC-044 to TC-050) |
| Meta Composition Spec (v3 innovation) | Phase 7 criteria (TC-051 to TC-052) |
| Package Assembly | Phase 8 criteria (TC-053 to TC-060) |
| Promotion | Phase 9 criteria (TC-061 to TC-064) |
| Negative constraints | Negative criteria (NC-001 to NC-006) |

### 12.2 Verifiability Check

Every criterion in this document is verifiable by one of these methods:

1. File existence check -- the artifact file exists at the declared path.
2. Frontmatter field check -- a specific field is present with a valid
   value in the YAML frontmatter.
3. Content count check -- the document contains exactly N items of a
   specified type (e.g., 8 component types, 22 steps, 11 checks).
4. Field presence check -- a specific named field or section exists in
   the document body.
5. Structural check -- the document follows a required structure (e.g.,
   3-part output, phase ordering).
6. Cross-reference check -- an artifact key or reference in one file
   matches a declaration in another file.
7. Negative check -- a forbidden pattern or content is absent.

No criterion relies on subjective judgment. All criteria can be evaluated
by a gatekeeper, reviewer, or deterministic validation script.

### 12.3 Criteria Count Summary

| Category | Count |
|---|---|
| Phase 1 (Foundation) | 7 |
| Phase 2 (Component Schema) | 9 |
| Phase 3 (Composition Format) | 7 |
| Phase 4 (Output Format) | 11 |
| Phase 5 (Operational Workflow) | 9 |
| Phase 6 (Composition Standard) | 7 |
| Phase 7 (Meta Composition Spec) | 2 |
| Phase 8 (Package Assembly) | 8 |
| Phase 9 (Promotion) | 4 |
| Negative Criteria | 6 |
| Total | 70 |

Note: The frontmatter total_criteria_count reflects the positive
acceptance criteria only (TC-001 through TC-064), which is 64. The
negative criteria (NC-001 through NC-006) are tracked separately.
The combined total of all criteria (positive and negative) is 70.

---

End of Test Criteria Document
