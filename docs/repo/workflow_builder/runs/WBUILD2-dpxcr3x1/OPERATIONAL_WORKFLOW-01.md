---
doc_type: "operational_workflow"
lifecycle_status: "draft"
effective_version: "WBUILD2-dpxcr3x1"
domain: "video_campaign_manuscript"
step_count: 6
action_count: 3
source_spec: "video_campaign_manuscript_v2.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
created_at: "2026-08-08"
---

# Operational Workflow Design: Video Campaign Manuscript Composition System

## Overview

This operational workflow design defines the execution pipeline for the video_campaign_manuscript composition system. The workflow implements the three-layer composition architecture: it takes a component library (Layer 1) of reusable creative building blocks and declarative composition definitions (Layer 2) as input, then produces fully resolved video production manuscripts (Layer 3) as output. The end-to-end transformation is: component files organized by type in a directory are scanned and validated into a structured inventory; composition YAML files referencing components by ID are resolved against the inventory with overrides and placeholder substitution applied; complete manuscripts are assembled with all component content expanded, all overrides merged, and all placeholders filled from external data sources. The domain context is short-form video campaign production (15-90 seconds) for platforms including TikTok, Instagram Reels, and YouTube Shorts, where manuscripts coordinate seven creative concerns -- opening hook, content scenes, voice direction, visual treatment, audio mood, text overlays, and scene transitions -- into a unified production guide consumed by downstream voiceover, visual asset, video editing, and platform adaptation workflows.

## Workflow Phases

### Scan Phase

**Objective:** Discover all component files in the component library directory, parse their YAML frontmatter, extract component properties, classify each component by its declared component_type, and validate each component against the domain schema rules.

**What is scanned:** All markdown files (*.md) within the COMPONENT_LIBRARY_DIR, which is organized into type-specific subdirectories: hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/. Each file contains YAML frontmatter with common properties (component_id, component_type, name, version, description, duration_range, platforms, tags) and type-specific properties.

**What validation is performed:**
- Required fields presence (GLOBAL-VR-001 through GLOBAL-VR-005): component_id, component_type, name, version, description must be present and non-empty.
- Component type validity (GLOBAL-VR-006): component_type must be one of the 7 recognized types.
- Component ID uniqueness (GLOBAL-VR-007): No duplicate component_id values across the entire library.
- Component ID naming convention (GLOBAL-VR-008): Must match pattern {type}-{descriptor}-{seq}.
- Type-specific property presence (GLOBAL-VR-009): All required type-specific properties for the declared type must be present.
- Type-specific property types (GLOBAL-VR-010): Each property value must match its declared data type.
- Property name conflicts (GLOBAL-VR-011): Type-specific properties must not use reserved common property names.
- Semantic version format (GLOBAL-VR-012): Must match MAJOR.MINOR.PATCH pattern.
- Duration format (GLOBAL-VR-014): duration_range must match \d+(-\d+)?s pattern.
- Type-specific enum validation: hook_style, energy_level, scene_purpose, voice_tone, pace, visual_style, lighting_mood, mood, tempo, text_treatment, text_animation, transition_type, transition_energy must use only declared enum values.
- Type-specific cross-property validation: e.g., hook_style=visual_reveal requires visual_cue >= 20 characters (HOOK-VR-006); transition_type=whip_pan requires transition_energy moderate or dramatic (TRANS-VR-005).

**Produces:** COMPONENT_INVENTORY_FILE (catalog of all discovered components with type classification and validation status), VALIDATION_REPORT_FILE (detailed validation results per component with rule IDs).

### Plan Phase

**Objective:** Read all composition YAML files from the compositions directory, resolve every component_id reference against the component inventory, validate overrides against type schemas, check binding constraints, and inventory all placeholders for resolvability assessment.

**What compositions are read:** All YAML files (*.yaml, *.yml) within the COMPOSITIONS_DIR. Each composition contains: composition_id, name, target_metadata (duration_target, target_platforms, campaign_type, brand), data_sources (product_master, campaign_input, platform_config paths), and component_bindings (opening, scenes, voice, visuals, audio, text, transitions).

**What references are resolved:**
- Reference integrity (CF-VAL-001, CF-VAL-002): Every component_id in every binding must exist in the component inventory and must match the expected component_type for its binding slot.
- Override conformance (CF-VAL-003 through CF-VAL-005): All override keys must be valid type-specific properties for the referenced component type. Override values must respect data type constraints and enum value restrictions.
- Required bindings (CF-VAL-006, CF-VAL-007): All required bindings (opening, scenes, voice, visuals, audio, transitions) must be present. Optional bindings (text) are validated only if present.
- Ordering constraints (CF-VAL-010, CF-VAL-011, CF-VAL-012): Scene count must be 3-8. Transition count must equal scene count minus 1. Singleton bindings must contain exactly one component reference.
- Placeholder resolvability (CF-VAL-008, CF-VAL-009): All {placeholder} tokens in override values and component property values are inventoried. Each placeholder is checked against the data source files declared in the composition. Unresolvable placeholders are flagged.

**Produces:** RESOLUTION_PLAN_FILE (for each composition: resolved component references, override details, placeholder inventory with resolvability status, binding constraint validation results).

### Generate Phase

**Objective:** For each composition described in the resolution plan, expand all component references to full content, apply all overrides, resolve all placeholders from data sources, interleave scenes and transitions, and assemble the complete manuscript output.

**What outputs are generated:** One resolved manuscript file per composition. Each output is a markdown file with YAML frontmatter containing: composition_id, composition_name, metadata (duration_target, target_platforms, campaign_type, brand), component_count, generation_date, lifecycle_status, unresolved_placeholder_count.

**How outputs are assembled:**
1. Component reference expansion: Each component_id from the resolution plan is replaced with the full component content (all common properties and all type-specific properties). Overrides from the composition are merged (override wins on conflict).
2. Placeholder resolution: All {placeholder} tokens are replaced with values from the data source files (Product Master, Campaign Input, Platform Config). Priority: Product Master > Campaign Input > Platform Config. Unresolvable placeholders are rendered as {UNRESOLVED: field_name}.
3. Scene-transition interleaving: Scenes and transitions are rendered in order: Scene 1, Transition 1, Scene 2, Transition 2, ..., Scene N.
4. Output sections: Opening (Hook), Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay (conditional -- only if text binding present), Production Notes.
5. Production Notes include: Timing Summary (total duration calculation), Platform Considerations (per-platform notes), Placeholder Resolution Summary (inventory of all placeholders with status), Component Summary (count per type).

**Produces:** OUTPUT_FILE (one resolved manuscript per composition).

### Review Phase

**Objective:** Quality review of each generated manuscript against the output format quality requirements, checking for dangling references, unresolved placeholders, schema conformance, completeness, and cross-section consistency.

**What quality checks are performed:**
- No dangling references: All component_id references must be fully expanded. No residual component_id text in the output.
- No unresolved raw placeholders: All {placeholder} tokens must be either resolved or flagged as {UNRESOLVED: field_name}.
- Schema conformance: All overrides applied must conform to the referenced component type schema. Enum values must be valid. Duration formats must match patterns.
- Completeness: All required output sections must be present (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Production Notes). Text Overlay section is conditionally required.
- Consistency: No contradictions between sections. Voice pace must be compatible with hook energy_level. Total duration must be consistent with sum of scene/transition durations. component_count in frontmatter must match actual expanded components. lifecycle_status must be consistent with unresolved_placeholder_count.
- Platform considerations: Output must note platform-specific constraints for each platform in target_platforms.
- Timing accuracy: Scene durations must sum to within the duration_target range.

**Produces:** REVIEW_FILE_SUGGESTED (quality review document with APPROVED/REJECTED verdict and specific findings).

### Refine Phase (Conditional)

**Objective:** Fix issues identified in the review report. The refine step addresses each finding individually, correcting the output manuscript to resolve dangling references, fix placeholder handling, correct override conformance issues, or add missing sections.

**What issues are fixed:**
- Missing sections are added.
- Dangling component references are expanded.
- Unresolved placeholders are properly flagged with {UNRESOLVED: field_name} syntax.
- Override conformance issues are corrected.
- Cross-section inconsistencies are resolved.
- Timing calculations are corrected.

**Produces:** Updated OUTPUT_FILE (corrected manuscript).

**Routing:** After refinement, the workflow returns to the review phase for re-validation. The refine step does not self-certify its fixes.

## Step Sequence

| Seq | Step Name | Type | Phase | Purpose | required_inputs | produces | onsuccess | on_reject_refine |
|---|---|---|---|---|---|---|---|---|
| 1 | scan_components | action | Scan | Discover and validate all components in the library | COMPONENT_LIBRARY_DIR | COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE | plan_compositions | -- |
| 2 | plan_compositions | action | Plan | Resolve compositions against inventory, validate bindings, inventory placeholders | COMPONENT_INVENTORY_FILE, COMPOSITIONS_DIR, DATA_SOURCE_DIR | RESOLUTION_PLAN_FILE | generate_output | -- |
| 3 | generate_output | prompt | Generate | Expand components, apply overrides, resolve placeholders, assemble manuscripts | COMPONENT_INVENTORY_FILE, RESOLUTION_PLAN_FILE, COMPONENT_SCHEMA_FILE, OUTPUT_FORMAT_FILE | OUTPUT_FILE | review_output | -- |
| 4 | review_output | prompt | Review | Quality review of generated manuscripts against format requirements | OUTPUT_FILE, RESOLUTION_PLAN_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | REVIEW_FILE_SUGGESTED | step_completion | refine_output (max 2) |
| 5 | refine_output | prompt | Refine | Fix issues found in review | REVIEW_FILE_SUGGESTED, OUTPUT_FILE, RESOLUTION_PLAN_FILE | OUTPUT_FILE | review_output | -- |
| 6 | step_completion | action | Terminal | Mark workflow as successfully completed | -- | -- | -- | -- |

### Step Details

#### Step 1: scan_components

- **Step name:** scan_components
- **Step type:** action
- **Purpose:** Scan the component library directory for markdown files with YAML frontmatter. Parse each file to extract component properties. Classify each component by component_type. Validate each component against the 7-type schema (GLOBAL-VR rules plus type-specific rules). Produce a structured inventory and a detailed validation report.
- **required_inputs:** COMPONENT_LIBRARY_DIR
- **produces:** COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE
- **Routing:** onsuccess -> plan_compositions
- **Error handling:** If the directory does not exist or contains no markdown files, return ActionResult with status "REJECTED" and remark explaining the failure. Individual component validation failures do not halt the scan -- invalid components are recorded with status "invalid" and specific validation errors in the VALIDATION_REPORT_FILE.

#### Step 2: plan_compositions

- **Step name:** plan_compositions
- **Step type:** action
- **Purpose:** Read all composition YAML files from COMPOSITIONS_DIR. For each composition, resolve every component_id against the component inventory. Validate overrides against type schemas. Check binding constraints (scene count 3-8, transition count = N-1, singleton bindings). Inventory all placeholders and assess resolvability against data source files in DATA_SOURCE_DIR. Produce a resolution plan that the generate step consumes.
- **required_inputs:** COMPONENT_INVENTORY_FILE, COMPOSITIONS_DIR, DATA_SOURCE_DIR
- **produces:** RESOLUTION_PLAN_FILE
- **Routing:** onsuccess -> generate_output
- **Error handling:** If COMPOSITIONS_DIR is empty, return ActionResult with status "REJECTED" and remark "No compositions found". If a data source file declared in a composition does not exist, flag the composition with a MAJOR finding but continue processing other compositions. CRITICAL findings (missing required bindings, broken references) prevent resolution of the affected composition but do not halt the overall plan.

#### Step 3: generate_output

- **Step name:** generate_output
- **Step type:** prompt
- **Purpose:** For each valid composition in the resolution plan, expand all component references to full content, apply overrides (override wins on conflict), resolve all placeholders from data sources, interleave scenes and transitions, and assemble the complete manuscript output in the format defined by OUTPUT_FORMAT_FILE.
- **required_inputs:** COMPONENT_INVENTORY_FILE, RESOLUTION_PLAN_FILE, COMPONENT_SCHEMA_FILE, OUTPUT_FORMAT_FILE
- **produces:** OUTPUT_FILE
- **Routing:** onsuccess -> review_output
- **Prompt template:** prompts/03_generate_output.txt
- **Context injection:** The prompt receives the component inventory (for looking up component content), the resolution plan (for knowing which components to expand and what overrides/placeholders to apply), the component schema (for understanding property types and enum values), and the output format specification (for structuring the output correctly).
- **Success criteria:** Every valid composition in the resolution plan produces a corresponding output file. All component references are fully expanded. All placeholders are resolved or flagged as {UNRESOLVED: field_name}. Output format matches OUTPUT_FORMAT_FILE specification.

#### Step 4: review_output

- **Step name:** review_output
- **Step type:** prompt
- **Purpose:** Quality review of each generated manuscript against the output format quality requirements. Check for dangling references, unresolved raw placeholders, schema conformance, section completeness, and cross-section consistency. Produce a verdict (APPROVED or REJECTED) with specific findings.
- **required_inputs:** OUTPUT_FILE, RESOLUTION_PLAN_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE
- **produces:** REVIEW_FILE_SUGGESTED
- **Routing:** onsuccess -> step_completion; on_reject_refine -> refine_output
- **Prompt template:** prompts/04_review_output.txt
- **Context injection:** The prompt receives the generated output, the resolution plan (to verify correct component expansion), the component schema (to check override conformance), the composition format (to verify binding rules), and the output format specification (to check section completeness and quality requirements).
- **Success criteria:** Verdict is supported by specific evidence per quality requirement. Each finding cites the section, the rule violated, and the specific issue.
- **on_reject_refine configuration:**
  - step: refine_output
  - artifact: REVIEW_FILE_SUGGESTED
  - max_iterations: 2
  - exhausted_failure_code: "OUTPUT_REVIEW_EXHAUSTED"
  - exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

#### Step 5: refine_output

- **Step name:** refine_output
- **Step type:** prompt
- **Purpose:** Fix each issue identified in the review report. Address findings individually -- correct dangling references, fix placeholder flagging, resolve override conformance issues, add missing sections, or correct cross-section inconsistencies. Do not make changes outside the scope of review findings.
- **required_inputs:** REVIEW_FILE_SUGGESTED, OUTPUT_FILE, RESOLUTION_PLAN_FILE
- **produces:** OUTPUT_FILE
- **Routing:** onsuccess -> review_output (returns to review for re-validation)
- **Prompt template:** prompts/05_refine_output.txt
- **Context injection:** The prompt receives the review report (with specific findings), the current output (to be corrected), and the resolution plan (to verify corrections).
- **Success criteria:** Every finding from the review report is addressed. Fix log lists each finding, the fix applied, and the section modified. No new issues introduced.

#### Step 6: step_completion

- **Step name:** step_completion
- **Step type:** action
- **Purpose:** Terminal step that marks the workflow as successfully completed. Sets job status to COMPLETED.
- **required_inputs:** --
- **produces:** --
- **Routing:** Terminal step (no onsuccess)
- **reused_from:** step_completion (existing core action)

## Artifact Contract

### Input Artifacts

| Artifact Key | Description | Required | Provided By |
|---|---|---|---|
| COMPONENT_LIBRARY_DIR | Directory containing component markdown files organized by type subdirectory (hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/) | Yes | User at workflow invocation |
| COMPOSITIONS_DIR | Directory containing composition YAML files defining how components are assembled | Yes | User at workflow invocation |
| DATA_SOURCE_DIR | Directory containing Product Master, Campaign Input, and Platform Config data files for placeholder resolution | Yes | User at workflow invocation |
| COMPONENT_SCHEMA_FILE | Component schema definition (7 types, common properties, type-specific properties, validation rules) | Yes | Builder Phase 2 output (deployed as supplementary file in package) |
| COMPOSITION_FORMAT_FILE | Composition format definition (binding rules, override mechanism, placeholder resolution rules) | Yes | Builder Phase 3 output (deployed as supplementary file in package) |
| OUTPUT_FORMAT_FILE | Output format definition (section structure, resolution rules, quality requirements) | Yes | Builder Phase 4 output (deployed as supplementary file in package) |

### Output Artifacts

| Artifact Key | Description | Produced By |
|---|---|---|
| COMPONENT_INVENTORY_FILE | Catalog of all discovered components with type classification, component_id, validation status (valid/invalid), and extracted properties | scan_components (Step 1) |
| VALIDATION_REPORT_FILE | Detailed validation results per component with rule IDs, error messages, and severity levels | scan_components (Step 1) |
| RESOLUTION_PLAN_FILE | For each composition: resolved component references, override details, placeholder inventory with resolvability status, binding constraint validation results | plan_compositions (Step 2) |
| OUTPUT_FILE | The assembled video campaign manuscript (one per valid composition) with all components expanded, overrides applied, placeholders resolved | generate_output (Step 3), refine_output (Step 5) |
| REVIEW_FILE_SUGGESTED | Quality review document with APPROVED/REJECTED verdict, specific findings per quality requirement, and evidence citations | review_output (Step 4) |

### Traceability Matrix

| Output Artifact | Produced By Step | Consumed By Steps |
|---|---|---|
| COMPONENT_INVENTORY_FILE | scan_components (Step 1) | plan_compositions (Step 2), generate_output (Step 3) |
| VALIDATION_REPORT_FILE | scan_components (Step 1) | (workflow-level output, not consumed by subsequent steps) |
| RESOLUTION_PLAN_FILE | plan_compositions (Step 2) | generate_output (Step 3), review_output (Step 4), refine_output (Step 5) |
| OUTPUT_FILE | generate_output (Step 3) | review_output (Step 4), refine_output (Step 5) |
| OUTPUT_FILE (revised) | refine_output (Step 5) | review_output (Step 4, on re-validation loop) |
| REVIEW_FILE_SUGGESTED | review_output (Step 4) | refine_output (Step 5) |

### Artifact Flow Verification

Every step's required_inputs reference artifacts produced by a prior step or declared as workflow-level inputs:

- scan_components reads COMPONENT_LIBRARY_DIR (workflow input). VALID.
- plan_compositions reads COMPONENT_INVENTORY_FILE (Step 1 output), COMPOSITIONS_DIR (workflow input), DATA_SOURCE_DIR (workflow input). VALID.
- generate_output reads COMPONENT_INVENTORY_FILE (Step 1 output), RESOLUTION_PLAN_FILE (Step 2 output), COMPONENT_SCHEMA_FILE (workflow input), OUTPUT_FORMAT_FILE (workflow input). VALID.
- review_output reads OUTPUT_FILE (Step 3 output), RESOLUTION_PLAN_FILE (Step 2 output), COMPONENT_SCHEMA_FILE (workflow input), COMPOSITION_FORMAT_FILE (workflow input), OUTPUT_FORMAT_FILE (workflow input). VALID.
- refine_output reads REVIEW_FILE_SUGGESTED (Step 4 output), OUTPUT_FILE (Step 3 output), RESOLUTION_PLAN_FILE (Step 2 output). VALID.
- step_completion reads no inputs. VALID.

No dangling references detected.

## Action Specifications

### Action 1: scan_components

- **Action name:** scan_components
- **Purpose:** Scan the component library directory for markdown files with YAML frontmatter. Parse each file, extract component properties, classify by component_type, validate against schema rules, and produce a structured inventory and validation report.
- **Inputs:**
  - context["COMPONENT_LIBRARY_DIR"]: Absolute path to the component library directory.
  - context["COMPONENT_SCHEMA_FILE"]: Absolute path to the component schema definition file (embedded in the workflow package at schema/component_schema.md).
  - project_root: The workflow package root directory.
- **Outputs:**
  - COMPONENT_INVENTORY_FILE: JSON file containing an array of component records. Each record: {component_id, component_type, name, version, description, duration_range, platforms, tags, validation_status ("valid" or "invalid"), validation_errors (list of rule IDs), file_path (relative path within library)}.
  - VALIDATION_REPORT_FILE: Markdown file with validation summary: total components scanned, count by type, count valid/invalid, detailed per-component findings with rule IDs and error messages.
- **Logic:**
  1. Walk the COMPONENT_LIBRARY_DIR recursively for *.md files.
  2. For each file, parse YAML frontmatter between --- markers.
  3. Extract common properties (component_id, component_type, name, version, description, duration_range, platforms, tags).
  4. Determine component_type and extract type-specific properties.
  5. Validate common properties against GLOBAL-VR rules (presence, type validity, uniqueness, naming convention, version format, duration format).
  6. Validate type-specific properties against type-specific rules (enum values, required fields, cross-property constraints).
  7. Record validation status and any errors with rule IDs.
  8. Build the component inventory sorted by type then component_id.
  9. Write COMPONENT_INVENTORY_FILE as JSON and VALIDATION_REPORT_FILE as markdown.
- **reused_from:** new
- **Error handling:**
  - Directory not found: Return REJECTED with "Component library directory not found at {path}".
  - No markdown files found: Return REJECTED with "No component files found in {path}".
  - YAML parse error in a file: Record as invalid component with parse error, continue scanning remaining files.
  - Duplicate component_id: Record both occurrences as invalid with GLOBAL-VR-007 violation.

### Action 2: plan_compositions

- **Action name:** plan_compositions
- **Purpose:** Read all composition YAML files, resolve component_id references against the inventory, validate overrides against type schemas, check binding constraints, inventory placeholders, and assess resolvability against data sources.
- **Inputs:**
  - context["COMPONENT_INVENTORY_FILE"]: Absolute path to the component inventory JSON file (from scan_components).
  - context["COMPOSITIONS_DIR"]: Absolute path to the directory containing composition YAML files.
  - context["DATA_SOURCE_DIR"]: Absolute path to the directory containing data source files.
  - context["COMPONENT_SCHEMA_FILE"]: Absolute path to the component schema definition file.
  - project_root: The workflow package root directory.
- **Outputs:**
  - RESOLUTION_PLAN_FILE: Markdown file containing, for each composition: (a) composition metadata (composition_id, name, target_metadata), (b) resolved component references listing each binding with its component_id, resolved properties, and applied overrides, (c) placeholder inventory listing each unique placeholder with its expected data source and resolvability status, (d) binding constraint validation results (scene count, transition count, singleton checks), (e) composition-level validation verdict (RESOLVABLE, RESOLVABLE_WITH_WARNINGS, or UNRESOLVABLE) with specific findings.
- **Logic:**
  1. Load the component inventory JSON. Build a lookup map: component_id -> component record.
  2. Walk COMPOSITIONS_DIR for *.yaml and *.yml files.
  3. For each composition file, parse the YAML structure.
  4. Validate required top-level fields: composition_id, name, target_metadata, data_sources, component_bindings.
  5. For each binding in component_bindings:
     a. Check binding name is recognized (opening, scenes, voice, visuals, audio, text, transitions).
     b. For each component_id reference, look up in the inventory map. If not found, flag as CRITICAL (CF-VAL-001).
     c. Verify component_type matches the expected type for the binding slot. If mismatch, flag as CRITICAL (CF-VAL-002).
     d. If overrides are present, validate each override key is a valid type-specific property for the component type (CF-VAL-003). Validate override values respect data type constraints and enum restrictions (CF-VAL-004, CF-VAL-005).
  6. Check binding constraints:
     a. All required bindings present (opening, scenes, voice, visuals, audio, transitions). Flag missing as CRITICAL (CF-VAL-006).
     b. Scene count between 3-8 (CF-VAL-010).
     c. Transition count = scene count - 1 (CF-VAL-011).
     d. Singleton bindings contain exactly one component reference (CF-VAL-012).
  7. Inventory placeholders: Scan all override values and component property values for {placeholder_name} patterns. For each placeholder:
     a. Read data source files declared in the composition's data_sources section.
     b. Check if the placeholder field_name exists in any data source.
     c. Record placeholder with its source and resolvability status (RESOLVABLE/UNRESOLVABLE).
  8. Assign composition verdict: RESOLVABLE (no CRITICAL findings), RESOLVABLE_WITH_WARNINGS (MAJOR findings only), UNRESOLVABLE (any CRITICAL finding).
  9. Write RESOLUTION_PLAN_FILE as markdown.
- **reused_from:** new
- **Error handling:**
  - COMPOSITIONS_DIR not found: Return REJECTED with "Compositions directory not found at {path}".
  - No composition files found: Return REJECTED with "No composition files found in {path}".
  - YAML parse error in a composition file: Flag composition as UNRESOLVABLE with parse error, continue processing others.
  - Data source file not found: Flag as MAJOR finding (CF-VAL-009) for affected composition.
  - Component inventory is empty: Return REJECTED with "Component inventory is empty -- cannot resolve compositions".

### Action 3: step_completion

- **Action name:** step_completion
- **Purpose:** Terminal step that finalizes the workflow. Sets job status to COMPLETED.
- **Inputs:** None.
- **Outputs:** None.
- **Logic:** Call set_job_status(state, "COMPLETED"). Return ActionResult with status "APPROVED".
- **reused_from:** step_completion (existing core action in agent_runner_v2/actions/step_completion.py)

## Routing Diagram

```
                          WORKFLOW INPUTS
                +---------------------------------+
                | COMPONENT_LIBRARY_DIR            |
                | COMPOSITIONS_DIR                 |
                | DATA_SOURCE_DIR                  |
                | COMPONENT_SCHEMA_FILE            |
                | COMPOSITION_FORMAT_FILE          |
                | OUTPUT_FORMAT_FILE               |
                +---------------------------------+
                              |
                              v
                  +------------------------+
                  | 1. scan_components     |
                  | (action)               |
                  | Phase: Scan            |
                  +------------------------+
                   |                      |
                   | produces:            |
                   |  COMPONENT_INVENTORY  |
                   |  _FILE               |
                   |  VALIDATION_REPORT   |
                   |  _FILE               |
                   v                      |
                  +------------------------+
                  | 2. plan_compositions   |
                  | (action)               |
                  | Phase: Plan            |
                  +------------------------+
                   |                      |
                   | produces:            |
                   |  RESOLUTION_PLAN     |
                   |  _FILE               |
                   v                      |
                  +------------------------+
                  | 3. generate_output     |
                  | (prompt)               |
                  | Phase: Generate        |
                  +------------------------+
                   |                      |
                   | produces:            |
                   |  OUTPUT_FILE         |
                   v                      |
              +------------------------+  |
              | 4. review_output       |  |
              | (prompt)               |  |
              | Phase: Review          |  |
              +------------------------+  |
               |         |               |
    onsuccess  |         | on_reject     |
               |         v               |
               |  +------------------------+
               |  | 5. refine_output      |
               |  | (prompt)              |
               |  | Phase: Refine         |
               |  +------------------------+
               |   |                      |
               |   | produces:            |
               |   |  OUTPUT_FILE (revised)|
               |   |                      |
               |   | onsuccess:           |
               |   +------> review_output |
               |         (loop back,      |
               |          max 2 iterations)|
               v                          |
          +------------------------+      |
          | 6. step_completion     |<-----+
          | (action)               |
          | Phase: Terminal        |
          +------------------------+
```

### Routing Summary

| Step | onsuccess | on_reject_refine |
|---|---|---|
| scan_components | plan_compositions | -- |
| plan_compositions | generate_output | -- |
| generate_output | review_output | -- |
| review_output | step_completion | refine_output (max_iterations=2, exhausted_failure_code="OUTPUT_REVIEW_EXHAUSTED") |
| refine_output | review_output | -- |
| step_completion | (terminal) | -- |

## Review/Refine Loop Design

### Loop: review_output / refine_output

**Which steps are involved:**
- review_output (Step 4): Reviews the generated manuscript and produces a verdict.
- refine_output (Step 5): Fixes issues found in the review and returns the manuscript for re-review.

**What triggers refinement:**
- The review_output step produces a REJECTED verdict in its REVIEW_FILE_SUGGESTED output.
- A REJECTED verdict means at least one CRITICAL or MAJOR finding was identified: missing required sections, dangling component references, unresolved raw placeholders, override conformance violations, cross-section contradictions, or timing inconsistencies.

**Loop flow:**
1. review_output produces REVIEW_FILE_SUGGESTED with verdict REJECTED.
2. on_reject_refine triggers, routing to refine_output.
3. refine_output reads the review findings and the current OUTPUT_FILE, fixes each issue, and writes a corrected OUTPUT_FILE.
4. refine_output's onsuccess routes back to review_output.
5. review_output re-evaluates the corrected OUTPUT_FILE.
6. If APPROVED: onsuccess routes to step_completion. Workflow succeeds.
7. If REJECTED again: on_reject_refine triggers again (iteration 2).

**Maximum iterations:** max_iterations = 2

This means the loop can execute at most twice:
- Iteration 1: review -> refine -> review
- Iteration 2: review -> refine -> review
- After iteration 2, if still REJECTED, the loop is exhausted.

**Exhaustion behavior:**
- exhausted_failure_code: "OUTPUT_REVIEW_EXHAUSTED"
- exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
- The workflow terminates with a failure status. A human operator must intervene to resolve the remaining issues.

**Rationale for max_iterations = 2:**
- Most quality issues are correctable in one refinement pass.
- Two iterations allow for cases where the first fix introduces secondary issues that need a second correction.
- Beyond two iterations, the issues are likely structural and require human judgment to resolve.

## Package File Inventory

This section enumerates EVERY file the generate_package step must create when assembling the target workflow package. The target workflow package implements the composition system workflow defined in this operational workflow design.

### Core Files

| File Name | Relative Path | Purpose |
|---|---|---|
| workflow.toml | workflow.toml | Workflow manifest defining all 6 steps (scan_components, plan_compositions, generate_output, review_output, refine_output, step_completion), their routing, artifact declarations, and coder role assignments. This is the primary configuration file the agent-runner-v2 engine reads to execute the workflow. |
| context_extensions.py | context_extensions.py | Python module that registers all artifact keys (COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR, COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE) with their resolved filesystem paths. The runner uses this to resolve {ARTIFACT_KEY} placeholders in prompts and action contexts. |
| README.md | README.md | User guide describing the workflow's purpose (video campaign manuscript composition system), inputs (component library, compositions, data sources), outputs (resolved manuscripts), execution command (ukbe-run-agent run --template-group video_campaign_manuscript), expected behavior, and troubleshooting guidance. |

### Conditional Files

| File Name | Relative Path | Condition | Purpose |
|---|---|---|---|
| actions.py | actions.py | Required (action steps exist) | Python module containing implementations for the two custom action steps: scan_components and plan_compositions. Each action follows the agent-runner-v2 action module pattern with the @action decorator, context/state/step_cfg/project_root parameters, and returns ActionResult. |
| .env.sample | .env.sample | Not needed | No API keys or external service credentials are required. The workflow operates entirely on local file I/O. |
| config.json.sample | config.json.sample | Not needed | No runtime configuration beyond the artifact paths is required. |

### Prompt Files

| File Name | Relative Path | Purpose |
|---|---|---|
| 03_generate_output.txt | prompts/03_generate_output.txt | Prompt template for the generate_output step (Step 3). Instructs the LLM to read the component inventory and resolution plan, expand all component references, apply overrides, resolve placeholders, interleave scenes and transitions, and assemble the complete manuscript output. Specifies the output format (YAML frontmatter + markdown sections) and requires file writing to {OUTPUT_FILE}. |
| 04_review_output.txt | prompts/04_review_output.txt | Prompt template for the review_output step (Step 4). Instructs the LLM to evaluate the generated manuscript against quality requirements: no dangling references, no unresolved raw placeholders, schema conformance, section completeness, cross-section consistency, and timing accuracy. Requires writing the review verdict and findings to {REVIEW_FILE_SUGGESTED}. |
| 05_refine_output.txt | prompts/05_refine_output.txt | Prompt template for the refine_output step (Step 5). Instructs the LLM to fix each issue from the review report individually, producing a corrected manuscript. Requires a fix log and writing the corrected output to {OUTPUT_FILE}. |

### Supplementary Files

| File Name | Relative Path | Purpose |
|---|---|---|
| component_schema.md | schema/component_schema.md | The complete component schema definition for the video_campaign_manuscript domain. Defines all 7 component types (hook, scene, voice_style, visual_direction, audio_mood, text_style, transition), their common properties, type-specific properties, validation rules (GLOBAL-VR-001 through GLOBAL-VR-014 plus type-specific rules), and example components. The scan_components action reads this file at runtime to validate components. Embedded from the builder's Phase 2 output (COMPONENT_SCHEMA_FILE). |
| output_format_spec.md | schema/output_format_spec.md | The complete output format specification for the video_campaign_manuscript domain. Defines the output file structure (YAML frontmatter fields, 7 required sections), resolution rules (component expansion, override application, placeholder resolution, scene-transition interleaving), quality requirements, and downstream extraction contracts. The generate_output prompt template references this file to instruct the LLM on output structure. The review_output prompt template references it for quality checks. Embedded from the builder's Phase 4 output (OUTPUT_FORMAT_FILE). |
| composition_format_spec.md | schema/composition_format_spec.md | The complete composition format specification for the video_campaign_manuscript domain. Defines the composition YAML structure (top-level fields, binding rules, override mechanism, placeholder resolution rules, ordering constraints). The plan_compositions action references this file at runtime to validate composition structure. The review_output prompt template references it for binding rule verification. Embedded from the builder's Phase 3 output (COMPOSITION_FORMAT_FILE). |

### File Count Summary

| Category | Count |
|---|---|
| Core files | 3 (workflow.toml, context_extensions.py, README.md) |
| Conditional files | 1 (actions.py) |
| Prompt files | 3 (03_generate_output.txt, 04_review_output.txt, 05_refine_output.txt) |
| Supplementary files | 3 (component_schema.md, output_format_spec.md, composition_format_spec.md) |
| **Total** | **10** |

### Package File Traceability

Every supplementary file in this inventory traces to a step in the Step Sequence or a requirement in the Artifact Contract:

| Supplementary File | Referenced By Step | Referenced By Artifact |
|---|---|---|
| schema/component_schema.md | scan_components (reads for validation rules), generate_output (reads for property types), review_output (reads for override conformance checks) | COMPONENT_SCHEMA_FILE (workflow input, resolved from this path) |
| schema/output_format_spec.md | generate_output (reads for output structure), review_output (reads for quality requirements) | OUTPUT_FORMAT_FILE (workflow input, resolved from this path) |
| schema/composition_format_spec.md | plan_compositions (reads for binding rules), review_output (reads for binding verification) | COMPOSITION_FORMAT_FILE (workflow input, resolved from this path) |

---

## Self-Validation

### Phase Completeness

| Phase | Covered By Step | Verification |
|---|---|---|
| Scan | scan_components (Step 1) | Action step discovers and validates components |
| Plan | plan_compositions (Step 2) | Action step resolves compositions and inventories placeholders |
| Generate | generate_output (Step 3) | Prompt step assembles manuscripts |
| Review | review_output (Step 4) | Prompt step performs quality checks |
| Refine | refine_output (Step 5) | Prompt step fixes issues (conditional) |

All 5 phases covered. PASS.

### Step Sequence Completeness

| Required Operation | Covered By Step |
|---|---|
| Component discovery | scan_components (Step 1) |
| Schema validation | scan_components (Step 1) |
| Composition parsing | plan_compositions (Step 2) |
| Reference resolution | plan_compositions (Step 2) |
| Override validation | plan_compositions (Step 2) |
| Placeholder inventory | plan_compositions (Step 2) |
| Output assembly | generate_output (Step 3) |
| Quality review | review_output (Step 4) |
| Issue refinement | refine_output (Step 5) |
| Workflow completion | step_completion (Step 6) |

All operations covered. PASS.

### Step Type Classification

| Step | Type | Justification |
|---|---|---|
| scan_components | action | File I/O, YAML parsing, schema validation -- all deterministic |
| plan_compositions | action | YAML parsing, reference lookup, constraint checking -- all deterministic |
| generate_output | prompt | Manuscript assembly requires LLM judgment for content expansion and formatting |
| review_output | prompt | Quality assessment requires LLM judgment for consistency and completeness |
| refine_output | prompt | Issue correction requires LLM judgment for interpreting findings and applying fixes |
| step_completion | action | Terminal status update -- fully deterministic |

Step types are appropriate. Deterministic operations are actions; judgment operations are prompts. PASS.

### Artifact Flow Integrity

Verified in the Traceability Matrix above. No dangling references. Every step reads artifacts produced by prior steps or declared as workflow inputs. PASS.

### Action Reuse Audit

| Action Step | New or Reused | Evidence |
|---|---|---|
| scan_components | new | No existing action performs component library scanning and schema validation |
| plan_compositions | new | No existing action performs composition resolution and placeholder inventory |
| step_completion | reused | Existing core action at agent_runner_v2/actions/step_completion.py |

Checked existing actions: validate_system_docs, validate_codebase_docs, sync_system_docs, sync_codebase_docs, step_completion, scan_repo_codebase, promote_init, promote_artifact, finalize_bootstrap, documentation_validation_core, copy_artifact, archive_inputs. None perform component scanning or composition resolution. PASS.

### Standard Conformance

The workflow follows the Universal Workflow Pattern from COMPOSITION_SYSTEM_STANDARD.md Section 6:
- Scan phase: Present (Step 1). PASS.
- Plan phase: Present (Step 2). PASS.
- Generate phase: Present (Step 3). PASS.
- Review phase: Present (Step 4). PASS.
- Refine phase: Present (Step 5). PASS.
- Mixed workflow type: Action steps for scanning/planning, prompt steps for generation/review. PASS.
- Input artifacts match Section 6.3: COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR. PASS.
- Output artifacts match Section 6.4: COMPONENT_INVENTORY_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED. PASS.

### Test Criteria Alignment (TC-OW-001 through TC-OW-N03)

| Criterion | Status | Evidence |
|---|---|---|
| TC-OW-001 (5 phases defined) | PASS | Workflow Phases section defines all 5 phases |
| TC-OW-002 (phase objectives) | PASS | Each phase has clear objective statement |
| TC-OW-003 (phase boundaries) | PASS | Each phase output is the next phase input |
| TC-OW-004 (logical ordering) | PASS | scan -> plan -> generate -> review -> refine |
| TC-OW-005 (completeness) | PASS | All operations have dedicated steps |
| TC-OW-006 (action + prompt mix) | PASS | 2 action steps + 3 prompt steps + 1 terminal |
| TC-OW-007 (artifact declarations) | PASS | Every step declares inputs and outputs |
| TC-OW-008 (artifact key naming) | PASS | Keys match spec Section 5.3 naming |
| TC-OW-009 (input artifacts) | PASS | COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR declared |
| TC-OW-010 (output artifacts) | PASS | COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED declared |
| TC-OW-011 (action steps identified) | PASS | scan_components and plan_compositions identified as custom actions |
| TC-OW-012 (action specs complete) | PASS | Each action specifies name, inputs, outputs, logic, error handling, reuse |
| TC-OW-013 (reuse opportunities) | PASS | step_completion reused from core |
| TC-OW-014 (prompt steps identified) | PASS | generate_output, review_output, refine_output identified as prompt-driven |
| TC-OW-015 (prompt specs complete) | PASS | Each prompt step specifies name, template, inputs, output, success criteria |
| TC-OW-016 (context injection) | PASS | Each prompt step lists upstream artifacts injected as context |
| TC-OW-017 (routing defined) | PASS | Every step has onsuccess; review_output has on_reject_refine |
| TC-OW-018 (review-refine loop) | PASS | review_output -> refine_output -> review_output loop defined |
| TC-OW-019 (exhaustion condition) | PASS | max_iterations=2, exhausted_failure_code="OUTPUT_REVIEW_EXHAUSTED" |
| TC-OW-020 (terminal step) | PASS | step_completion is the terminal step |
| TC-OW-021 (self-check phases) | PASS | This Self-Validation section verifies all 5 phases |
| TC-OW-022 (self-check artifact flow) | PASS | Artifact Flow Verification subsection confirms no dangling references |
| TC-OW-023 (no orphan steps) | PASS | Routing Diagram shows all steps connected |
| TC-OW-N01 (no unsupported phases) | PASS | All phases trace to COMPOSITION_SYSTEM_STANDARD.md Section 6.1 |
| TC-OW-N02 (scan not skipped) | PASS | scan_components is Step 1, first in sequence |
| TC-OW-N03 (no prompt for deterministic) | PASS | File scanning is action, not prompt |

All 26 criteria satisfied. PASS.

---

**End of Operational Workflow Design**
