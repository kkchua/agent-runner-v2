---
doc_type: "composition_format"
lifecycle_status: "draft"
effective_version: "WBUILD2-dpxcr3x1"
domain: "video_campaign_manuscript"
source_spec: "video_campaign_manuscript_v2.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
component_schema: "COMPONENT_SCHEMA-01.md"
created_at: "2026-08-08"
---

# Composition Format: Video Campaign Manuscript Domain

## Overview

The composition format defines Layer 2 of the three-layer composition architecture for the video_campaign_manuscript domain. A composition is a declarative YAML document that specifies how reusable components (Layer 1) are assembled into a complete video production manuscript (Layer 3). Rather than duplicating component content, compositions reference components by their component_id and optionally override specific properties to customize them for a particular campaign. Placeholders within override values are resolved from external data sources at generation time, producing a self-contained manuscript that downstream workflows consume for voiceover generation, visual asset creation, video editing, and platform-specific adaptation.

In the three-layer architecture, compositions occupy the middle layer: they sit above the component library (which defines WHAT the building blocks are) and below the resolved output (which is the RESULT). Compositions define HOW components fit together -- which components to use, in what order, with what customizations, and which external data sources supply the variable content.

The domain context is short-form video campaign production (15-90 seconds) for platforms including TikTok, Instagram Reels, and YouTube Shorts. A manuscript coordinates seven creative concerns -- opening hook, content scenes, voice direction, visual treatment, audio mood, text overlays, and scene transitions -- into a unified production guide.

## Composition Structure

A composition is a YAML document with five required top-level fields. The structure follows the universal pattern defined in COMPOSITION_SYSTEM_STANDARD.md Section 4.1.

### Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| composition_id | string | Yes | Unique identifier for this composition. Format: comp-{descriptor}-{seq} (e.g., comp-skincare-launch-001). No two compositions may share the same composition_id. |
| name | string | Yes | Human-readable display name. Used in output headings and review documents. Non-empty string, max 100 characters. |
| target_metadata | object | Yes | Domain-specific metadata describing the target deliverable. See target_metadata fields below. |
| data_sources | object | Yes | Declares external data sources for placeholder resolution. Each field is a file path to the data source. See data_sources fields below. |
| component_bindings | object | Yes | Assembly instructions mapping binding names to component references. See Component Bindings section. |

### target_metadata Fields

| Field | Type | Required | Description |
|---|---|---|---|
| duration_target | string | Yes | Total target video duration. Format: N-Ns (e.g., "45-60s"). All scene durations and transitions must sum within this range. |
| target_platforms | array | Yes | List of target platforms. Valid values: tiktok, reels, shorts. Must contain at least one platform. |
| campaign_type | string | Yes | The type of campaign. Examples: product_launch, brand_awareness, seasonal_promo, feature_highlight. |
| brand | string | Yes | Brand or product line name. Used for brand consistency checks and output metadata. |

### data_sources Fields

| Field | Type | Required | Description |
|---|---|---|---|
| product_master | string | Yes | Relative or absolute path to the Product Master data file. Provides product_name, product_category, brand_name, key_benefit, pain_point, target_audience. |
| campaign_input | string | Yes | Relative or absolute path to the campaign-specific input file. Provides campaign_name, call_to_action_url, seasonal_angle, campaign_tagline. |
| platform_config | string | No | Relative or absolute path to platform configuration file. Provides platform_defaults, aspect_ratios, duration_limits, trending_formats. |

### Example Structure Skeleton

```yaml
composition_id: "comp-{descriptor}-{seq}"
name: "Human-readable composition name"
target_metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Brand Name"
data_sources:
  product_master: "data/products/product_name.yaml"
  campaign_input: "data/campaigns/campaign_name.yaml"
  platform_config: "data/platforms/platform_config.yaml"
component_bindings:
  opening:
    component_id: "hook-dramatic-001"
  scenes:
    - component_id: "scene-problem-001"
    - component_id: "scene-solution-001"
    - component_id: "scene-cta-001"
  voice:
    component_id: "voice-conversational-001"
  visuals:
    component_id: "visual-minimalist-warm-001"
  audio:
    component_id: "audio-uplifting-001"
  text:
    component_id: "text-subtitles-001"
  transitions:
    - component_id: "transition-match-cut-001"
    - component_id: "transition-fade-001"
```

## Component Bindings

Component bindings define which components are assembled and how. Each binding maps a binding name to one or more component references. Components are referenced by component_id, never copied or inlined. The workflow resolves each component_id against the component library at generation time.

### Binding Rules

The following table defines all binding slots for the video_campaign_manuscript domain. This table is domain-specific and authoritative.

| Binding Name | Component Type | Cardinality | Required | Validation on Missing |
|---|---|---|---|---|
| opening | hook | Singleton | Yes | Error: missing required binding 'opening' |
| scenes | scene | Ordered list (3-8) | Yes | Error: missing required binding 'scenes' |
| voice | voice_style | Singleton | Yes | Error: missing required binding 'voice' |
| visuals | visual_direction | Singleton | Yes | Error: missing required binding 'visuals' |
| audio | audio_mood | Singleton | Yes | Error: missing required binding 'audio' |
| text | text_style | Singleton | No | No error; section omitted from output |
| transitions | transition | Ordered list (N-1 for N scenes) | Yes | Error: missing required binding 'transitions' |

### Singleton Bindings

A singleton binding references exactly one component. The binding value is a single object containing a component_id and optional overrides.

```yaml
# Singleton binding: exactly one component
voice:
  component_id: "voice-conversational-001"
```

Singleton bindings are used for creative concerns that apply uniformly across the entire manuscript: voice direction, visual treatment, audio mood, and text treatment all govern the whole video, not individual segments.

### Ordered List Bindings

An ordered list binding references multiple components in sequence. The binding value is a YAML array of objects, each containing a component_id and optional overrides. The position in the array determines the order.

```yaml
# Ordered list binding: multiple components in sequence
scenes:
  - component_id: "scene-problem-001"
    overrides:
      scene_script: "Most {product_category} products promise {key_benefit} but fail."
  - component_id: "scene-solution-001"
  - component_id: "scene-demo-001"
  - component_id: "scene-cta-001"
    overrides:
      scene_script: "Try {product_name} today. Link in bio."
```

Ordered list bindings are used for content segments that follow a narrative sequence (scenes) and the transitions between them. Order matters: the first scene is the opening content segment after the hook, and subsequent scenes follow in narrative progression.

### Required vs Optional Bindings

Required bindings MUST be present in every composition. If a required binding is missing, the composition fails validation with a specific error identifying the missing binding name. Optional bindings MAY be omitted. When an optional binding is absent, the corresponding output section is omitted from the resolved manuscript. If an optional binding IS present, its content must be valid (valid component_id reference, conforming overrides).

In this domain, the text binding (text_style) is the only optional binding. Not all campaigns require on-screen text treatment. A campaign that relies solely on voiceover without captions or kinetic typography can omit the text binding entirely.

### Reference Pattern

Components are NEVER copied into compositions. A composition file contains only the component_id reference and any overrides. The full component content is resolved at generation time by looking up the component_id in the component library. This ensures:

- Components remain the single source of truth for their content
- Multiple compositions can reference the same component without duplication
- Updating a component in the library automatically affects all compositions that reference it (unless overridden)
- Composition files remain compact and readable

## Override Mechanism

Overrides allow per-composition customization of component properties without modifying the original component in the library. When a composition needs a component to behave differently for a specific campaign, it declares overrides for the specific properties that change.

### Override Semantics

1. **Merge behavior:** Overrides are merged with the component's base properties. The component's original property values serve as defaults. Override values take precedence on conflict. Non-overridden properties retain their component-defined values.

2. **Schema conformance:** Overrides MUST conform to the referenced component's type schema. An override key must be a valid type-specific property for the declared component_type. An override cannot introduce properties that do not exist in the type definition. Override values must respect data type constraints (string, enum, array) and enum value restrictions.

3. **Placeholder support:** Override values may contain {placeholder} references. These placeholders are resolved from the composition's declared data_sources at generation time.

### Override Rules by Component Type

The following tables list which properties each component type accepts in overrides. Only these properties may appear in an override block for the corresponding binding.

**opening (hook type):**

| Property | Type | Valid Override Values |
|---|---|---|
| hook_style | enum | dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook |
| hook_script | string | Any string, max 50 words. May contain {placeholders}. |
| visual_cue | string | Any non-empty string. |
| energy_level | enum | low, medium, high |

**scenes (scene type):**

| Property | Type | Valid Override Values |
|---|---|---|
| scene_purpose | enum | problem, solution, demo, testimonial, CTA, education, comparison |
| scene_script | string | Any string. May contain {placeholders}. Word count proportional to duration_target. |
| visual_direction | string | Any non-empty string describing the visual. |
| duration_target | string | Duration format: Ns or N-Ns. Range: 3-30s. |
| camera_work | string | Any string describing camera movement. |

**voice (voice_style type):**

| Property | Type | Valid Override Values |
|---|---|---|
| voice_tone | enum | authoritative, conversational, energetic, empathetic, playful |
| pace | enum | slow, moderate, fast, varied |
| emphasis_pattern | string | Any non-empty string. |
| voice_character | string | Any non-empty string. |

**visuals (visual_direction type):**

| Property | Type | Valid Override Values |
|---|---|---|
| visual_style | enum | cinematic, minimalist, vibrant, documentary, animated, mixed_media |
| color_palette | string | Any non-empty string. Should include brand hex codes when available. |
| lighting_mood | enum | bright, moody, natural, dramatic, soft |
| camera_work | string | Any string describing camera approach. |
| aspect_ratio | string | Standard ratio format (e.g., "9:16", "16:9", "1:1"). |

**audio (audio_mood type):**

| Property | Type | Valid Override Values |
|---|---|---|
| mood | enum | uplifting, tense, inspirational, playful, calm, dramatic |
| tempo | enum | slow, moderate, fast, dynamic |
| instrumentation | string | Any non-empty string. |
| volume_balance | string | Any non-empty string. |

**text (text_style type):**

| Property | Type | Valid Override Values |
|---|---|---|
| text_treatment | enum | subtitles, kinetic_typography, lower_thirds, title_cards, callouts |
| font_style | string | Any non-empty string. |
| text_animation | enum | none, fade, slide, typewriter, bounce |
| text_color_scheme | string | Any non-empty string. |

**transitions (transition type):**

| Property | Type | Valid Override Values |
|---|---|---|
| transition_type | enum | cut, fade, dissolve, wipe, zoom, match_cut, whip_pan |
| transition_duration | string | Duration format: Ns, N.Ns, or N-Ns. Range: 0.1-3.0s. |
| transition_energy | enum | subtle, moderate, dramatic |

### Example of Overrides

```yaml
component_bindings:
  opening:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_name} was wrong?"
      energy_level: "high"
  visuals:
    component_id: "visual-minimalist-warm-001"
    overrides:
      color_palette: "Warm neutrals with gold. Brand hex: #C5A572"
```

In this example:
- The opening hook uses hook-dramatic-reveal-001 from the library. The hook_script is overridden to include a product-specific placeholder {product_name}. The energy_level is explicitly set to "high" (which may match the base value -- redundant overrides are valid but unnecessary).
- The visual direction uses visual-minimalist-warm-001. Only the color_palette is overridden to include brand-specific hex codes. All other properties (visual_style, lighting_mood, camera_work, aspect_ratio) retain their base values from the component.

## Placeholder Resolution

Placeholders are {placeholder_name} tokens that appear in override values and in component property values (specifically hook_script and scene_script). They are resolved from external data sources declared in the composition's data_sources section at generation time.

### Placeholder Syntax

Placeholders use the syntax {field_name} where field_name is a key from one of the declared data sources. Curly braces delimit the placeholder. The field_name must match a key provided by one of the data sources exactly (case-sensitive).

Examples of valid placeholder syntax:
- {product_name}
- {key_benefit}
- {pain_point}
- {campaign_tagline}

### Data Sources and Their Fields

Each data source provides a specific set of fields. The composition declares which data source files to use, and the workflow reads the field values from those files at generation time.

**Product Master** (required, path from data_sources.product_master):

| Field | Description | Example Value |
|---|---|---|
| product_name | The product's consumer-facing name | "Lumiere Radiance Serum" |
| product_category | Product category or class | "skincare serum" |
| brand_name | Full brand name | "Lumiere Skincare" |
| key_benefit | Primary product benefit | "visible radiance in 7 days" |
| pain_point | Consumer pain point the product addresses | "dull, uneven skin tone" |
| target_audience | Intended audience description | "millennial women, 25-35" |

**Campaign Input** (required, path from data_sources.campaign_input):

| Field | Description | Example Value |
|---|---|---|
| campaign_name | Campaign display name | "Summer Glow Launch 2026" |
| call_to_action_url | URL for the call-to-action | "https://lumiere.shop/serum" |
| seasonal_angle | Seasonal relevance or angle | "summer radiance" |
| campaign_tagline | Campaign tagline or slogan | "Glow beyond ordinary" |

**Platform Config** (optional, path from data_sources.platform_config):

| Field | Description | Example Value |
|---|---|---|
| platform_defaults | Default settings per platform | Map of platform to default config |
| aspect_ratios | Aspect ratio per platform | Map of platform to ratio (e.g., all 9:16) |
| duration_limits | Duration constraints per platform | Map of platform to max duration |
| trending_formats | Current trending format guidance | List of trending styles per platform |

### Resolution Process

1. The workflow reads the data source files declared in the composition's data_sources section.
2. For each {placeholder} encountered in override values or component property values, the workflow searches the data source fields for a matching key.
3. If found, the placeholder is replaced with the field's value.
4. If not found in any data source, the placeholder is flagged as unresolved (see below).

### Priority Rules

When multiple data sources provide the same field name, the following priority order applies:

1. Product Master (highest priority)
2. Campaign Input (second priority)
3. Platform Config (lowest priority)

In practice, field names are typically unique to one data source (product_name comes only from Product Master, campaign_name comes only from Campaign Input). Priority rules handle edge cases where fields might overlap.

### Unresolved Placeholders

If a placeholder cannot be resolved from any declared data source, it is flagged in the output as:

```
{UNRESOLVED: field_name}
```

This makes it immediately visible to reviewers that a value is missing. The composition remains valid but the resolved output receives lifecycle_status "draft" instead of "final" until all placeholders are resolved.

Rules for unresolved placeholders:
- No raw {placeholder} syntax may appear in the output without either being resolved or flagged as {UNRESOLVED: field_name}.
- The flagging syntax is consistent: always {UNRESOLVED: field_name}, never "TODO", "[MISSING]", or other alternatives.
- The output's frontmatter includes an unresolved_placeholder_count field indicating how many placeholders could not be resolved.

### Example of Placeholder Resolution

Given a composition with:
```yaml
data_sources:
  product_master: "data/products/lumiere_serum.yaml"
  campaign_input: "data/campaigns/summer_launch_2026.yaml"
```

And a Product Master file containing:
```yaml
product_name: "Lumiere Radiance Serum"
product_category: "skincare serum"
key_benefit: "visible radiance in 7 days"
pain_point: "dull, uneven skin tone"
```

An override value of:
```yaml
hook_script: "What if your {product_category} routine was missing one key ingredient?"
```

Resolves to:
```
"What if your skincare serum routine was missing one key ingredient?"
```

An override value of:
```yaml
scene_script: "Introducing {product_name} -- formulated with {key_ingredient} for real {key_benefit}."
```

Resolves to (assuming key_ingredient is NOT in any data source):
```
"Introducing Lumiere Radiance Serum -- formulated with {UNRESOLVED: key_ingredient} for real visible radiance in 7 days."
```

## Ordering Rules

Bindings in the composition format follow two ordering models, determined by the domain's creative requirements. The component schema defines which model applies to each binding.

### Singleton Bindings (No Ordering)

Singleton bindings reference exactly one component. There is no ordering concern because there is only one element. The following bindings are singletons:

- **opening** (hook): Exactly one opening sequence per manuscript. The hook is the first thing the viewer sees, but its position is always first by definition, so ordering within the binding is irrelevant.
- **voice** (voice_style): One voice direction applies uniformly across the entire manuscript.
- **visuals** (visual_direction): One visual treatment applies uniformly across the entire manuscript.
- **audio** (audio_mood): One audio mood applies uniformly across the entire manuscript.
- **text** (text_style): One text treatment applies uniformly across the entire manuscript (when present).

### Ordered List Bindings (Position Matters)

Ordered list bindings reference multiple components in a specific sequence. The position in the YAML array determines the order. The following bindings are ordered lists:

- **scenes** (scene): Scenes follow a narrative arc. Position determines where in the story each scene falls. The first scene typically establishes the problem, middle scenes develop the solution and demonstration, and the final scene drives the call to action. The narrative order is determined by the composition author's arrangement in the YAML array.
- **transitions** (transition): Transitions are interleaved between scenes. The i-th transition connects scene i to scene i+1. The count constraint (transitions count = scenes count - 1) ensures proper interleaving.

### Ordering Constraints

The following constraints apply to ordered bindings:

| Constraint | Rule | Error if Violated |
|---|---|---|
| Scene count | Must be between 3 and 8 (inclusive) | "Scene count {count} is outside the 3-8 range" |
| Transition count | Must equal scene count minus 1 | "Transition count {count} does not match scenes count {scene_count} - 1" |
| Scene narrative order | Determined by array position | N/A (author determines order) |
| Interleaving | In output: scene_1, transition_1, scene_2, transition_2, ..., scene_N | Enforced by the resolution process |

### Example of Ordered vs Singleton

```yaml
component_bindings:
  # Singleton: one component, no ordering concern
  voice:
    component_id: "voice-conversational-001"

  # Ordered list: position in array determines narrative order
  scenes:
    - component_id: "scene-problem-001"     # Position 1: problem
    - component_id: "scene-solution-001"     # Position 2: solution
    - component_id: "scene-demo-001"         # Position 3: demonstration
    - component_id: "scene-cta-001"          # Position 4: call to action

  # Ordered list: N-1 transitions for N scenes
  transitions:
    - component_id: "transition-match-cut-001"  # Between scene 1 and 2
    - component_id: "transition-fade-001"       # Between scene 2 and 3
    - component_id: "transition-dissolve-001"   # Between scene 3 and 4
```

## Composition Validation

Every composition must pass the following validation checks before it can be resolved into an output. These checks correspond to the rules defined in COMPOSITION_SYSTEM_STANDARD.md Section 4.3 and the domain-specific requirements from video_campaign_manuscript_v2.md Section 3.

### Reference Integrity

| Rule ID | Check | Error Condition | Severity |
|---|---|---|---|
| CF-VAL-001 | All referenced component_ids exist in the component library | A component_id does not match any component in the inventory | CRITICAL |
| CF-VAL-002 | Referenced component_ids match expected type for their binding slot | A binding for type "hook" references a component of type "scene" | CRITICAL |

### Override Conformance

| Rule ID | Check | Error Condition | Severity |
|---|---|---|---|
| CF-VAL-003 | All override keys are valid properties for the referenced component's type | An override key is not a recognized type-specific property | CRITICAL |
| CF-VAL-004 | Override values respect data type constraints | A string property overridden with a number, or vice versa | MAJOR |
| CF-VAL-005 | Enum-type properties overridden only with valid enum values | An enum override uses a value not in the declared enum list | CRITICAL |

### Required Bindings

| Rule ID | Check | Error Condition | Severity |
|---|---|---|---|
| CF-VAL-006 | All required bindings are present | A required binding (opening, scenes, voice, visuals, audio, transitions) is missing | CRITICAL |
| CF-VAL-007 | Optional bindings, if present, contain valid content | An optional binding has an invalid component_id or non-conforming overrides | MAJOR |

### Placeholder Resolvability

| Rule ID | Check | Error Condition | Severity |
|---|---|---|---|
| CF-VAL-008 | All {placeholder} values can be resolved from declared data sources | A placeholder name does not match any field in any declared data source | MAJOR |
| CF-VAL-009 | Data source files exist and are readable | A declared data source path does not resolve to a file | MAJOR |

### Ordering Constraints

| Rule ID | Check | Error Condition | Severity |
|---|---|---|---|
| CF-VAL-010 | Scene count is between 3 and 8 | scenes array has fewer than 3 or more than 8 entries | CRITICAL |
| CF-VAL-011 | Transition count equals scene count minus 1 | transitions array length != (scenes array length - 1) | CRITICAL |
| CF-VAL-012 | Singleton bindings contain exactly one component reference | A singleton binding is a list instead of a single object | CRITICAL |

### Validation Behavior

Invalid compositions are flagged with specific error messages but do not block the entire workflow. The workflow proceeds with flagged compositions, noting missing components as gaps in the output. CRITICAL findings prevent resolution of the affected composition. MAJOR findings are reported but allow resolution with warnings.

## Example Compositions

### Example 1: Skincare Product Launch

This composition demonstrates a product launch campaign for a skincare serum. It uses all seven binding types (including the optional text binding), overrides with placeholders, and both singleton and ordered list bindings.

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
  platform_config: "data/platforms/default_config.yaml"
component_bindings:
  opening:
    component_id: "hook-question-001"
    overrides:
      hook_script: "What if your {product_category} routine was missing one key ingredient?"
  scenes:
    - component_id: "scene-problem-001"
      overrides:
        scene_script: "Most {product_category} products promise {key_benefit}, but most ingredients cannot penetrate deep enough to make a real difference."
    - component_id: "scene-solution-001"
      overrides:
        scene_script: "Introducing {product_name} -- formulated with a proprietary delivery system for real {key_benefit}."
    - component_id: "scene-demo-001"
      overrides:
        scene_script: "In just 7 days, users reported visibly brighter, more even-toned skin."
    - component_id: "scene-cta-001"
      overrides:
        scene_script: "Try {product_name} today. Link in bio."
  voice:
    component_id: "voice-conversational-001"
  visuals:
    component_id: "visual-minimalist-warm-001"
    overrides:
      color_palette: "Warm neutrals with gold accents. Primary: #F5F0E8, Accent: #C5A572, Text: #2C2C2C"
  audio:
    component_id: "audio-uplifting-001"
  text:
    component_id: "text-subtitles-001"
  transitions:
    - component_id: "transition-match-cut-001"
    - component_id: "transition-fade-001"
    - component_id: "transition-dissolve-001"
```

**Features demonstrated:**
- Singleton bindings: opening, voice, visuals, audio, text (all use single component references)
- Ordered list bindings: scenes (4 scenes in narrative order: problem, solution, demo, CTA), transitions (3 transitions for 4 scenes)
- Overrides with placeholders: opening hook_script uses {product_category}; scenes use {product_category}, {key_benefit}, {product_name}
- Overrides without placeholders: visuals color_palette overridden with brand-specific hex codes
- No overrides: voice, audio, text use components exactly as defined in the library
- Optional binding included: text binding is present (optional but included for accessibility)
- Constraint satisfied: 4 scenes, 3 transitions (N-1 rule)

### Example 2: Brand Awareness Campaign (Minimal Composition)

This composition demonstrates a brand awareness campaign that omits the optional text binding and uses fewer overrides. It shows that compositions can be minimal while still satisfying all required binding rules.

```yaml
composition_id: "comp-brand-awareness-001"
name: "Lumiere Brand Awareness -- Summer Vibes"
target_metadata:
  duration_target: "30-45s"
  target_platforms: ["tiktok", "reels"]
  campaign_type: "brand_awareness"
  brand: "Lumiere Skincare"
data_sources:
  product_master: "data/products/lumiere_serum.yaml"
  campaign_input: "data/campaigns/summer_awareness_2026.yaml"
component_bindings:
  opening:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "This summer, redefine what your skin can do."
  scenes:
    - component_id: "scene-problem-001"
      overrides:
        scene_script: "Summer heat, pollution, and stress leave your {pain_point} worse than ever."
    - component_id: "scene-education-001"
      overrides:
        scene_script: "Your skin needs more than surface-level care. It needs ingredients that reach deeper layers."
    - component_id: "scene-cta-001"
      overrides:
        scene_script: "Discover {product_name}. Your best summer skin starts now."
  voice:
    component_id: "voice-energetic-001"
    overrides:
      pace: "fast"
  visuals:
    component_id: "visual-vibrant-001"
    overrides:
      lighting_mood: "bright"
  audio:
    component_id: "audio-playful-001"
  transitions:
    - component_id: "transition-whip-pan-001"
    - component_id: "transition-zoom-001"
```

**Features demonstrated:**
- Optional binding omitted: no text binding (brand awareness relies on voiceover only)
- Singleton bindings with overrides: voice overrides pace to "fast"; visuals overrides lighting_mood to "bright"
- Singleton bindings without overrides: audio uses component as-is
- Ordered list bindings: scenes (3 scenes in narrative order: problem, education, CTA), transitions (2 transitions for 3 scenes)
- Overrides with placeholders: scenes use {pain_point}, {product_name}
- Override with enum value: voice pace overridden to "fast" (valid enum value for voice_style.pace)
- Override with enum value: visuals lighting_mood overridden to "bright" (valid enum value for visual_direction.lighting_mood)
- Constraint satisfied: 3 scenes, 2 transitions (N-1 rule)
- Constraint satisfied: 3 scenes is within the 3-8 range

## Self-Validation Checklist

This section verifies that the composition format covers all required rules and that the example compositions collectively exercise all defined features.

### Rule Coverage

| Rule | Covered? | Section | Evidence |
|---|---|---|---|
| Reference pattern (component_id, not copies) | YES | Component Bindings - Reference Pattern | Explicit statement and enforcement |
| Override mechanism (merge, override wins) | YES | Override Mechanism | Semantic rules defined, property tables per type |
| Override schema conformance | YES | Override Mechanism - Override Rules by Component Type | All 7 types enumerated with valid properties |
| Placeholder syntax ({field_name}) | YES | Placeholder Resolution - Placeholder Syntax | Syntax defined with examples |
| Placeholder resolution from data sources | YES | Placeholder Resolution - Data Sources and Their Fields | Three data sources with field tables |
| Unresolved placeholder handling ({UNRESOLVED: field_name}) | YES | Placeholder Resolution - Unresolved Placeholders | Exact syntax defined, lifecycle_status impact |
| Placeholder priority rules | YES | Placeholder Resolution - Priority Rules | Product Master > Campaign Input > Platform Config |
| Binding rules (all 7 bindings) | YES | Component Bindings - Binding Rules | Table with cardinality, required/optional, validation |
| Singleton bindings | YES | Component Bindings - Singleton Bindings | Defined with example |
| Ordered list bindings | YES | Component Bindings - Ordered List Bindings | Defined with example |
| Required vs optional bindings | YES | Component Bindings - Required vs Optional Bindings | Validation behavior specified |
| Ordering constraints | YES | Ordering Rules - Ordering Constraints | Scene count 3-8, transition count N-1 |
| Composition validation rules | YES | Composition Validation | 12 validation rules with IDs, conditions, severity |

### Example Coverage

| Feature | Example 1 (Skincare Launch) | Example 2 (Brand Awareness) |
|---|---|---|
| Singleton binding (no overrides) | voice, audio, text | audio |
| Singleton binding (with overrides, no placeholders) | visuals (color_palette) | visuals (lighting_mood) |
| Singleton binding (with overrides, with enum value) | -- | voice (pace: "fast") |
| Ordered list (scenes with overrides) | 4 scenes with placeholder overrides | 3 scenes with placeholder overrides |
| Ordered list (transitions) | 3 transitions, no overrides | 2 transitions, no overrides |
| Optional binding included | text binding present | -- |
| Optional binding omitted | -- | text binding omitted |
| Placeholder in hook_script | {product_category} | No placeholders in hook |
| Placeholder in scene_script | {product_category}, {key_benefit}, {product_name} | {pain_point}, {product_name} |
| Placeholder in override without data source match | -- (all resolve) | -- (all resolve) |
| Constraint: scene count 3-8 | 4 scenes | 3 scenes |
| Constraint: transition count = N-1 | 3 transitions for 4 scenes | 2 transitions for 3 scenes |

### Completeness Summary

- All 7 binding types defined with cardinality and required/optional: YES
- Override rules enumerate all type-specific properties for all 7 component types: YES
- Data sources define all fields from the spec (product_master: 6 fields, campaign_input: 4 fields, platform_config: 4 fields): YES
- Unresolved placeholder syntax defined: YES
- Priority rules defined: YES
- At least 2 complete example compositions: YES (2 examples)
- Examples collectively exercise all features (reference, override, placeholder, ordering, optional omission): YES
- Validation rules cover reference integrity, override conformance, required bindings, placeholder resolvability, ordering constraints: YES
- Composition structure matches COMPOSITION_SYSTEM_STANDARD.md Section 4.1: YES
- Composition structure matches video_campaign_manuscript_v2.md Section 3.1: YES

---

**End of Composition Format**
