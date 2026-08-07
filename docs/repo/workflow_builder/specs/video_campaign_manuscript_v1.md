# Workflow Specification: Video Campaign Manuscript v1

## Overview

**Workflow name:** `video_campaign_manuscript_v1`
**Label:** Video Campaign Manuscript Generator v1
**Job prefix:** `VCAMP`
**Description:** Defines a LEGO-like manuscript asset component system for
social media video campaigns. Standardized components (hooks, scenes, voice
styles, visual directions, audio moods, text styles, transitions) are composed
into complete video production manuscripts via a declarative composition format.

## Purpose

Content creators need to produce social media video campaigns at scale.
Creating manuscripts from scratch for every campaign is slow and inconsistent.

This workflow introduces a **component-based manuscript system**:
- A library of reusable **manuscript asset components**, each with a
  standardized schema
- A **composition format** that snaps components together into complete
  manuscripts
- Components are mixed and matched -- a "dramatic hook" can appear in a
  product promo, a sales hook, or a brand story

**Trigger:** A user prepares a target repository with:
1. A `components/` directory containing manuscript asset component files
2. A `manuscripts/` directory containing manuscript composition definitions
3. A `product_master/` directory containing the Product Master knowledge base

**Outcome:** Generated manuscripts that resolve all component references,
apply overrides, and fill placeholders from the Product Master.

## Workflow Type

**Mixed** -- Action step for component scanning and validation, prompt-driven
steps for manuscript generation and review.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `COMPONENT_LIBRARY_DIR` | Directory containing manuscript asset component files | Yes |
| `MANUSCRIPT_COMPOSITIONS_DIR` | Directory containing manuscript composition definitions | Yes |
| `PRODUCT_MASTER_DIR` | Directory containing Product Master documents | Yes |

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `COMPONENT_INVENTORY_FILE` | `COMP_INV-{date}-{seq}_{slug}.md` | Catalog of all discovered components with validation status |
| `MANUSCRIPT_PLAN_FILE` | `MSC_PLAN-{date}-{seq}_{slug}.md` | Resolution plan for compositions |
| `MANUSCRIPT_FILE` | `MANUSCRIPT-{date}-{seq}_{slug}.md` | The assembled manuscript |
| `REVIEW_FILE_SUGGESTED` | `VCAMP-REV-{date}-{seq}_{slug}.md` | Quality review |

---

## Component Schema

This is the core of the system. Every manuscript asset component conforms to
a unified schema regardless of type. Components are markdown files with YAML
frontmatter.

### Common Properties

All component types share these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique identifier (e.g., `hook-dramatic-reveal-001`) |
| `component_type` | enum | Yes | One of the 7 supported types |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (e.g., `1.0.0`) |
| `duration_range` | string | No | Applicable duration range (e.g., `5-15s`, `30-60s`) |
| `platforms` | array | No | Target platforms (e.g., `[tiktok, reels, shorts]`) |
| `tags` | array | No | Classification tags (e.g., `[dramatic, suspense, product]`) |
| `description` | string | Yes | What this component does and when to use it |

### Component Types

The system defines 7 component types. Each type adds type-specific properties
on top of the common schema.

#### 1. hook

Opening sequence that captures attention in the first seconds.

| Property | Type | Description |
|---|---|---|
| `hook_style` | enum | `question`, `shocking_stat`, `visual_reveal`, `challenge`, `story_teaser` |
| `hook_script` | string | The opening words/text |
| `visual_cue` | string | Description of the visual opening |
| `energy_level` | enum | `low`, `medium`, `high`, `explosive` |

#### 2. scene

A content segment within the manuscript.

| Property | Type | Description |
|---|---|---|
| `scene_purpose` | enum | `problem_statement`, `solution_intro`, `feature_showcase`, `social_proof`, `emotional_appeal`, `call_to_action`, `brand_story` |
| `scene_script` | string | The spoken/written content |
| `visual_direction` | string | What the viewer sees during this scene |
| `duration_target` | integer | Target duration in seconds |

#### 3. voice_style

Voiceover delivery direction.

| Property | Type | Description |
|---|---|---|
| `voice_tone` | enum | `authoritative`, `friendly`, `dramatic`, `conversational`, `inspirational`, `urgent` |
| `pace` | enum | `slow`, `moderate`, `fast`, `varied` |
| `emphasis_pattern` | string | How key words/phrases are emphasized |
| `voice_character` | enum | `narrator`, `character`, `testimonial`, `inner_monologue` |

#### 4. visual_direction

Visual style and treatment for the video.

| Property | Type | Description |
|---|---|---|
| `visual_style` | enum | `cinematic`, `minimalist`, `dynamic`, `documentary`, `stylized`, `raw` |
| `color_palette` | string | Color treatment description |
| `lighting_mood` | enum | `warm`, `dramatic`, `natural`, `neon`, `moody`, `bright` |
| `camera_work` | enum | `static`, `handheld`, `drone`, `mixed`, `tracking`, `zoom` |
| `aspect_ratio` | enum | `9:16`, `16:9`, `1:1`, `4:5` |

#### 5. audio_mood

Background audio/music direction.

| Property | Type | Description |
|---|---|---|
| `mood` | enum | `uplifting`, `tense`, `melancholic`, `energetic`, `mysterious`, `triumphant` |
| `tempo` | enum | `slow`, `moderate`, `fast` |
| `instrumentation` | string | Description of desired audio elements |
| `volume_balance` | string | How audio mixes with voiceover |

#### 6. text_style

On-screen text/typography direction.

| Property | Type | Description |
|---|---|---|
| `text_treatment` | enum | `bold_captions`, `subtle_lower_thirds`, `kinetic_typography`, `minimal_labels`, `none` |
| `font_style` | enum | `sans_serif_bold`, `handwritten`, `elegant_serif`, `monospace`, `display` |
| `text_animation` | enum | `fade_in`, `slide_up`, `typewriter`, `bounce`, `pop`, `none` |
| `text_color_scheme` | string | Color treatment for text overlays |

#### 7. transition

Transition between scenes or segments.

| Property | Type | Description |
|---|---|---|
| `transition_type` | enum | `cut`, `dissolve`, `whip_pan`, `zoom_through`, `match_cut`, `fade_to_black`, `glitch` |
| `transition_duration` | string | Duration (e.g., `0.5s`, `1s`, `24frames`) |
| `transition_energy` | enum | `subtle`, `moderate`, `dramatic` |

### Extensibility

The schema is designed to be extensible. New component types can be added
without breaking existing compositions. The common properties (component_id,
component_type, name, version, duration_range, platforms, tags, description)
remain stable across all types.

This same LEGO-like pattern can be applied to other content domains (podcasts,
blog posts, presentations) by defining new component types while reusing the
common schema foundation.

---

## Composition Format

A composition defines how components are assembled into a manuscript. It
references components by `component_id` and optionally overrides specific
properties. Compositions are YAML files.

### Structure

```yaml
composition_id: "product-promo-tech-gadget-001"
name: "Tech Gadget Product Promo - Dramatic Reveal"
target_duration: 60
target_platforms: [tiktok, reels, shorts]

component_bindings:
  hook:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_name} was wrong?"

  voice_style:
    component_id: "voice-authoritative-dramatic-001"

  visual_direction:
    component_id: "visual-cinematic-dark-001"
    overrides:
      color_palette: "Deep blacks with {brand_accent_color} highlights"

  scenes:
    - component_id: "scene-problem-statement-001"
      overrides:
        scene_script: "You've been struggling with {pain_point} for years..."
    - component_id: "scene-solution-reveal-001"
      overrides:
        scene_script: "Until now. Introducing {product_name}..."
    - component_id: "scene-social-proof-001"
    - component_id: "scene-call-to-action-001"
      overrides:
        scene_script: "Get yours today. Link in bio."

  audio_mood:
    component_id: "audio-tense-building-001"

  text_style:
    component_id: "text-bold-captions-001"

  transitions:
    - component_id: "transition-whip-pan-001"
    - component_id: "transition-zoom-through-001"
```

### Composition Rules

- **References, not duplicates**: Components are referenced by `component_id`.
  The workflow resolves references against the component library at generation
  time.
- **Overrides**: Allow per-manuscript customization without modifying the
  component. Overrides must conform to the component type's schema.
- **Placeholders**: `{placeholder}` values in overrides are resolved from the
  Product Master (e.g., `{product_name}`, `{pain_point}`, `{brand_accent_color}`).
- **Optional bindings**: Not all component types are required. A composition
  may omit `text_style` (no on-screen text) or `transitions` (simple cuts).
- **Scenes are ordered**: The `scenes` binding is an ordered list. Other
  bindings are single components.

---

## Manuscript Output

The generated manuscript resolves all component references, applies overrides,
and fills placeholders. It is a self-contained markdown document with sections
for: Opening (hook), Voice Direction, Visual Treatment, Scene-by-Scene
Breakdown, Audio Direction, Text Overlay Direction, and Production Notes
(unresolved placeholders, missing components, platform considerations).

YAML frontmatter includes: composition_id, target_duration, target_platforms,
product_name, component_count, generation_date.

---

## Quality Requirements

### Component Inventory
- Every component file is discovered and classified by type
- Invalid components (missing required fields, unknown type) are flagged but
  do not block the workflow
- Duplicate component IDs are detected and reported

### Manuscript
- All component references fully resolved (no dangling IDs)
- All placeholders resolved or flagged as `{UNRESOLVED: field_name}`
- Overrides conform to component type schema
- Missing components flagged as gaps but do not block generation

### Constraints
- Components, compositions, and Product Master are read-only
- Manuscripts are downstream-agnostic -- describe WHAT, not HOW
- Extensible schema -- new types don't break existing compositions

---

## Builder Instructions

**Suggested phases** (builder may adjust):

1. **Scan** -- Discover and validate components. Build inventory.
2. **Plan** -- Resolve composition references against inventory. Identify
   overrides and placeholder bindings.
3. **Generate** -- For each composition, resolve components + placeholders,
   assemble manuscript.
4. **Review** -- Quality review of generated manuscripts.
5. **Refine** -- Fix issues (conditional).

### Action: scan_components

Scan `components/` for component files. Parse YAML frontmatter, validate
required fields, classify by type, detect duplicates. Write
COMPONENT_INVENTORY_FILE.

**Returns:** APPROVED when at least one valid component found. REJECTED with
`NO_COMPONENTS_FOUND` if directory missing or empty.

---

## Notes

- Downstream chain: `product_master_gen_v2` -> `video_campaign_manuscript_v1`
  -> `voiceover_gen` / `image_gen` / `video_gen` / `video_assembly`
- The component schema is generic -- reusable across content types by defining
  new component types with the same common property foundation.
- Reference: `product_master_gen_v2` for scanning/inventory pattern.
