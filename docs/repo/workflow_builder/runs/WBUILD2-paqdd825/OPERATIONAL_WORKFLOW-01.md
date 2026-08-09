---
doc_type: "operational_workflow"
lifecycle_status: "draft"
effective_version: "WBUILD2-paqdd825"
domain: "video_campaign_manuscript"
step_count: 7
action_count: 3
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
component_schema_source: "COMPONENT_SCHEMA-01.md"
composition_format_source: "COMPOSITION_FORMAT-01.md"
output_format_source: "OUTPUT_FORMAT-01.md"
created_at: "2026-08-08"
---

# Operational Workflow Design: Video Campaign Manuscript Composition System

## 1. Overview

This document defines the operational workflow for the video campaign manuscript composition system. The workflow implements the three-layer composition architecture by taking a component library (Layer 1: reusable creative building blocks such as hooks, scenes, voice styles, visual directions, audio moods, text styles, and transitions) and a set of declarative composition definitions (Layer 2: assembly instructions referencing components by ID with overrides and placeholder bindings) as input, then producing self-contained, fully resolved video campaign production manuscripts (Layer 3: complete deliverables with all references expanded, overrides applied, and placeholders filled from external data sources). The workflow follows the universal five-phase pattern from COMPOSITION_SYSTEM_STANDARD.md Section 6: scan, plan, generate, review, and refine. The domain context is short-form video campaign production for digital advertising and branded content across platforms such as TikTok, Instagram Reels, and YouTube Shorts. The end deliverable is a production manuscript that downstream workflows consume to generate voiceovers, visual assets, video edits, and platform-specific adaptations.

**End-to-end transformation:**

```
INPUTS:
  COMPONENT_LIBRARY_DIR  -->  [scan_components]  -->  COMPONENT_INVENTORY_FILE
                               [validate_components] --> VALIDATION_REPORT_FILE
  COMPOSITIONS_DIR       -->  [plan_compositions] --> RESOLUTION_PLAN_FILE
  DATA_SOURCE_DIR        |
  COMPONENT_INVENTORY_FILE
  VALIDATION_REPORT_FILE -->  [generate_output]   -->  OUTPUT_FILE
  RESOLUTION_PLAN_FILE
  DATA_SOURCE_DIR
  OUTPUT_FILE            -->  [review_output]     -->  REVIEW_FILE_SUGGESTED
  REVIEW_FILE_SUGGESTED  -->  [refine_output]     -->  OUTPUT_FILE (revised)
```

## 2. Workflow Phases

### 2.1 Scan Phase

**Objective:** Discover all component files in the component library directory, parse their YAML frontmatter, classify them by component_type, and build a complete inventory. Simultaneously, validate each component against the component schema (COMPONENT_SCHEMA-01.md) rules including common property checks, type enumeration checks, type-specific property checks, unique identifier checks, and semantic version checks.

**What is scanned:**
- All markdown files with YAML frontmatter under COMPONENT_LIBRARY_DIR
- Files organized in subdirectories by type: hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/
- Each file's frontmatter is parsed to extract component_id, component_type, name, version, description, and type-specific properties

**What validation is performed:**
- GLOBAL-VR-001 through GLOBAL-VR-013: Common property presence, type enumeration conformance, unique identifier format and uniqueness, semantic version format, type-specific property conformance, data type conformance, enum value conformance, no-override rule
- HOOK-VR-001 through HOOK-VR-006: Hook-specific rules
- SCENE-VR-001 through SCENE-VR-006: Scene-specific rules
- VOICE-VR-001 through VOICE-VR-004: Voice style-specific rules
- VISDIR-VR-001 through VISDIR-VR-005: Visual direction-specific rules
- AUDIO-VR-001 through AUDIO-VR-004: Audio mood-specific rules
- TEXT-VR-001 through TEXT-VR-005: Text style-specific rules
- TRANS-VR-001 through TRANS-VR-005: Transition-specific rules

**Artifacts produced:**
- COMPONENT_INVENTORY_FILE: Catalog of all discovered components with type classification, validation status (valid/invalid), and validation errors
- VALIDATION_REPORT_FILE: Detailed validation results per component with rule IDs and error messages

### 2.2 Plan Phase

**Objective:** Read all composition definition files from COMPOSITIONS_DIR, resolve every component_id reference against the component inventory, identify all overrides and placeholder bindings, validate override conformance against component type schemas, check required vs optional binding presence, verify ordering constraints (scene count 3-8, transition count equals N-1 for N scenes), and produce a resolution plan.

**What compositions are read:**
- All YAML composition files in COMPOSITIONS_DIR
- Each composition's composition_id, name, target_metadata, data_sources, and component_bindings are parsed

**What references are resolved:**
- Every component_id in every binding is looked up in the COMPONENT_INVENTORY_FILE
- The referenced component's type is verified against the expected type for the binding slot
- Override properties are checked against the component type's schema for existence, data type, and enum conformance
- Placeholders ({placeholder_name}) in overrides and component property values are inventoried
- Data source files declared in each composition are verified as present in DATA_SOURCE_DIR
- Placeholder resolvability is assessed against the declared data sources

**Artifacts produced:**
- RESOLUTION_PLAN_FILE: For each composition, the plan lists all bindings, resolved component references, override details, placeholder inventory with resolution status, required/optional binding presence check results, and ordering constraint validation results.

### 2.3 Generate Phase

**Objective:** For each composition in the resolution plan, generate a fully resolved output document. This involves expanding every component_id reference with the full component content from the inventory, merging overrides with base properties (override wins on conflict), resolving all placeholders from data source files, handling unresolved placeholders with {UNRESOLVED: field_name} flagging, assembling the output into the required section structure (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay, Production Notes), handling conditional sections (omitting Audio Direction if audio_mood binding absent, omitting Text Overlay if text_style binding absent), rendering transition directives between consecutive scenes, computing duration summaries, and writing the YAML frontmatter with correct metadata.

**What outputs are generated:**
- One OUTPUT_FILE per composition, formatted as markdown with YAML frontmatter per OUTPUT_FORMAT-01.md
- Each output contains: YAML frontmatter (composition_id, composition_name, metadata, component_count, generation_date, lifecycle_status, unresolved_placeholder_count), Opening section, Voice Direction section, Visual Treatment section, Scene-by-Scene Breakdown section (with transition directives), conditional Audio Direction section, conditional Text Overlay section, and Production Notes section (with placeholder resolution summary, unresolved placeholder list, duration summary, binding summary, platform notes)

**How they are assembled:**
- The generate_output step is prompt-driven (LLM judgment) because assembling human-readable deliverables from structured data requires creative formatting decisions, narrative coherence assessment, and contextual quality judgment
- The LLM receives the COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, and DATA_SOURCE_DIR content as context injection
- The LLM writes the output file(s) using file-writing tools

**Artifacts produced:**
- OUTPUT_FILE: The fully resolved production manuscript(s)

### 2.4 Review Phase

**Objective:** Perform quality review of all generated outputs against the quality requirements from OUTPUT_FORMAT-01.md Section 5 and the test criteria TC-GOF-001 through TC-GOF-016.

**What quality checks are performed:**
- Reference expansion: Verify all component_id references are fully expanded (no residual component_id strings in output)
- Placeholder completeness: Verify all placeholders are either resolved or flagged as {UNRESOLVED: field_name}
- Override correctness: Verify override values appear where overrides were specified, component values where not
- Section completeness: Verify all required sections present (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Production Notes), conditional sections correct
- Frontmatter validity: Verify all required fields present with correct values
- Cross-section consistency: Verify no contradictions between sections
- component_count accuracy: Verify frontmatter count matches actual expanded components
- lifecycle_status correctness: Verify "draft" if unresolved placeholders exist, "final" only if all resolved
- Downstream feasibility: Verify downstream workflows can extract their required concerns

**Artifacts produced:**
- REVIEW_FILE_SUGGESTED: Structured review report with findings table (severity, location, description), verdict (APPROVED or REJECTED), and evidence per finding

### 2.5 Refine Phase (Conditional)

**Objective:** Fix issues found during the review phase. This phase only executes when the review step produces a REJECTED verdict.

**What issues are fixed:**
- Missing sections added
- Incorrect override applications corrected
- Unresolved placeholder flagging syntax corrected to {UNRESOLVED: field_name}
- Cross-section contradictions resolved
- Frontmatter metadata corrected
- Duration calculations fixed
- Any finding from REVIEW_FILE_SUGGESTED addressed individually

**Artifacts produced:**
- OUTPUT_FILE (revised): The corrected output file, overwriting the previous version

## 3. Step Sequence

| Step # | Step Name | Step Type | Phase | Purpose | required_inputs | produces | onsuccess | on_reject_refine |
|---|---|---|---|---|---|---|---|---|
| 1 | scan_components | action | Scan | Discover all component files in the library directory, parse YAML frontmatter, and build a component inventory catalog | COMPONENT_LIBRARY_DIR, COMPONENT_SCHEMA_FILE | COMPONENT_INVENTORY_FILE | validate_components | -- |
| 2 | validate_components | action | Scan | Validate each discovered component against the schema rules (common properties, type-specific properties, enums, cross-property rules, unique IDs, semantic versions) | COMPONENT_INVENTORY_FILE, COMPONENT_SCHEMA_FILE | VALIDATION_REPORT_FILE | plan_compositions | -- |
| 3 | plan_compositions | action | Plan | Parse all composition files, resolve component_id references against inventory, validate overrides, inventory placeholders, check binding requirements and ordering constraints | COMPOSITIONS_DIR, COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, DATA_SOURCE_DIR | RESOLUTION_PLAN_FILE | generate_output | -- |
| 4 | generate_output | prompt | Generate | Generate fully resolved output documents by expanding all component references, merging overrides, resolving placeholders, and assembling into the required section structure | RESOLUTION_PLAN_FILE, COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, DATA_SOURCE_DIR, OUTPUT_FORMAT_FILE | OUTPUT_FILE | review_output | -- |
| 5 | review_output | prompt | Review | Quality review of generated outputs against output format requirements, checking reference expansion, placeholder completeness, section integrity, and cross-section consistency | OUTPUT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FORMAT_FILE | REVIEW_FILE_SUGGESTED | stepCompletion | refine_output |
| 6 | refine_output | prompt | Refine | Fix issues identified in the review report, correcting any defects in the output document | REVIEW_FILE_SUGGESTED, OUTPUT_FILE, RESOLUTION_PLAN_FILE, COMPONENT_INVENTORY_FILE, DATA_SOURCE_DIR | OUTPUT_FILE | review_output | -- |
| 7 | stepCompletion | action | -- | Terminal step marking successful workflow completion | -- | -- | -- | -- |

## 4. Artifact Contract

### 4.1 Input Artifacts

| Artifact Key | Description | Required/Optional | Provided By |
|---|---|---|---|
| COMPONENT_LIBRARY_DIR | Directory path containing component markdown files organized by type subdirectories (hooks/, scenes/, voice_styles/, etc.) | Required | External (user provides) |
| COMPOSITIONS_DIR | Directory path containing composition YAML files defining assembly instructions | Required | External (user provides) |
| DATA_SOURCE_DIR | Directory path containing placeholder resolution data files (product_master/, platform_config/, campaign_input/) | Required | External (user provides) |
| COMPONENT_SCHEMA_FILE | Path to the component schema document defining types, properties, and validation rules for this domain | Required | Upstream workflow step (generate_component_schema in builder) |
| OUTPUT_FORMAT_FILE | Path to the output format specification document defining section structure and formatting rules | Required | Upstream workflow step (generate_output_format in builder) |

### 4.2 Output Artifacts

| Artifact Key | Description | Produced By | Consumed By |
|---|---|---|---|
| COMPONENT_INVENTORY_FILE | Catalog of all discovered components with component_id, component_type, name, version, validation status (valid/invalid), and file path. Structured as a YAML or JSON inventory. | scan_components (Step 1) | validate_components (Step 2), plan_compositions (Step 3), generate_output (Step 4), refine_output (Step 6) |
| VALIDATION_REPORT_FILE | Detailed per-component validation results listing each validation rule checked (GLOBAL-VR-xxx, HOOK-VR-xxx, etc.), pass/fail status, and error messages for failures. | validate_components (Step 2) | plan_compositions (Step 3), generate_output (Step 4) |
| RESOLUTION_PLAN_FILE | For each composition: binding map with resolved component references, override details, placeholder inventory with data source mapping and resolvability status, required/optional binding presence check, ordering constraint validation. | plan_compositions (Step 3) | generate_output (Step 4), review_output (Step 5), refine_output (Step 6) |
| OUTPUT_FILE | Fully resolved production manuscript in markdown with YAML frontmatter. Contains all required sections (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Production Notes) and conditional sections (Audio Direction, Text Overlay). All component references expanded, overrides applied, placeholders resolved or flagged. | generate_output (Step 4), refine_output (Step 6) | review_output (Step 5) |
| REVIEW_FILE_SUGGESTED | Structured quality review report with findings table (severity, location, description), overall verdict (APPROVED/REJECTED), and evidence citations. | review_output (Step 5) | refine_output (Step 6) |

### 4.3 Traceability

```
COMPONENT_LIBRARY_DIR --> scan_components --> COMPONENT_INVENTORY_FILE
                                                  |
COMPONENT_SCHEMA_FILE --> scan_components --------+
                       --> validate_components --> VALIDATION_REPORT_FILE
                                                  |
COMPOSITIONS_DIR ------> plan_compositions -------+--> RESOLUTION_PLAN_FILE
DATA_SOURCE_DIR -------> plan_compositions --------+
COMPONENT_INVENTORY_FILE -> plan_compositions -----+
VALIDATION_REPORT_FILE --> plan_compositions ------+

RESOLUTION_PLAN_FILE --> generate_output ---> OUTPUT_FILE
COMPONENT_INVENTORY_FILE -> generate_output --+
VALIDATION_REPORT_FILE ----> generate_output --+
DATA_SOURCE_DIR -----------> generate_output --+
OUTPUT_FORMAT_FILE --------> generate_output --+

OUTPUT_FILE ---------> review_output -----> REVIEW_FILE_SUGGESTED
RESOLUTION_PLAN_FILE -> review_output ------+
OUTPUT_FORMAT_FILE ----> review_output -----+

REVIEW_FILE_SUGGESTED --> refine_output ----> OUTPUT_FILE (revised)
OUTPUT_FILE (current) --> refine_output -----+
RESOLUTION_PLAN_FILE --> refine_output ------+
COMPONENT_INVENTORY_FILE -> refine_output ---+
DATA_SOURCE_DIR ---------> refine_output ----+
```

## 5. Action Specifications

### 5.1 Action: scan_components

- **Action name:** scan_components
- **Purpose:** Discover all component markdown files in the component library directory, parse their YAML frontmatter, extract component properties (common and type-specific), classify each by component_type, and produce a structured inventory of all discovered components.
- **Inputs:**
  - `COMPONENT_LIBRARY_DIR`: Directory path containing component files organized in subdirectories by type (hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/)
  - `COMPONENT_SCHEMA_FILE`: Path to the component schema document, used to determine the valid component_type enumeration for classification
- **Outputs:**
  - `COMPONENT_INVENTORY_FILE`: A structured inventory file (YAML format) containing:
    - A list of all discovered component entries, each with: component_id, component_type, name, version, description, file_path, validation_status ("pending"), and all extracted properties (common + type-specific)
    - Summary counts: total components discovered, count per component_type
    - Discovery metadata: scan timestamp, source directory path, total files scanned
- **Logic:**
  1. Recursively walk the COMPONENT_LIBRARY_DIR for all .md files
  2. For each file, read the YAML frontmatter block (content between --- delimiters)
  3. Parse the frontmatter as YAML to extract all properties
  4. Classify the component by its component_type field
  5. Record the file path, component_id, component_type, name, version, description, and all type-specific properties
  6. Set initial validation_status to "pending" for each component
  7. Build summary counts per component_type
  8. Write the inventory to COMPONENT_INVENTORY_FILE
  9. If a file lacks valid YAML frontmatter or a component_id, record it with validation_status "invalid" and an error message
- **Error handling:** If COMPONENT_LIBRARY_DIR does not exist or is empty, return REJECTED with reject_code "EMPTY_COMPONENT_LIBRARY". If no .md files are found, return REJECTED with reject_code "NO_COMPONENTS_FOUND". Individual file parse failures are recorded in the inventory with validation_status "invalid" but do not halt the scan.
- **reused_from:** "new"

### 5.2 Action: validate_components

- **Action name:** validate_components
- **Purpose:** Validate each component in the inventory against the component schema rules. Check common property presence, type enumeration conformance, type-specific property conformance, enum value validity, unique identifier format and uniqueness, semantic version format, cross-property rules, and no-override rule compliance.
- **Inputs:**
  - `COMPONENT_INVENTORY_FILE`: The inventory produced by scan_components containing all discovered components with their properties
  - `COMPONENT_SCHEMA_FILE`: Path to the component schema document containing the validation rules (GLOBAL-VR-001 through GLOBAL-VR-013 and type-specific rules HOOK-VR-xxx, SCENE-VR-xxx, VOICE-VR-xxx, VISDIR-VR-xxx, AUDIO-VR-xxx, TEXT-VR-xxx, TRANS-VR-xxx)
- **Outputs:**
  - `VALIDATION_REPORT_FILE`: A structured validation report containing:
    - Per-component validation results: component_id, validation_status ("valid" or "invalid"), list of rule checks performed, pass/fail per rule, error messages for failures
    - Summary: total components validated, count valid, count invalid, list of invalid component_ids with their error codes
    - Global checks: uniqueness verification (no duplicate component_ids), component_id format verification (matches {type}-{descriptor}-{sequence} pattern)
- **Logic:**
  1. Load the component inventory from COMPONENT_INVENTORY_FILE
  2. Load the validation rules from COMPONENT_SCHEMA_FILE (parse the rule tables for common rules GLOBAL-VR-001 to GLOBAL-VR-013 and type-specific rules)
  3. For each component in the inventory:
     a. Check required common properties: component_id, component_type, name, version, description (GLOBAL-VR-001 to GLOBAL-VR-005)
     b. Check component_type is in the valid enumeration (GLOBAL-VR-006)
     c. Check component_id format matches {type}-{descriptor}-{sequence} pattern (GLOBAL-VR-008)
     d. Check version follows MAJOR.MINOR.PATCH format (GLOBAL-VR-009)
     e. Check all required type-specific properties are present for the declared component_type (GLOBAL-VR-010)
     f. Check data types of property values (GLOBAL-VR-011)
     g. Check enum values are in valid sets (GLOBAL-VR-012)
     h. Apply type-specific validation rules based on component_type (HOOK-VR-xxx, SCENE-VR-xxx, etc.)
     i. Check cross-property rules (e.g., HOOK-VR-006, SCENE-VR-005, VOICE-VR-003)
     j. Record warnings for non-blocking issues (e.g., VOICE-VR-003 dramatic+fast warning)
  4. Perform global uniqueness check: verify no duplicate component_ids (GLOBAL-VR-007)
  5. Check no type-specific property conflicts with common property names (GLOBAL-VR-013)
  6. Update each component's validation_status in the report
  7. Write the validation report to VALIDATION_REPORT_FILE
- **Error handling:** If COMPONENT_INVENTORY_FILE is missing or empty, return REJECTED with reject_code "NO_INVENTORY". If COMPONENT_SCHEMA_FILE is missing, return REJECTED with reject_code "MISSING_SCHEMA". Individual component validation failures are recorded but do not halt processing.
- **reused_from:** "new"

### 5.3 Action: plan_compositions

- **Action name:** plan_compositions
- **Purpose:** Parse all composition files, resolve every component_id reference against the component inventory, validate override conformance, inventory all placeholders and assess resolvability, check required/optional binding presence, verify ordering constraints, and produce a resolution plan that the generate step consumes.
- **Inputs:**
  - `COMPOSITIONS_DIR`: Directory path containing composition YAML files
  - `COMPONENT_INVENTORY_FILE`: The component inventory from scan_components, providing the lookup table for component_id resolution
  - `VALIDATION_REPORT_FILE`: The validation report from validate_components, used to flag references to invalid components
  - `DATA_SOURCE_DIR`: Directory path containing data source files (product_master/, platform_config/, campaign_input/) for placeholder resolvability checking
- **Outputs:**
  - `RESOLUTION_PLAN_FILE`: A structured resolution plan containing, for each composition:
    - composition_id, name, target_metadata
    - Binding map: for each binding, the resolved component (full properties from inventory), applied overrides, and merged result
    - Reference integrity report: each component_id checked against inventory (RESOLVED/MISSING), type matching verified
    - Override conformance report: each override key checked against component type schema (VALID/INVALID_PROPERTY/INVALID_TYPE/INVALID_ENUM)
    - Placeholder inventory: each {placeholder_name} found across all overrides and component values, with data source mapping and resolvability status (RESOLVABLE/UNRESOLVABLE)
    - Binding presence check: required bindings verified present, optional bindings noted as present or omitted
    - Ordering constraint check: scene count (3-8), transition count (N-1 for N scenes if present), singleton bindings verified as single entries (not arrays)
    - Data source availability: each declared data source file checked for existence in DATA_SOURCE_DIR
- **Logic:**
  1. Discover all YAML composition files in COMPOSITIONS_DIR
  2. Load the component inventory as a dictionary keyed by component_id
  3. For each composition file:
     a. Parse the YAML to extract composition_id, name, target_metadata, data_sources, component_bindings
     b. For each binding entry, look up the component_id in the inventory
     c. Verify the referenced component's component_type matches the expected type for the binding slot
     d. For each override, verify the key is a valid property for the component type, verify data type conformance, verify enum value conformance
     e. Scan all override values and resolved component property values for {placeholder_name} patterns
     f. For each placeholder, determine which data source provides the field (Product Master, Platform Config, or Campaign Input)
     g. Load data source files from DATA_SOURCE_DIR and check field availability
     h. Verify required bindings are present (opening_hook, voice_style, visual_direction, scenes)
     i. Check scene count is between 3 and 8
     j. If transitions present, verify count equals (scene count - 1)
     k. Verify singleton bindings contain exactly one component reference
  4. Write the resolution plan to RESOLUTION_PLAN_FILE
- **Error handling:** If COMPOSITIONS_DIR is empty, return REJECTED with reject_code "NO_COMPOSITIONS". If a composition file is not valid YAML, record the composition with status "parse_error" and continue. If a component_id reference is missing from the inventory, flag as CRITICAL in the resolution plan but continue processing other bindings.
- **reused_from:** "new"

### 5.4 Action: step_completion

- **Action name:** step_completion
- **Purpose:** Terminal step that marks the workflow as successfully finished.
- **Inputs:** None
- **Outputs:** None
- **Logic:** Standard terminal action. Returns APPROVED status.
- **reused_from:** "step_completion" (core framework action in agent_runner_v2/actions/step_completion.py)

## 6. Routing Diagram

```
                       +---------------------+
                       | COMPONENT_LIBRARY_DIR|
                       | COMPOSITIONS_DIR     |
                       | DATA_SOURCE_DIR      |
                       | COMPONENT_SCHEMA_FILE|
                       | OUTPUT_FORMAT_FILE   |
                       +---------+-----------+
                                 |
                                 v
                  +-----------------------------+
                  | Step 1: scan_components     |
                  | Type: action                |
                  | Produces: COMPONENT_INVENTORY|
                  +-------------+---------------+
                                | onsuccess
                                v
                  +-----------------------------+
                  | Step 2: validate_components |
                  | Type: action                |
                  | Produces: VALIDATION_REPORT |
                  +-------------+---------------+
                                | onsuccess
                                v
                  +-----------------------------+
                  | Step 3: plan_compositions   |
                  | Type: action                |
                  | Produces: RESOLUTION_PLAN   |
                  +-------------+---------------+
                                | onsuccess
                                v
                  +-----------------------------+
                  | Step 4: generate_output     |
                  | Type: prompt                |
                  | Produces: OUTPUT_FILE       |
                  +-------------+---------------+
                                | onsuccess
                                v
                  +-----------------------------+
                  | Step 5: review_output       |
                  | Type: prompt                |
                  | Produces: REVIEW_FILE       |
                  +---+---------------------+---+
                      |                     |
        onsuccess     |                     | on_reject_refine
                      |                     v
                      |         +-------------------------+
                      |         | Step 6: refine_output   |
                      |         | Type: prompt            |<---+
                      |         | Produces: OUTPUT_FILE   |    |
                      |         +---+---------------------+    |
                      |             | onsuccess                |
                      |             +--------------------------+
                      |             (returns to review_output)
                      v
                  +-----------------------------+
                  | Step 7: stepCompletion      |
                  | Type: action (core)         |
                  +-----------------------------+
```

**Review/Refine Loop Detail:**

```
                  +-------------------+
            +---> | review_output     |--------APPROVED-------> stepCompletion
            |     +---------+---------+
            |               |
            |         REJECTED
            |               |
            |               v
            |     +-------------------+
            +-----+ refine_output     |
                  | (max 2 iterations)|
                  +-------------------+
                         |
                   exhaustion
                         |
                         v
              TERMINAL FAILURE:
              OUTPUT_REVIEW_EXHAUSTED
              class: HUMAN_RETRY_REQUIRED
```

## 7. Review/Refine Loop Design

### 7.1 Loop Configuration

| Attribute | Value |
|---|---|
| Review step | review_output (Step 5) |
| Refine step | refine_output (Step 6) |
| Trigger | review_output produces verdict REJECTED in REVIEW_FILE_SUGGESTED |
| Loop path | review_output --REJECTED--> refine_output --onsuccess--> review_output |
| max_iterations | 2 |
| exhausted_failure_code | OUTPUT_REVIEW_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |

### 7.2 Loop Behavior

1. The review_output step evaluates the generated OUTPUT_FILE against quality criteria.
2. If the verdict is APPROVED, the workflow proceeds to stepCompletion.
3. If the verdict is REJECTED, the workflow routes to refine_output with the REVIEW_FILE_SUGGESTED artifact.
4. The refine_output step addresses each finding from the review, produces a revised OUTPUT_FILE, and routes back to review_output.
5. The review_output step re-evaluates the revised output.
6. If APPROVED on the second pass, the workflow proceeds to stepCompletion.
7. If REJECTED again (max_iterations = 2 reached), the workflow terminates with failure code OUTPUT_REVIEW_EXHAUSTED and failure class HUMAN_RETRY_REQUIRED.

### 7.3 Refinement Scope

The refine_output step must:
- Address each finding from REVIEW_FILE_SUGGESTED individually
- Produce a fix log listing each finding ID, the fix applied, and the section modified
- Not change content that was not flagged by the review
- Maintain cross-section consistency after fixes
- Preserve all fixes from prior iterations (cumulative refinement)

## 8. Package File Inventory

This section enumerates EVERY file the generate_package step must CREATE when packaging this operational workflow into a deployable workflow package. If a file is not listed here, it will not be generated.

### 8.1 Core Files

| File Name | Relative Path | Purpose |
|---|---|---|
| workflow.toml | workflow.toml | The workflow manifest defining all 7 steps, their types (action/prompt), routing (onsuccess, on_reject_refine), artifact declarations (required_inputs, produces), coder role assignments, and review/refine loop configuration. This is the machine-readable execution contract. |
| context_extensions.py | context_extensions.py | The artifact key registration and context injection module. Registers all artifact keys (COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR, COMPONENT_SCHEMA_FILE, OUTPUT_FORMAT_FILE, COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED) with their path patterns and provides context injection for prompt-driven steps. |
| README.md | README.md | User guide describing the workflow's purpose (resolve component compositions into video campaign manuscripts), inputs required (component library, compositions, data sources), execution command (ukbe-run-agent run --template-group video_campaign_manuscript), expected outputs, and troubleshooting guidance. |

### 8.2 Conditional Files

| File Name | Relative Path | Purpose | Condition |
|---|---|---|---|
| actions.py | actions.py | Custom action implementations for scan_components, validate_components, and plan_compositions. Contains three @action-decorated functions with the logic specified in Section 5. | Present because the workflow has 3 custom action steps (scan_components, validate_components, plan_compositions) that are not covered by existing reusable actions. |

### 8.3 Prompt Files

| File Name | Relative Path | Purpose |
|---|---|---|
| 04_generate_output.txt | prompts/04_generate_output.txt | Prompt template for the generate_output step (Step 4). Instructs the LLM to read the RESOLUTION_PLAN_FILE, COMPONENT_INVENTORY_FILE, and DATA_SOURCE_DIR, expand all component references, merge overrides, resolve placeholders, handle unresolved placeholders with {UNRESOLVED: field_name} flagging, and assemble the output into the required section structure per OUTPUT_FORMAT_FILE. Specifies the output path as {OUTPUT_FILE}. Includes file-writing instructions and self-critic section. |
| 05_review_output.txt | prompts/05_review_output.txt | Prompt template for the review_output step (Step 5). Instructs the LLM to evaluate the OUTPUT_FILE against the quality requirements from OUTPUT_FORMAT_FILE: verify reference expansion, placeholder completeness, section integrity, override correctness, cross-section consistency, frontmatter validity, and downstream feasibility. Produces REVIEW_FILE_SUGGESTED with findings table and verdict. |
| 06_refine_output.txt | prompts/06_refine_output.txt | Prompt template for the refine_output step (Step 6). Instructs the LLM to read the REVIEW_FILE_SUGGESTED findings, address each finding individually, fix the OUTPUT_FILE, and write the corrected version. Includes fix log requirement and cross-consistency verification instructions. |

### 8.4 Supplementary Files

| File Name | Relative Path | Purpose |
|---|---|---|
| component_schema.yaml | data/component_schema.yaml | Embedded component schema for the video campaign manuscript domain. Contains the type enumeration (hook, scene, voice_style, visual_direction, audio_mood, text_style, transition), all common property definitions, all type-specific property definitions with data types and enum values, and all validation rules (GLOBAL-VR-xxx, HOOK-VR-xxx, SCENE-VR-xxx, VOICE-VR-xxx, VISDIR-VR-xxx, AUDIO-VR-xxx, TEXT-VR-xxx, TRANS-VR-xxx). The validate_components action reads this file at runtime to perform schema conformance checks. Must be identical to the schema validated by the gatekeeper in the builder's Phase 2 (COMPONENT_SCHEMA_FILE). |
| composition_rules.yaml | data/composition_rules.yaml | Embedded composition format rules for the domain. Defines binding slot names and their expected component_types (opening_hook->hook, voice_style->voice_style, etc.), binding modes (singleton vs ordered_list), required/optional status, ordering constraints (scene count 3-8, transition count N-1), and override conformance rules. The plan_compositions action reads this file at runtime to validate composition structure. Must be identical to the format validated by the gatekeeper in the builder's Phase 3 (COMPOSITION_FORMAT_FILE). |
| output_format_rules.yaml | data/output_format_rules.yaml | Embedded output format specification for the domain. Defines required sections (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay, Production Notes), conditional section rules, frontmatter field requirements, lifecycle_status rules, placeholder flagging syntax, and downstream extraction contracts. The generate_output prompt template and review_output prompt template reference this file for format guidance. Must be identical to the format validated by the gatekeeper in the builder's Phase 4 (OUTPUT_FORMAT_FILE). |
| audiences/definition.yaml | data/audiences/definition.yaml | Audience definition file for the video campaign manuscript domain. Defines target audience segments (e.g., "women aged 25-40 seeking clean beauty", "tech-savvy Gen Z consumers") that may be referenced as data source values for the {target_audience} placeholder. The plan_compositions action uses this to verify placeholder resolvability when {target_audience} appears in compositions. |

### 8.5 Package File Inventory Summary

| Category | Count | Files |
|---|---|---|
| Core files | 3 | workflow.toml, context_extensions.py, README.md |
| Conditional files | 1 | actions.py |
| Prompt files | 3 | prompts/04_generate_output.txt, prompts/05_review_output.txt, prompts/06_refine_output.txt |
| Supplementary files | 4 | data/component_schema.yaml, data/composition_rules.yaml, data/output_format_rules.yaml, data/audiences/definition.yaml |
| **Total** | **11** | |

### 8.6 Files NOT Required

| File | Reason Not Required |
|---|---|
| .env.sample | No external API keys or service URLs required. The workflow operates entirely on local files. |
| config.json.sample | No runtime configuration beyond artifact paths. All settings are deterministic. |

## 9. Self-Check

### 9.1 Phase Coverage Verification

| Phase (from COMPOSITION_SYSTEM_STANDARD.md Section 6) | Covered By Step | Step Type | Status |
|---|---|---|---|
| Scan: Discover and validate components | scan_components (Step 1) + validate_components (Step 2) | action + action | COVERED |
| Plan: Resolve compositions against inventory | plan_compositions (Step 3) | action | COVERED |
| Generate: Assemble outputs | generate_output (Step 4) | prompt | COVERED |
| Review: Quality review | review_output (Step 5) | prompt | COVERED |
| Refine: Fix issues (conditional) | refine_output (Step 6) | prompt | COVERED |

All five phases are covered. No phase is missing.

### 9.2 Artifact Flow Verification

| Step | Input Artifacts | All Inputs Produced By Prior Step or External? |
|---|---|---|
| scan_components | COMPONENT_LIBRARY_DIR (external), COMPONENT_SCHEMA_FILE (external) | YES - both are declared workflow inputs |
| validate_components | COMPONENT_INVENTORY_FILE (Step 1), COMPONENT_SCHEMA_FILE (external) | YES |
| plan_compositions | COMPOSITIONS_DIR (external), COMPONENT_INVENTORY_FILE (Step 1), VALIDATION_REPORT_FILE (Step 2), DATA_SOURCE_DIR (external) | YES |
| generate_output | RESOLUTION_PLAN_FILE (Step 3), COMPONENT_INVENTORY_FILE (Step 1), VALIDATION_REPORT_FILE (Step 2), DATA_SOURCE_DIR (external), OUTPUT_FORMAT_FILE (external) | YES |
| review_output | OUTPUT_FILE (Step 4), RESOLUTION_PLAN_FILE (Step 3), OUTPUT_FORMAT_FILE (external) | YES |
| refine_output | REVIEW_FILE_SUGGESTED (Step 5), OUTPUT_FILE (Step 4), RESOLUTION_PLAN_FILE (Step 3), COMPONENT_INVENTORY_FILE (Step 1), DATA_SOURCE_DIR (external) | YES |
| stepCompletion | -- | YES (no inputs required) |

No dangling references. Every step's inputs are produced by a prior step or declared as workflow-level inputs.

### 9.3 Step Type Classification Verification

| Step | Type | Justification |
|---|---|---|
| scan_components | action | File discovery and YAML parsing are deterministic operations |
| validate_components | action | Schema validation against defined rules is deterministic |
| plan_compositions | action | Reference resolution, override validation, and placeholder inventory are deterministic |
| generate_output | prompt | Assembling human-readable deliverables requires LLM judgment for formatting and coherence |
| review_output | prompt | Quality assessment against criteria requires LLM judgment for interpretation |
| refine_output | prompt | Fixing semantic issues requires LLM judgment for understanding context |
| stepCompletion | action | Terminal signal, no judgment required |

### 9.4 Test Criteria Alignment (TC-OW-001 through TC-OW-N03)

| Test Criteria ID | Requirement | Status | Evidence |
|---|---|---|---|
| TC-OW-001 | All five phases defined | SATISFIED | Section 2 defines scan, plan, generate, review, refine |
| TC-OW-002 | Each phase has clear objective | SATISFIED | Section 2.1-2.5 each have objective statements |
| TC-OW-003 | Phase boundaries explicit | SATISFIED | Each phase's output feeds the next phase's input (Section 4.3) |
| TC-OW-004 | Logical step ordering | SATISFIED | scan -> validate -> plan -> generate -> review (-> refine) -> complete |
| TC-OW-005 | Complete step sequence | SATISFIED | All operations covered: discovery, validation, resolution, assembly, review, refinement |
| TC-OW-006 | At least one action and one prompt step | SATISFIED | 4 action steps, 3 prompt steps |
| TC-OW-007 | Every step declares inputs and outputs | SATISFIED | Section 3 table lists required_inputs and produces for each step |
| TC-OW-008 | Artifact key naming convention | SATISFIED | Keys follow UPPER_SNAKE_CASE with _FILE suffix |
| TC-OW-009 | Input artifacts from Standard Section 6.3 | SATISFIED | COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR declared |
| TC-OW-010 | Output artifacts from Standard Section 6.4 | SATISFIED | COMPONENT_INVENTORY_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED declared |
| TC-OW-011 | Deterministic operations as action steps | SATISFIED | scan, validate, plan are actions |
| TC-OW-012 | Action step specifications complete | SATISFIED | Section 5 specifies name, inputs, outputs, logic, error handling, reuse |
| TC-OW-013 | Action reuse identified | SATISFIED | step_completion reused from core; scan/validate/plan are new |
| TC-OW-014 | LLM-judgment steps as prompt-driven | SATISFIED | generate_output, review_output, refine_output are prompts |
| TC-OW-015 | Prompt step specifications complete | SATISFIED | Section 3 specifies step name, produces, required_inputs, routing |
| TC-OW-016 | Prompt context injection specified | SATISFIED | Section 3 lists required_inputs for each prompt step |
| TC-OW-017 | Routing defined per step | SATISFIED | Section 3 table shows onsuccess and on_reject_refine for each step |
| TC-OW-018 | Review-refine loop correctly wired | SATISFIED | review routes to refine on reject, refine routes to review on success |
| TC-OW-019 | Exhaustion condition defined | SATISFIED | max_iterations=2, exhausted_failure_code=OUTPUT_REVIEW_EXHAUSTED |
| TC-OW-020 | Terminal step is step_completion | SATISFIED | Step 7 is stepCompletion using core step_completion action |
| TC-OW-021 | Self-check covers all phases | SATISFIED | Section 9.1 verifies phase coverage |
| TC-OW-022 | Artifact flow complete | SATISFIED | Section 9.2 verifies no dangling references |
| TC-OW-023 | No orphan steps | SATISFIED | Section 6 routing diagram shows all steps connected |
| TC-OW-N01 | No steps without phase | SATISFIED | All 6 non-terminal steps map to one of the 5 phases |
| TC-OW-N02 | Scan phase not skipped | SATISFIED | Steps 1-2 implement scan phase |
| TC-OW-N03 | No prompt steps for deterministic ops | SATISFIED | scan, validate, plan are actions (not prompts) |

### 9.5 Package Inventory Traceability

| Supplementary File | Referenced In Design | Step That Uses It |
|---|---|---|
| data/component_schema.yaml | Section 5.1 (scan_components inputs), Section 5.2 (validate_components inputs) | scan_components, validate_components |
| data/composition_rules.yaml | Section 5.3 (plan_compositions logic references binding rules) | plan_compositions |
| data/output_format_rules.yaml | Section 2.3 (generate_output references output format rules) | generate_output, review_output |
| data/audiences/definition.yaml | Section 2.2 (plan_compositions checks placeholder resolvability for {target_audience}) | plan_compositions |

All supplementary files are traceable to specific steps and operations.

---

**End of Operational Workflow Design**
