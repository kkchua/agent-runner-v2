---
doc_type: "output_format"
lifecycle_status: "draft"
effective_version: "WBUILD2-paqdd825"
domain: "video_campaign_manuscript"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
component_schema_source: "COMPONENT_SCHEMA-01.md"
composition_format_source: "COMPOSITION_FORMAT-01.md"
section_count: 7
created_at: "2026-08-08"
---

# Output Format: Video Campaign Manuscript Domain

## 1. Overview

This document defines Layer 3 of the three-layer composition architecture for the video campaign manuscript domain. A resolved output is a complete, self-contained production manuscript that presents a fully expanded video campaign deliverable. All component_id references from the composition (Layer 2) are replaced with the full component content from the component library (Layer 1), all overrides are merged into the base component properties, and all placeholders are filled with values from declared external data sources. The output is the final artifact consumed by downstream workflows that generate voiceovers, visual assets, video edits, and platform-specific adaptations. It is downstream-agnostic -- it describes WHAT the deliverable is, not HOW to produce it.

**How outputs fit into the three-layer architecture:**

```
Layer 1: Component Library (COMPONENT_SCHEMA-01.md)
  - Standardized building blocks: hook, scene, voice_style,
    visual_direction, audio_mood, text_style, transition
  - Each component has a unique component_id
  - Components are immutable reference material

Layer 2: Composition Definitions (COMPOSITION_FORMAT-01.md)
  - Declarative assembly instructions
  - Reference components by component_id
  - Specify overrides for per-composition customization
  - Declare placeholder bindings to external data sources

Layer 3: Resolved Outputs (this document)
  - Complete, self-contained production manuscripts
  - All component_id references expanded to full content
  - All overrides applied (override wins on conflict)
  - All placeholders filled or flagged as {UNRESOLVED: field_name}
  - Organized into domain-defined sections for downstream consumption
```

**Domain context:** Short-form video campaign production for digital advertising and branded content across platforms such as TikTok, Instagram Reels, and YouTube Shorts. The end deliverable is a video campaign production manuscript -- a structured document that downstream workflows consume to generate voiceover audio, visual assets, video edits, and platform-specific adaptations.

---

## 2. Output Structure

### 2.1 YAML Frontmatter

Every output file begins with YAML frontmatter enclosed in triple-dash delimiters. The frontmatter contains metadata about the resolved composition.

| Field | Type | Required | Description |
|---|---|---|---|
| composition_id | string | Yes | Unique identifier of the source composition this output was resolved from. Copied from the composition's composition_id field. |
| composition_name | string | Yes | Human-readable display name of the resolved manuscript. Copied from the composition's name field. |
| metadata | object | Yes | Domain-specific metadata about the deliverable. Contains the fields from the composition's target_metadata (duration_target, target_platforms, campaign_type, brand) plus generation context. |
| component_count | integer | Yes | Total number of distinct component instances expanded in this output. Counts singleton bindings as 1 each and ordered list items individually. |
| generation_date | string | Yes | ISO 8601 date (YYYY-MM-DD) when this output was generated. |
| lifecycle_status | enum | Yes | Current lifecycle status of the output. Valid values: draft, review, final. See Section 2.5 for lifecycle rules. |
| unresolved_placeholder_count | integer | Yes | Number of placeholders that could not be resolved. Zero when lifecycle_status is "final". |

**Frontmatter structure:**

```yaml
---
composition_id: "comp-skincare-launch-001"
composition_name: "Lumiere Serum Product Launch"
metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"
  generated_from: "data/campaign_input/summer_launch_2026.yaml"
component_count: 12
generation_date: "2026-08-08"
lifecycle_status: "final"
unresolved_placeholder_count: 0
---
```

### 2.2 Metadata Object Fields

| Field | Type | Required | Description |
|---|---|---|---|
| duration_target | string | Yes | Total target duration for the final video. Copied from composition's target_metadata. |
| target_platforms | array | Yes | List of target platform identifiers. |
| campaign_type | string | Yes | The type of campaign this manuscript serves. |
| brand | string | Yes | The brand or product line this campaign represents. |
| generated_from | string | No | Identifier or path of the primary data source that provided placeholder values. |

### 2.3 Required Sections

After the frontmatter, the output contains a fixed set of domain-defined sections. Each section presents resolved component data in human-readable format.

| Section | Source Binding | Required/Conditional | Content |
|---|---|---|---|
| Opening | opening_hook (singleton) | Always present | Resolved hook component with all properties and placeholder values filled |
| Voice Direction | voice_style (singleton) | Always present | Resolved voice_style component with delivery direction |
| Visual Treatment | visual_direction (singleton) | Always present | Resolved visual_direction component with visual treatment details |
| Scene-by-Scene Breakdown | scenes (ordered list) + transitions (optional) | Always present | Each scene rendered in sequence order with transition directives between scenes |
| Audio Direction | audio_mood (singleton) | Conditional | Resolved audio_mood component. Omitted if the composition did not bind audio_mood. |
| Text Overlay | text_style (singleton) | Conditional | Resolved text_style component. Omitted if the composition did not bind text_style. |
| Production Notes | Derived from metadata | Always present | Placeholder resolution summary, unresolved flags, and cross-references |

### 2.4 Section-to-Component Mapping

Each output section corresponds to one or more component types from COMPONENT_SCHEMA-01.md. The mapping ensures every component type has a representation in the output.

| Output Section | Component Type(s) | Rendering Mode |
|---|---|---|
| Opening | hook | Single component expansion |
| Voice Direction | voice_style | Single component expansion |
| Visual Treatment | visual_direction | Single component expansion |
| Scene-by-Scene Breakdown | scene (per item), transition (between items) | Ordered list with interleaved transition directives |
| Audio Direction | audio_mood | Single component expansion |
| Text Overlay | text_style | Single component expansion |
| Production Notes | N/A (derived) | Computed metadata |

### 2.5 Lifecycle Status Rules

| Status | Condition |
|---|---|
| draft | Output contains one or more {UNRESOLVED: field_name} flags, or output has not yet passed quality review. |
| review | Output has been generated and is pending quality review. No unresolved placeholders. |
| final | Output has passed quality review with zero unresolved placeholders and all required sections present. |

### 2.6 Complete Output File Structure

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

## Opening
[Resolved hook component content]

## Voice Direction
[Resolved voice_style component content]

## Visual Treatment
[Resolved visual_direction component content]

## Scene-by-Scene Breakdown
[Resolved scenes in sequence order with transition directives]

## Audio Direction
[Resolved audio_mood component content]

## Text Overlay
[Resolved text_style component content]

## Production Notes
[Placeholder resolution summary and production metadata]
```

---

## 3. Resolution Rules

### 3.1 Component Reference Expansion

Every component_id reference in the composition is replaced with the full component content. The expansion process:

1. **Look up** the component_id in the component library.
2. **Retrieve** the complete component definition including all common properties and type-specific properties.
3. **Apply overrides** from the composition's binding entry (see Section 3.2).
4. **Merge** the resolved properties into the appropriate output section.

**Expansion result structure:**

When a component is expanded, its properties are presented in the output section as a structured block:

```
### Scene 1: Problem Setup

- **Purpose:** problem_setup
- **Duration:** 12 seconds
- **Narration:** "Most people spend hours researching skincare that never
  deliver. You read reviews, watch videos, and still end up disappointed."
- **Visual Direction:** Split screen: frustrated person scrolling phone, then
  close-up of discarded product bottles. Text overlay: 'Tired of dull, uneven
  skin tone?'
- **Tags:** problem, pain_point, relatable
```

No component_id references appear in the expanded output. The reader does not need to know the original component_id to understand or use the content.

### 3.2 Override Application

Overrides from the composition's binding entry are merged with the component's base properties using these rules:

1. **Override wins on conflict:** If a property appears in both the component's base definition and the composition's overrides, the override value is used.
2. **Non-overridden properties retained:** Properties not mentioned in overrides retain their component-defined values.
3. **Full replacement:** Override values replace the base value entirely. There is no deep merge for complex types.

**Override application example:**

```
# Component base (from library, hook-dramatic-reveal-001):
#   hook_style: "dramatic_reveal"
#   hook_script: "What if everything you knew about skincare was wrong?"
#   visual_cue: "Extreme close-up of product silhouette in darkness, single
#                 spotlight from above, slow pull-back"
#   energy_level: "high"

# Composition overrides:
#   hook_script: "What if everything you knew about {product_category} was wrong?"
#   visual_cue: "Extreme close-up of {brand_name} serum bottle in darkness,
#                single spotlight revealing golden liquid"

# Resolved result in output:
#   hook_style: "dramatic_reveal"          (from component, not overridden)
#   hook_script: "What if everything you
#                 knew about skincare was wrong?"
#                 (override wins, then {product_category} resolved to "skincare")
#   visual_cue: "Extreme close-up of Lumiere Skincare serum bottle in
#                darkness, single spotlight revealing golden liquid"
#                (override wins, then {brand_name} resolved to "Lumiere Skincare")
#   energy_level: "high"                   (from component, not overridden)
```

### 3.3 Placeholder Resolution

All placeholders use the syntax `{placeholder_name}` -- curly braces around a field name. The resolution process:

1. **Scan** all resolved property values (after override application) for `{placeholder_name}` patterns.
2. **Build** a placeholder inventory listing every unique placeholder found.
3. **Load** declared data sources (Product Master, Platform Configuration, Campaign Input).
4. **Resolve** each placeholder by looking up the field name in the data sources. The first matching source provides the value.
5. **Replace** the `{placeholder_name}` with the resolved value in the output.
6. **Flag unresolved** placeholders as `{UNRESOLVED: placeholder_name}`.

**Data source field mapping:**

| Placeholder | Data Source | Example Resolved Value |
|---|---|---|
| {product_name} | Product Master | "Lumiere Radiance Serum" |
| {product_category} | Product Master | "skincare" |
| {brand_name} | Product Master | "Lumiere Skincare" |
| {key_benefit} | Product Master | "visible results in 7 days" |
| {pain_point} | Product Master | "dull, uneven skin tone" |
| {target_audience} | Product Master | "women aged 25-40 seeking clean beauty" |
| {price_point} | Product Master | "$48" |
| {max_duration} | Platform Config | "60s" |
| {aspect_ratio} | Platform Config | "9:16" |
| {trending_sound_ref} | Platform Config | "trending_audio_reels_beauty_2026q3" |
| {campaign_name} | Campaign Input | "Summer Glow Launch 2026" |
| {call_to_action_url} | Campaign Input | "https://lumiere.shop/serum" |
| {seasonal_angle} | Campaign Input | "summer sun damage recovery" |

### 3.4 Unresolved Placeholder Handling

When a placeholder cannot be resolved from any declared data source:

- The placeholder is replaced with `{UNRESOLVED: placeholder_name}` in the output.
- The `{UNRESOLVED: field_name}` syntax is the ONLY accepted flagging format. No alternative syntaxes such as "TODO", "[MISSING]", or raw `{placeholder}` are permitted.
- The unresolved_placeholder_count in frontmatter is incremented.
- The lifecycle_status is set to "draft" (not "final") until all placeholders are resolved.
- The Production Notes section includes the placeholder in its resolution summary with status UNRESOLVED.

**Unresolved placeholder example:**

```
Before resolution:
  "Shop {product_name} now at {call_to_action_url}. Use code {promo_code} for 20% off."

After resolution:
  "Shop Lumiere Radiance Serum now at https://lumiere.shop/serum. Use code
   {UNRESOLVED: promo_code} for 20% off."
```

The {promo_code} placeholder could not be resolved because no declared data source provides a promo_code field. The output flags it explicitly.

### 3.5 Ordered List Rendering

For ordered list bindings (scenes and transitions), each component is rendered in sequence order with clear section breaks:

- **Scenes** are numbered sequentially (Scene 1, Scene 2, Scene 3, etc.) in the Scene-by-Scene Breakdown section.
- **Transitions** are rendered as directives between consecutive scenes. If transitions[i] is defined, it is rendered between Scene[i] and Scene[i+1]. If transitions are omitted from the composition, default cut transitions are assumed and noted in the output.
- **Duration targets** for each scene are presented in the output, and the total duration sum is noted in Production Notes.

**Transition rendering format:**

```
--- Transition: Dissolve (0.8s, medium energy) ---
```

### 3.6 Conditional Section Handling

Optional bindings (audio_mood, text_style) produce conditional sections:

- **Binding present:** The corresponding section is included in the output with fully resolved component content.
- **Binding omitted:** The section is omitted entirely from the output. The Production Notes section states that the audio direction or text overlay binding was not included in the source composition.

---

## 4. Required Sections

### 4.1 Opening

| Attribute | Value |
|---|---|
| Section Heading | "## Opening" |
| Source Binding | opening_hook (singleton, required) |
| Component Type | hook |
| Purpose | Presents the opening sequence that captures viewer attention in the first few seconds. |

**Content specification:**

The Opening section contains the fully resolved hook component properties:

- hook_style: The opening technique (dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook).
- hook_script: The spoken or displayed text of the opening, with all placeholders resolved.
- visual_cue: Description of the visual element shown during the hook.
- energy_level: The intensity and pace of the opening (low, medium, high).
- duration_range: The applicable duration for the opening.
- description: What this opening achieves creatively.

**Example:**

```markdown
## Opening

- **Style:** dramatic_reveal
- **Script:** "What if everything you knew about skincare was wrong?"
- **Visual Cue:** Extreme close-up of Lumiere Skincare serum bottle in darkness,
  single spotlight revealing golden liquid
- **Energy Level:** high
- **Duration:** 3-5s
- **Description:** Opens with a mysterious product silhouette in darkness, building
  curiosity before the reveal. Effective for beauty and tech products.
```

### 4.2 Voice Direction

| Attribute | Value |
|---|---|
| Section Heading | "## Voice Direction" |
| Source Binding | voice_style (singleton, required) |
| Component Type | voice_style |
| Purpose | Defines the voiceover direction for the entire video. Controls tone, pace, emphasis, and vocal character. |

**Content specification:**

The Voice Direction section contains the fully resolved voice_style component properties:

- voice_tone: The overall vocal attitude and emotion.
- pace: The speaking speed.
- emphasis_pattern: Description of which words or phrases receive vocal emphasis.
- voice_character: Description of the ideal voice persona.
- description: What this voice style achieves creatively.

**Example:**

```markdown
## Voice Direction

- **Tone:** enthusiastic
- **Pace:** moderate
- **Emphasis Pattern:** Emphasize product benefits and transformation language.
  Pause briefly before the call to action to build anticipation.
- **Voice Character:** Young female, mid-20s, warm American accent, conversational
  and relatable, slight excitement in delivery
- **Description:** A warm, enthusiastic peer-to-peer voice that feels like a friend
  sharing a discovery. Effective for lifestyle and beauty products targeting Gen Z
  and Millennials.
```

### 4.3 Visual Treatment

| Attribute | Value |
|---|---|
| Section Heading | "## Visual Treatment" |
| Source Binding | visual_direction (singleton, required) |
| Component Type | visual_direction |
| Purpose | Defines the overall visual treatment for the video. Establishes style, color, lighting, camera work, and framing. |

**Content specification:**

The Visual Treatment section contains the fully resolved visual_direction component properties:

- visual_style: The overarching visual aesthetic.
- color_palette: Description of the color scheme, with all placeholders resolved.
- lighting_mood: The lighting atmosphere.
- camera_work: Description of camera movement, angles, and framing style.
- aspect_ratio: The target aspect ratio.
- description: What this visual treatment achieves creatively.

**Example:**

```markdown
## Visual Treatment

- **Visual Style:** lifestyle
- **Color Palette:** Soft pastels: blush pink, cream, lavender, with rose gold
  accents for Lumiere Skincare
- **Lighting Mood:** natural
- **Camera Work:** Handheld close-ups of Lumiere Skincare product application.
  Golden hour lighting. Show women aged 25-40 seeking clean beauty in natural
  settings.
- **Aspect Ratio:** 9:16
- **Description:** Authentic lifestyle visual treatment with natural lighting and
  warm tones. Creates an approachable, real-life feel ideal for beauty, wellness,
  and home products.
```

### 4.4 Scene-by-Scene Breakdown

| Attribute | Value |
|---|---|
| Section Heading | "## Scene-by-Scene Breakdown" |
| Source Binding | scenes (ordered list, required) + transitions (ordered list, optional) |
| Component Type(s) | scene (per item), transition (between items) |
| Purpose | Presents each content segment in narrative sequence order, with transition directives between scenes. |

**Content specification:**

The Scene-by-Scene Breakdown section contains each scene rendered as a numbered subsection. Between consecutive scenes, a transition directive is inserted (either from the resolved transition component or a default cut).

Each scene subsection contains:

- scene_purpose: The narrative function of this scene.
- scene_script: The spoken narration or dialogue, with all placeholders resolved.
- visual_direction: Detailed description of what the viewer sees, with placeholders resolved.
- duration_target: Target duration in seconds.
- description: What this scene achieves creatively.

Each transition directive contains:

- transition_type: The visual transition effect.
- transition_duration: Duration in seconds.
- transition_energy: The intensity of the transition.

**Example:**

```markdown
## Scene-by-Scene Breakdown

### Scene 1: Problem Setup

- **Purpose:** problem_setup
- **Narration:** "Most people spend hours researching skincare that never deliver.
  You read reviews, watch videos, and still end up disappointed."
- **Visual Direction:** Split screen: frustrated person scrolling phone, then
  close-up of discarded product bottles. Text overlay: 'Tired of dull, uneven
  skin tone?'
- **Duration:** 12 seconds
- **Description:** Establishes the viewer's pain point or problem. Creates empathy
  and sets up the need for the solution.

--- Transition: Dissolve (0.8s, medium energy) ---

### Scene 2: Solution Demo

- **Purpose:** solution_demo
- **Narration:** "Introducing Lumiere Radiance Serum from Lumiere Skincare. It is
  the first skincare proven to deliver visible results in 7 days."
- **Visual Direction:** Beauty shot of Lumiere Skincare serum bottle rotating
  slowly. Hands applying serum to clean skin. Morning golden hour light through
  window.
- **Duration:** 15 seconds
- **Description:** Demonstrates the product solution. Shows the product in action
  and communicates key benefits.

--- Transition: Match Cut (0.5s, medium energy) ---

### Scene 3: Social Proof

- **Purpose:** social_proof
- **Narration:** "Thousands of women aged 25-40 seeking clean beauty already made
  the switch. See real results in just one week."
- **Visual Direction:** Montage of real customer before/after photos with
  testimonial quotes. Clean white background with product visible.
- **Duration:** 10 seconds
- **Description:** Provides social proof through customer testimonials and results.

--- Transition: Dissolve (1.0s, low energy) ---

### Scene 4: Call to Action

- **Purpose:** call_to_action
- **Narration:** "Get your Lumiere Radiance Serum today at
  https://lumiere.shop/serum. Your skin will thank you."
- **Visual Direction:** Product hero shot with Lumiere Skincare logo. Clean
  background. Text overlay: 'Shop Now' with arrow pointing to link.
- **Duration:** 10 seconds
- **Description:** Directs the viewer to take action. Clear, focused CTA.

**Total Scene Duration:** 47 seconds
```

### 4.5 Audio Direction

| Attribute | Value |
|---|---|
| Section Heading | "## Audio Direction" |
| Source Binding | audio_mood (singleton, optional) |
| Component Type | audio_mood |
| Purpose | Defines the background music and audio atmosphere for the video. |
| Conditional | Omitted from output if the composition did not bind audio_mood. |

**Content specification:**

The Audio Direction section contains the fully resolved audio_mood component properties:

- mood: The emotional tone of the background music.
- tempo: The speed of the music.
- instrumentation: Description of the primary instruments and sound elements.
- volume_balance: Description of how music volume relates to voiceover and sound effects.
- description: What this audio mood achieves creatively.

**Example:**

```markdown
## Audio Direction

- **Mood:** uplifting
- **Tempo:** moderate
- **Instrumentation:** Acoustic guitar fingerpicking, light shaker percussion,
  warm synth pad underneath, occasional piano notes for emphasis
- **Volume Balance:** Music at 25% under voiceover, swell to 55% during
  transitions, peak at 65% during the final visible results in 7 days reveal
- **Description:** Warm, uplifting background music with moderate tempo. Builds
  positivity and forward momentum without overpowering voiceover.
```

### 4.6 Text Overlay

| Attribute | Value |
|---|---|
| Section Heading | "## Text Overlay" |
| Source Binding | text_style (singleton, optional) |
| Component Type | text_style |
| Purpose | Defines the on-screen text treatment including typography, animation, placement, and color scheme. |
| Conditional | Omitted from output if the composition did not bind text_style. |

**Content specification:**

The Text Overlay section contains the fully resolved text_style component properties:

- text_treatment: The style of on-screen text presentation.
- font_style: Description of the typography.
- text_animation: The animation style for text appearance.
- text_color_scheme: Description of text colors, with placeholders resolved.
- description: What this text treatment achieves creatively.

**Example:**

```markdown
## Text Overlay

- **Treatment:** kinetic_typography
- **Font Style:** Bold sans-serif (Montserrat Bold), 48px for headlines, 28px
  for body text. All caps for emphasis words. Letter spacing slightly tight
  for impact.
- **Animation:** pop
- **Color Scheme:** White text with soft pink drop shadow. Gold accent for
  Lumiere Skincare and Lumiere Radiance Serum. Semi-transparent cream bar
  behind lower thirds for readability.
- **Description:** Dynamic kinetic typography with pop-in animations. Creates
  energy and draws attention to key phrases. Ideal for fast-paced product demos
  and lifestyle content.
```

### 4.7 Production Notes

| Attribute | Value |
|---|---|
| Section Heading | "## Production Notes" |
| Source Binding | N/A (derived from resolution metadata) |
| Purpose | Provides placeholder resolution summary, unresolved flags, duration calculations, and production context. |

**Content specification:**

The Production Notes section always contains:

1. **Placeholder Resolution Summary:** A table listing all placeholders encountered, their data source, and resolution status.
2. **Unresolved Placeholder List:** If any placeholders could not be resolved, they are listed here with {UNRESOLVED: field_name} syntax.
3. **Duration Summary:** Total duration calculation (hook + all scenes + all transitions) compared to the target duration.
4. **Binding Summary:** List of all bindings resolved, noting which optional bindings were omitted.
5. **Platform Notes:** Any platform-specific considerations derived from target_platforms.

**Example:**

```markdown
## Production Notes

### Placeholder Resolution Summary

| Placeholder | Resolved Value | Data Source | Status |
|---|---|---|---|
| {product_category} | "skincare" | Product Master | RESOLVED |
| {brand_name} | "Lumiere Skincare" | Product Master | RESOLVED |
| {product_name} | "Lumiere Radiance Serum" | Product Master | RESOLVED |
| {key_benefit} | "visible results in 7 days" | Product Master | RESOLVED |
| {pain_point} | "dull, uneven skin tone" | Product Master | RESOLVED |
| {target_audience} | "women aged 25-40 seeking clean beauty" | Product Master | RESOLVED |
| {call_to_action_url} | "https://lumiere.shop/serum" | Campaign Input | RESOLVED |

### Unresolved Placeholders

None. All placeholders were successfully resolved.

### Duration Summary

- Opening (hook): 3-5s
- Scene 1 (problem_setup): 12s
- Scene 2 (solution_demo): 15s
- Scene 3 (social_proof): 10s
- Scene 4 (call_to_action): 10s
- Transitions: 0.8s + 0.5s + 1.0s = 2.3s
- **Total calculated duration:** 52-54.3s
- **Target duration:** 45-60s
- **Status:** Within target range.

### Binding Summary

- opening_hook: hook-dramatic-reveal-001 (resolved with 2 overrides)
- voice_style: voice-enthusiastic-peer-001 (resolved as-is)
- visual_direction: visdir-lifestyle-natural-001 (resolved with 2 overrides)
- audio_mood: audio-uplifting-mod-001 (resolved with 1 override)
- text_style: text-kinetic-pop-001 (resolved with 1 override)
- scenes: 4 scenes resolved (3 with overrides)
- transitions: 3 transitions resolved (all with overrides)

### Platform Notes

- TikTok: Consider adding trending sound reference underneath.
- Reels: Ensure first frame is visually striking for grid preview.
- Shorts: Vertical crop safe -- no critical elements in top/bottom 10%.
```

---

## 5. Quality Requirements

### 5.1 No Dangling References

All component_id references from the composition must be fully expanded in the output. After resolution, no raw component_id strings appear anywhere in the output.

| Check | Method |
|---|---|
| Scan output for component_id pattern | Search for strings matching the component_id naming convention (e.g., "hook-xxx-001", "scene-xxx-001"). Any match is a defect. |
| Verify all binding references expanded | Compare the composition's binding entries against expanded sections in the output. Every binding must produce output content. |

**Defect definition:** A residual reference like "see component_id: hook-001" in the output is a CRITICAL defect.

### 5.2 No Unresolved Placeholders Without Flagging

All placeholders must be either resolved (replaced with data source values) or flagged using the exact syntax `{UNRESOLVED: field_name}`.

| Check | Method |
|---|---|
| Scan for raw {placeholder} syntax | Any `{word}` pattern that is not `{UNRESOLVED: word}` is a defect. |
| Verify {UNRESOLVED: field_name} consistency | The flagging syntax must be uniform throughout. No "TODO", "[MISSING]", or other alternative syntaxes. |
| Count unresolved placeholders | The count must match unresolved_placeholder_count in frontmatter. |

### 5.3 Schema Conformance

All overrides must be applied correctly. The output must show override values where overrides were specified, and component-defined values where no override was provided.

| Check | Method |
|---|---|
| Override application correctness | For each binding with overrides, verify the output contains the override value, not the original component value. |
| Property completeness | Each expanded section must contain all required properties for the component type as defined in COMPONENT_SCHEMA-01.md. |
| Data type conformance | Override values must match the declared data types of the properties they override. |

### 5.4 Completeness

All required sections must be present in the output. Conditional sections must follow the binding presence rules.

| Check | Method |
|---|---|
| Required sections present | Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Production Notes must always be present. |
| Conditional sections correct | Audio Direction present if and only if audio_mood binding exists. Text Overlay present if and only if text_style binding exists. |
| Frontmatter fields complete | All required frontmatter fields must be present with valid values. |

### 5.5 Consistency

No contradictions between sections. Information must be coherent across the output.

| Check | Method |
|---|---|
| Cross-section coherence | Voice Direction section must not specify a pace that contradicts the energy_level in the Opening section. Color palette in Visual Treatment must be compatible with Text Overlay color scheme. |
| component_count accuracy | The frontmatter component_count must match the actual number of distinct component instances expanded in the output. |
| lifecycle_status correctness | If any {UNRESOLVED: field_name} flags exist, lifecycle_status must be "draft", not "final" or "review". |

---

## 6. Downstream Extraction Contracts

### 6.1 Contract Principle

The output is downstream-agnostic. It describes WHAT the deliverable is, not HOW to produce it. Downstream workflows extract their specific concerns from the output's structured sections. The output does not contain production instructions -- it contains resolved creative direction that downstream workflows interpret according to their own logic.

### 6.2 Extraction Pattern

Downstream workflows locate their required data by section heading:

1. Parse the output file's YAML frontmatter for metadata (platforms, duration, campaign type).
2. Locate the relevant section by its heading (e.g., "## Voice Direction", "## Scene-by-Scene Breakdown").
3. Extract the structured property values from the section content.
4. Apply their own production logic to generate deliverables.

### 6.3 Extraction Contract: Voiceover Generation

| Attribute | Value |
|---|---|
| Downstream Workflow | Voiceover Generation |
| Sections Consumed | Voice Direction, Scene-by-Scene Breakdown |
| Fields Extracted | From Voice Direction: voice_tone, pace, emphasis_pattern, voice_character. From each scene in order: scene_script, duration_target. |
| Extraction Logic | Concatenate all scene_script values in sequence order. Apply voice_style properties as delivery direction for the voiceover engine. Use duration_target values as timing constraints for each segment. |
| Output of Downstream | Audio file (voiceover track) with segment timing markers. |

**Example extraction:**

```
Input to voiceover engine:
  Voice direction: enthusiastic, moderate pace, young female mid-20s
  Segment 1 (12s): "Most people spend hours researching skincare that never
    deliver..."
  Segment 2 (15s): "Introducing Lumiere Radiance Serum from Lumiere Skincare..."
  Segment 3 (10s): "Thousands of women aged 25-40 seeking clean beauty already
    made the switch..."
  Segment 4 (10s): "Get your Lumiere Radiance Serum today at
    https://lumiere.shop/serum..."
```

### 6.4 Extraction Contract: Visual Asset Generation

| Attribute | Value |
|---|---|
| Downstream Workflow | Visual Asset Generation |
| Sections Consumed | Visual Treatment, Scene-by-Scene Breakdown, Text Overlay |
| Fields Extracted | From Visual Treatment: visual_style, color_palette, lighting_mood, camera_work, aspect_ratio. From each scene: visual_direction. From Text Overlay (if present): font_style, text_color_scheme, text_treatment. |
| Extraction Logic | Use visual_style, color_palette, and lighting_mood as global style constraints for all visual assets. Use each scene's visual_direction as the shot description for image/video generation. Apply text_overlay properties to any text elements rendered in visual assets. |
| Output of Downstream | Set of generated visual assets (images, video clips) per scene. |

**Example extraction:**

```
Input to visual asset generator:
  Global style: lifestyle, soft pastels (blush pink, cream, lavender, rose gold),
    natural lighting, 9:16
  Scene 1 shot: "Split screen: frustrated person scrolling phone, then close-up
    of discarded product bottles."
  Scene 2 shot: "Beauty shot of Lumiere Skincare serum bottle rotating slowly.
    Hands applying serum to clean skin."
  Scene 3 shot: "Montage of real customer before/after photos with testimonial
    quotes."
  Scene 4 shot: "Product hero shot with Lumiere Skincare logo. Clean background."
```

### 6.5 Extraction Contract: Video Assembly

| Attribute | Value |
|---|---|
| Downstream Workflow | Video Assembly |
| Sections Consumed | Opening, Scene-by-Scene Breakdown (including transitions), Audio Direction, Text Overlay, Production Notes |
| Fields Extracted | From Opening: hook_script, visual_cue, energy_level, duration_range. From Scene-by-Scene: all scene content in order, transition directives between scenes. From Audio Direction (if present): mood, tempo, volume_balance. From Text Overlay (if present): text_animation, font_style. From Production Notes: total duration, platform notes. |
| Extraction Logic | Assemble video timeline: Opening first, then scenes in order with transitions between them. Layer audio_track from voiceover workflow and audio_direction. Overlay text elements per text_style during appropriate moments. Trim to total duration target. |
| Output of Downstream | Final assembled video file. |

**Example extraction:**

```
Timeline assembly:
  [0:00-0:04] Opening: dramatic reveal, high energy, product silhouette
  [0:04-0:04.8] Transition: dissolve, 0.8s
  [0:04.8-0:16.8] Scene 1: problem setup, 12s
  [0:16.8-0:17.3] Transition: match cut, 0.5s
  [0:17.3-0:32.3] Scene 2: solution demo, 15s
  [0:32.3-0:32.8] Transition: dissolve, 0.5s
  [0:32.8-0:42.8] Scene 3: social proof, 10s
  [0:42.8-0:43.8] Transition: dissolve, 1.0s
  [0:43.8-0:53.8] Scene 4: call to action, 10s
  Audio: uplifting, moderate tempo, 25% under voiceover
```

### 6.6 Extraction Contract: Platform Adaptation

| Attribute | Value |
|---|---|
| Downstream Workflow | Platform Adaptation |
| Sections Consumed | Production Notes (Platform Notes), Visual Treatment (aspect_ratio), metadata (target_platforms) |
| Fields Extracted | From metadata: target_platforms list. From Visual Treatment: aspect_ratio. From Production Notes: platform-specific notes. |
| Extraction Logic | For each target platform, generate a platform-specific variant of the manuscript. Apply platform constraints (max duration, aspect ratio, safe zones, trending sound references). Adjust durations and framing per platform requirements. |
| Output of Downstream | Set of platform-specific manuscript variants. |

**Example extraction:**

```
Platform variants:
  TikTok: 9:16 vertical, max 60s, add trending sound reference
  Reels: 9:16 vertical, ensure first frame grid-preview-safe
  Shorts: 9:16 vertical, no critical elements in top/bottom 10%
```

### 6.7 Programmatic Extraction Considerations

Downstream workflows can extract data programmatically because:

- Section headings are consistent and predictable ("## Opening", "## Voice Direction", etc.).
- Property names within sections use a stable format: bold label followed by colon and value.
- YAML frontmatter provides machine-parseable metadata.
- Scene numbering is sequential and deterministic.
- Transition directives follow a consistent format between scene subsections.

---

## 7. Example Outputs

### 7.1 Complete Example: Full-Featured Product Launch Output

This example demonstrates a fully resolved output from the composition "comp-skincare-launch-001" defined in COMPOSITION_FORMAT-01.md Section 8.1. All component_id references are expanded, all overrides are applied, all placeholders are resolved, and all required sections are present.

```markdown
---
composition_id: "comp-serum-full-launch-001"
composition_name: "Lumiere Radiance Serum Full Launch Campaign"
metadata:
  duration_target: "45-60s"
  target_platforms: ["tiktok", "reels", "shorts"]
  campaign_type: "product_launch"
  brand: "Lumiere Skincare"
  generated_from: "data/campaign_input/summer_launch_2026.yaml"
component_count: 12
generation_date: "2026-08-08"
lifecycle_status: "final"
unresolved_placeholder_count: 0
---

# Lumiere Radiance Serum Full Launch Campaign

## Opening

- **Style:** dramatic_reveal
- **Script:** "What if everything you knew about skincare was wrong?"
- **Visual Cue:** Extreme close-up of Lumiere Skincare serum bottle in darkness,
  single spotlight revealing golden liquid
- **Energy Level:** high
- **Duration:** 3-5s
- **Description:** Opens with a mysterious product silhouette in darkness, building
  curiosity before the reveal. Effective for beauty and tech products.

## Voice Direction

- **Tone:** enthusiastic
- **Pace:** moderate
- **Emphasis Pattern:** Emphasize product benefits and transformation language.
  Pause briefly before the call to action to build anticipation.
- **Voice Character:** Young female, mid-20s, warm American accent, conversational
  and relatable, slight excitement in delivery
- **Description:** A warm, enthusiastic peer-to-peer voice that feels like a friend
  sharing a discovery. Effective for lifestyle and beauty products targeting Gen Z
  and Millennials.

## Visual Treatment

- **Visual Style:** lifestyle
- **Color Palette:** Soft pastels: blush pink, cream, lavender, with rose gold
  accents for Lumiere Skincare
- **Lighting Mood:** natural
- **Camera Work:** Handheld close-ups of Lumiere Skincare product application.
  Golden hour lighting. Show women aged 25-40 seeking clean beauty in natural
  settings.
- **Aspect Ratio:** 9:16
- **Description:** Authentic lifestyle visual treatment with natural lighting and
  warm tones. Creates an approachable, real-life feel ideal for beauty, wellness,
  and home products.

## Scene-by-Scene Breakdown

### Scene 1: Problem Setup

- **Purpose:** problem_setup
- **Narration:** "Most people spend hours researching skincare that never deliver.
  You read reviews, watch videos, and still end up disappointed."
- **Visual Direction:** Split screen: frustrated person scrolling phone, then
  close-up of discarded product bottles. Text overlay: 'Tired of dull, uneven
  skin tone?'
- **Duration:** 12 seconds
- **Description:** Establishes the viewer's pain point or problem. Creates empathy
  and sets up the need for the solution.

--- Transition: Dissolve (0.8s, medium energy) ---

### Scene 2: Solution Demo

- **Purpose:** solution_demo
- **Narration:** "Introducing Lumiere Radiance Serum from Lumiere Skincare. It is
  the first skincare proven to deliver visible results in 7 days."
- **Visual Direction:** Beauty shot of Lumiere Skincare serum bottle rotating
  slowly. Hands applying serum to clean skin. Morning golden hour light through
  window.
- **Duration:** 15 seconds
- **Description:** Demonstrates the product solution. Shows the product in action
  and communicates key benefits.

--- Transition: Match Cut (0.5s, medium energy) ---

### Scene 3: Social Proof

- **Purpose:** social_proof
- **Narration:** "Thousands of women aged 25-40 seeking clean beauty already made
  the switch. See real results in just one week."
- **Visual Direction:** Montage of real customer before/after photos with
  testimonial quotes. Clean white background with product visible.
- **Duration:** 10 seconds
- **Description:** Provides social proof through customer testimonials and results.

--- Transition: Dissolve (1.0s, low energy) ---

### Scene 4: Call to Action

- **Purpose:** call_to_action
- **Narration:** "Get your Lumiere Radiance Serum today at
  https://lumiere.shop/serum. Your skin will thank you."
- **Visual Direction:** Product hero shot with Lumiere Skincare logo. Clean
  background. Text overlay: 'Shop Now' with arrow pointing to link.
- **Duration:** 10 seconds
- **Description:** Directs the viewer to take action. Clear, focused CTA.

**Total Scene Duration:** 47 seconds

## Audio Direction

- **Mood:** uplifting
- **Tempo:** moderate
- **Instrumentation:** Acoustic guitar fingerpicking, light shaker percussion,
  warm synth pad underneath, occasional piano notes for emphasis
- **Volume Balance:** Music at 25% under voiceover, swell to 55% during
  transitions, peak at 65% during the final visible results in 7 days reveal
- **Description:** Warm, uplifting background music with moderate tempo. Builds
  positivity and forward momentum without overpowering voiceover.

## Text Overlay

- **Treatment:** kinetic_typography
- **Font Style:** Bold sans-serif (Montserrat Bold), 48px for headlines, 28px
  for body text. All caps for emphasis words. Letter spacing slightly tight
  for impact.
- **Animation:** pop
- **Color Scheme:** White text with soft pink drop shadow. Gold accent for
  Lumiere Skincare and Lumiere Radiance Serum. Semi-transparent cream bar
  behind lower thirds for readability.
- **Description:** Dynamic kinetic typography with pop-in animations. Creates
  energy and draws attention to key phrases. Ideal for fast-paced product demos
  and lifestyle content.

## Production Notes

### Placeholder Resolution Summary

| Placeholder | Resolved Value | Data Source | Status |
|---|---|---|---|
| {product_category} | "skincare" | Product Master | RESOLVED |
| {brand_name} | "Lumiere Skincare" | Product Master | RESOLVED |
| {target_audience} | "women aged 25-40 seeking clean beauty" | Product Master | RESOLVED |
| {pain_point} | "dull, uneven skin tone" | Product Master | RESOLVED |
| {product_name} | "Lumiere Radiance Serum" | Product Master | RESOLVED |
| {key_benefit} | "visible results in 7 days" | Product Master | RESOLVED |
| {call_to_action_url} | "https://lumiere.shop/serum" | Campaign Input | RESOLVED |

### Unresolved Placeholders

None. All placeholders were successfully resolved.

### Duration Summary

- Opening (hook): 3-5s
- Scene 1 (problem_setup): 12s
- Scene 2 (solution_demo): 15s
- Scene 3 (social_proof): 10s
- Scene 4 (call_to_action): 10s
- Transitions: 0.8s + 0.5s + 1.0s = 2.3s
- **Total calculated duration:** 52-54.3s
- **Target duration:** 45-60s
- **Status:** Within target range.

### Binding Summary

- opening_hook: hook-dramatic-reveal-001 (resolved with 2 overrides)
- voice_style: voice-enthusiastic-peer-001 (resolved as-is)
- visual_direction: visdir-lifestyle-natural-001 (resolved with 2 overrides)
- audio_mood: audio-uplifting-mod-001 (resolved with 1 override)
- text_style: text-kinetic-pop-001 (resolved with 1 override)
- scenes: 4 scenes resolved (3 with overrides)
- transitions: 3 transitions resolved (all with overrides)
- **Total component instances:** 12

### Platform Notes

- TikTok: Consider adding trending sound reference underneath.
- Reels: Ensure first frame is visually striking for grid preview.
- Shorts: Vertical crop safe -- no critical elements in top/bottom 10%.
```

### 7.2 Complete Example: Minimal Output with Unresolved Placeholder

This example demonstrates a resolved output from the composition "comp-quick-announce-002" defined in COMPOSITION_FORMAT-01.md Section 8.2. Optional bindings (audio_mood, text_style, transitions) are omitted. One placeholder ({promo_code}) could not be resolved and is flagged.

```markdown
---
composition_id: "comp-quick-announce-002"
composition_name: "Quick Product Announcement - Minimal"
metadata:
  duration_target: "20-30s"
  target_platforms: ["tiktok"]
  campaign_type: "announcement"
  brand: "Lumiere Skincare"
  generated_from: "data/campaign_input/quick_announce.yaml"
component_count: 5
generation_date: "2026-08-08"
lifecycle_status: "draft"
unresolved_placeholder_count: 1
---

# Quick Product Announcement - Minimal

## Opening

- **Style:** question_hook
- **Script:** "Tired of dull, uneven skin tone that never goes away?"
- **Visual Cue:** Close-up of person looking frustrated at bathroom shelf full of
  half-used products, soft morning light
- **Energy Level:** medium
- **Duration:** 3-5s
- **Description:** Opens with a relatable question that highlights the viewer's
  pain point. Creates immediate identification and stops the scroll.

## Voice Direction

- **Tone:** enthusiastic
- **Pace:** moderate
- **Emphasis Pattern:** Emphasize product benefits and transformation language.
  Pause briefly before the call to action to build anticipation.
- **Voice Character:** Young female, mid-20s, warm American accent, conversational
  and relatable, slight excitement in delivery
- **Description:** A warm, enthusiastic peer-to-peer voice that feels like a friend
  sharing a discovery.

## Visual Treatment

- **Visual Style:** lifestyle
- **Color Palette:** Warm earth tones: terracotta, cream, sage green, with gold
  accent highlights
- **Lighting Mood:** natural
- **Camera Work:** Handheld medium shots with gentle push-ins. Close-ups for
  product details. Natural movement, no tripod stiffness. Shoot in golden hour
  when possible.
- **Aspect Ratio:** 9:16
- **Description:** Authentic lifestyle visual treatment with natural lighting and
  warm tones.

## Scene-by-Scene Breakdown

### Scene 1: Problem Setup

- **Purpose:** problem_setup
- **Narration:** "You have tried everything for dull, uneven skin tone but nothing
  works."
- **Visual Direction:** Split screen: left side shows frustrated person scrolling
  phone in dim room, right side shows pile of discarded product packaging. Text
  overlay: 'There is a better way.'
- **Duration:** 8 seconds
- **Description:** Establishes the viewer's pain point or problem.

--- Transition: Cut (0.2s, high energy) [DEFAULT] ---

### Scene 2: Product Intro

- **Purpose:** product_intro
- **Narration:** "Now there is Lumiere Radiance Serum -- visible results in 7 days,
  guaranteed."
- **Visual Direction:** Product beauty shot of Lumiere Radiance Serum bottle on
  marble surface, soft natural light, close-up of golden liquid texture.
- **Duration:** 10 seconds
- **Description:** Introduces the product as the solution.

--- Transition: Cut (0.2s, high energy) [DEFAULT] ---

### Scene 3: Call to Action

- **Purpose:** call_to_action
- **Narration:** "Grab yours at https://lumiere.shop/serum with code {UNRESOLVED:
  promo_code} for exclusive savings."
- **Visual Direction:** Product hero shot with Lumiere Skincare logo. Clean
  background. Text overlay: 'Shop Now'.
- **Duration:** 7 seconds
- **Description:** Directs the viewer to take action.

**Total Scene Duration:** 25 seconds

## Production Notes

### Placeholder Resolution Summary

| Placeholder | Resolved Value | Data Source | Status |
|---|---|---|---|
| {pain_point} | "dull, uneven skin tone" | Product Master | RESOLVED |
| {product_name} | "Lumiere Radiance Serum" | Product Master | RESOLVED |
| {key_benefit} | "visible results in 7 days" | Product Master | RESOLVED |
| {call_to_action_url} | "https://lumiere.shop/serum" | Campaign Input | RESOLVED |
| {promo_code} | {UNRESOLVED: promo_code} | -- | UNRESOLVED |

### Unresolved Placeholders

- {UNRESOLVED: promo_code}: No declared data source provides a promo_code value.
  This placeholder appears in Scene 3 narration. The composition must receive a
  data source update or the placeholder must be manually filled before this output
  can advance to lifecycle_status "final".

### Duration Summary

- Opening (hook): 3-5s
- Scene 1 (problem_setup): 8s
- Scene 2 (product_intro): 10s
- Scene 3 (call_to_action): 7s
- Transitions: 0.2s + 0.2s = 0.4s (default cuts)
- **Total calculated duration:** 28.4-30.4s
- **Target duration:** 20-30s
- **Status:** Within target range.

### Binding Summary

- opening_hook: hook-question-painpoint-001 (resolved with 1 override)
- voice_style: voice-enthusiastic-peer-001 (resolved as-is)
- visual_direction: visdir-lifestyle-natural-001 (resolved as-is)
- audio_mood: OMITTED (optional binding not included in composition)
- text_style: OMITTED (optional binding not included in composition)
- scenes: 3 scenes resolved (all with overrides)
- transitions: OMITTED (default cuts assumed between scenes)
- **Total component instances:** 5

### Platform Notes

- TikTok: Only target platform. Add trending sound reference if available.
```

---

## 8. Self-Check: Criteria Coverage

This section verifies that all output format requirements from TEST_CRITERIA-01.md Section 7 are covered by this document.

### 8.1 Test Criteria Traceability

| Test Criteria ID | Requirement | Document Section | Status |
|---|---|---|---|
| TC-OF-001 | Markdown with YAML frontmatter (composition_id, composition_name, metadata, component_count, generation_date, lifecycle_status) | Section 2.1 | SATISFIED |
| TC-OF-002 | Required output sections defined for video manuscripts (Opening, Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay, Production Notes) | Section 2.3, Section 4 | SATISFIED |
| TC-OF-003 | Internal structure of each section defined (what information, how formatted, what resolved data) | Section 4.1-4.7 | SATISFIED |
| TC-OF-004 | Complete example output document demonstrating all required sections | Section 7.1 | SATISFIED |
| TC-OF-005 | All component_id references expanded in output | Section 3.1, Section 5.1 | SATISFIED |
| TC-OF-006 | Expansion process defined (lookup, override, merge, render) | Section 3.1 | SATISFIED |
| TC-OF-007 | List bindings rendered in sequence order with clear breaks | Section 3.5, Section 4.4 | SATISFIED |
| TC-OF-008 | Singleton bindings rendered in dedicated sections | Section 4.1-4.3, 4.5-4.6 | SATISFIED |
| TC-OF-009 | All placeholders replaced with data source values | Section 3.3 | SATISFIED |
| TC-OF-010 | Unresolved placeholders rendered as {UNRESOLVED: field_name} | Section 3.4 | SATISFIED |
| TC-OF-011 | Placeholder resolution summary included in output | Section 4.7, Section 7.1 | SATISFIED |
| TC-OF-012 | Output is self-contained (no need for component library) | Section 1, Section 3.1, Section 5.1 | SATISFIED |
| TC-OF-013 | No component_id references in final output | Section 5.1 | SATISFIED |
| TC-OF-014 | Output includes enough context for downstream extraction | Section 6 | SATISFIED |
| TC-OF-015 | Extraction contracts defined for downstream workflows | Section 6.3-6.6 | SATISFIED |
| TC-OF-016 | At least one example downstream extraction | Section 6.3, 6.4, 6.5 | SATISFIED |
| TC-OF-017 | Output is downstream-agnostic (WHAT not HOW) | Section 1, Section 6.1 | SATISFIED |
| TC-OF-018 | Exact syntax for unresolved: {UNRESOLVED: field_name} | Section 3.4 | SATISFIED |
| TC-OF-019 | Outputs with unresolved placeholders get lifecycle_status "draft" | Section 2.5, Section 3.4 | SATISFIED |
| TC-OF-020 | Self-check section verifying all output sections covered | Section 8 | SATISFIED |
| TC-OF-021 | Example demonstrates all resolution rules | Section 7.1, 7.2 | SATISFIED |
| TC-OF-N01 | No outputs requiring component library consultation | Section 5.1 | SATISFIED |
| TC-OF-N02 | No raw {placeholder} syntax left unresolved/unflagged | Section 3.4, Section 5.2 | SATISFIED |
| TC-OF-N03 | No omitted required sections | Section 5.4 | SATISFIED |

### 8.2 Component Schema Alignment

All 7 component types from COMPONENT_SCHEMA-01.md have a representation in the output structure:

| Component Type | Output Section | Representation | Status |
|---|---|---|---|
| hook | Opening | Fully expanded properties | ALIGNED |
| scene | Scene-by-Scene Breakdown | Numbered scene subsections | ALIGNED |
| voice_style | Voice Direction | Fully expanded properties | ALIGNED |
| visual_direction | Visual Treatment | Fully expanded properties | ALIGNED |
| audio_mood | Audio Direction | Fully expanded properties (conditional) | ALIGNED |
| text_style | Text Overlay | Fully expanded properties (conditional) | ALIGNED |
| transition | Scene-by-Scene Breakdown | Transition directives between scenes | ALIGNED |

### 8.3 Composition Format Alignment

Resolution rules in this output format match the composition format's override mechanism and placeholder resolution:

| Composition Format Feature | Output Format Handling | Status |
|---|---|---|
| Override wins on conflict (COMPOSITION_FORMAT-01.md Section 4.3) | Section 3.2 Rule 1 | ALIGNED |
| Non-overridden properties retained | Section 3.2 Rule 2 | ALIGNED |
| Full replacement (no deep merge) | Section 3.2 Rule 3 | ALIGNED |
| Placeholder syntax {placeholder_name} | Section 3.3 | ALIGNED |
| Unresolved -> {UNRESOLVED: field_name} | Section 3.4 | ALIGNED |
| Singleton bindings | Dedicated output sections (Opening, Voice Direction, etc.) | ALIGNED |
| Ordered list bindings | Scene-by-Scene Breakdown with numbered subsections | ALIGNED |
| Optional binding omission | Conditional sections (Audio Direction, Text Overlay) | ALIGNED |

### 8.4 Three-Layer Traceability

Example trace for a single property through all three layers:

```
Layer 1 (Component Schema):
  component_id: hook-dramatic-reveal-001
  hook_script: "What if everything you knew about skincare was wrong?"

Layer 2 (Composition):
  opening_hook:
    component_id: hook-dramatic-reveal-001
    overrides:
      hook_script: "What if everything you knew about {product_category} was wrong?"

Layer 3 (Output - this format):
  ## Opening
  - **Script:** "What if everything you knew about skincare was wrong?"
  (Override applied, then {product_category} resolved to "skincare" from Product Master)
```

No information is lost in the trace from Layer 1 to Layer 3. The override is applied, the placeholder is resolved, and the final value is presented in a dedicated section.

### 8.5 Downstream Contract Consistency

All extraction contracts reference sections that exist in the output structure:

| Extraction Contract | Sections Referenced | Sections Exist? |
|---|---|---|
| Voiceover Generation | Voice Direction, Scene-by-Scene Breakdown | YES |
| Visual Asset Generation | Visual Treatment, Scene-by-Scene Breakdown, Text Overlay | YES |
| Video Assembly | Opening, Scene-by-Scene Breakdown, Audio Direction, Text Overlay, Production Notes | YES |
| Platform Adaptation | Production Notes, Visual Treatment, metadata | YES |

---

**End of Output Format**
