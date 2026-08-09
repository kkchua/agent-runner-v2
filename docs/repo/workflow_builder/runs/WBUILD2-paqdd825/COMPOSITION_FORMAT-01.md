---
doc_type: "composition_format"
lifecycle_status: "draft"
effective_version: "WBUILD2-paqdd825"
domain: "video_campaign_manuscript"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
component_schema_source: "COMPONENT_SCHEMA-01.md"
binding_count: 7
binding_modes: "singleton, ordered_list"
placeholder_data_sources: 3
---

# Composition Format: Video Campaign Manuscript Domain

## 1. Overview

The composition format defines Layer 2 of the three-layer composition architecture for the video campaign manuscript domain. A composition is a declarative assembly instruction that specifies which reusable components (from the Layer 1 component library) are combined, in what order, and with what per-composition customizations, to produce a complete video campaign production manuscript (Layer 3 resolved output). Compositions reference components by component_id -- they never duplicate or inline component content. The workflow resolves all references, merges any overrides with base component properties, fills placeholders from external data sources, and assembles the final self-contained deliverable at generation time.

**How compositions fit into the three-layer architecture:**

```
Layer 1: Component Library (COMPONENT_SCHEMA-01.md)
  - Standardized building blocks: hook, scene, voice_style,
    visual_direction, audio_mood, text_style, transition
  - Each component has a unique component_id
  - Components are immutable reference material

Layer 2: Composition Definitions (this document)
  - Declarative assembly instructions
  - Reference components by component_id
  - Specify overrides for per-composition customization
  - Declare placeholder bindings to external data sources

Layer 3: Resolved Outputs (Output Format specification)
  - Complete, self-contained production manuscripts
  - All component_id references expanded
  - All placeholders filled or flagged
  - All overrides applied
```

**Domain context:** Short-form video campaign production for digital advertising and branded content across platforms such as TikTok, Instagram Reels, and YouTube Shorts. A composition in this domain produces a video campaign manuscript -- a structured production document that downstream workflows consume to generate voiceovers, visual assets, video edits, and platform-specific adaptations.

---

## 2. Composition Structure

### 2.1 YAML Structure Definition

Compositions are YAML files with the following top-level structure:

| Field | Type | Required | Description |
|---|---|---|---|
| composition_id | string | Yes | Unique identifier for this composition. Format: "comp-{descriptor}-{sequence}" (e.g., comp-skincare-launch-001). Must be unique across all compositions. |
| name | string | Yes | Human-readable display name for the composition. Used in output headers and documentation. |
| target_metadata | object | Yes | Domain-specific metadata describing the target deliverable. Contains duration_target, target_platforms, campaign_type, and brand. |
| data_sources | object | Yes | Declares the external data sources available for placeholder resolution in this composition. Maps source names to file paths or identifiers. |
| component_bindings | object | Yes | The assembly instructions. A dictionary mapping binding names to component references. Each binding specifies a component_id and optional overrides. |

### 2.2 Target Metadata Fields

The target_metadata object contains the following fields:

| Field | Type | Required | Description | Example Value |
|---|---|---|---|---|
| duration_target | string | Yes | Total target duration for the final video. | "45-60s" |
| target_platforms | array | Yes | List of target platform identifiers. | ["tiktok", "reels", "shorts"] |
| campaign_type | string | Yes | The type of campaign this manuscript serves. | "product_launch" |
| brand | string | Yes | The brand or product line this campaign represents. | "Lumiere Skincare" |

### 2.3 Data Sources Declaration

The data_sources object declares which external data sources are available for placeholder resolution in this composition:

| Field | Type | Required | Description |
|---|---|---|---|
| product_master | string | Yes | Path to the Product Master data file containing product_name, product_category, brand_name, key_benefit, pain_point, target_audience. |
| platform_config | string | No | Path to the Platform Configuration file containing platform-specific defaults and constraints. |
| campaign_input | string | Yes | Path to the Campaign Input file containing campaign_name, call_to_action_url, seasonal_angle, and other campaign-specific values. |

### 2.4 Complete Composition File Example

```yaml
composition_id: "comp-skincare-launch-001"
name: "Lumiere Serum Product Launch"
target_metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"

data_sources:
  product_master: "data/product_master/lumiere_serum.yaml"
  platform_config: "data/platform_config/tiktok_reels.yaml"
  campaign_input: "data/campaign_input/summer_launch_2026.yaml"

component_bindings:
  opening_hook:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_category} was wrong?"
  voice_style:
    component_id: "voice-enthusiastic-peer-001"
  visual_direction:
    component_id: "visdir-lifestyle-natural-001"
    overrides:
      color_palette: "Soft pastels: blush pink, cream, lavender, with rose gold accents for {brand_name}"
  scenes:
    - component_id: "scene-problem-setup-001"
      overrides:
        scene_script: "Most people spend hours researching {product_category} that end up disappointing them."
    - component_id: "scene-solution-demo-001"
      overrides:
        scene_script: "That is where {product_name} changes everything."
    - component_id: "scene-cta-final-001"
      overrides:
        scene_script: "Try {product_name} today and see the difference."
  audio_mood:
    component_id: "audio-uplifting-mod-001"
  text_style:
    component_id: "text-kinetic-pop-001"
  transitions:
    - component_id: "transition-dissolve-smooth-001"
    - component_id: "transition-dissolve-smooth-001"
```

---

## 3. Component Bindings

### 3.1 Reference Pattern

Compositions reference components by component_id. The composition file contains only the reference identifier and any overrides -- never the full content of a component. At generation time, the workflow resolves each component_id against the component library (Layer 1), retrieves the full component definition, merges any overrides, and produces the expanded output.

**Reference, not duplication:**

```yaml
# CORRECT: Reference by component_id
opening_hook:
  component_id: "hook-dramatic-reveal-001"
  overrides:
    hook_script: "Custom script for this campaign"

# INCORRECT: Inlining component content
opening_hook:
  component_type: "hook"
  hook_style: "dramatic_reveal"
  hook_script: "Custom script for this campaign"
  visual_cue: "Some visual"
  energy_level: "high"
```

### 3.2 Singleton Bindings

A singleton binding binds exactly one component to a binding slot. The binding value is a single object with component_id and optional overrides. Singleton bindings are used for components that apply globally to the entire manuscript.

**Singleton binding structure:**

```yaml
binding_name:
  component_id: "referenced-component-id"
  overrides:
    property_name: "override value"
```

**Domain singleton bindings:**

| Binding Name | Expected component_type | Required/Optional | Description |
|---|---|---|---|
| opening_hook | hook | Required | The opening sequence. Exactly one hook component per composition. |
| voice_style | voice_style | Required | The voiceover direction. Applies globally across all scenes. |
| visual_direction | visual_direction | Required | The overall visual treatment. Applies globally to all scenes. |
| audio_mood | audio_mood | Optional | The background music direction. Applies globally to the audio mix. May be omitted for silent or music-free campaigns. |
| text_style | text_style | Optional | The on-screen text treatment. Applies globally to all text overlays. May be omitted for campaigns without text overlays. |

**Example singleton binding:**

```yaml
opening_hook:
  component_id: "hook-dramatic-reveal-001"
  overrides:
    hook_script: "What if everything you knew about {product_category} was wrong?"
    energy_level: "high"
```

### 3.3 Ordered List Bindings

An ordered list binding binds multiple components in sequence. The binding value is a YAML array, where each element contains a component_id and optional overrides. The position in the array determines the rendering order in the output.

**Ordered list binding structure:**

```yaml
binding_name:
  - component_id: "first-component-id"
    overrides: { ... }
  - component_id: "second-component-id"
    overrides: { ... }
  - component_id: "third-component-id"
    # No overrides -- use component as-is
```

**Domain ordered list bindings:**

| Binding Name | Expected component_type | Required/Optional | Description |
|---|---|---|---|
| scenes | scene | Required | The content segments in narrative order. A composition must contain between 3 and 8 scenes. Position in the array determines viewing sequence. |
| transitions | transition | Optional | The visual transitions between consecutive scenes. When present, the array must contain exactly (N-1) entries where N is the number of scenes. Each transition[i] applies between scenes[i] and scenes[i+1]. If omitted, default cut transitions are assumed. |

**Example ordered list binding:**

```yaml
scenes:
  - component_id: "scene-problem-setup-001"
    overrides:
      scene_script: "Most people spend hours researching {product_category} that end up disappointing them."
  - component_id: "scene-solution-demo-001"
    overrides:
      scene_script: "That is where {product_name} changes everything."
      duration_target: 15
  - component_id: "scene-social-proof-001"
    # No overrides -- use component defaults
  - component_id: "scene-cta-final-001"
    overrides:
      scene_script: "Try {product_name} today at {call_to_action_url}."
```

### 3.4 Required vs Optional Bindings

The domain defines which bindings are required and which are optional. Required bindings must always be present in every composition. Optional bindings may be omitted if they are not needed for a particular deliverable.

**Binding requirement matrix:**

| Binding Name | Binding Mode | Required/Optional | Omission Behavior |
|---|---|---|---|
| opening_hook | singleton | Required | CRITICAL validation error if missing. |
| voice_style | singleton | Required | CRITICAL validation error if missing. |
| visual_direction | singleton | Required | CRITICAL validation error if missing. |
| audio_mood | singleton | Optional | No error. Audio direction section omitted from output. |
| text_style | singleton | Optional | No error. Text overlay section omitted from output. |
| scenes | ordered_list | Required | CRITICAL validation error if missing. Must contain 3-8 items. |
| transitions | ordered_list | Optional | No error. Default cut transitions assumed between scenes. |

**Validation behavior:**

- **Missing required binding:** The composition fails validation with a CRITICAL error. The error message names the missing binding and the composition_id.
- **Missing optional binding:** No error. The composition is valid. The corresponding section is simply not included in the resolved output.
- **Present optional binding with invalid content:** If an optional binding is included, its component_id must exist and its overrides must conform to the component type schema. Invalid optional bindings are flagged as errors.

**Example composition omitting optional bindings:**

```yaml
composition_id: "comp-minimal-announcement-001"
name: "Quick Product Announcement"
target_metadata:
  duration_target: "20-30s"
  target_platforms: ["tiktok"]
  campaign_type: "announcement"
  brand: "Lumiere Skincare"

data_sources:
  product_master: "data/product_master/lumiere_serum.yaml"
  campaign_input: "data/campaign_input/quick_announce.yaml"

component_bindings:
  opening_hook:
    component_id: "hook-question-painpoint-001"
  voice_style:
    component_id: "voice-enthusiastic-peer-001"
  visual_direction:
    component_id: "visdir-lifestyle-natural-001"
  # audio_mood omitted -- no background music for this short announcement
  # text_style omitted -- no text overlays for this composition
  scenes:
    - component_id: "scene-problem-setup-001"
    - component_id: "scene-cta-final-001"
  # transitions omitted -- default cuts assumed
```

---

## 4. Override Mechanism

### 4.1 Override Purpose

Overrides allow per-composition customization of components without modifying the component itself. A component in the library represents a reusable creative template. Overrides let a composition adapt that template for a specific product, campaign, or audience while preserving the component's base creative DNA.

### 4.2 Override Structure

Overrides are specified as a key-value map under the `overrides` key within a binding entry:

```yaml
binding_name:
  component_id: "referenced-component-id"
  overrides:
    property_name: "override value"
    another_property: "another override value"
```

| Override Field | Type | Required | Description |
|---|---|---|---|
| overrides | object | No | A dictionary of property overrides. Keys must be valid property names for the referenced component's type. Values are the override values. If omitted or empty, the component is used as-is. |

### 4.3 Override Merge Rules

When the workflow resolves a composition, it merges overrides with the component's base properties using these rules:

1. **Override wins on conflict:** If a property appears in both the component's base definition and the composition's overrides, the override value is used.
2. **Non-overridden properties retained:** Properties not mentioned in overrides retain their component-defined values.
3. **Full replacement:** Override values replace the base value entirely. There is no deep merge for complex types. A string override replaces the entire string.

**Merge example:**

```yaml
# Component base (from library):
# hook_style: "dramatic_reveal"
# hook_script: "What if everything you knew about skincare was wrong?"
# visual_cue: "Product silhouette in darkness, single spotlight"
# energy_level: "high"

# Composition override:
opening_hook:
  component_id: "hook-dramatic-reveal-001"
  overrides:
    hook_script: "What if everything you knew about {product_category} was wrong?"

# Resolved result:
# hook_style: "dramatic_reveal"        (from component, not overridden)
# hook_script: "What if everything..."  (override wins)
# visual_cue: "Product silhouette..."   (from component, not overridden)
# energy_level: "high"                  (from component, not overridden)
```

### 4.4 Override Schema Conformance

Overrides must conform to the referenced component's type schema:

1. **Property existence:** Each override key must be a property defined in the component type's schema. An override cannot introduce properties that do not exist in the type definition.
2. **Data type conformance:** Override values must match the declared data type of the property. A string property must be overridden with a string. An enum property must be overridden with a valid enum value. A number property must be overridden with a number.
3. **Enum value conformance:** Enum properties can only be overridden with values from their valid value list.

**Valid override example:**

```yaml
# voice_style component type defines:
#   voice_tone: enum (authoritative, conversational, enthusiastic, empathetic, dramatic)
#   pace: enum (slow, moderate, fast, varied)
#   emphasis_pattern: string (optional)
#   voice_character: string (optional)

voice_style:
  component_id: "voice-enthusiastic-peer-001"
  overrides:
    voice_tone: "conversational"         # Valid -- "conversational" is in the enum
    emphasis_pattern: "Emphasize {key_benefit} and transformation language."
    # pace not overridden -- retains component's "moderate" value
```

**Invalid override examples:**

```yaml
# INVALID: "whisper" is not a valid voice_tone enum value
voice_style:
  component_id: "voice-enthusiastic-peer-001"
  overrides:
    voice_tone: "whisper"

# INVALID: "narration_speed" is not a property of voice_style type
voice_style:
  component_id: "voice-enthusiastic-peer-001"
  overrides:
    narration_speed: "fast"

# INVALID: voice_tone expects a string enum, not a number
voice_style:
  component_id: "voice-enthusiastic-peer-001"
  overrides:
    voice_tone: 3
```

### 4.5 Override Examples per Component Type

**Hook override (string property with placeholder):**

```yaml
opening_hook:
  component_id: "hook-dramatic-reveal-001"
  overrides:
    hook_script: "What if everything you knew about {product_category} was wrong?"
```

**Scene override (multiple properties):**

```yaml
scenes:
  - component_id: "scene-solution-demo-001"
    overrides:
      scene_script: "Introducing {product_name}, the {product_category} that actually delivers on its promises."
      visual_direction: "Close-up of {brand_name} product being applied to clean skin, morning light through window, warm and inviting"
      duration_target: 15
```

**Visual direction override (single property):**

```yaml
visual_direction:
  component_id: "visdir-lifestyle-natural-001"
  overrides:
    color_palette: "Soft pastels: blush pink, cream, lavender, with rose gold accents for {brand_name}"
```

**Transition override (enum and number):**

```yaml
transitions:
  - component_id: "transition-dissolve-smooth-001"
    overrides:
      transition_duration: 0.5
      transition_energy: "high"
```

---

## 5. Placeholder Resolution

### 5.1 Placeholder Syntax

Placeholders use the syntax `{placeholder_name}` -- curly braces around a field name. Placeholders can appear in:

- Override values within component_bindings
- Component property values in the component library itself

The workflow resolves all placeholders at generation time by looking up values from declared external data sources.

### 5.2 Data Sources

The video campaign manuscript domain defines three data sources for placeholder resolution:

#### 5.2.1 Product Master

The Product Master contains product-specific information. It is the primary data source for most placeholders.

| Placeholder | Type | Description | Example Value |
|---|---|---|---|
| {product_name} | string | The full product name. | "Lumiere Radiance Serum" |
| {product_category} | string | The product category or type. | "skincare" |
| {brand_name} | string | The brand name. | "Lumiere Skincare" |
| {key_benefit} | string | The primary product benefit or selling point. | "visible results in 7 days" |
| {pain_point} | string | The customer problem this product solves. | "dull, uneven skin tone" |
| {target_audience} | string | Description of the intended audience. | "women aged 25-40 seeking clean beauty" |
| {price_point} | string | The product price or price range. | "$48" |

#### 5.2.2 Platform Configuration

Platform Configuration contains platform-specific defaults and constraints.

| Placeholder | Type | Description | Example Value |
|---|---|---|---|
| {max_duration} | string | Maximum video duration for the target platform. | "60s" |
| {aspect_ratio} | string | Target aspect ratio for the platform. | "9:16" |
| {trending_sound_ref} | string | Reference to a trending sound for the platform. | "trending_audio_id_12345" |

#### 5.2.3 Campaign Input

Campaign Input contains campaign-specific values provided by the user or marketing team.

| Placeholder | Type | Description | Example Value |
|---|---|---|---|
| {campaign_name} | string | The campaign name or theme. | "Summer Glow Launch 2026" |
| {call_to_action_url} | string | The URL for the call to action. | "https://lumiere.shop/serum" |
| {seasonal_angle} | string | A seasonal or topical hook for the campaign. | "summer sun damage recovery" |

### 5.3 Resolution Process

The workflow resolves placeholders in this order:

1. **Identify all placeholders:** Scan all override values and resolved component property values for `{placeholder_name}` patterns.
2. **Build placeholder inventory:** Create a list of all unique placeholders found, noting where each appears.
3. **Load data sources:** Read the declared data source files (Product Master, Platform Configuration, Campaign Input).
4. **Resolve each placeholder:** For each `{placeholder_name}`, look up the value in the data sources. The first matching source provides the value.
5. **Replace:** Substitute the `{placeholder_name}` with the resolved value in the output.
6. **Flag unresolved:** Any placeholder that cannot be resolved from any declared data source is flagged as `{UNRESOLVED: placeholder_name}`.

### 5.4 Unresolved Placeholder Handling

When a placeholder cannot be resolved:

- The placeholder is NOT silently omitted or left as raw `{placeholder_name}`.
- It is replaced with `{UNRESOLVED: placeholder_name}` in the output.
- This flagging makes it immediately visible to reviewers that a data source value is missing.
- Outputs containing unresolved placeholders receive `lifecycle_status: "draft"` (not "final") until all placeholders are resolved.

**Resolution example:**

```yaml
# Composition overrides contain these placeholders:
opening_hook:
  component_id: "hook-dramatic-reveal-001"
  overrides:
    hook_script: "What if everything you knew about {product_category} was wrong?"

scenes:
  - component_id: "scene-solution-demo-001"
    overrides:
      scene_script: "Introducing {product_name}, proven to deliver {key_benefit}."

  - component_id: "scene-cta-final-001"
    overrides:
      scene_script: "Shop {product_name} now at {call_to_action_url}. Use code {promo_code} for 20% off."
```

**Resolution result (with sample data):**

```
# {product_category} -> "skincare" (from Product Master)
# {product_name} -> "Lumiere Radiance Serum" (from Product Master)
# {key_benefit} -> "visible results in 7 days" (from Product Master)
# {call_to_action_url} -> "https://lumiere.shop/serum" (from Campaign Input)
# {promo_code} -> {UNRESOLVED: promo_code} (no data source provides this value)

Resolved hook_script: "What if everything you knew about skincare was wrong?"
Resolved scene_script: "Introducing Lumiere Radiance Serum, proven to deliver visible results in 7 days."
Resolved CTA: "Shop Lumiere Radiance Serum now at https://lumiere.shop/serum. Use code {UNRESOLVED: promo_code} for 20% off."
```

### 5.5 Placeholder Resolution Summary

Every resolved output includes a placeholder resolution summary listing all placeholders encountered, their data source, and resolution status:

```
Placeholder Resolution Summary:
  {product_category}    -> "skincare"                   [RESOLVED from Product Master]
  {product_name}        -> "Lumiere Radiance Serum"     [RESOLVED from Product Master]
  {key_benefit}         -> "visible results in 7 days"  [RESOLVED from Product Master]
  {call_to_action_url}  -> "https://lumiere.shop/serum" [RESOLVED from Campaign Input]
  {promo_code}          -> {UNRESOLVED: promo_code}     [UNRESOLVED - no data source]
```

---

## 6. Ordering Rules

### 6.1 Singleton vs Ordered List Distinction

The domain defines which binding types are ordered lists and which are singletons. This distinction is a domain-level declaration, not inferred from the YAML structure.

| Binding Name | Binding Mode | Reasoning |
|---|---|---|
| opening_hook | Singleton | A video has exactly one opening. The hook is the first thing viewers see. |
| voice_style | Singleton | A video uses one consistent voiceover style throughout. Multiple voice styles would create tonal inconsistency. |
| visual_direction | Singleton | A video uses one visual treatment globally. Scene-level visual details are captured within each scene component's visual_direction property. |
| audio_mood | Singleton | A video uses one background music mood for the entire audio mix. |
| text_style | Singleton | A video uses one text treatment for all on-screen text. |
| scenes | Ordered list | A video contains multiple content segments in a specific narrative sequence. Order determines the viewer's experience flow (problem -> solution -> proof -> action). |
| transitions | Ordered list | Transitions occur between consecutive scene pairs. Each transition[i] bridges scenes[i] to scenes[i+1]. The order must match the scene order. |

### 6.2 Ordering Constraints

**For ordered list bindings:**

1. **Scene ordering:** Scenes are ordered by position in the YAML array. Scene[0] is the first content segment after the hook. Scene[N-1] is the last. The narrative flow should follow a logical progression (e.g., problem_setup before solution_demo before social_proof before call_to_action).
2. **Duration sum constraint:** The sum of all scene duration_target values (plus hook duration_range and transition durations) should approximate the composition's target_metadata.duration_target. Significant deviations should be flagged during review.
3. **Transition-scene alignment:** When transitions are present, the transitions array must contain exactly (N-1) entries where N is the number of scenes. transitions[0] applies between scenes[0] and scenes[1]. If the count does not match, the composition fails validation.
4. **Scene count constraint:** A composition must contain between 3 and 8 scenes. Fewer than 3 does not provide enough narrative depth. More than 8 exceeds typical short-form video duration limits.

**For singleton bindings:**

1. **Exactly one component:** A singleton binding must contain exactly one component reference. It cannot be an array. If a singleton binding contains a list, the composition fails validation.
2. **Type matching:** The referenced component's component_type must match the expected type for that binding slot.

### 6.3 Example: Ordered vs Singleton

```yaml
component_bindings:
  # SINGLETON: Exactly one component
  opening_hook:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_category} was wrong?"

  # SINGLETON: Exactly one component, no overrides
  voice_style:
    component_id: "voice-enthusiastic-peer-001"

  # ORDERED LIST: Multiple components in sequence
  scenes:
    - component_id: "scene-problem-setup-001"    # Position 0: problem
      overrides:
        scene_script: "Most people spend hours on {pain_point}."
    - component_id: "scene-solution-demo-001"    # Position 1: solution
      overrides:
        scene_script: "{product_name} delivers {key_benefit}."
    - component_id: "scene-social-proof-001"     # Position 2: proof
    - component_id: "scene-cta-final-001"        # Position 3: action
      overrides:
        scene_script: "Get {product_name} at {call_to_action_url}."

  # ORDERED LIST: Transitions align with scene boundaries
  # 4 scenes = 3 transitions (between 0-1, 1-2, 2-3)
  transitions:
    - component_id: "transition-dissolve-smooth-001"  # scene[0] -> scene[1]
    - component_id: "transition-match-cut-001"         # scene[1] -> scene[2]
      overrides:
        transition_duration: 0.5
    - component_id: "transition-dissolve-smooth-001"  # scene[2] -> scene[3]
```

---

## 7. Composition Validation

Every composition must pass the following validation checks before it can be resolved into an output.

### 7.1 Reference Integrity

| Rule ID | Condition | Expected Result | Error Severity |
|---|---|---|---|
| CF-VR-001 | Every component_id in every binding | Must exist in the component library | CRITICAL |
| CF-VR-002 | Referenced component's component_type | Must match the expected type for its binding slot | CRITICAL |

### 7.2 Override Conformance

| Rule ID | Condition | Expected Result | Error Severity |
|---|---|---|---|
| CF-VR-003 | Each override key | Must be a valid property for the referenced component's type | CRITICAL |
| CF-VR-004 | Override value data types | Must conform to the property's declared data type | CRITICAL |
| CF-VR-005 | Enum property overrides | Must use values from the property's valid value list | CRITICAL |

### 7.3 Required Bindings

| Rule ID | Condition | Expected Result | Error Severity |
|---|---|---|---|
| CF-VR-006 | opening_hook binding | Must be present with a valid component_id reference | CRITICAL |
| CF-VR-007 | voice_style binding | Must be present with a valid component_id reference | CRITICAL |
| CF-VR-008 | visual_direction binding | Must be present with a valid component_id reference | CRITICAL |
| CF-VR-009 | scenes binding | Must be present with 3-8 scene component references | CRITICAL |
| CF-VR-010 | audio_mood binding | Optional. If present, must contain a valid reference. | N/A (optional) |
| CF-VR-011 | text_style binding | Optional. If present, must contain a valid reference. | N/A (optional) |
| CF-VR-012 | transitions binding | Optional. If present, must have (N-1) entries for N scenes. | MAJOR if count mismatch |

### 7.4 Placeholder Resolvability

| Rule ID | Condition | Expected Result | Error Severity |
|---|---|---|---|
| CF-VR-013 | All {placeholder} values in overrides and resolved component values | Must be resolvable from declared data sources | MAJOR (flagged as {UNRESOLVED: field_name}) |
| CF-VR-014 | Data source declarations | Each declared data source file must exist and be readable | CRITICAL |

### 7.5 Ordering Constraints

| Rule ID | Condition | Expected Result | Error Severity |
|---|---|---|---|
| CF-VR-015 | scenes array length | Must be between 3 and 8 | CRITICAL |
| CF-VR-016 | transitions array length (if present) | Must equal (scenes count - 1) | MAJOR |
| CF-VR-017 | Singleton bindings | Must contain exactly one component reference, not an array | CRITICAL |
| CF-VR-018 | Scene duration sum | Sum of duration_target values should approximate target_metadata.duration_target | MINOR (warning) |

---

## 8. Example Compositions

### 8.1 Example 1: Full-Featured Product Launch Composition

This composition demonstrates all binding types (singleton, ordered list), overrides with placeholders, required and optional bindings, and full data source usage.

```yaml
composition_id: "comp-serum-full-launch-001"
name: "Lumiere Radiance Serum Full Launch Campaign"
target_metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"

data_sources:
  product_master: "data/product_master/lumiere_serum.yaml"
  platform_config: "data/platform_config/short_form_vertical.yaml"
  campaign_input: "data/campaign_input/summer_launch_2026.yaml"

component_bindings:
  # Singleton binding (required) - hook with override containing placeholder
  opening_hook:
    component_id: "hook-dramatic-reveal-001"
    overrides:
      hook_script: "What if everything you knew about {product_category} was wrong?"
      visual_cue: "Extreme close-up of {brand_name} serum bottle in darkness, single spotlight revealing golden liquid"

  # Singleton binding (required) - no overrides, use component as-is
  voice_style:
    component_id: "voice-enthusiastic-peer-001"

  # Singleton binding (required) - override color palette with placeholder
  visual_direction:
    component_id: "visdir-lifestyle-natural-001"
    overrides:
      color_palette: "Soft pastels: blush pink, cream, lavender, with rose gold accents for {brand_name}"
      camera_work: "Handheld close-ups of {brand_name} product application. Golden hour lighting. Show {target_audience} in natural settings."

  # Singleton binding (optional) - included for this composition
  audio_mood:
    component_id: "audio-uplifting-mod-001"
    overrides:
      volume_balance: "Music at 25% under voiceover, swell to 55% during transitions, peak at 65% during the final {key_benefit} reveal"

  # Singleton binding (optional) - included with overrides
  text_style:
    component_id: "text-kinetic-pop-001"
    overrides:
      text_color_scheme: "White text with soft pink drop shadow. Gold accent for {brand_name} and {product_name}. Semi-transparent cream bar behind lower thirds."

  # Ordered list binding (required) - 4 scenes with overrides
  scenes:
    - component_id: "scene-problem-setup-001"
      overrides:
        scene_script: "Most people spend hours researching {product_category} that never deliver. You read reviews, watch videos, and still end up disappointed."
        visual_direction: "Split screen: frustrated person scrolling phone, then close-up of discarded product bottles. Text overlay: 'Tired of {pain_point}?'"
        duration_target: 12

    - component_id: "scene-solution-demo-001"
      overrides:
        scene_script: "Introducing {product_name} from {brand_name}. It is the first {product_category} proven to deliver {key_benefit}."
        visual_direction: "Beauty shot of {brand_name} serum bottle rotating slowly. Hands applying serum to clean skin. Morning golden hour light through window."
        duration_target: 15

    - component_id: "scene-social-proof-001"
      overrides:
        scene_script: "Thousands of {target_audience} already made the switch. See real results in just one week."

    - component_id: "scene-cta-final-001"
      overrides:
        scene_script: "Get your {product_name} today at {call_to_action_url}. Your skin will thank you."
        visual_direction: "Product hero shot with {brand_name} logo. Clean background. Text overlay: 'Shop Now' with arrow pointing to link."
        duration_target: 10

  # Ordered list binding (optional) - 3 transitions for 4 scenes
  transitions:
    - component_id: "transition-dissolve-smooth-001"
      overrides:
        transition_duration: 0.8

    - component_id: "transition-match-cut-001"
      overrides:
        transition_duration: 0.5
        transition_energy: "medium"

    - component_id: "transition-dissolve-smooth-001"
      overrides:
        transition_duration: 1.0
        transition_energy: "low"
```

**Placeholder inventory for Example 1:**

| Placeholder | Source | Resolution |
|---|---|---|
| {product_category} | Product Master | RESOLVED: "skincare" |
| {brand_name} | Product Master | RESOLVED: "Lumiere Skincare" |
| {target_audience} | Product Master | RESOLVED: "women aged 25-40 seeking clean beauty" |
| {pain_point} | Product Master | RESOLVED: "dull, uneven skin tone" |
| {product_name} | Product Master | RESOLVED: "Lumiere Radiance Serum" |
| {key_benefit} | Product Master | RESOLVED: "visible results in 7 days" |
| {call_to_action_url} | Campaign Input | RESOLVED: "https://lumiere.shop/serum" |

All placeholders resolved. lifecycle_status: "final" is valid.

---

### 8.2 Example 2: Minimal Composition with Omitted Optional Bindings and Unresolved Placeholder

This composition demonstrates omission of optional bindings (audio_mood, text_style, transitions), and includes an unresolvable placeholder to show {UNRESOLVED: field_name} flagging.

```yaml
composition_id: "comp-quick-announce-002"
name: "Quick Product Announcement - Minimal"
target_metadata:
  duration_target: "20-30s"
  target_platforms: ["tiktok"]
  campaign_type: "announcement"
  brand: "Lumiere Skincare"

data_sources:
  product_master: "data/product_master/lumiere_serum.yaml"
  campaign_input: "data/campaign_input/quick_announce.yaml"

component_bindings:
  # Singleton binding (required)
  opening_hook:
    component_id: "hook-question-painpoint-001"
    overrides:
      hook_script: "Tired of {pain_point} that never goes away?"

  # Singleton binding (required) - use as-is
  voice_style:
    component_id: "voice-enthusiastic-peer-001"

  # Singleton binding (required) - use as-is
  visual_direction:
    component_id: "visdir-lifestyle-natural-001"

  # audio_mood OMITTED (optional) - no background music for this quick announcement
  # text_style OMITTED (optional) - no text overlays for this composition

  # Ordered list binding (required) - only 3 scenes for a short video
  scenes:
    - component_id: "scene-problem-setup-001"
      overrides:
        scene_script: "You have tried everything for {pain_point} but nothing works."
        duration_target: 8

    - component_id: "scene-product-intro-001"
      overrides:
        scene_script: "Now there is {product_name} -- {key_benefit}, guaranteed."
        duration_target: 10

    - component_id: "scene-cta-final-001"
      overrides:
        scene_script: "Grab yours at {call_to_action_url} with code {promo_code} for exclusive savings."
        duration_target: 7

  # transitions OMITTED (optional) - default cuts between scenes
```

**Placeholder inventory for Example 2:**

| Placeholder | Source | Resolution |
|---|---|---|
| {pain_point} | Product Master | RESOLVED: "dull, uneven skin tone" |
| {product_name} | Product Master | RESOLVED: "Lumiere Radiance Serum" |
| {key_benefit} | Product Master | RESOLVED: "visible results in 7 days" |
| {call_to_action_url} | Campaign Input | RESOLVED: "https://lumiere.shop/serum" |
| {promo_code} | -- | UNRESOLVED: no data source provides promo_code |

Because {promo_code} cannot be resolved, the resolved output contains:
```
"Grab yours at https://lumiere.shop/serum with code {UNRESOLVED: promo_code} for exclusive savings."
```

This composition receives `lifecycle_status: "draft"` until {promo_code} is provided by a data source.

---

### 8.3 Example 3: Multi-Platform Composition with Platform Configuration Placeholders

This composition demonstrates platform-specific placeholder resolution from the Platform Configuration data source.

```yaml
composition_id: "comp-reels-exclusive-003"
name: "Instagram Reels Exclusive Campaign"
target_metadata:
  duration_target: "30-45s"
  target_platforms: ["reels"]
  campaign_type: "brand_awareness"
  brand: "Lumiere Skincare"

data_sources:
  product_master: "data/product_master/lumiere_serum.yaml"
  platform_config: "data/platform_config/instagram_reels.yaml"
  campaign_input: "data/campaign_input/brand_awareness_q3.yaml"

component_bindings:
  opening_hook:
    component_id: "hook-visual-reveal-001"
    overrides:
      hook_script: "The secret to {key_benefit} is finally here."
      visual_cue: "Dramatic product reveal of {brand_name} serum with {aspect_ratio} framing optimized for Reels grid preview"

  voice_style:
    component_id: "voice-authoritative-expert-001"

  visual_direction:
    component_id: "visdir-cinematic-dramatic-001"
    overrides:
      aspect_ratio: "{aspect_ratio}"

  audio_mood:
    component_id: "audio-mysterious-slow-001"
    overrides:
      volume_balance: "Music at 35% under voiceover, referencing {trending_sound_ref} for Reels audio trends"

  text_style:
    component_id: "text-lower-thirds-001"

  scenes:
    - component_id: "scene-education-001"
      overrides:
        scene_script: "Dermatologists say {pain_point} affects millions. But the science behind {product_name} offers a new approach."
        duration_target: 15

    - component_id: "scene-solution-demo-001"
      overrides:
        scene_script: "{product_name} uses advanced formulation to deliver {key_benefit}."
        duration_target: 12

    - component_id: "scene-emotional-appeal-001"
      overrides:
        scene_script: "Imagine waking up every morning confident in your skin. That is what {brand_name} makes possible for {target_audience}."
        duration_target: 10

  transitions:
    - component_id: "transition-dissolve-smooth-001"
      overrides:
        transition_duration: 1.0

    - component_id: "transition-dissolve-smooth-001"
      overrides:
        transition_duration: 0.8
```

**Placeholder inventory for Example 3:**

| Placeholder | Source | Resolution |
|---|---|---|
| {key_benefit} | Product Master | RESOLVED: "visible results in 7 days" |
| {brand_name} | Product Master | RESOLVED: "Lumiere Skincare" |
| {pain_point} | Product Master | RESOLVED: "dull, uneven skin tone" |
| {product_name} | Product Master | RESOLVED: "Lumiere Radiance Serum" |
| {target_audience} | Product Master | RESOLVED: "women aged 25-40 seeking clean beauty" |
| {aspect_ratio} | Platform Config | RESOLVED: "9:16" |
| {trending_sound_ref} | Platform Config | RESOLVED: "trending_audio_reels_beauty_2026q3" |

All placeholders resolved. lifecycle_status: "final" is valid.

---

## 9. Self-Check: Criteria Coverage

This section verifies that all composition format requirements from TEST_CRITERIA-01.md Section 5 are covered by this document.

### 9.1 Cross-Reference Table

| Test Criteria ID | Requirement | Document Section | Status |
|---|---|---|---|
| TC-CF-001 | YAML structure with composition_id, name, target_metadata, component_bindings | Section 2 | SATISFIED |
| TC-CF-002 | Singleton and list binding modes | Section 3.2, 3.3 | SATISFIED |
| TC-CF-003 | component_id required, overrides optional | Section 3.1, 4.2 | SATISFIED |
| TC-CF-004 | Override YAML structure as key-value map | Section 4.2 | SATISFIED |
| TC-CF-005 | Components referenced by component_id, not copied | Section 3.1 | SATISFIED |
| TC-CF-006 | Resolution process defined | Section 5.3 | SATISFIED |
| TC-CF-007 | Example with 3+ component bindings referencing different IDs | Section 8.1 | SATISFIED |
| TC-CF-008 | Override merge semantics (override wins, non-overridden retained) | Section 4.3 | SATISFIED |
| TC-CF-009 | Overrides must conform to component type schema | Section 4.4 | SATISFIED |
| TC-CF-010 | Override example with placeholder | Section 8.1 | SATISFIED |
| TC-CF-011 | Placeholder syntax {placeholder_name} defined | Section 5.1 | SATISFIED |
| TC-CF-012 | Data sources identified with available fields | Section 5.2 | SATISFIED |
| TC-CF-013 | Unresolved placeholders flagged as {UNRESOLVED: field_name} | Section 5.4 | SATISFIED |
| TC-CF-014 | Example with 2+ resolved and 1 unresolved placeholder | Section 8.2 | SATISFIED |
| TC-CF-015 | Ordered vs singleton binding distinction | Section 6.1 | SATISFIED |
| TC-CF-016 | Ordering by YAML array position, ordering constraints | Section 6.2 | SATISFIED |
| TC-CF-017 | Explicit declaration of ordered vs singleton per domain | Section 6.1 | SATISFIED |
| TC-CF-018 | Required vs optional bindings defined | Section 3.4 | SATISFIED |
| TC-CF-019 | Validation behavior for missing required vs optional | Section 3.4 | SATISFIED |
| TC-CF-020 | Example with omitted optional binding | Section 8.2 | SATISFIED |
| TC-CF-021 | Self-check section covering all rules | Section 9 | SATISFIED |
| TC-CF-022 | Examples collectively exercise all features | Section 8.1, 8.2, 8.3 | SATISFIED |
| TC-CF-N01 | No inlining of component content | Section 3.1 | SATISFIED |
| TC-CF-N02 | No invented properties in overrides | Section 4.4 | SATISFIED |
| TC-CF-N03 | No silent placeholder ignoring | Section 5.4 | SATISFIED |

### 9.2 Feature Coverage by Examples

| Feature | Example 1 | Example 2 | Example 3 |
|---|---|---|---|
| Singleton required binding | opening_hook, voice_style, visual_direction | opening_hook, voice_style, visual_direction | opening_hook, voice_style, visual_direction |
| Singleton optional binding (included) | audio_mood, text_style | -- (omitted) | audio_mood, text_style |
| Singleton optional binding (omitted) | -- | audio_mood, text_style | -- |
| Ordered list binding (scenes) | 4 scenes with overrides | 3 scenes with overrides | 3 scenes with overrides |
| Ordered list binding (transitions) | 3 transitions | -- (omitted) | 2 transitions |
| Overrides with placeholders | Multiple placeholders | Multiple placeholders | Multiple placeholders |
| Unresolved placeholder flagging | -- (all resolved) | {promo_code} unresolved | -- (all resolved) |
| Platform config data source | -- | -- | {aspect_ratio}, {trending_sound_ref} |

### 9.3 Component Schema Alignment

All binding names in this format reference component types defined in COMPONENT_SCHEMA-01.md:

| Binding Name | Expected component_type | Schema Section | Status |
|---|---|---|---|
| opening_hook | hook | COMPONENT_SCHEMA-01.md Section 3.2 | ALIGNED |
| scenes | scene | COMPONENT_SCHEMA-01.md Section 3.3 | ALIGNED |
| voice_style | voice_style | COMPONENT_SCHEMA-01.md Section 3.4 | ALIGNED |
| visual_direction | visual_direction | COMPONENT_SCHEMA-01.md Section 3.5 | ALIGNED |
| audio_mood | audio_mood | COMPONENT_SCHEMA-01.md Section 3.6 | ALIGNED |
| text_style | text_style | COMPONENT_SCHEMA-01.md Section 3.7 | ALIGNED |
| transitions | transition | COMPONENT_SCHEMA-01.md Section 3.8 | ALIGNED |

### 9.4 Override Property Alignment

All override properties used in examples reference actual type-specific properties from COMPONENT_SCHEMA-01.md:

| Component Type | Override Properties Used | Schema Properties | Status |
|---|---|---|---|
| hook | hook_script, visual_cue, energy_level | hook_style, hook_script, visual_cue, energy_level | ALIGNED |
| scene | scene_script, visual_direction, duration_target | scene_purpose, scene_script, visual_direction, duration_target | ALIGNED |
| voice_style | voice_tone, emphasis_pattern | voice_tone, pace, emphasis_pattern, voice_character | ALIGNED |
| visual_direction | color_palette, camera_work, aspect_ratio | visual_style, color_palette, lighting_mood, camera_work, aspect_ratio | ALIGNED |
| audio_mood | volume_balance | mood, tempo, instrumentation, volume_balance | ALIGNED |
| text_style | text_color_scheme | text_treatment, font_style, text_animation, text_color_scheme | ALIGNED |
| transition | transition_duration, transition_energy | transition_type, transition_duration, transition_energy | ALIGNED |

No invented properties. All override keys trace to type-specific properties in the component schema.

---

**End of Composition Format**
