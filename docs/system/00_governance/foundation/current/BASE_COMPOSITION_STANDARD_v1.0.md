# Composition System Standard v1

> **Abstract:** This document defines the universal pattern for LEGO-like
> composition systems — a standardized approach to building complex deliverables
> from reusable, composable components. This pattern is domain-agnostic and can
> be applied to any field where modular assembly produces value: video production
> manuscripts, software applications, content creation, podcast production, and
> more.
>
> **Status:** DRAFT
> **Version:** 1.1
> **Effective Date:** 2026-08-14

---

## 1. Purpose

Complex deliverables (manuscripts, applications, content packages) are often
created from scratch for each instance, leading to inconsistency, slow production,
and difficulty scaling. A **composition-based approach** solves this by:

- Defining standardized **components** (reusable building blocks)
- Providing a **composition format** (how components snap together)
- Generating **resolved outputs** (complete deliverables with all references expanded)

This standard defines the universal pattern that any domain can adopt.

---

## 2. The Three-Layer Architecture

All composition systems follow a three-layer architecture. This architecture supports two distinct patterns:

### Pattern 1: Component Assembly

Pre-defined components are assembled into a deliverable.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: COMPONENT LIBRARY                                   │
│ Standardized building blocks with unified schema             │
│ Example: hook, scene, voice_style, visual_direction          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: COMPOSITION DEFINITIONS                             │
│ Declarative assembly instructions referencing components     │
│ Example: "Use hook-dramatic-001 + scene-problem-001 + ..."   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: RESOLVED OUTPUTS                                    │
│ Complete deliverables with all references expanded           │
│ Example: Full manuscript with all creative directions        │
└─────────────────────────────────────────────────────────────┘
```

**Use case:** Video campaign manuscripts, software blueprints, content packages — where you have a library of pre-defined components that are assembled in different combinations.

### Pattern 2: Input Transformation

Input content is transformed into output content through a pipeline.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: INPUT PARSING                                       │
│ Parse input into structured intermediate representation      │
│ Example: Document → Sections → Paragraphs → Sentences        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: TRANSFORMATION                                      │
│ Analyze, transform, and compose intermediate results         │
│ Example: Sentences → KeyPoints → RedundancyClusters → Blocks │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: OUTPUT RENDERING                                    │
│ Render final output from transformed components              │
│ Example: Summary, Bullet Points, Key Phrases, Q&A            │
└─────────────────────────────────────────────────────────────┘
```

**Use case:** Text summarization, content conversion, format transformation — where input content is processed through a pipeline to produce different output types.

**Key difference:** Pattern 1 assembles pre-existing components. Pattern 2 transforms input content into new output content. Both follow the same 3-layer architecture, but the nature of each layer differs.

### Separation of Concerns

**Pattern 1 (Assembly):**
- **Components** define WHAT the building blocks are
- **Compositions** define HOW they fit together
- **Outputs** are the RESULT (assembled deliverables)

**Pattern 2 (Transformation):**
- **Input Parsing** defines HOW to decompose input into structured form
- **Transformation** defines HOW to analyze and compose intermediate results
- **Output Rendering** defines HOW to produce final deliverables

Both patterns support **multiple output types** through different runtime implementations (see Section 13).

---

## 3. Universal Component Schema

All components, regardless of domain or type, conform to a unified schema.

### 3.1 Common Properties

Every component has these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique identifier within the component library |
| `component_type` | enum | Yes | Domain-specific type (e.g., `hook`, `scene`, `api_endpoint`) |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (e.g., `1.0.0`) |
| `duration_range` | string | No | Applicable duration/scope (domain-specific) |
| `platforms` | array | No | Target platforms/contexts (domain-specific) |
| `tags` | array | No | Classification tags for search/filter |
| `description` | string | Yes | What this component does and when to use it |

### 3.2 Type-Specific Properties

Each `component_type` defines additional type-specific properties. These are
domain-defined and extend the common schema.

**Example (Video Manuscript Domain):**
```yaml
component_type: hook
hook_style: dramatic_reveal
hook_script: "What if everything you knew was wrong?"
visual_cue: "Product silhouette in darkness"
energy_level: high
```

**Example (Software Domain):**
```yaml
component_type: api_endpoint
http_method: POST
path: /api/users
auth_required: true
request_schema: { ... }
response_schema: { ... }
```

### 3.3 Component File Format

Components are stored as markdown files with YAML frontmatter:

```markdown
---
component_id: "hook-dramatic-reveal-001"
component_type: "hook"
name: "Dramatic Reveal Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: [tiktok, reels, shorts]
tags: [dramatic, suspense, product]
description: "Opens with a mysterious silhouette reveal, building curiosity"

# Type-specific properties
hook_style: visual_reveal
hook_script: "What if everything you knew about {product_name} was wrong?"
visual_cue: "Close-up of product silhouette in darkness, single spotlight"
energy_level: high
---

# Dramatic Reveal Hook

Additional documentation, usage notes, examples...
```

### 3.4 Validation Rules

Components must pass these validation checks:

- **Required fields present:** component_id, component_type, name, version, description
- **Valid component_type:** Must be a recognized type for the domain
- **Unique component_id:** No duplicates within the library
- **Type-specific schema conformance:** All required properties for the declared type must be present
- **Semantic version format:** Must follow `MAJOR.MINOR.PATCH` pattern

Invalid components are flagged but do not block the workflow. They are included
in the inventory with status "invalid" and specific validation errors.

### 3.5 Extensibility Model

New component types can be added without breaking existing compositions:

1. Define the new type's specific properties
2. Document the type in the domain's component schema
3. Existing compositions continue to work (they reference by component_id, not type)
4. New compositions can reference the new type

The common properties (component_id, component_type, name, version, tags, description)
remain stable across all types.

---

## 4. Composition Format Standard

Compositions define how components are assembled into deliverables. They are
declarative assembly instructions.

### 4.1 Composition Structure

Compositions are YAML files with this structure:

```yaml
composition_id: "unique-identifier"
name: "Human-readable composition name"
target_metadata: { ... }  # Domain-specific (duration, platform, etc.)

component_bindings:
  binding_name:
    component_id: "referenced-component-id"
    overrides:
      property_name: "override value with {placeholder}"
  
  another_binding:
    component_id: "another-component-id"
    # No overrides — use component as-is
  
  list_binding:
    - component_id: "first-component"
      overrides: { ... }
    - component_id: "second-component"
      # No overrides
```

### 4.2 Composition Rules

**References, not duplicates:**
Components are referenced by `component_id`, not copied. The workflow resolves
references against the component library at generation time.

**Overrides:**
Allow per-composition customization without modifying the component. Overrides
must conform to the component type's schema. Overrides are merged with the
component's base properties (override wins on conflict).

**Placeholders:**
`{placeholder}` values in overrides are resolved from external data sources
(e.g., Product Master, configuration files, user input). Unresolved placeholders
are flagged in the output as `{UNRESOLVED: field_name}`.

**Optional bindings:**
Not all component types are required in every composition. A composition may
omit certain bindings if they're not needed for that deliverable.

**Ordering:**
Some bindings are ordered lists (e.g., scenes in a manuscript, pages in an app).
Others are singletons (e.g., voice_style, visual_direction). The domain defines
which is which.

### 4.3 Composition Validation

Compositions must pass these checks:

- **All referenced component_ids exist** in the component library
- **Overrides conform to component type schema** (no invalid properties)
- **Required bindings present** (domain-defined)
- **Placeholders are resolvable** from available data sources
- **Ordering constraints satisfied** (e.g., scenes have sequential ordering)

Invalid compositions are flagged but do not block the workflow. Missing components
are noted as gaps in the output.

---

## 5. Output Format Standard

The resolved output is a complete, self-contained deliverable with all component
references expanded, overrides applied, and placeholders filled.

### 5.1 Output Structure

Outputs are markdown files with YAML frontmatter:

```yaml
---
composition_id: "unique-identifier"
composition_name: "Human-readable name"
metadata: { ... }  # Domain-specific (duration, platform, etc.)
component_count: 12
generation_date: "2026-08-07"
lifecycle_status: "draft"
---
```

Followed by structured sections that present the resolved components in a
human-readable, downstream-consumable format.

### 5.2 Resolution Rules

**All references expanded:**
Every `component_id` reference is replaced with the full component content
(common properties + type-specific properties + overrides applied).

**Placeholders resolved:**
Every `{placeholder}` is replaced with the value from the external data source.
Unresolved placeholders are marked as `{UNRESOLVED: field_name}`.

**Self-contained:**
The output contains all information needed to understand and use the deliverable.
No need to reference the component library or composition file.

**Downstream-agnostic:**
The output describes WHAT the deliverable is, not HOW to produce it. Downstream
workflows extract their specific concerns from the output.

### 5.3 Output Quality Requirements

- **No dangling references:** All component_ids resolved
- **No unresolved placeholders:** All placeholders filled or explicitly flagged
- **Schema conformance:** Overrides applied correctly
- **Completeness:** All required sections present (domain-defined)
- **Consistency:** No contradictions between sections

---

## 6. Universal Workflow Pattern

All composition-based workflows follow this pattern:

### 6.1 Workflow Phases

1. **Scan phase:** Discover and validate all components in the library. Build
   component inventory with type classification and validation status.

2. **Plan phase:** Read all compositions, resolve component references against
   the inventory, identify overrides and placeholder bindings. Produce a
   resolution plan.

3. **Generate phase:** For each composition, resolve all components and
   placeholders, apply overrides, assemble the complete output.

4. **Review phase:** Quality review of generated outputs against constraints
   and quality requirements.

5. **Refine phase:** Fix issues found in review (conditional).

### 6.2 Workflow Type

**Mixed:** Action step for component scanning and validation, prompt-driven
steps for output generation and review.

### 6.3 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `COMPONENT_LIBRARY_DIR` | Directory containing component files | Yes |
| `COMPOSITIONS_DIR` | Directory containing composition definitions | Yes |
| `DATA_SOURCE_DIR` | Directory containing placeholder resolution data | Yes (domain-specific) |

### 6.4 Output Artifacts

| Artifact Key | Description |
|---|---|
| `COMPONENT_INVENTORY_FILE` | Catalog of all discovered components |
| `RESOLUTION_PLAN_FILE` | Plan mapping compositions to components |
| `OUTPUT_FILE` | The assembled deliverable |
| `REVIEW_FILE_SUGGESTED` | Quality review |

### 6.5 Input Artifact Contract

All composition-based workflows SHALL follow a consistent input artifact
naming convention so that callers (operator consoles, CLI, or automated
pipelines) can distinguish between file inputs and inline text inputs.

**File input artifacts** — Any input that represents a user-provided
document or file MUST use the `_FILE` suffix in its artifact key. This
suffix is the universal signal that the input is a file to be selected,
not inline text to be typed.

| Artifact Key | Kind |
|---|---|
| `*_FILE` | File input — caller provides a file path |
| `*_DIR` | Directory input — caller provides a directory path |
| Other keys | Inline or pipeline-internal values |

Every workflow MUST declare its input artifacts with correct suffixes.
The composition standard SHALL document which inputs are file inputs
and what formats they accept.

### 6.6 Output Delivery Contract

Every composition-based workflow SHALL declare where final output
artifacts are delivered. The output destination is the contract between
the generating workflow and its consumers.

**Requirements:**

1. **Dedicated output location** — Final deliverables SHALL be written
   to a declared output location, separate from intermediate working
   artifacts.

2. **Output catalog** — The composition standard SHALL document which
   artifact keys represent final deliverables and their file formats.

3. **Delivery step** — The workflow SHALL include a delivery phase
   (or equivalent) that places final artifacts into the declared
   output location after all validation passes.

---

## 7. Domain Examples

### 7.1 Video Campaign Manuscripts

**Component types:**
- `hook` — Opening sequence (hook_style, hook_script, visual_cue, energy_level)
- `scene` — Content segment (scene_purpose, scene_script, visual_direction, duration_target)
- `voice_style` — Voiceover direction (voice_tone, pace, emphasis_pattern, voice_character)
- `visual_direction` — Visual treatment (visual_style, color_palette, lighting_mood, camera_work, aspect_ratio)
- `audio_mood` — Audio direction (mood, tempo, instrumentation, volume_balance)
- `text_style` — On-screen text (text_treatment, font_style, text_animation, text_color_scheme)
- `transition` — Scene transitions (transition_type, transition_duration, transition_energy)

**Composition:** References components by ID, overrides specific properties,
resolves `{product_name}`, `{pain_point}` from Product Master.

**Output:** Complete video production manuscript with Opening, Voice Direction,
Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay,
Production Notes.

**Reference:** `video_campaign_manuscript_v1` workflow spec.

### 7.2 Software Applications

**Component types:**
- `ui_page` — Application screen (page_type, layout, route, auth_required)
- `ui_component` — Reusable UI element (component_kind, props, events, styling)
- `api_endpoint` — REST/GraphQL endpoint (http_method, path, auth_required, request_schema, response_schema)
- `data_model` — Entity definition (entity_name, fields, relations, constraints)
- `service_module` — Business logic unit (service_name, operations, dependencies)
- `integration` — Third-party connection (integration_type, endpoint, auth_method, payload_format)
- `infrastructure` — Cross-cutting concern (concern_type, configuration, scope)

**Composition:** References components by ID, overrides specific properties,
resolves `{app_name}`, `{db_host}`, `{api_key}` from configuration.

**Output:** Complete application blueprint with UI Structure, API Specification,
Data Model, Service Architecture, Integration Points, Infrastructure Config.

**Downstream workflows:**
- `app_blueprint_to_scaffold_v1` — Generate project structure
- `app_blueprint_to_api_v1` — Generate backend API code
- `app_blueprint_to_frontend_v1` — Generate UI code
- `app_blueprint_to_tests_v1` — Generate test suites
- `app_blueprint_to_docs_v1` — Generate documentation

**Status:** Conceptual — not yet implemented.

### 7.3 Content Creation (Future)

**Component types:**
- `article_section` — Content section (section_type, heading, content, word_count_target)
- `tone` — Writing style (tone_type, formality, voice, audience)
- `visual_style` — Image/visual direction (visual_style, color_palette, mood)
- `cta` — Call-to-action (cta_type, message, link, placement)

**Output:** Complete content package (article, social posts, visuals).

### 7.4 Podcast Production (Future)

**Component types:**
- `segment` — Podcast segment (segment_type, script, duration_target, guest_prompt)
- `music_bed` — Background music (mood, tempo, instrumentation, volume)
- `ad_slot` — Advertisement placement (ad_type, duration, placement, script)
- `intro_outro` — Show opening/closing (script, music_cue, duration)

**Output:** Complete podcast episode script with timing, music cues, ad placements.

---

## 8. Downstream Workflow Pattern

Composition outputs feed into downstream workflows that generate specific
deliverables.

### 8.1 Extraction Contracts

Downstream workflows extract their specific concerns from the output:

**Example (Video Manuscript → Voiceover Generation):**
- Extract all `scene_script` fields in order
- Combine with `voice_style` properties for delivery direction
- Generate voiceover audio

**Example (Software Blueprint → API Generation):**
- Extract all `api_endpoint` components
- Combine with `data_model` definitions for schema validation
- Generate API route handlers, request validation, response formatting

### 8.2 Platform-Specific Considerations

Outputs may include platform-specific notes or variations:

**Example (Video Manuscript):**
- TikTok: Add trending sound reference
- Reels: Ensure first frame is visually striking for grid preview
- Shorts: Vertical crop safe — no critical elements in top/bottom 10%

**Example (Software Blueprint):**
- Web: Responsive design considerations
- Mobile: Touch interaction patterns
- Desktop: Keyboard shortcuts, menu bars

---

## 9. Governance

### 9.1 Proposing New Component Types

To add a new component type to a domain:

1. Define the type's specific properties (name, type, required/optional, description)
2. Document the type in the domain's component schema
3. Provide at least one example component
4. Update the domain's workflow spec to recognize the new type
5. Ensure backward compatibility (existing compositions continue to work)

### 9.2 Versioning

**Component versions:** Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to type-specific schema
- MINOR: New optional properties added
- PATCH: Documentation fixes, no schema changes

**Standard version:** This document is versioned separately. Changes to the
universal pattern (common properties, composition format, output format) require
a standard version increment.

### 9.3 Compatibility Rules

- **Backward compatible:** New component types can be added without breaking existing compositions
- **Forward compatible:** Compositions can reference components that don't exist yet (flagged as gaps)
- **Schema evolution:** Type-specific properties can be added (MINOR) but not removed or changed incompatibly (MAJOR)

---

## 10. Meta-Workflow Builder Factory

This standard enables a **factory pattern** for generating artifact generators.
The **Artifact Generator Builder (AGB)** workflow reads a requirement document
and produces a complete artifact generator with all required deliverables.

**Input:** Requirement document (with codename, input artifacts, output artifacts, transformation requirements, constraints)
**Output:** Three required deliverables (see Section 10.1)

**Implementation:** `artifact_generator_builder` (AGB) workflow

### 10.1 Required Deliverables

Every AGB run MUST produce exactly two deliverables:

| # | Deliverable | Filename Pattern | Description |
|---|-------------|------------------|-------------|
| 1 | Composition Standard | `standards/COMPOSITION_STANDARD.md` | The generator-specific composition standard -- step contracts (purpose, input/output, constraints), transformation rules, invariants, extension interfaces, input/output contracts. Derived from this base standard (Section 1-9) tailored to the generator's domain. |
| 2 | Workflow Package | `workflow.toml`, `context_extensions.py`, `actions.py`, `prompts/`, `README.md`, `impls/` | The executable workflow package. The `workflow.toml` IS the default implementation -- every step has its prompt or action assigned. At least one alternative implementation MUST be provided via `impls/{name}/impl.yaml` to validate the override pattern (see Section 13.8). |

All deliverables share the same **codename** assigned in the requirement
document frontmatter. The codename is NOT generated by the LLM -- it is
assigned by the human author of the requirement document.

### 10.2 Required Generator File Structure

After promotion, every AGB-generated generator MUST follow this file structure:

```
workflows/{codename}/
    standards/
        COMPOSITION_STANDARD.md       ← step contracts & invariants
    impls/
        {impl_name}/                  ← one folder per alternative impl
            impl.yaml                 ← step overrides (partial mapping)
            prompts/                  ← impl-specific prompts (optional)
            actions.py                ← impl-specific actions (optional)
    workflow.toml                     ← step sequence + DEFAULT implementation
    context_extensions.py
    actions.py                        ← shared actions (all impls can use)
    prompts/                          ← shared prompts (all impls can use)
        *.txt
    README.md
    Specs/
        *.md                          ← requirement docs for this generator
```

This structure is MANDATORY. All AGB-generated generators must have:
- `standards/` -- contains the generator-specific composition standard (step contracts)
- `workflow.toml` -- the step sequence AND default implementation (every step has prompt= or action= assigned). MUST include `[[workflow.implementation]]` declarations for all alternative implementations.
- `impls/` -- contains at least one alternative runtime implementation (REQUIRED, not optional)
- `impls/{name}/impl.yaml` -- override file that maps only the steps that differ from the default (see Section 13.8)
- Root files -- shared actions, prompts, and the executable workflow package

### 10.3 AGB Run Behavior

During an AGB run, ALL artifacts (intermediate and final) are written to the
AGB's own run directory:

```
docs/repo/artifact_generator_builder/runs/{job_id}/
    REQUIREMENT_ANALYSIS-01.md
    COMPOSITION_SPEC-01.md        (intermediate design artifact)
    RUNTIME_IMPL-01.md            (intermediate design artifact)
    ARTIFACT_CONTRACT-01.md
    STEP_SEQUENCE-01.md
    output/
        standards/
            COMPOSITION_STANDARD.md
        workflow.toml
        context_extensions.py
        actions.py
        prompts/
        README.md
```

The promote action (Phase 7) then packages and publishes the deliverables
from `output/` to `workflows/{codename}/` following the structure in Section 10.2.

### 10.4 Factory Workflow Phases

| Phase | Description | Key Output |
|-------|-------------|------------|
| 1. Analyze Requirement | Understand input/output specifications, read codename from requirement doc | REQUIREMENT_ANALYSIS_FILE |
| 2. Design Composition Spec | Define step contracts, transformation rules, meta schema, invariants | COMPOSITION_SPEC_FILE |
| 3. Design Runtime Implementation | Design the default executor that follows the spec | RUNTIME_IMPL_FILE |
| 4. Define Artifacts | Specify all artifact keys and paths | ARTIFACT_CONTRACT_FILE |
| 5. Design Steps | Define workflow steps and routing | STEP_SEQUENCE_FILE |
| 6. Generate Package | Produce workflow files (workflow.toml as default impl) + composition standard | WORKFLOW_PACKAGE + COMPOSITION_STANDARD_FILE |
| 7. Promote Package | Package deliverables to workflows/{codename}/ | PROMOTION_REPORT_FILE |

### 10.5 Example

**Input (Requirement Doc):**
```yaml
---
codename: "text_summarizer"
generator_name: "Text Summarizer"
version: "1.0.0"
---
input: INPUT_TEXT_FILE (.txt or .md)
output: SUMMARY_FILE, KEY_POINTS_FILE
constraints: max 20% compression, same language, no new information
```

**Output (after promote):**
```
workflows/text_summarizer/
    standards/COMPOSITION_STANDARD.md
    workflow.toml              ← default implementation
    context_extensions.py
    actions.py
    prompts/
    README.md
```

### 10.6 Self-Bootstrap

AGB can build itself. The self-bootstrap requirement specifies:

- **Input:** Requirement documents
- **Output:** Artifact generators (deliverables per Section 10.1)

This creates a recursive chain where AGB can produce improved versions of itself.

**Status:** Implemented -- `workflows/artifact_generator_builder/`

---

## 11. Authoring a Requirement Document

A **Requirement Document** is the input to the Artifact Generator Builder (AGB). It describes what artifact generator to build using the composition system pattern.

### 11.1 Document Structure

The requirement document is a markdown file with YAML frontmatter:

```yaml
---
codename: "text_summarizer"
generator_name: "Text Summarizer"
version: "1.0.0"
---
```

| Frontmatter Field | Required | Description |
|---|---|---|
| `codename` | Yes | Unique identifier for the generated workflow. Used as directory name, file prefixes, and identity throughout all deliverables. Assigned by the human author -- NOT generated by the LLM. |
| `generator_name` | Yes | Human-readable display name for the generator. |
| `version` | Yes | Semantic version of the generator. |

Followed by these sections:

| Section | Purpose | Example |
|---------|---------|---------|
| **Purpose** | What the generator does | "Transforms long text into concise summary" |
| **Input Artifacts** | What content the generator accepts | INPUT_TEXT_FILE (.txt or .md) |
| **Output Artifacts** | What content the generator produces (at least 2) | SUMMARY_FILE, KEY_POINTS_FILE |
| **Transformation Requirements** | How to convert input to output | Extract key points, remove redundancy, preserve meaning |
| **Constraints** | Hard requirements | Max 20% compression, same language, no new information |
| **Extension Points** (optional) | Future output types or variations | Bullet-point summary, key phrases extraction |

### 11.2 Key Principles

**Be specific about input and output.** The requirement doc must clearly define:
- Input artifact keys and formats
- Output artifact keys and formats
- What transformation happens between them

**Define constraints, not implementation.** The requirement doc specifies WHAT must be achieved (e.g., "max 20% compression"), not HOW to achieve it. The composition spec and runtime implementation (generated by AGB) define the HOW.

**Support multiple output types.** If the generator should support different output types (summary, bullet points, key phrases), list them as extension points. The composition spec will be output-type-agnostic (see Section 13), and different runtime implementations will produce different outputs.

### 11.3 Example

See `workflows/artifact_generator_builder/Specs/simple_text_summarizer.md` for a complete example.

### 11.4 Relationship to Composition Spec and Runtime Implementation

```
Requirement Document (human-written)
    ↓ AGB Phase 1-2
Composition Spec (generated, output-type-agnostic contract)
    ↓ AGB Phase 3
Runtime Implementation (generated, concrete executor)
    ↓ AGB Phase 4-6
Workflow Package (generated, executable workflow)
```

The requirement document is the **source of truth** for what the generator should do. The composition spec and runtime implementation are **derived artifacts** that satisfy the requirement.

---

## 13. Composition Spec vs Runtime Implementation

A **Composition Spec** and a **Runtime Implementation** serve distinct but complementary roles in the composition system architecture.

### 13.1 Separation of Concerns

| Aspect | Composition Spec | Runtime Implementation |
|--------|-----------------|----------------------|
| **Purpose** | Defines WHAT the transformation does | Defines HOW the transformation executes |
| **Nature** | Declarative contract | Concrete executor |
| **Contains** | Meta schema, invariants, constraints, interfaces | Algorithms, data structures, code logic |
| **Changes when** | Requirements change | Performance/implementation details change |
| **Stability** | Stable across implementations | May have multiple implementations |

### 13.2 Composition Spec (The Contract)

The Composition Spec defines:

1. **Meta Schema** — The intermediate representation (Layer 1, Layer 2, Layer 3 components)
2. **Input Mapping** — How input artifacts map to Layer 1 components
3. **Transformation Rules** — The stages that transform Layer 1 → Layer 2 → Layer 3
4. **Invariants** — Conditions that must hold at each stage
5. **Constraints** — Hard requirements (e.g., compression ratio ≤ 20%)
6. **Extension Interfaces** — Protocol definitions for pluggable components
7. **Output Contract** — What the output must satisfy (not how it's formatted)

**The spec is output-type-agnostic.** It defines the transformation contract, not the specific output format. The spec should use generic output interfaces that different runtime implementations can satisfy.

**Example (Generic Output Contract):**
```
OutputDocument (interface)
  - output_type: enum (summary, bullet_points, key_phrases, etc.)
  - content_structure: varies by output_type
  - validation_rules: varies by output_type
  - metadata: dict
```

### 13.3 Runtime Implementation (The Executor)

The Runtime Implementation defines:

1. **Pipeline Architecture** — How stages are organized and executed
2. **Algorithms** — Concrete implementations of each transformation stage
3. **Data Structures** — How components are represented in memory
4. **Extension Implementations** — Concrete classes that satisfy the spec's Protocol interfaces
5. **Error Handling** — Recovery mechanisms and failure modes
6. **Configuration** — Runtime parameters and their defaults
7. **Output Rendering** — How Layer 3 components are serialized to disk

**Multiple runtime implementations can satisfy the same composition spec.** Each implementation may produce different output types or use different algorithms, as long as all invariants and constraints are satisfied.

**Example (Multiple Implementations):**
```
SummaryRuntime       → produces SummaryDocument       → SUMMARY_FILE
BulletPointRuntime   → produces BulletPointDocument   → BULLET_POINT_FILE
KeyPhraseRuntime     → produces KeyPhraseList         → KEY_PHRASE_FILE
```

All three satisfy the same composition spec (same input parsing, same Layer 1/Layer 2 transformation), but produce different outputs via different Layer 3 components and different output rendering.

### 13.4 Output-Type-Agnostic Design

The composition spec should **not hardcode a specific output type**. Instead, it should define a generic output contract that supports multiple output types through different runtime implementations.

**Anti-pattern (Output-Type-Specific):**
```
Layer 3: SummaryDocument (hardcoded)
Output: SUMMARY_FILE (hardcoded)
```

This design only supports summary output. To support bullet points or key phrases, you would need a completely different composition spec.

**Correct pattern (Output-Type-Agnostic):**
```
Layer 3: OutputDocument (interface)
  - output_type: enum (summary, bullet_points, key_phrases, etc.)
  - content_blocks: array
  - validation_rules: varies by output_type

Runtime Implementation chooses:
  - SummaryRuntime → SummaryDocument → SUMMARY_FILE
  - BulletPointRuntime → BulletPointDocument → BULLET_POINT_FILE
```

This design supports multiple output types from the same composition spec. The requirement document specifies which output type is desired, and the appropriate runtime implementation is selected.

### 13.5 Extension Points

The composition spec defines **extension points** where runtime implementations can vary:

| Extension Point | Purpose | Example Variations |
|----------------|---------|-------------------|
| InputParser | Parse different input formats | .txt, .md, .pdf, .docx |
| TransformationAlgorithm | Different algorithms for the same stage | TF-IDF vs TextRank for importance scoring |
| OutputRenderer | Render different output formats | Text, Markdown, JSON, YAML, HTML |
| ValidationStrategy | Different validation approaches | Rule-based vs ML-based validation |

Each extension point is defined as a Protocol interface in the composition spec. Runtime implementations provide concrete classes that satisfy these interfaces.

### 13.6 Relationship to Requirement Document

The **requirement document** specifies:
- Input artifacts (what content to transform)
- Output type (summary, bullet points, key phrases, etc.)
- Transformation requirements (what the transformation should achieve)
- Constraints (hard requirements)

The **composition spec** is derived from the requirement document and defines:
- Meta schema (intermediate representation)
- Transformation rules (stages and invariants)
- Extension interfaces (pluggable components)
- Output contract (generic interface, not specific format)

The **runtime implementation** is designed to satisfy the composition spec and produces:
- Concrete output (specific format based on output type)
- Output file (SUMMARY_FILE, BULLET_POINT_FILE, etc.)

### 13.7 Design Checklist

When authoring a composition spec, ensure:

- [ ] Layer 3 defines a generic output interface, not a specific output type
- [ ] Extension interfaces are defined as Protocols, not concrete classes
- [ ] Multiple runtime implementations can satisfy the spec via overrides
- [ ] Output type is determined by the requirement document, not hardcoded in the spec
- [ ] Invariants and constraints are output-type-agnostic (apply to all output types)
- [ ] Extension points are clearly documented with example variations
- [ ] Each step has a step contract (purpose, input/output, constraints)
- [ ] Input artifacts use `_FILE` suffix for file inputs (Section 6.5)
- [ ] Output delivery location is declared (Section 6.6)
- [ ] `workflow.toml` assigns `prompt =` or `action =` for every step (default implementation is complete)
- [ ] Alternative implementations use `impl.yaml` with partial overrides only (Section 13.8)

### 13.8 Runtime Implementation Model

The runtime implementation model uses an **override pattern** — like CSS
cascading or config inheritance. The `workflow.toml` IS the default
implementation: every step has its `prompt =` or `action =` assigned.
Alternative implementations provide an `impl.yaml` that overrides ONLY
the steps that differ. Steps not mentioned in `impl.yaml` inherit their
behavior from `workflow.toml` unchanged.

#### Core Principle

```
workflow.toml       = step sequence + DEFAULT implementation (all steps assigned)
impls/{name}/impl.yaml = OVERRIDES ONLY (partial — only steps that differ)

Runtime resolution: workflow.toml defaults + impl overrides = effective config
```

This means:
- The default implementation requires NO separate mapping file — `workflow.toml` already contains all assignments
- Alternative implementations only specify what CHANGES, not the full mapping
- Adding a new implementation is proportional to what differs, not the workflow size

#### workflow.toml as Default Implementation

The `workflow.toml` defines the step sequence AND the default implementation.
Every step MUST have either `prompt = "path/to/prompt.txt"` (for prompt-driven
steps) or `action = "action_name"` (for action-driven steps). There are no
"abstract" or unassigned steps in `workflow.toml` — it is always a complete,
executable definition.

```toml
[[step]]
name = "analyze_input"
type = "prompt"
prompt = "prompts/01_analyze_input.txt"    # ← default implementation
role_policy = "analyst"
onsuccess = "transform_content"

[[step]]
name = "transform_content"
type = "prompt"
prompt = "prompts/02_transform.txt"        # ← default implementation
role_policy = "transformer"
onsuccess = "render_output"

[[step]]
name = "render_output"
type = "action"
action = "render_media"                    # ← default implementation
```

The `workflow.toml` is both the contract with the backend/daemon AND the
default implementation. No separate "default impl mapping" file is needed.

#### Implementation Override Format (impl.yaml)

Alternative implementations use `impls/{name}/impl.yaml` to override specific
steps. The file contains ONLY the steps that differ from the default:

```yaml
# impls/anime/impl.yaml
name: anime
description: "Anime-style output variant"

overrides:
  analyze_input:
    prompt: "impls/anime/prompts/01_analyze_input.txt"

  render_output:
    action: "render_anime"
```

**Rules:**

1. Each key under `overrides:` MUST match a step name in `workflow.toml`
2. Each override entry MUST specify `prompt` (for prompt-driven steps) or `action` (for action-driven steps)
3. Steps NOT listed in `overrides:` use the `workflow.toml` default unchanged
4. Override `prompt` paths are relative to the workflow root
5. Override `action` names reference functions in either the impl's own `actions.py` or the shared `actions.py`

**Minimal override** — change just one step:

```yaml
# impls/watercolor/impl.yaml
name: watercolor

overrides:
  render_output:
    action: "render_watercolor"
```

#### File Structure

```
workflows/{codename}/
    workflow.toml                 ← step sequence + DEFAULT implementation
    context_extensions.py
    actions.py                    ← shared action functions
    prompts/                      ← shared prompt templates
        *.txt
    standards/
        COMPOSITION_STANDARD.md   ← step contracts & invariants
    impls/
        anime/
            impl.yaml             ← overrides for anime variant
            prompts/              ← anime-specific prompt templates (optional)
                01_analyze_input.txt
            actions.py            ← anime-specific actions (optional)
        watercolor/
            impl.yaml             ← overrides for watercolor variant
            actions.py            ← watercolor-specific actions (optional)
```

**Shared vs impl-specific components:**

| Component | Location | Used by |
|-----------|----------|---------|
| Shared prompts | `prompts/*.txt` | All implementations (default fallback) |
| Shared actions | `actions.py` (root) | All implementations (default fallback) |
| Impl-specific prompts | `impls/{name}/prompts/*.txt` | Only that implementation |
| Impl-specific actions | `impls/{name}/actions.py` | Only that implementation |

Implementations SHOULD reuse shared components and only provide
impl-specific components when the behavior MUST differ.

#### Runtime Resolution Algorithm

At runtime, the step runner SHALL resolve each step's effective configuration
using this algorithm:

```
1. Load workflow.toml → get step sequence and default assignments
2. If selected_impl is not "default":
     Load impls/{selected_impl}/impl.yaml → get override mappings
3. For each step:
     effective_config = workflow.toml step config
     If step has override in impl.yaml:
       Merge override into effective_config (override wins)
     Execute step with effective_config
```

**Python pseudocode:**

```python
def resolve_step(step_name, workflow_toml, selected_impl):
    """Resolve effective config for a step."""
    # Start with workflow.toml default
    config = workflow_toml.get_step(step_name)

    # Apply impl overrides if not using default
    if selected_impl and selected_impl != "default":
        impl_overrides = load_yaml(f"impls/{selected_impl}/impl.yaml")
        if step_name in impl_overrides.get("overrides", {}):
            config.update(impl_overrides["overrides"][step_name])

    return config
```

**Resolution example** — workflow with 3 steps, anime impl overrides 1:

| Step | workflow.toml (default) | anime impl.yaml | Effective config |
|------|------------------------|-----------------|------------------|
| analyze_input | prompt = "prompts/01_analyze.txt" | prompt = "impls/anime/prompts/01_analyze.txt" | **impls/anime/prompts/01_analyze.txt** |
| transform_content | prompt = "prompts/02_transform.txt" | *(not listed)* | **prompts/02_transform.txt** |
| render_output | action = "render_media" | *(not listed)* | **render_media** |

Only `analyze_input` uses the anime-specific prompt. The other two steps
use the shared defaults unchanged.

#### Implementation Selection

Implementations are selected at workflow invocation time. The workflow.toml
MUST declare all available implementations so that operator consoles and
CLI tools can discover them.

**Declaration in workflow.toml:**

When a workflow has alternative implementations, it MUST declare them in
a `[[workflow.implementation]]` array of tables. The `default`
implementation (workflow.toml itself) is always implicitly available and
does NOT need to be listed.

```toml
[workflow]
name = "image_generator"
# ... other workflow fields ...

[[workflow.implementation]]
name = "anime"
description = "Anime-style output variant"
label = "Anime Style"

[[workflow.implementation]]
name = "watercolor"
description = "Watercolor painting style with soft edges"
label = "Watercolor"
```

**Field specification:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Matches the `impls/{name}/` directory name. Must be unique. |
| `description` | Yes | Human-readable description of what this variant does. |
| `label` | No | Short display label for UI dropdowns. Defaults to `name`. |

**Discovery flow:**

```
workflow.toml declares [[workflow.implementation]]
        |
        v
sync_workflows.py sends full workflow definition to backend
        |
        v
Backend stores and returns workflow metadata (including implementations)
        |
        v
Operator console extracts implementations list → shows dropdown
        |
        v
User selects implementation → sent as impl_name
        |
        v
Runtime resolves: load_workflow_package(pkg_dir, impl_name=selected)
```

**CLI selection:**
```bash
ukbe-run-agent run --template-group {codename} --impl anime
```

**Operator console selection:**

The submit page reads the workflow's `implementations` list from backend
metadata and renders a dropdown. The `default` option (no overrides) is
always first. User selection is sent as `impl_name` in the run request.

When no implementation is specified, the `default` implementation is used
(which is `workflow.toml` with no overrides).

#### Design Constraints

1. **workflow.toml is always complete** — every step MUST have `prompt =` or `action =`. There are no abstract or unassigned steps.
2. **impl.yaml is always partial** — it only lists steps that differ. An empty `overrides: {}` is valid (identical to default).
3. **No impl.yaml for default** — the `default` implementation is `workflow.toml` itself. The `impls/default/` folder is NOT required.
4. **Step sequence is fixed** — implementations cannot add, remove, or reorder steps. They can only change WHAT fulfills each step.
5. **Shared components are the fallback** — if an impl doesn't override a step, the shared prompt/action from workflow.toml is used.
6. **At least one alternative implementation is required** — every AGB-generated workflow MUST include at least one `impls/{name}/` directory with a valid `impl.yaml` and a matching `[[workflow.implementation]]` declaration in workflow.toml. This validates the override pattern end-to-end. The composition spec (Phase 2) MUST identify at least one output variant.

#### Validation Rules

1. `workflow.toml` MUST have `prompt` or `action` for every step
2. `impl.yaml` override keys MUST reference existing step names in `workflow.toml`
3. Each override entry MUST specify at least one of `prompt` or `action`
4. Override `prompt` paths MUST reference existing files
5. Override `action` names MUST reference existing functions (in shared or impl-specific `actions.py`)
6. Implementation names MUST be unique within a workflow
7. Each `[[workflow.implementation]]` name MUST have a matching `impls/{name}/` directory with a valid `impl.yaml`
8. `default` MUST NOT appear in `[[workflow.implementation]]` — it is always implicit

---

## 14. References

- **Artifact Generator Builder workflow:** `workflows/artifact_generator_builder/`
- **AGB sample requirement doc:** `workflows/artifact_generator_builder/Specs/sample_requirement.md`
- **AGB simple test case:** `workflows/artifact_generator_builder/Specs/simple_text_summarizer.md`
- **Workflow package system:** `agent_runner_v2/workflow_packages/`
- **Workflow extensions base:** `agent_runner_v2/workflow_packages/extensions_base.py`

---

## Appendix A: Glossary

**Component:** A reusable building block with a standardized schema.

**Composition:** A declarative assembly instruction that references components by ID.

**Output:** A resolved, self-contained deliverable with all references expanded.

**Component Library:** A collection of components for a specific domain.

**Resolution:** The process of expanding component references, applying overrides, and filling placeholders.

**Override:** A per-composition customization that modifies a component's properties.

**Placeholder:** A `{variable}` reference resolved from external data at generation time.

---

## Appendix B: Checklist for Adopting This Standard

When creating a new domain-specific composition system:

- [ ] Define domain-specific component types and their properties
- [ ] Document the component schema (common + type-specific)
- [ ] Define the composition format (which bindings, ordering rules)
- [ ] Define the output format (required sections, metadata)
- [ ] Identify external data sources for placeholder resolution
- [ ] Define downstream extraction contracts
- [ ] Create at least one example component and composition
- [ ] Define step contracts for each workflow step (purpose, input/output, constraints)
- [ ] Apply input artifact naming convention (Section 6.5 — `_FILE` suffix)
- [ ] Declare output delivery location (Section 6.6)
- [ ] Ensure `workflow.toml` is a complete default implementation (every step has prompt= or action=)
- [ ] Create alternative impl.yaml files for any output variants (partial overrides only, Section 13.8)
- [ ] Write a workflow spec following this standard
- [ ] Test with the workflow builder

---

**End of Standard**
