# Composition System Standard v2

> **Abstract:** This document defines the universal pattern for LEGO-like
> composition systems — a standardized approach to building complex deliverables
> from reusable, composable components. This pattern is domain-agnostic and can
> be applied to any field where modular assembly produces value: video production
> manuscripts, software applications, content creation, podcast production, and
> more.
>
> This standard serves as the **base schema** — the "pre-trained model" that
> meta-builders fine-tune for specific domains. Each generated domain standard
> is a specialization of this base, keeping relevant universal patterns and
> adding domain-specific extensions.
>
> **Status:** DRAFT
> **Version:** 2.0
> **Effective Date:** 2026-08-09
> **Supersedes:** v1.0 (2026-08-07)

---

## 1. Purpose

Complex deliverables (manuscripts, applications, content packages) are often
created from scratch for each instance, leading to inconsistency, slow production,
and difficulty scaling. A **composition-based approach** solves this by:

- Defining standardized **components** (reusable building blocks)
- Providing a **composition format** (how components snap together)
- Generating **resolved outputs** (complete deliverables with all references expanded)

This standard defines the universal pattern that any domain can adopt. It is
designed to be **fine-tuned** — not copied verbatim — by meta-builders that
specialize it for specific domains.

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
generation_date: "2026-08-09"
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

## 6. Output Delivery Types

Not all composition outputs follow the same delivery pipeline. The output type
determines how the deliverable is produced, reviewed, and stored. The runtime
spec declares which type applies, and the meta-builder designs the workflow
accordingly.

### 6.1 Documented/Versioned Output

Full lifecycle pipeline with review, approval, promotion, publishing, and
history tracking.

**Pipeline:** generate → review → refine → approve → promote → publish → archive

**When to use:**
- Output needs version tracking (history of changes)
- Output needs audit trail (who approved what, when)
- Output needs approval gates (human review before publishing)
- Output uses staging lifecycle (stage → review → refine → backup → history → publish)
- Rollback capability required (restore previous version)

**Examples:** Governance documents, SDLC delivery artifacts, workflow packages,
codebase documentation, composition standards.

**Workflow characteristics:**
- `promote_workflow_package` or equivalent action
- `requires_human_approval_after` at key points
- Archive actions for versioning
- Review/refine loops with exhaustion handling

### 6.2 Direct Output

Produce and deliver. No versioning, no promotion, no history.

**Pipeline:** generate → [optional human approval] → deliver

**When to use:**
- Output is consumed immediately by downstream processes
- Output doesn't need versioning or audit trail
- Output is expensive to produce (API calls, compute) — needs human approval
  *before* execution, not after
- Output lives in a single location (no staging/history)

**Examples:** Videos (agnes_gen_video), images + videos (agnes_media_gen),
real-time data transforms, API responses.

**Workflow characteristics:**
- No promote/publish actions
- Human approval *before* expensive operations (not after)
- Deferred archive pattern (archive after approval if needed)
- Simpler routing — linear pipeline with optional review

### 6.3 Spec Declaration

The runtime spec must declare the output type:

```yaml
## Output Delivery

output_type: documented_versioned  # or "direct"
approval_before_execution: false   # true for direct type with expensive ops
archive_after_approval: true       # standard for documented type
```

The meta-builder reads this declaration and designs the workflow's output
delivery mechanism accordingly.

---

## 7. Fine-Tuning Protocol

This standard is the **base schema** — the "pre-trained model." Meta-builders
fine-tune it for specific domains rather than copying it verbatim. The
fine-tuning process produces a **domain component schema** that is a
specialization of this base.

### 7.1 Fine-Tuning Operations

| Operation | Description | Example |
|---|---|---|
| **Keep** | Retain universal common properties unchanged | component_id, component_type, name, version, tags, description |
| **Select** | Choose relevant type categories from base examples | Video domain keeps `hook`, `scene`; drops `api_endpoint` |
| **Add** | Introduce domain-specific component types and properties | Codebase domain adds `audience_profile`, `content_template` |
| **Drop** | Remove types that don't apply to the target domain | Software domain drops `hook`, `voice_style` |
| **Specialize** | Narrow validation rules or property constraints for the domain | Version format stays semver; duration_range becomes mandatory for video |

### 7.2 Fine-Tuning Process

```
Base Component Schema (this document)
    ├── Universal Component Schema (common properties)
    ├── Composition Format Standard (binding rules)
    └── Output Format (resolved deliverables)
         │
         ▼  fine-tune per domain
    ┌─────────────────────────────────────────┐
    │ Domain Component Schema                  │
    │ ├── Keep: universal common properties    │
    │ ├── Select: relevant base types          │
    │ ├── Add: domain-specific types           │
    │ ├── Drop: irrelevant types               │
    │ └── Specialize: domain constraints       │
    └─────────────────────────────────────────┘
```

### 7.3 Fine-Tuning Constraints

The fine-tuned schema MUST:
- Retain all common properties (component_id, component_type, name, version, description)
- Follow the same file format (markdown with YAML frontmatter)
- Maintain the extensibility model (new types without breaking existing compositions)
- Preserve validation rule structure (required fields, unique IDs, type conformance)

The fine-tuned schema MAY:
- Add domain-specific common properties (beyond the universal set)
- Define entirely new component types not in the base
- Specialize validation rules (stricter, not looser)
- Add domain-specific file format extensions

### 7.4 Fine-Tuning Input

The meta-builder derives the domain schema from:
1. **This base standard** — the universal patterns to specialize
2. **The runtime spec** — the target domain's requirements, natural phases, component inventory
3. **Domain knowledge** — inferred from the spec's domain description

### 7.5 Example: Fine-Tuning for Codebase-to-Meta Domain

```
Base: Universal Component Schema
    ├── Keep: all common properties
    ├── Select: (no base types directly applicable)
    ├── Add: audience_profile, content_template, meta_content_block,
    │        review_criteria, publish_target
    ├── Drop: hook, scene, voice_style, api_endpoint, etc.
    └── Specialize: validation requires audience_id cross-reference
```

---

## 8. Recursive Composition

Composition standards are **recursive** — every level follows the same pattern
but with domain-specific content. A meta-builder's output and the output's
ByProduct are structurally identical: both are workflow packages with schema,
artifacts, actions, steps, and gatekeepers.

### 8.1 The Recursive Chain

```
Workflow Builder v2
    → reads AMB v1 spec (follows WF Builder v2's composition standard)
    → produces AMB v1 package (AMB Standard v1, derived from WF Builder v2's standard)
    → promotes to workflows/ in agent-runner-v2 repo

AMB v1
    → reads codebase_to_meta_v1 spec (follows AMB v1's composition standard)
    → produces codebase_to_meta_v1 package (CTM Standard v1, derived from AMB Standard v1)
    → promotes per runtime spec definition
```

Each generated standard is a **specialization of its parent's standard**. The
parent's composition standard becomes the child's base schema.

### 8.2 Structural Identity

| Aspect | Meta-Builder Output | ByProduct Output |
|---|---|---|
| **What** | The workflow package itself | What the generated workflow produces at runtime |
| **Example** | AMB v1 package (workflow.toml, prompts, actions.py) | codebase_to_meta_v1's audience-specific meta content |
| **Structure** | Schema + artifacts + actions + steps + gatekeepers | Schema + artifacts + actions + steps + gatekeepers |
| **Delivery** | Documented/versioned (promote, approve, history) | Depends on output type declaration |

Both follow the same structural pattern: define domain → define schema → define
artifacts → define actions → define steps → define gatekeepers → deliver.

### 8.3 Standard Specialization

When a meta-builder produces a new workflow, the new workflow's composition
standard is derived from the meta-builder's own standard:

```
Parent Standard (meta-builder's composition standard)
    → fine-tuned for target domain
    → becomes Child Standard (target workflow's composition standard)
    → named per identity contract (Section 9)
```

The child standard inherits the parent's structural patterns (three-layer
architecture, validation rule structure, extensibility model) but with
domain-specific content.

### 8.4 Implications

- Every meta-builder must itself conform to a composition standard
- The base `COMPOSITION_SYSTEM_STANDARD.md` is the root of the specialization chain
- Each level can add domain-specific extensions but must preserve the universal patterns
- A meta-builder cannot produce output that violates its own standard

---

## 9. Identity Contract

Every composition standard and its associated workflow must declare and maintain
a consistent identity. Identity flows from the runtime spec through all
downstream artifacts.

### 9.1 Required Identity Fields

Every runtime spec must declare:

```yaml
## Workflow Identity

workflow_name: "codebase_to_meta_v1"
standard_name: "CODEBASE_TO_META_STANDARD"
standard_version: "1.0.0"
standard_filename: "CODEBASE_TO_META_STANDARD-v1.md"
```

### 9.2 Identity Propagation Chain

```
WORKFLOW_SPEC_FILE (identity fields)
    → analyze_spec (extract identity)
        → component_schema (uses domain name)
            → composition_format (uses domain name)
                → output_format (uses domain name)
                    → runtime_standard (standard_name + version from spec)
                        → operational_workflow (workflow_name from spec)
                            → package (all identity from spec)
```

### 9.3 Identity Rules

1. **Single source of truth:** Identity fields are declared ONCE in the runtime spec
2. **No derivation:** Downstream artifacts use the exact values from the spec — they do not derive, transform, or substitute
3. **No builder leakage:** The meta-builder's name, standard name, or identity must NEVER appear in the output
4. **Filename consistency:** The standard filename matches `standard_name` + version suffix
5. **Class name consistency:** Generated Python classes derive from `workflow_name` (e.g., `CodebaseToMetaV1Extensions`)

### 9.4 Forbidden Content (all meta-builder prompts)

- Do NOT use the builder's name as the workflow name
- Do NOT use the builder's standard name
- Do NOT copy the builder's step structure
- Do NOT hardcode component types — derive from spec via fine-tuning
- Do NOT assume output type — check spec's declaration

---

## 10. Domain Workflow Pattern

All composition-based workflows follow a flexible pattern adapted to their
domain. Unlike the previous version of this standard, the workflow phases are
**not fixed** — they are derived from the domain's natural phases as declared
in the runtime spec.

### 10.1 Universal Pattern (Flexible)

Every composition workflow has these logical concerns, but the number of steps,
their ordering, and their implementation (action vs prompt) depend on the domain:

1. **Foundation** — Test criteria, quality requirements
2. **Domain Analysis** — Understand the spec, identify components, lock identity
3. **Schema Design** — Fine-tune base schema for domain (Section 7)
4. **Composition Design** — Define how components bind together
5. **Output Design** — Define what the workflow produces
6. **Artifact Design** — Define artifact keys and filename patterns
7. **Step Design** — Define the workflow's operational steps
8. **Standard Consolidation** — Produce the domain's composition standard
9. **Workflow Assembly** — Generate the executable workflow package
10. **Delivery** — Based on output type (Section 6)

### 10.2 Pattern Variants

**Documented/Versioned workflows** add review, approve, promote, publish steps:
```
generate → review → refine → validate → approve → promote → archive → step_completion
```

**Direct workflows** skip promotion and focus on production:
```
generate → [human approval] → produce → [deferred archive] → step_completion
```

**Mixed workflows** combine action steps (scanning, publishing) with prompt-driven
steps (generation, review):
```
scan(action) → generate(prompt) → review(prompt) → refine(prompt) → publish(action) → step_completion
```

### 10.3 Workflow Type

The runtime spec declares the workflow type:

| Type | Step Implementation | Examples |
|---|---|---|
| **Action-only** | All steps are Python @action functions | Scanning, validation, publishing |
| **Prompt-only** | All steps are LLM-driven | Document generation, review, refinement |
| **Mixed** | Combination of action and prompt | Scan(action) → Generate(prompt) → Review(prompt) → Publish(action) |

### 10.4 Input Artifacts (Universal)

| Artifact Key | Description | Required? |
|---|---|---|
| `WORKFLOW_SPEC_FILE` | The runtime specification | Yes |
| `COMPONENT_LIBRARY_DIR` | Directory containing component files | Domain-dependent |
| `COMPOSITIONS_DIR` | Directory containing composition definitions | Domain-dependent |
| `DATA_SOURCE_DIR` | Directory containing placeholder resolution data | Domain-dependent |

### 10.5 Output Artifacts (Universal)

| Artifact Key | Description |
|---|---|
| `DOMAIN_COMPONENT_SCHEMA_FILE` | Fine-tuned schema for the domain |
| `COMPOSITION_STANDARD_FILE` | The domain's composition standard |
| `META_COMPOSITION_SPEC_FILE` | Self-contained reference for the domain |
| `WORKFLOW_PACKAGE_DIR_FILE` | The executable workflow package |
| `REVIEW_FILE_SUGGESTED` | Quality review (for documented/versioned type) |

---

## 11. Domain Examples

### 11.1 Video Campaign Manuscripts

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

**Output:** Complete video production manuscript. **Output type:** Direct
(produced for immediate use by video generation workflows).

**Reference:** `video_campaign_manuscript_v1` workflow spec.

### 11.2 Software Applications

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

**Output:** Complete application blueprint. **Output type:** Documented/versioned
(needs approval, versioning, and downstream extraction contracts).

**Status:** Conceptual — not yet implemented.

---

## 12. Downstream Workflow Pattern

Composition outputs feed into downstream workflows that generate specific
deliverables.

### 12.1 Extraction Contracts

Downstream workflows extract their specific concerns from the output:

**Example (Video Manuscript → Voiceover Generation):**
- Extract all `scene_script` fields in order
- Combine with `voice_style` properties for delivery direction
- Generate voiceover audio

**Example (Software Blueprint → API Generation):**
- Extract all `api_endpoint` components
- Combine with `data_model` definitions for schema validation
- Generate API route handlers, request validation, response formatting

### 12.2 Platform-Specific Considerations

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

## 13. Governance

### 13.1 Proposing New Component Types

To add a new component type to a domain:

1. Define the type's specific properties (name, type, required/optional, description)
2. Document the type in the domain's component schema
3. Provide at least one example component
4. Update the domain's workflow spec to recognize the new type
5. Ensure backward compatibility (existing compositions continue to work)

### 13.2 Versioning

**Component versions:** Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to type-specific schema
- MINOR: New optional properties added
- PATCH: Documentation fixes, no schema changes

**Standard version:** This document is versioned separately. Changes to the
universal pattern (common properties, composition format, output format,
fine-tuning protocol, identity contract) require a standard version increment.

### 13.3 Compatibility Rules

- **Backward compatible:** New component types can be added without breaking existing compositions
- **Forward compatible:** Compositions can reference components that don't exist yet (flagged as gaps)
- **Schema evolution:** Type-specific properties can be added (MINOR) but not removed or changed incompatibly (MAJOR)
- **Fine-tuning compatibility:** Domain schemas must remain valid specializations of the base (Section 7.3)

---

## 14. Meta-Builder Pipeline

This standard enables a **factory pattern** for generating meta-workflow builders.
The meta-builder reads this standard, fine-tunes it for a target domain, and
produces a complete workflow package.

### 14.1 TDD as DNA

TDD is NOT a phase — it is the **operating principle** embedded in every phase.
Every phase follows the same standardized pattern:

```
1. generate_test_criteria   — Define what "correct" means for this phase
2. review_test_criteria     — Critic: do these tests test the right thing?
3. generate_artifact        — Produce the phase deliverable
4. validate_artifact        — Deterministic: docs exist, parse, identity correct
5. gatekeep_artifact        — LLM: run test criteria against artifact, pass/fail
   [on fail → refine → back to step 4, max N retries]
```

**Key roles:**
- **Critic** (step 2): Reviews the TEST, not the artifact. Questions whether
  the test criteria actually prove the artifact's correctness.
- **Validate** (step 4): Deterministic checks — docs exist, parse correctly,
  identity matches, structural completeness.
- **Gatekeeper** (step 5): Runs validated test criteria against the artifact.
  Pass/fail with evidence. Ensures tests are fully implemented and pass.

### 14.2 Nine-Phase Pipeline

Each phase produces one design artifact and follows the standardized TDD pattern:

```
Phase 1: Analyze Spec
         Pre-step: validate_input_spec (action) — reject spec if identity
         fields or output_type missing.
         → Domain analysis + meta-test-criteria (cross-phase invariants)

Phase 2: Domain Component Schema
         → Fine-tuned from Base Component Schema (keep/add/drop/specialize)

Phase 3: Composition Format
         → How domain components bind together (binding rules, overrides)

Phase 4: Output Format
         → What the target workflow produces (structure, resolution, quality)

Phase 5: Component Artifacts
         → Artifact keys and filename patterns (validated against global registry)

Phase 6: Domain Steps
         → Step sequence + target workflow's own review/approval design
           (for documented/versioned output type)

Phase 7: Runtime Standard
         → Consolidation of Phases 1-6 into the domain's composition standard

Phase 8: Operational Workflow
         → Concrete workflow step sequence using the runtime standard

Phase 9: Package
         → Complete executable workflow package + self-bootstrap embedding
           + promote
```

Phases 1-8 follow the standardized TDD pattern. Phase 9 uses the standard
terminal pattern (validate + review + refine + promote + step_completion).

**Meta-test-criteria:** Phase 1 generates cross-phase invariants (identity
correctness, no builder leakage, output type consistency) that are injected
into ALL subsequent phases' gatekeep steps.

### 14.3 Three-Tier Quality Gate

Every phase uses a three-tier quality gate:

1. **Critic (LLM)** — Reviews test criteria quality:
   - Do the tests actually test the right thing?
   - Are they meaningful? Do they cover edge cases?
   - Would a passing test actually prove correctness?

2. **Validate (action)** — Deterministic structural checks:
   - Parse validity (TOML, Python, YAML)
   - Structural completeness (required sections present)
   - Key consistency (artifact keys match across files)
   - Identity verification (standard_name matches spec)

3. **Gatekeeper (LLM)** — Runs validated test criteria against artifact:
   - Domain appropriateness (components make sense for the domain)
   - Completeness (all spec requirements addressed)
   - Consistency (cross-file coherence)
   - Pass/fail with specific evidence

### 14.4 Recursive Application

The meta-builder itself is a workflow package that conforms to this standard.
When a meta-builder produces a new workflow, the new workflow may itself be a
meta-builder — creating a recursive chain of specialization:

```
Base Standard → Meta-Builder A Standard (specialized) → Meta-Builder B Standard (further specialized)
```

Each level inherits the structural patterns but with increasingly domain-specific
content. See Section 8 for the full recursive composition model.

---

## 15. Authoring a Composition System Specification

A **Composition System Specification** is the input document for meta-builders.
It describes a domain's composition system using the three-layer architecture
defined in this standard. The meta-builder reads the spec and generates a
complete workflow package that implements the composition system.

### 15.1 Spec Structure

The spec is a single markdown document with these sections:

| Section | Layer | Content |
|---|---|---|
| 1. Domain Overview | — | Domain name, purpose, context |
| 2. Workflow Identity | — | workflow_name, standard_name, standard_version, standard_filename |
| 3. Output Delivery | — | output_type (documented_versioned or direct) |
| 4. Component Schema | Layer 1 | Component types, properties, validation rules, examples |
| 5. Composition Format | Layer 2 | Binding rules, override mechanism, placeholder resolution, example |
| 6. Output Format | Layer 3 | Output sections, resolution rules, quality requirements, skeleton |
| 7. Operational Requirements | — | Workflow phases, artifacts, action steps, domain constraints |

### 15.2 Key Principles

**The spec is authoritative.** The meta-builder reads component types, composition
rules, and output structure directly from the spec's structured sections.
It does not infer these from narrative text. If the spec lists 7 component
types, the builder generates exactly those 7 types.

**Describe WHAT, not HOW.** The spec defines the domain's composition
architecture. The builder designs the operational workflow (step sequence,
routing, prompts) that implements it.

**Include examples.** Each layer should include at least one concrete
example: a sample component file, a sample composition, and a sample
output skeleton. Examples disambiguate the schema definitions.

**Declare identity and output type.** The spec must include workflow identity
fields (Section 9.1) and output delivery type (Section 6.3). These are not
optional — they drive identity propagation and workflow structure.

### 15.3 Template and Examples

- **Template:** `docs/repo/workflow_builder/current/templates/COMPOSITION_SYSTEM_SPEC_TEMPLATE.md`
- **Example (Video Campaign Manuscript):** `docs/repo/workflow_builder/specs/video_campaign_manuscript_v2.md`

### 15.4 Relationship to v1-Style Specs

The v1-style workflow spec (overview, purpose, artifacts, actions, quality)
describes a workflow in terms of its execution structure. The composition
system spec describes a domain in terms of its compositional architecture.

| Aspect | v1-Style Spec | Composition System Spec |
|---|---|---|
| Focus | Workflow execution structure | Domain composition architecture |
| Input to | workflow_builder_v1 | Meta-builders (AMB v2+) |
| Describes | Steps, artifacts, actions, routing | Components, compositions, outputs |
| Builder infers | Step sequence, routing, prompts | Operational workflow, step sequence |
| Best for | Any workflow pattern | Composition-based workflows |

---

## 16. References

- **AMB v2 Design Document:** `docs/repo/workflow_builder/AMB_V2_DESIGN.md`
- **Composition System Spec Template:** `docs/repo/workflow_builder/current/templates/COMPOSITION_SYSTEM_SPEC_TEMPLATE.md`
- **Video Campaign Manuscript spec (v2 format):** `docs/repo/workflow_builder/specs/video_campaign_manuscript_v2.md`
- **Video Campaign Manuscript implementation (v1 format):** `docs/repo/workflow_builder/specs/video_campaign_manuscript_v1.md`
- **Workflow Builder architecture:** `docs/repo/workflow_builder/current/WORKFLOW_CREATION_GUIDE.md`
- **Plugin Workflow System:** `docs/repo/workflow_builder/current/PLUGIN_WORKFLOW_SYSTEM.md`
- **Builder Requirements:** `docs/repo/workflow_builder/current/BUILDER_REQUIREMENTS.md`

---

## Appendix A: Glossary

**Component:** A reusable building block with a standardized schema.

**Composition:** A declarative assembly instruction that references components by ID.

**Output:** A resolved, self-contained deliverable with all references expanded.

**Component Library:** A collection of components for a specific domain.

**Resolution:** The process of expanding component references, applying overrides, and filling placeholders.

**Override:** A per-composition customization that modifies a component's properties.

**Placeholder:** A `{variable}` reference resolved from external data at generation time.

**Fine-Tuning:** The process of specializing the base component schema for a specific domain (keep/add/drop/specialize).

**Domain Component Schema:** A fine-tuned specialization of the base schema for a specific domain.

**Identity Contract:** The set of identity fields (workflow_name, standard_name, standard_version, standard_filename) declared in the runtime spec and propagated through all artifacts.

**Output Type:** The delivery pattern for a workflow's output — documented/versioned (full lifecycle) or direct (produce and deliver).

**Recursive Composition:** The pattern where meta-builder output and ByProduct output are structurally identical, and each generated standard specializes its parent's standard.

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
- [ ] **Declare workflow identity** (workflow_name, standard_name, standard_version, standard_filename)
- [ ] **Declare output type** (documented_versioned or direct)
- [ ] **Fine-tune base schema** — document keep/add/drop/specialize decisions
- [ ] Write a workflow spec following this standard
- [ ] Test with a meta-builder

---

**End of Standard**
