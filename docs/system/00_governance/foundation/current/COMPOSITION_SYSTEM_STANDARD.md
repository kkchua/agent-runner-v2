# Composition System Standard v1

> **Abstract:** This document defines the universal pattern for LEGO-like
> composition systems — a standardized approach to building complex deliverables
> from reusable, composable components. This pattern is domain-agnostic and can
> be applied to any field where modular assembly produces value: video production
> manuscripts, software applications, content creation, podcast production, and
> more.
>
> **Status:** DRAFT
> **Version:** 1.0
> **Effective Date:** 2026-08-07

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

All composition systems follow a three-layer architecture:

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

### Separation of Concerns

- **Components** define WHAT the building blocks are (their properties, constraints, creative DNA)
- **Compositions** define HOW they fit together (which components, in what order, with what overrides)
- **Outputs** are the RESULT (complete, self-contained deliverables ready for downstream consumption)

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

This standard enables a **factory pattern** for generating meta-workflow builders:

**Input:** Domain specification (component types, composition rules, output format)
**Output:** A meta-workflow builder that knows how to work with that domain's components

**Example:**
- Input: "Video manuscript domain with 7 component types"
- Output: `video_manuscript_builder_v1` workflow that scans components, resolves compositions, generates manuscripts

**Factory workflow:**
1. Read domain specification
2. Generate component schema validation logic
3. Generate composition resolution logic
4. Generate output assembly logic
5. Generate review/refine prompts
6. Package as a complete workflow bundle

This creates a **workflow that builds workflows** — a meta-meta-workflow.

**Status:** Conceptual — not yet implemented.

---

## 11. Authoring a Composition System Specification

A **Composition System Specification** is the input document for
workflow_builder_v2. It describes a domain's composition system using
the three-layer architecture defined in this standard. The builder reads
the spec and generates a complete workflow package that implements the
composition system.

### 11.1 Spec Structure

The spec is a single markdown document with these sections:

| Section | Layer | Content |
|---|---|---|
| 1. Domain Overview | — | Domain name, purpose, context |
| 2. Component Schema | Layer 1 | Component types, properties, validation rules, examples |
| 3. Composition Format | Layer 2 | Binding rules, override mechanism, placeholder resolution, example |
| 4. Output Format | Layer 3 | Output sections, resolution rules, quality requirements, skeleton |
| 5. Operational Requirements | — | Workflow phases, artifacts, action steps, domain constraints |

### 11.2 Key Principles

**The spec is authoritative.** The builder reads component types, composition
rules, and output structure directly from the spec's structured sections.
It does not infer these from narrative text. If the spec lists 7 component
types, the builder generates exactly those 7 types.

**Describe WHAT, not HOW.** The spec defines the domain's composition
architecture. The builder designs the operational workflow (step sequence,
routing, prompts) that implements it.

**Include examples.** Each layer should include at least one concrete
example: a sample component file, a sample composition, and a sample
output skeleton. Examples disambiguate the schema definitions.

### 11.3 Template and Examples

- **Template:** `docs/repo/workflow_builder/current/templates/COMPOSITION_SYSTEM_SPEC_TEMPLATE.md`
- **Example (Video Campaign Manuscript):** `docs/repo/workflow_builder/specs/video_campaign_manuscript_v2.md`

### 11.4 Relationship to v1-Style Specs

The v1-style workflow spec (overview, purpose, artifacts, actions, quality)
describes a workflow in terms of its execution structure. The composition
system spec describes a domain in terms of its compositional architecture.

| Aspect | v1-Style Spec | Composition System Spec |
|---|---|---|
| Focus | Workflow execution structure | Domain composition architecture |
| Input to | workflow_builder_v1 | workflow_builder_v2 |
| Describes | Steps, artifacts, actions, routing | Components, compositions, outputs |
| Builder infers | Step sequence, routing, prompts | Operational workflow, step sequence |
| Best for | Any workflow pattern | Composition-based workflows |

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
- [ ] Multiple runtime implementations can satisfy the spec
- [ ] Output type is determined by the requirement document, not hardcoded in the spec
- [ ] Invariants and constraints are output-type-agnostic (apply to all output types)
- [ ] Extension points are clearly documented with example variations

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
- [ ] Write a workflow spec following this standard
- [ ] Test with the workflow builder

---

**End of Standard**
