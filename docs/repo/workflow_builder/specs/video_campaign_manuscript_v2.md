# Composition System Specification: Video Campaign Manuscript

> **Domain:** Short-form video campaign production
> **Input to:** workflow_builder_v2
> **Standard:** COMPOSITION_SYSTEM_STANDARD.md

---

## 1. Domain Overview

**Domain name:** `video_campaign_manuscript`
**Label:** Video Campaign Manuscript
**Job prefix:** `VCAMP`
**Description:** Generates complete video production manuscripts from reusable creative components and declarative composition definitions.

### 1.1 Purpose

Video campaign production requires coordinating multiple creative concerns (opening hook, scene structure, voice direction, visual treatment, audio mood, text overlays, transitions) across platforms (TikTok, Reels, Shorts). Currently, manuscripts are written from scratch for each campaign, leading to inconsistency and slow iteration.

This composition system decomposes manuscripts into reusable components that can be mixed, matched, and overridden per campaign. A declarative composition references components by ID, specifies overrides, and resolves placeholders from a Product Master data source.

**Trigger:** User provides a component library directory, composition definitions, and product data.

**Outcome:** A complete video production manuscript with all components expanded, overrides applied, and placeholders resolved. Downstream workflows consume this to generate voiceovers, visual assets, video edits, and platform-specific adaptations.

### 1.2 Domain Context

Short-form video advertising (15-90 seconds) across TikTok, Instagram Reels, and YouTube Shorts. The manuscript is the master creative document that guides all downstream production. It must be platform-aware (aspect ratios, duration constraints, trending formats) and brand-consistent.

---

## 2. Component Schema (Layer 1)

### 2.1 Component Types

| Component Type | Purpose | Required? | Cardinality |
|---|---|---|---|
| `hook` | Opening sequence that captures attention in first 3-5 seconds | Yes | Singleton (exactly 1 per manuscript) |
| `scene` | Content segment with a specific purpose (problem, solution, demo, CTA) | Yes | Ordered list (3-8 scenes per manuscript) |
| `voice_style` | Voiceover direction (tone, pace, emphasis) | Yes | Singleton |
| `visual_direction` | Visual treatment (style, color, lighting, camera) | Yes | Singleton |
| `audio_mood` | Background music/audio direction | Yes | Singleton |
| `text_style` | On-screen text treatment (captions, titles, lower thirds) | No | Singleton |
| `transition` | Scene transition effect | Yes | Ordered list (N-1 transitions for N scenes) |

### 2.2 Common Properties

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique ID (format: `{type}-{descriptor}-{seq}`, e.g., `hook-dramatic-001`) |
| `component_type` | enum | Yes | One of the 7 types in 2.1 |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| `description` | string | Yes | Creative intent and when to use |
| `duration_range` | string | No | Applicable duration (e.g., "3-5s", "10-15s") |
| `platforms` | array | No | Target platforms (e.g., ["tiktok", "reels", "shorts"]) |
| `tags` | array | No | Classification tags for search/filter |

### 2.3 Type-Specific Properties

#### Type: hook

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `hook_style` | enum | Yes | Opening technique. Values: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook | `dramatic_reveal` |
| `hook_script` | string | Yes | Spoken/displayed text. Max 50 words. May contain {placeholders} | `"What if everything you knew about skincare was wrong?"` |
| `visual_cue` | string | Yes | Visual element during hook | `"Extreme close-up of cracked serum bottle, dark background"` |
| `energy_level` | enum | Yes | Intensity. Values: low, medium, high | `high` |

#### Type: scene

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `scene_purpose` | enum | Yes | Role in narrative. Values: problem, solution, demo, testimonial, CTA, education, comparison | `problem` |
| `scene_script` | string | Yes | Spoken text for this scene. May contain {placeholders} | `"Most products promise results but deliver disappointment."` |
| `visual_direction` | string | Yes | What the viewer sees during this scene | `"Split-screen: left shows frustrated customer, right shows product"` |
| `duration_target` | string | Yes | Target duration for this scene | `"8-12s"` |
| `camera_work` | string | No | Camera movement/angle | `"Slow push-in on customer face"` |

#### Type: voice_style

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `voice_tone` | enum | Yes | Vocal quality. Values: authoritative, conversational, energetic, empathetic, playful | `conversational` |
| `pace` | enum | Yes | Speaking speed. Values: slow, moderate, fast, varied | `moderate` |
| `emphasis_pattern` | string | No | How key words are stressed | `"Stress product benefits, pause before CTA"` |
| `voice_character` | string | No | Voice persona description | `"Friendly expert, like a knowledgeable friend"` |

#### Type: visual_direction

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `visual_style` | enum | Yes | Overall aesthetic. Values: cinematic, minimalist, vibrant, documentary, animated, mixed_media | `minimalist` |
| `color_palette` | string | Yes | Color scheme | `"Warm neutrals with gold accents. Brand hex: #C5A572"` |
| `lighting_mood` | enum | Yes | Lighting quality. Values: bright, moody, natural, dramatic, soft | `soft` |
| `camera_work` | string | No | General camera approach | `"Mostly static shots with occasional slow movement"` |
| `aspect_ratio` | string | No | Video dimensions | `"9:16 vertical (safe crop for all platforms)"` |

#### Type: audio_mood

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `mood` | enum | Yes | Musical feel. Values: uplifting, tense, inspirational, playful, calm, dramatic | `uplifting` |
| `tempo` | enum | Yes | Speed. Values: slow, moderate, fast, dynamic | `moderate` |
| `instrumentation` | string | No | Instrument preferences | `"Acoustic guitar with light percussion"` |
| `volume_balance` | string | No | Music vs voice balance | `"Music at 20% under voiceover, swell to 40% in transitions"` |

#### Type: text_style

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `text_treatment` | enum | Yes | Text display style. Values: subtitles, kinetic_typography, lower_thirds, title_cards, callouts | `subtitles` |
| `font_style` | string | No | Font guidance | `"Clean sans-serif, bold for emphasis"` |
| `text_animation` | enum | No | Animation style. Values: none, fade, slide, typewriter, bounce | `fade` |
| `text_color_scheme` | string | No | Color guidance | `"White text with dark shadow for readability"` |

#### Type: transition

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `transition_type` | enum | Yes | Effect type. Values: cut, fade, dissolve, wipe, zoom, match_cut, whip_pan | `match_cut` |
| `transition_duration` | string | Yes | Duration of transition | `"0.5s"` |
| `transition_energy` | enum | Yes | Intensity. Values: subtle, moderate, dramatic | `moderate` |

### 2.4 Component File Format

Components are stored as markdown files with YAML frontmatter:

```markdown
---
component_id: "hook-dramatic-reveal-001"
component_type: "hook"
name: "Dramatic Reveal Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["dramatic", "product", "suspense"]
description: "Opens with a mysterious silhouette reveal, building curiosity"

hook_style: "visual_reveal"
hook_script: "What if everything you knew about {product_category} was wrong?"
visual_cue: "Close-up of product silhouette in darkness, single spotlight"
energy_level: "high"
---

# Dramatic Reveal Hook

Usage notes: Best for product launches or reveals. Pair with dramatic_reveal
transition for maximum impact. Works well with voice_tone=authoritative.
```

### 2.5 Validation Rules

- **Required fields:** component_id, component_type, name, version, description + all required type-specific properties
- **Valid component_type:** Must be one of: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition
- **Unique component_id:** No duplicates within the library
- **Enum values:** All enum properties must use declared values only
- **Duration format:** duration_range and duration_target must match pattern `\d+(-\d+)?s`
- **Placeholder syntax:** hook_script and scene_script may use `{placeholder_name}` syntax

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

Compositions are YAML files:

| Field | Type | Required | Description |
|---|---|---|---|
| `composition_id` | string | Yes | Unique ID (format: `comp-{descriptor}-{seq}`) |
| `name` | string | Yes | Human-readable name |
| `target_metadata` | object | Yes | Deliverable metadata (see 3.1.1) |
| `data_sources` | object | Yes | Placeholder resolution data (see 3.1.2) |
| `component_bindings` | object | Yes | Assembly instructions (see 3.2) |

#### 3.1.1 target_metadata

| Field | Type | Required | Description |
|---|---|---|---|
| `duration_target` | string | Yes | Total video duration (e.g., "45-60s") |
| `target_platforms` | array | Yes | Platforms (e.g., ["tiktok", "reels", "shorts"]) |
| `campaign_type` | string | Yes | Campaign type (e.g., "product_launch", "brand_awareness") |
| `brand` | string | Yes | Brand or product line name |

#### 3.1.2 data_sources

| Field | Type | Required | Description |
|---|---|---|---|
| `product_master` | string | Yes | Path to Product Master data file |
| `campaign_input` | string | Yes | Path to campaign-specific input file |
| `platform_config` | string | No | Path to platform configuration file |

### 3.2 Binding Rules

| Binding Name | Component Type | Cardinality | Required? | Description |
|---|---|---|---|---|
| `opening` | hook | Singleton | Yes | The opening sequence |
| `scenes` | scene | Ordered list | Yes | Content segments (3-8, in narrative order) |
| `voice` | voice_style | Singleton | Yes | Voiceover direction |
| `visuals` | visual_direction | Singleton | Yes | Visual treatment |
| `audio` | audio_mood | Singleton | Yes | Background music direction |
| `text` | text_style | Singleton | No | On-screen text treatment |
| `transitions` | transition | Ordered list | Yes | Scene transitions (count = scenes count - 1) |

### 3.3 Override Mechanism

```yaml
component_bindings:
  opening:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_name} was wrong?"
      energy_level: "high"
  scenes:
    - component_id: "scene-problem-001"
      overrides:
        scene_script: "Most {product_category} products promise {key_benefit} but fail."
    - component_id: "scene-solution-001"
      # No overrides — use component as-is
```

**Rules:**
- Overrides must conform to the component type's schema
- Override wins on conflict with base properties
- Placeholders in overrides are resolved from data sources

### 3.4 Placeholder Resolution

| Data Source | Fields Provided | Required? |
|---|---|---|
| Product Master | product_name, product_category, brand_name, key_benefit, pain_point, target_audience | Yes |
| Campaign Input | campaign_name, call_to_action_url, seasonal_angle, campaign_tagline | Yes |
| Platform Config | platform_defaults, aspect_ratios, duration_limits, trending_formats | No |

**Rules:**
- Unresolved placeholders flagged as `{UNRESOLVED: field_name}`
- Placeholders in hook_script and scene_script are mandatory to resolve
- Platform-specific placeholders resolved from platform_config when available

### 3.5 Example Composition

```yaml
composition_id: "comp-skincare-launch-001"
name: "Lumiere Serum Product Launch"
target_metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"
data_sources:
  product_master: "data/products/lumiere_serum.yaml"
  campaign_input: "data/campaigns/summer_launch_2026.yaml"
component_bindings:
  opening:
    component_id: "hook-question-001"
    overrides:
      hook_script: "What if your {product_category} routine was missing one key ingredient?"
  scenes:
    - component_id: "scene-problem-001"
      overrides:
        scene_script: "Most serums claim to deliver {key_benefit}, but most ingredients can't penetrate deep enough."
    - component_id: "scene-solution-001"
      overrides:
        scene_script: "Introducing {product_name} — formulated with {key_ingredient} for real {key_benefit}."
    - component_id: "scene-cta-001"
      overrides:
        scene_script: "Try {product_name} today. Link in bio."
  voice:
    component_id: "voice-conversational-001"
  visuals:
    component_id: "visual-minimalist-warm-001"
    overrides:
      color_palette: "Warm neutrals with gold. Brand hex: #C5A572"
  audio:
    component_id: "audio-uplifting-001"
  text:
    component_id: "text-subtitles-001"
  transitions:
    - component_id: "transition-match-cut-001"
    - component_id: "transition-fade-001"
```

---

## 4. Output Format (Layer 3)

### 4.1 Output Structure

The output is a markdown file with YAML frontmatter:

| Section | Source | Description |
|---|---|---|
| Frontmatter | Composition metadata | composition_id, name, metadata, component_count, generation_date, lifecycle_status |
| Opening | opening binding (expanded) | Full hook component with overrides applied |
| Voice Direction | voice binding (expanded) | Full voice_style component |
| Visual Treatment | visuals binding (expanded) | Full visual_direction component |
| Scene-by-Scene Breakdown | scenes + transitions (interleaved) | Each scene expanded, with transitions between them |
| Audio Direction | audio binding (expanded) | Full audio_mood component |
| Text Overlay | text binding (expanded, if present) | Full text_style component |
| Production Notes | Generated | Platform-specific notes, timing summary, unresolved placeholders |

### 4.2 Resolution Rules

- All component_id references expanded to full component content (common + type-specific properties)
- Overrides merged into base properties (override wins)
- All {placeholders} resolved from declared data sources
- Scenes and transitions interleaved: scene_1 → transition_1 → scene_2 → transition_2 → ... → scene_N
- Unresolved placeholders marked as `{UNRESOLVED: field_name}`

### 4.3 Quality Requirements

- No dangling component references
- No unresolved placeholders (unless lifecycle_status is "draft")
- Scene count between 3-8
- Transition count = scene count - 1
- Total duration within duration_target range
- All required bindings present
- Platform-specific considerations noted (aspect ratio, duration limits)

### 4.4 Example Output (Skeleton)

```markdown
---
composition_id: "comp-skincare-launch-001"
composition_name: "Lumiere Serum Product Launch"
metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"
component_count: 12
generation_date: "2026-08-08"
lifecycle_status: "final"
unresolved_placeholder_count: 0
---

# Lumiere Serum Product Launch

## Opening (Hook)
{Expanded hook component with overrides applied}

## Voice Direction
{Expanded voice_style component}

## Visual Treatment
{Expanded visual_direction component}

## Scene-by-Scene Breakdown

### Scene 1: Problem
{Expanded scene component}

*Transition: {expanded transition component}*

### Scene 2: Solution
{Expanded scene component}

*Transition: {expanded transition component}*

### Scene 3: Call to Action
{Expanded scene component}

## Audio Direction
{Expanded audio_mood component}

## Text Overlay
{Expanded text_style component}

## Production Notes
- Total estimated duration: 52s (within 45-60s target)
- Platform considerations: Vertical crop safe, first frame visually striking
- All placeholders resolved from product master and campaign input
```

---

## 5. Operational Requirements

### 5.1 Workflow Phases

| Phase | Purpose |
|---|---|
| **Scan** | Discover all component files in COMPONENT_LIBRARY_DIR, parse frontmatter, classify by type, validate against schema |
| **Plan** | Read compositions from COMPOSITIONS_DIR, resolve component_id references against inventory, identify overrides and placeholders, validate binding constraints |
| **Generate** | For each composition, expand all component references, apply overrides, resolve placeholders, assemble complete manuscript |
| **Review** | Quality review of generated manuscripts against quality requirements |
| **Refine** | Fix issues found in review (conditional) |

### 5.2 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `COMPONENT_LIBRARY_DIR` | Directory containing component markdown files (organized by type subdirectory) | Yes |
| `COMPOSITIONS_DIR` | Directory containing composition YAML files | Yes |
| `DATA_SOURCE_DIR` | Directory containing Product Master and campaign input files | Yes |

### 5.3 Output Artifacts

| Artifact Key | Description |
|---|---|
| `COMPONENT_INVENTORY_FILE` | Catalog of all discovered components with type classification and validation status |
| `VALIDATION_REPORT_FILE` | Detailed validation results per component with rule IDs |
| `RESOLUTION_PLAN_FILE` | For each composition: resolved references, override details, placeholder inventory |
| `OUTPUT_FILE` | The assembled video campaign manuscript |
| `REVIEW_FILE_SUGGESTED` | Quality review document |

### 5.4 Action Steps

Two custom action steps needed:

1. **scan_components** — Scan COMPONENT_LIBRARY_DIR for markdown files with YAML frontmatter. Parse each file, extract component properties, classify by component_type, validate against schema rules. Produce COMPONENT_INVENTORY_FILE and VALIDATION_REPORT_FILE.

2. **plan_compositions** — Read all YAML files from COMPOSITIONS_DIR. For each composition, resolve every component_id against the inventory, validate overrides against type schemas, check binding constraints (scene count 3-8, transition count = N-1), inventory all placeholders and assess resolvability against DATA_SOURCE_DIR. Produce RESOLUTION_PLAN_FILE.

### 5.5 Domain-Specific Requirements

- **Platform awareness:** Output must note platform-specific considerations (aspect ratio safety, duration limits, trending formats)
- **Timing accuracy:** Scene durations must sum to within duration_target range
- **Brand consistency:** Color palette overrides must reference brand hex codes when available
- **Placeholder priority:** Product Master fields take priority over Campaign Input when both provide the same field

---

## 6. References

- **Composition System Standard:** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`
- **Related workflows:** `video_campaign_manuscript_v1` (v1-style spec, same domain)
- **Downstream consumers:** Voiceover generation, visual asset generation, video editing workflows

---

**End of Specification**
