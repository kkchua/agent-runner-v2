---
doc_type: "output_format"
lifecycle_status: "draft"
layer: 3
resolution_rule_count: 7
quality_requirement_count: 8
domain: "ar_meta_builder"
spec_reference: "codebase_to_meta_v1.md Section 4"
---

# Output Format (Layer 3)

## Overview

This document defines the Layer 3 output format for the AR Meta Builder v1 composition system. Layer 3 is the final layer in the 3-layer architecture. It defines HOW the abstract component definitions (Layer 1) and composition bindings (Layer 2) resolve into concrete output files that form the deliverable workflow package.

**Layer 3 role in the 3-layer architecture:**

- Layer 1 (COMPONENT_SCHEMA.md) -- Defines the 8 universal component types and their schemas. Read-only authority for component definitions.
- Layer 2 (COMPOSITION_FORMAT.md) -- Defines how component instances are bound into compositions. Specifies binding rules, override mechanisms, placeholder resolution, and ordering constraints.
- Layer 3 (this document) -- Defines the concrete output file structure, resolution rules for transforming abstractions into files, quality requirements for output validation, and downstream extraction contracts.

**Domain context:** The codebase_to_meta domain produces a self-contained workflow package that, when deployed and executed, transforms codebase documentation into audience-specific Rich Markdown meta content files. The output format defines the structure of both the workflow package itself (3 parts) and the meta content files it produces at runtime.

**Output principle:** Every file in the output must be traceable to a component type or composition binding from Layer 1/Layer 2. No file exists without a resolution rule that explains its presence.

**Traceability:** All content in this document traces to the input specification (codebase_to_meta_v1.md, Sections 4 and 5) and the upstream Layer 1/Layer 2 documents (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md). The 7 resolution rules correspond to the 7 component-related concerns from the composition. The 8 quality requirements incorporate the 7 from spec Section 4.3 plus one package-level quality requirement.

---

## Output Structure

The Layer 3 output is organized into 3 parts. Each part serves a distinct purpose in the deployed workflow package.

### Part 1: Standards/COMPOSITION_STANDARD.md

**Purpose:** The composition standard defines the schema sections, component type expectations, and extensibility model for the generated workflow package.

**Location in output:** `Standards/COMPOSITION_STANDARD.md`

**Contents:**
- YAML frontmatter with standard_name, standard_version, component_type_count
- Component type definitions (all 8 universal types from COMPONENT_SCHEMA.md)
- Schema sections listing
- Extensibility model description

**Resolution source:** composition_standard component type (BR-006 from COMPOSITION_FORMAT.md). This file is generated at Phase 6 of the ar_meta_builder_v1 workflow.

**Dependencies:**
- References all 8 component types from COMPONENT_SCHEMA.md
- Defines naming conventions for artifacts within the workflow package
- Establishes the schema contract that downstream composition systems must follow

### Part 2: Specs/ Directory

**Purpose:** Contains the runtime specification that the generated workflow reads to understand WHAT meta content to produce. This is the bootstrap chain integrity link -- the spec is copied verbatim from the input.

**Location in output:** `Specs/codebase_to_meta_v1.md`

**Contents:**
- The complete codebase_to_meta_v1.md specification, content-identical to the input WORKFLOW_SPEC_FILE
- YAML frontmatter with domain, domain_label, job_prefix, workflow_pattern
- Sections 1 through 6 covering domain overview, component schema, composition format, output format, operational requirements, and references

**Resolution source:** The input WORKFLOW_SPEC_FILE is copied without modification to preserve bootstrap chain integrity.

**Dependencies:**
- The generate_meta_content prompt step references this spec via {ARTIFACT_KEY} placeholder
- The review_meta_content prompt step references this spec to validate output
- Downstream composition systems (e.g., meta_content_renderer_v1) consume this spec to understand the meta content format

### Part 3: Workflow Package Files

**Purpose:** The operational workflow package that can be deployed to the global runner home and executed. Contains all files needed for workflow execution.

**Location in output:** Root of the workflow package directory.

**Contents:**

| File/Directory | Description | Resolution Source |
|---|---|---|
| `workflow.toml` | Workflow manifest declaring 5 steps, 5 artifacts, routing, and step types | RR-001 (step_definition), RR-002 (role_policy), RR-003 (routing_pattern) |
| `context_extensions.py` | Artifact key registration with hardcoded context variable paths | RR-005 (artifact_contract), RR-007 (placeholder) |
| `actions.py` | Python implementations of scan_audiences and publish_meta_content | RR-001 (step_definition for action steps) |
| `prompts/` | Directory containing prompt template files for the 3 prompt-type steps | RR-004 (prompt_pattern) |
| `prompts/generate_meta_content.txt` | Prompt template for generate step | RR-004 |
| `prompts/review_meta_content.txt` | Prompt template for review step | RR-004 |
| `prompts/refine_meta_content.txt` | Prompt template for refine step | RR-004 |
| `audiences/` | Directory containing audience definition plugin files | RR-007 (placeholder, audience data) |
| `audiences/developer.md` | Developer audience definition | RR-007 |
| `audiences/architect.md` | Architect audience definition | RR-007 |
| `audiences/executive.md` | Executive audience definition | RR-007 |
| `README.md` | Human documentation for the workflow package | RR-006 (composition_standard) |

**Conditional files:**
- If the composition defines output_variances (BR-007), per-audience format override files may be included.
- If the composition references additional audience definitions beyond the initial 3, corresponding .md files are included in audiences/.

**Resolution source:** workflow.toml is assembled from step_definition (RR-001), role_policy (RR-002), routing_pattern (RR-003), and artifact_contract (RR-005) resolutions. Python files are generated from step_definition and prompt_pattern resolutions.

---

## Resolution Rules

The following 7 resolution rules define how abstract component types from Layer 1 and composition bindings from Layer 2 resolve into concrete files in the 3-part output structure.

### RR-001: step_definition Resolution

**Component type:** step_definition

**Resolution target:** Workflow package files (Part 3)

**Rule:** Each step_definition component resolves to one or more concrete elements in the workflow package based on its step_type:

- If step_type is "action": The step resolves to a function implementation in actions.py AND a [[step]] section in workflow.toml with type = "action".
- If step_type is "prompt": The step resolves to a prompt template file in prompts/ AND a [[step]] section in workflow.toml with type = "prompt".

**Constraints:**
- Every step_definition in step_bindings must produce at least one concrete element.
- Action steps (scan_audiences, publish_meta_content) resolve to actions.py functions.
- Prompt steps (generate_meta_content, review_meta_content, refine_meta_content) resolve to prompts/*.txt files.
- The step_name in workflow.toml must match the step_name in the component definition exactly.

**Verification condition:** For each step_definition in the composition, a corresponding entry exists in workflow.toml and the appropriate implementation file (actions.py for action, prompts/*.txt for prompt).

**Traceability:** Maps to BR-001 (step_bindings) in COMPOSITION_FORMAT.md. Corresponds to spec Section 2.1 (5 steps across 5 phases).

### RR-002: role_policy Resolution

**Component type:** role_policy

**Resolution target:** workflow.toml [step] sections (Part 3)

**Rule:** Each role_policy component for a prompt-type step resolves to a role assignment within the corresponding [[step]] section in workflow.toml. The policy_name determines which coder role is invoked when executing the step.

**Constraints:**
- Only prompt-type steps receive role assignments. Action steps must NOT have a role entry.
- The step_name in the role_policy must match a step_name in workflow.toml.
- The policy_name must correspond to a registered coder role in the runner's coder registry.
- Each prompt-type step must have exactly one role_policy resolution.

**Verification condition:** For each role_policy in the composition, the corresponding prompt-type step in workflow.toml contains a role field with the correct policy_name. No action-type step contains a role field.

**Traceability:** Maps to BR-002 (role_bindings) in COMPOSITION_FORMAT.md. Corresponds to spec Section 2.2 (role assignments for 3 prompt steps).

### RR-003: routing_pattern Resolution

**Component type:** routing_pattern

**Resolution target:** workflow.toml routing directives (Part 3)

**Rule:** Each routing_pattern component resolves to onsuccess and optional on_reject_refine directives within the corresponding [[step]] section in workflow.toml. The routing determines control flow between steps.

**Constraints:**
- Every step must have exactly one routing_pattern resolution.
- The onsuccess target must reference a valid step_name or "step_completion".
- If on_reject_refine is specified, max_iterations and exhaustion_code must also be present.
- Exactly one step must have onsuccess = "step_completion" (the terminal step).
- Refine loops must not create unresolvable cycles.

**Verification condition:** For each routing_pattern in the composition, the corresponding step in workflow.toml has correct onsuccess and (if applicable) on_reject_refine directives. The step_completion terminal is present. The review-refine loop specifies max_iterations = 2 and exhaustion_code = META_CONTENT_REVIEW_EXHAUSTED.

**Traceability:** Maps to BR-003 (routing_bindings) in COMPOSITION_FORMAT.md. Corresponds to spec Section 2.3 (routing table with exhaustion codes).

### RR-004: prompt_pattern Resolution

**Component type:** prompt_pattern

**Resolution target:** Prompt template files in prompts/ (Part 3)

**Rule:** Each prompt_pattern component resolves to a section within one or more prompt template files. The patterns are assembled into complete prompt templates by concatenating the applicable patterns for each prompt-type step.

**Constraints:**
- The 6 prompt patterns (reference_inputs, generation_tasks, self_critic, self_validation, forbidden_content, output_instructions) are combined per step according to their applied_to lists.
- Every prompt-type step must include at least: reference_inputs, self_critic, self_validation, output_instructions.
- Generate and refine steps must additionally include: generation_tasks, forbidden_content.
- Each {ARTIFACT_KEY} placeholder in the assembled prompt must correspond to a declared artifact in the step's required_inputs or produces.

**Verification condition:** For each prompt-type step, the assembled prompt template contains all required pattern sections. All {PLACEHOLDER} references in the template are declared in the step's artifact declarations.

**Traceability:** Maps to BR-004 (prompt_bindings) in COMPOSITION_FORMAT.md. Corresponds to spec Section 2.4 (6 prompt patterns with applicability rules).

### RR-005: artifact_contract Resolution

**Component type:** artifact_contract

**Resolution target:** workflow.toml artifact declarations AND context_extensions.py registrations (Part 3)

**Rule:** Each artifact_contract component resolves to:
1. An artifact key declaration in workflow.toml under the appropriate [[step]] section (in the produces array).
2. A path registration in context_extensions.py mapping the artifact key to its resolved filesystem path pattern.

**Constraints:**
- Every artifact_key must be unique across the composition.
- The produced_by field must reference an existing step_name in workflow.toml.
- The filename_pattern must not contain filesystem-incompatible characters.
- Required artifacts must be produced by steps that always execute (not conditional-only).
- The context_extensions.py must register all 5 artifact keys: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, META_MANIFEST_FILE.

**Verification condition:** For each artifact_contract in the composition, a corresponding entry exists in workflow.toml and a path registration exists in context_extensions.py. All 5 artifact keys are covered.

**Traceability:** Maps to BR-005 (artifact_bindings) in COMPOSITION_FORMAT.md. Corresponds to spec Section 2.5 (5 artifact contracts with filename patterns).

### RR-006: composition_standard Resolution

**Component type:** composition_standard

**Resolution target:** Standards/COMPOSITION_STANDARD.md (Part 1)

**Rule:** The composition_standard component (if bound) resolves to the Standards/COMPOSITION_STANDARD.md file in the output package. This file defines the schema contract for the workflow package, including component type expectations, naming conventions, and extensibility model.

**Constraints:**
- At most one composition_standard may be bound (singleton).
- The standard_name must identify the standard for the domain (e.g., "CODEBASE_TO_META_STANDARD").
- The standard_version must follow semantic versioning format.
- The component_type_count must match the actual number of type definitions in the standard body.
- The standard must include sections for: component_schema, composition_format, output_format, operational_requirements.

**Verification condition:** The Standards/COMPOSITION_STANDARD.md file exists, has valid YAML frontmatter, and its component_type_count matches the number of type definitions in the body.

**Traceability:** Maps to BR-006 (composition_standard_binding) in COMPOSITION_FORMAT.md. Consumed at Phase 6 of ar_meta_builder_v1.

### RR-007: placeholder Resolution

**Component type:** placeholder (cross-cutting, applies to all component types)

**Resolution target:** Runtime values in all output files (Parts 1, 2, 3)

**Rule:** Placeholders in prompt templates, context_extensions.py, and workflow.toml resolve from 4 priority-ordered data sources:

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Runtime context | CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR |
| 2 | Audience definition | audience_id, label, tone, focus_areas, section_structure |
| 3 | Codebase manifest | doc_inventory, section_list, total_doc_count |
| 4 (lowest) | Job runtime | job_id, seq, workspace_root |

**Constraints:**
- Context variable placeholders (CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR) must be hardcoded in context_extensions.py and resolved at Priority 1.
- Audience field placeholders resolve per-audience at Priority 2.
- Codebase manifest placeholders resolve from codebase_manifest.json at Priority 3.
- Job runtime placeholders resolve from the execution context at Priority 4.
- Unresolved artifact key placeholders ({ARTIFACT_KEY}) must be declared in the step's required_inputs or produces.
- Unresolved context variable placeholders are a CRITICAL error.

**Verification condition:** Every {PLACEHOLDER} in every output file resolves from at least one data source. No dangling references exist.

**Traceability:** Maps to the placeholder resolution mechanism defined in COMPOSITION_FORMAT.md Section "Placeholder Resolution" and spec Section 3.4.

---

## Meta Content Output Format (Spec Section 4.2/4.3)

In addition to the 7 component resolution rules above, the output format defines the meta content file format that the generated workflow produces at runtime. These rules are embedded in the workflow package (specifically in the prompt templates and the runtime spec at Specs/codebase_to_meta_v1.md) and govern how meta content files are structured.

### Meta Content Resolution Rules

These 7 rules from spec Section 4.2 govern the structure of each generated meta content file:

| Rule | Description | Verifiable Condition |
|---|---|---|
| RR-META-001 | Each audience definition produces exactly one meta content file | Count of META_CONTENT_FILE outputs equals count of discovered audience definitions |
| RR-META-002 | Output filename uses audience_id prefix: META-{AUD}-{date}-{seq}.md | Filename matches pattern where AUD is derived from audience_id (DEV, ARCH, EXEC) |
| RR-META-003 | Output subdirectory matches audience_id | Parent directory name equals the audience_id value from the audience definition frontmatter |
| RR-META-004 | Section order follows audience definition's section_structure | Output file sections appear in the order specified by the audience's section_structure array |
| RR-META-005 | Tone follows audience definition's tone field | Writing style and technical depth match the tone value from the audience definition |
| RR-META-006 | Excluded topics from exclude field must not appear in output | No content related to excluded topics is present in the generated file |
| RR-META-007 | Source attribution via inline references to codebase doc filenames | Every factual claim includes an inline reference identifying the source codebase doc file |

### Meta Content Quality Requirements

These 7 rules from spec Section 4.3 define quality constraints for each generated meta content file:

| Rule | Requirement | Severity | Verifiable Condition |
|---|---|---|---|
| QR-META-001 | Completeness -- All codebase sections represented in each audience output (filtered by focus_areas/exclude) | CRITICAL | Every section in codebase_manifest.json section_list is either represented in the output or explicitly excluded by the audience's exclude field |
| QR-META-002 | Audience fidelity -- Tone, focus, and section structure match audience definition frontmatter | CRITICAL | Output tone matches audience.tone, emphasized content matches audience.focus_areas, section order matches audience.section_structure |
| QR-META-003 | Self-contained -- Each meta file readable without reference to source docs | HIGH | The file contains sufficient context to understand all claims without accessing codebase documentation |
| QR-META-004 | Source attribution -- Claims trace to specific codebase doc files | HIGH | Every factual statement includes an inline reference to the source file path under CODEBASE_DOC_ROOT |
| QR-META-005 | No hallucination -- No information invented beyond codebase docs | CRITICAL | Every claim in the output can be verified by reading the referenced source codebase doc file |
| QR-META-006 | YAML frontmatter -- All required fields present with correct values | HIGH | Frontmatter contains: title, audience, audience_label, generated_date, source_version, section_count |
| QR-META-007 | ASCII-only -- No em-dashes, no curly quotes in generated content | HIGH | All characters in the file are within the ASCII range (0x00-0x7F). No Unicode special characters. |

---

## Required Sections

This section defines the required sections for each part of the 3-part output structure.

### Part 1 Required Sections (Standards/COMPOSITION_STANDARD.md)

| Section | Required | Description |
|---|---|---|
| YAML frontmatter | Yes | standard_name, standard_version, component_type_count |
| Component Type Definitions | Yes | One subsection per component type (all 8 universal types) |
| Schema Sections | Yes | List of sections the generated workflow's schemas must contain |
| Extensibility Model | Yes | Description of how new types or definitions can be added |

### Part 2 Required Sections (Specs/codebase_to_meta_v1.md)

| Section | Required | Description |
|---|---|---|
| YAML frontmatter | Yes | doc_type, lifecycle_status, domain, domain_label, job_prefix, workflow_pattern |
| Section 1: Domain Overview | Yes | Domain name, label, job prefix, purpose, audience model |
| Section 2: Component Schema (Layer 1) | Yes | 5 domain-active component types, validation rules |
| Section 3: Composition Format (Layer 2) | Yes | Binding rules, override mechanism, placeholder resolution |
| Section 4: Output Format (Layer 3) | Yes | Frontmatter schema, resolution rules, quality requirements |
| Section 5: Operational Requirements | Yes | 5 phases, step sequence, action steps, artifact declarations |
| Section 6: References | Yes | Downstream consumers, source data paths |

### Part 3 Required Sections (Workflow Package Files)

#### workflow.toml

| Section | Required | Description |
|---|---|---|
| [workflow] header | Yes | name, label, job_prefix, description |
| [[step]] sections | Yes | One per step (5 total), in canonical order |
| [step.artifacts] | Yes | Artifact key declarations per step |
| [step.routing] | Yes | onsuccess, on_reject_refine (if applicable) |

#### context_extensions.py

| Section | Required | Description |
|---|---|---|
| Module docstring | Yes | Purpose and scope of the extensions module |
| Artifact key registrations | Yes | All 5 artifact keys with path patterns |
| Context variable definitions | Yes | CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR |
| known_artifact_paths() function | Yes | Returns dict mapping artifact keys to resolved paths |

#### actions.py

| Section | Required | Description |
|---|---|---|
| Module docstring | Yes | Purpose and scope of the actions module |
| scan_audiences function | Yes | Directory scan, frontmatter parsing, inventory building, error handling |
| publish_meta_content function | Yes | 4-stage lifecycle: backup, history, publish, manifest |

#### prompts/ Directory

| File | Required | Description |
|---|---|---|
| generate_meta_content.txt | Yes | Prompt template for content generation step |
| review_meta_content.txt | Yes | Prompt template for quality review step |
| refine_meta_content.txt | Yes | Prompt template for content refinement step |

#### audiences/ Directory

| File | Required | Description |
|---|---|---|
| developer.md | Yes | Developer audience definition (implementation-focused) |
| architect.md | Yes | Architect audience definition (design-focused) |
| executive.md | Yes | Executive audience definition (business-focused) |

#### README.md

| Section | Required | Description |
|---|---|---|
| Purpose | Yes | What this workflow does |
| Inputs | Yes | Context variables and their hardcoded paths |
| Outputs | Yes | 5 artifact descriptions |
| Audience Definitions | Yes | Description of the 3 initial audiences |
| Invocation | Yes | How to run the workflow |

---

## Quality Requirements

The following 8 quality requirements apply to all output files in the 3-part structure. QR-001 through QR-007 correspond to the meta content quality requirements from spec Section 4.3. QR-008 is a package-level quality requirement.

### QR-001: Completeness

**Severity:** CRITICAL

**Applies to:** Meta content files (runtime output)

**Condition:** All codebase sections are represented in each audience output, filtered by the audience's focus_areas and exclude fields. Every section in codebase_manifest.json section_list must either appear in the output or be explicitly excluded.

**Verification:** Compare the output's section coverage against codebase_manifest.json section_list, accounting for the audience's focus_areas emphasis and exclude omissions.

### QR-002: Audience Fidelity

**Severity:** CRITICAL

**Applies to:** Meta content files (runtime output)

**Condition:** Tone, focus, and section structure in the output match the corresponding audience definition frontmatter. The writing style reflects the tone field. The emphasized content matches focus_areas. The section order matches section_structure.

**Verification:** Compare output characteristics against the audience definition's frontmatter fields.

### QR-003: Self-Contained

**Severity:** HIGH

**Applies to:** Meta content files (runtime output)

**Condition:** Each meta content file is readable without reference to source codebase documentation. All necessary context is included within the file itself.

**Verification:** A reader with no access to CODEBASE_DOC_ROOT can understand all claims and relationships presented in the file.

### QR-004: Source Attribution

**Severity:** HIGH

**Applies to:** Meta content files (runtime output)

**Condition:** Every factual claim in the output traces to a specific codebase doc file via inline reference. The reference identifies the source file path under CODEBASE_DOC_ROOT.

**Verification:** Each factual statement in the output has a corresponding inline reference that can be resolved to an actual file in CODEBASE_DOC_ROOT.

### QR-005: No Hallucination

**Severity:** CRITICAL

**Applies to:** Meta content files (runtime output)

**Condition:** No information is invented beyond what the codebase documentation provides. Every factual claim can be verified by reading the referenced source file.

**Verification:** For each claim, read the referenced source file and confirm the information is present. No claim exists without a verifiable source.

### QR-006: YAML Frontmatter

**Severity:** HIGH

**Applies to:** Meta content files (runtime output) and all output package Markdown files

**Condition:** All required frontmatter fields are present with correct values. For meta content files: title, audience, audience_label, generated_date, source_version, section_count. For audience definitions: audience_id, label, tone, focus_areas, section_structure.

**Verification:** Parse the YAML frontmatter and check each required field is present and non-empty.

### QR-007: ASCII-Only

**Severity:** HIGH

**Applies to:** All output files (all 3 parts)

**Condition:** No em-dashes, no curly quotes, no Unicode characters. All characters are within the ASCII range (0x00-0x7F).

**Verification:** Scan every byte of every output file. Reject if any byte exceeds 0x7F or if forbidden ASCII substitutions (em-dash replacement, curly quotes) are detected.

### QR-008: Package Traceability

**Severity:** HIGH

**Applies to:** All output package files (all 3 parts)

**Condition:** Every file in the output package is traceable to a resolution rule (RR-001 through RR-007). No file exists without a documented resolution path. Every requirement, component type, binding rule, or step in the output traces back to the input specification (codebase_to_meta_v1.md).

**Verification:** For each file in the output, identify which resolution rule produces it and which spec section defines the requirement. No untraceable files exist.

---

## Downstream Extraction Contracts

These contracts define how downstream consumers extract information from the 3-part output structure. Each contract is self-contained and specifies the extraction interface, data format, and access patterns.

### DEC-001: Meta Content Extraction Contract

**Consumer:** meta_content_renderer_v1 (and similar downstream composition systems)

**Extraction target:** Meta content files produced at runtime by the generated workflow

**Contract:**

| Field | Type | Description |
|---|---|---|
| file_path | string | Absolute path to the meta content file: {audience_id}/META-{AUD}-{date}-{seq}.md |
| frontmatter | object | YAML frontmatter with: title, audience, audience_label, generated_date, source_version, section_count |
| sections | array | Ordered list of sections per the audience's section_structure |
| source_refs | array | List of inline source attribution references |

**Access pattern:** Downstream systems read meta content files from META_CONTENT_ROOT/current/{audience_id}/. The meta_manifest.json file lists all available files with their metadata.

**Extraction rules:**
1. Parse YAML frontmatter to extract metadata.
2. Parse section headings (## level) to extract section structure.
3. Extract inline source references (file paths under CODEBASE_DOC_ROOT) for traceability.
4. The audience_id determines which rendering template to apply.

**Data available:**
- title: Human-readable document title
- audience: Machine-readable audience identifier
- audience_label: Human-readable audience name
- generated_date: Date of generation (YYYY-MM-DD format)
- source_version: Version identifier of the source codebase
- section_count: Number of sections in the document

### DEC-002: Workflow Package Extraction Contract

**Consumer:** agent-runner-v2 daemon/CLI (workflow execution engine)

**Extraction target:** The deployed workflow package directory

**Contract:**

| Field | Type | Description |
|---|---|---|
| manifest_path | string | Path to workflow.toml |
| step_count | integer | Number of steps declared (5 for codebase_to_meta) |
| artifact_keys | array | List of all declared artifact keys |
| context_variables | object | Map of variable names to hardcoded paths |
| action_modules | array | List of action step names with their function locations |
| prompt_templates | array | List of prompt step names with their template file paths |

**Access pattern:** Downstream systems (the runner engine) read workflow.toml to discover steps, routing, and artifacts. context_extensions.py provides path resolution. actions.py provides action implementations.

**Extraction rules:**
1. Parse workflow.toml (TOML format) to extract step definitions and routing.
2. Import context_extensions.py and call known_artifact_paths() to get path mappings.
3. Import actions.py and look up action functions by step_name.
4. Read prompt template files from prompts/ directory.
5. Read audience definitions from audiences/ directory.

**Data available:**
- 5 step definitions with types, roles, and routing
- 5 artifact key registrations with path patterns
- 3 context variable paths (CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR)
- 2 action implementations (scan_audiences, publish_meta_content)
- 3 prompt templates (generate, review, refine)
- 3 audience definitions (developer, architect, executive)

### DEC-003: Composition Standard Extraction Contract

**Consumer:** Future composition systems and meta-meta builders

**Extraction target:** Standards/COMPOSITION_STANDARD.md

**Contract:**

| Field | Type | Description |
|---|---|---|
| standard_name | string | Identifier for the composition standard |
| standard_version | string | Semantic version of the standard |
| component_types | array | List of all component type definitions |
| schema_sections | array | Required schema sections for compliant workflows |
| extensibility_model | string | Description of extension mechanisms |

**Access pattern:** Downstream systems read the composition standard to understand the schema contract for the domain. This enables validation of workflow packages against the standard.

**Extraction rules:**
1. Parse YAML frontmatter to extract standard metadata.
2. Parse component type subsections (#### Type N: type_name) to extract type definitions.
3. Extract schema_sections list for compliance checking.
4. Extract extensibility_model for understanding extension constraints.

**Data available:**
- 8 universal component type definitions
- Schema section requirements
- Extensibility model (3 levels of extension)
- Backward compatibility guarantees

---

## Example Output

This section shows the complete resolved output for the codebase_to_meta domain.

### 3-Part Output Directory Structure

```
ar_meta_builder_v1/                      # Workflow package root
|
|-- Standards/                           # Part 1: Composition Standard
|   +-- COMPOSITION_STANDARD.md          # RR-006 resolution
|
|-- Specs/                               # Part 2: Runtime Specification
|   +-- codebase_to_meta_v1.md           # Bootstrap chain copy
|
|-- workflow.toml                        # Part 3: Workflow Manifest
|-- context_extensions.py                # Part 3: Path Registration
|-- actions.py                           # Part 3: Action Implementations
|-- README.md                            # Part 3: Human Documentation
|
|-- prompts/                             # Part 3: Prompt Templates
|   |-- generate_meta_content.txt        # RR-004 resolution
|   |-- review_meta_content.txt          # RR-004 resolution
|   +-- refine_meta_content.txt          # RR-004 resolution
|
+-- audiences/                           # Part 3: Audience Definitions
    |-- developer.md                     # RR-007 resolution
    |-- architect.md                     # RR-007 resolution
    +-- executive.md                     # RR-007 resolution
```

### Runtime Output (Produced by the Generated Workflow)

```
docs/repo/meta_content/
|
|-- current/                             # Published output
|   |-- developer/
|   |   +-- META-DEV-20260809-001.md    # RR-META-001 through RR-META-007
|   |-- architect/
|   |   +-- META-ARCH-20260809-001.md
|   |-- executive/
|   |   +-- META-EXEC-20260809-001.md
|   +-- meta_manifest.json              # META_MANIFEST_FILE
|
|-- runs/                                # Per-job staging
|   +-- AMB-ai99miop/
|       |-- AUDIENCE_INV-20260809-001.md # AUDIENCE_INVENTORY_FILE
|       |-- meta_index.json              # META_INDEX_FILE
|       +-- META-REV-20260809-001.md     # REVIEW_FILE_SUGGESTED
|
|-- history/                             # Version history
|   +-- {prior_job_ids}/
|
+-- backups/                             # Backup snapshots
    +-- BACKUP-{timestamp}/
```

### Example: Resolved workflow.toml Structure

```toml
[workflow]
name = "codebase_to_meta_v1"
label = "Codebase to Meta Content v1"
job_prefix = "META"
description = "Transforms codebase documentation into audience-specific Rich Markdown meta content files."

[[step]]
name = "scan_audiences"
type = "action"
action_module = "actions"
action_function = "scan_audiences"
onsuccess = "generate_meta_content"

[step.artifacts]
produces = ["AUDIENCE_INVENTORY_FILE"]

[[step]]
name = "generate_meta_content"
type = "prompt"
role = "architect_standard"
prompt_template = "prompts/generate_meta_content.txt"
onsuccess = "review_meta_content"

[step.artifacts]
produces = ["META_CONTENT_FILE", "META_INDEX_FILE"]

[[step]]
name = "review_meta_content"
type = "prompt"
role = "reviewer_standard"
prompt_template = "prompts/review_meta_content.txt"
onsuccess = "publish_meta_content"
on_reject_refine = "refine_meta_content"
max_iterations = 2
exhaustion_code = "META_CONTENT_REVIEW_EXHAUSTED"
exhaustion_classification = "HUMAN_RETRY_REQUIRED"

[step.artifacts]
produces = ["REVIEW_FILE_SUGGESTED"]

[[step]]
name = "refine_meta_content"
type = "prompt"
role = "architect_standard"
prompt_template = "prompts/refine_meta_content.txt"
onsuccess = "review_meta_content"

[[step]]
name = "publish_meta_content"
type = "action"
action_module = "actions"
action_function = "publish_meta_content"
onsuccess = "step_completion"

[step.artifacts]
produces = ["META_MANIFEST_FILE"]
```

### Example: Meta Content File (Developer Audience)

```markdown
---
title: "Agent Runner V2 -- Developer Guide"
audience: developer
audience_label: "Developer"
generated_date: "2026-08-09"
source_version: "SDLC00CB-bgmxg5vi"
section_count: 5
---

# Agent Runner V2 -- Developer Guide

## Overview

The agent-runner-v2 is a Python 3.12+ daemon and CLI execution engine...
(Source: docs/repo/codebase/current/modules/agent_runner_v2.md)

## Module Catalog

### agent_runner_v2.run_agent
Entry point for the ukbe-run-agent CLI...
(Source: docs/repo/codebase/current/modules/run_agent.md)

### agent_runner_v2.step_runner
Core step execution engine...
(Source: docs/repo/codebase/current/modules/step_runner.md)

## API Reference

[Detailed function signatures, parameters, return types]

## Dependency Map

[Module dependency relationships]

## Developer Guide

[Setup, contribution, testing instructions]
```

---

## Self-Validation

This section verifies the completeness and correctness of the output format document.

### Resolution Rule Coverage

| # | Rule ID | Component Type | Resolution Target | Defined |
|---|---|---|---|---|
| 1 | RR-001 | step_definition | workflow.toml + actions.py/prompts/ | Yes |
| 2 | RR-002 | role_policy | workflow.toml [step] role field | Yes |
| 3 | RR-003 | routing_pattern | workflow.toml routing directives | Yes |
| 4 | RR-004 | prompt_pattern | prompts/*.txt template files | Yes |
| 5 | RR-005 | artifact_contract | workflow.toml + context_extensions.py | Yes |
| 6 | RR-006 | composition_standard | Standards/COMPOSITION_STANDARD.md | Yes |
| 7 | RR-007 | placeholder | Runtime values in all output files | Yes |

**Count: 7 resolution rules defined. Matches frontmatter resolution_rule_count: 7.**

### Quality Requirement Coverage

| # | Rule ID | Requirement | Severity | Defined |
|---|---|---|---|---|
| 1 | QR-001 | Completeness | CRITICAL | Yes |
| 2 | QR-002 | Audience fidelity | CRITICAL | Yes |
| 3 | QR-003 | Self-contained | HIGH | Yes |
| 4 | QR-004 | Source attribution | HIGH | Yes |
| 5 | QR-005 | No hallucination | CRITICAL | Yes |
| 6 | QR-006 | YAML frontmatter | HIGH | Yes |
| 7 | QR-007 | ASCII-only | HIGH | Yes |
| 8 | QR-008 | Package traceability | HIGH | Yes |

**Count: 8 quality requirements defined. Matches frontmatter quality_requirement_count: 8.**

### Output Part Coverage

| # | Part | Location | Required Files | Defined |
|---|---|---|---|---|
| 1 | Standards | Standards/COMPOSITION_STANDARD.md | 1 file | Yes |
| 2 | Specs | Specs/codebase_to_meta_v1.md | 1 file | Yes |
| 3 | Workflow Package | Root + prompts/ + audiences/ | 10+ files | Yes |

**Count: 3 output parts defined.**

### Downstream Contract Coverage

| # | Contract ID | Consumer | Extraction Target | Defined |
|---|---|---|---|---|
| 1 | DEC-001 | meta_content_renderer_v1 | Meta content files | Yes |
| 2 | DEC-002 | agent-runner-v2 engine | Workflow package | Yes |
| 3 | DEC-003 | Future composition systems | Composition standard | Yes |

**Count: 3 downstream extraction contracts defined.**

### Meta Content Resolution Rule Coverage (spec Section 4.2)

| # | Rule ID | Description | Verifiable |
|---|---|---|---|
| 1 | RR-META-001 | One file per audience | Yes |
| 2 | RR-META-002 | Filename uses audience_id prefix | Yes |
| 3 | RR-META-003 | Subdirectory matches audience_id | Yes |
| 4 | RR-META-004 | Section order follows section_structure | Yes |
| 5 | RR-META-005 | Tone follows tone field | Yes |
| 6 | RR-META-006 | Excluded topics must not appear | Yes |
| 7 | RR-META-007 | Source attribution via inline references | Yes |

**Count: 7 meta content resolution rules defined. Matches spec Section 4.2.**

### Meta Content Quality Requirement Coverage (spec Section 4.3)

| # | Rule ID | Requirement | Severity | Verifiable |
|---|---|---|---|---|
| 1 | QR-META-001 | Completeness | CRITICAL | Yes |
| 2 | QR-META-002 | Audience fidelity | CRITICAL | Yes |
| 3 | QR-META-003 | Self-contained | HIGH | Yes |
| 4 | QR-META-004 | Source attribution | HIGH | Yes |
| 5 | QR-META-005 | No hallucination | CRITICAL | Yes |
| 6 | QR-META-006 | YAML frontmatter | HIGH | Yes |
| 7 | QR-META-007 | ASCII-only | HIGH | Yes |

**Count: 7 meta content quality requirements defined. Matches spec Section 4.3.**

### Verification Checklist

- [x] Exactly 7 component resolution rules defined (RR-001 through RR-007).
- [x] Exactly 8 quality requirements defined (QR-001 through QR-008).
- [x] Exactly 3 output parts defined (Standards, Specs, Workflow Package).
- [x] 3 downstream extraction contracts defined (DEC-001, DEC-002, DEC-003).
- [x] 7 meta content resolution rules from spec Section 4.2 included (RR-META-001 through RR-META-007).
- [x] 7 meta content quality requirements from spec Section 4.3 included (QR-META-001 through QR-META-007).
- [x] Each resolution rule specifies a verifiable condition.
- [x] Each quality requirement specifies a verifiable condition and severity level.
- [x] 3 initial audience files specified: developer.md, architect.md, executive.md.
- [x] YAML frontmatter schema includes 6 fields: title, audience, audience_label, generated_date, source_version, section_count.
- [x] Output directory structure matches spec Section 3.5 example.
- [x] Meta content file format example matches spec Section 4.4.
- [x] Placeholder resolution defines 4 priority-ordered data sources.
- [x] Package file inventory matches spec Section 5.6.
- [x] Self-contained output requirement specified (QR-003, QR-META-003).
- [x] Audience fidelity requirement specified (QR-002, QR-META-002).
- [x] Source attribution requirement specified (QR-004, QR-META-004).
- [x] No hallucination requirement specified (QR-005, QR-META-005).
- [x] Downstream contracts are self-contained with extraction rules and data formats.
- [x] All files in the output are traceable to a resolution rule (QR-008).
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] All content traces to the input specification (codebase_to_meta_v1.md). No scope invention.
- [x] Governance path references use filenames only (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md), not filesystem paths.
- [x] YAML frontmatter includes: doc_type, lifecycle_status, layer, resolution_rule_count, quality_requirement_count.

---

**End of Output Format Document**
