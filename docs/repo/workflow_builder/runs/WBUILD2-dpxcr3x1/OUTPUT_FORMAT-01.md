---
doc_type: "output_format"
lifecycle_status: "draft"
effective_version: "WBUILD2-dpxcr3x1"
domain: "video_campaign_manuscript"
output_section_count: 7
source_spec: "video_campaign_manuscript_v2.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
component_schema: "COMPONENT_SCHEMA-01.md"
composition_format: "COMPOSITION_FORMAT-02.md"
created_at: "2026-08-08"
---

# Output Format: Video Campaign Manuscript Domain

## Overview

This document defines Layer 3 of the three-layer composition architecture for the video_campaign_manuscript domain. A resolved output is a complete, self-contained video production manuscript -- the final deliverable that results from expanding all component references, applying all overrides, and resolving all placeholders declared in a composition. Unlike compositions (Layer 2), which reference components by ID and contain no actual component content, outputs contain the full expanded content of every referenced component, merged with composition-specific customizations and enriched with data-source values. The output is consumed exclusively by downstream workflows (voiceover generation, visual asset creation, video editing, platform adaptation) and by human reviewers who must understand the complete creative direction without consulting the component library or the original composition file.

In the three-layer architecture, outputs occupy the top layer: they sit above the component library (Layer 1, which defines WHAT the building blocks are) and above the composition definitions (Layer 2, which define HOW components fit together). Outputs are the RESULT -- the assembled, production-ready manuscript that coordinates all creative concerns into a unified guide. The domain context is short-form video campaign production (15-90 seconds) for platforms including TikTok, Instagram Reels, and YouTube Shorts. Each output manuscript integrates seven creative concerns -- opening hook, content scenes, voice direction, visual treatment, audio mood, text overlays, and scene transitions -- into a single coherent document.

The output format follows the universal pattern defined in COMPOSITION_SYSTEM_STANDARD.md Section 5. The domain-specific structure (section names, content specifications, resolution details) is derived from video_campaign_manuscript_v2.md Section 4.

## Output Structure

The output is a markdown file with YAML frontmatter. The frontmatter carries metadata about the resolved deliverable; the markdown body presents the resolved components in a structured, human-readable format organized by creative concern.

### Frontmatter Fields

Every output file begins with YAML frontmatter delimited by `---` markers. The following table defines each frontmatter field.

| Field | Type | Required | Description |
|---|---|---|---|
| composition_id | string | Yes | The unique identifier from the source composition. Copied directly from the composition's composition_id field. Format: comp-{descriptor}-{seq}. |
| composition_name | string | Yes | The human-readable display name from the source composition. Copied from the composition's name field. Max 100 characters. |
| metadata | object | Yes | Domain-specific metadata copied from the composition's target_metadata. Contains: duration_target (string), target_platforms (array), campaign_type (string), brand (string). |
| component_count | integer | Yes | The total number of distinct components expanded in the output. Calculated as the sum of all component references across all bindings (singletons count as 1, list bindings count as their array length). |
| generation_date | string | Yes | The date this output was generated, in ISO 8601 format (YYYY-MM-DD). |
| lifecycle_status | enum | Yes | The maturity status of this output. Valid values: draft, review, final. An output with unresolved placeholders must be "draft". An output that has passed quality review but is not yet approved may be "review". An output that has passed all quality gates is "final". |
| unresolved_placeholder_count | integer | Yes | The number of placeholders that could not be resolved from the declared data sources. Must be 0 when lifecycle_status is "final". May be greater than 0 when lifecycle_status is "draft". |

### Required Sections

The markdown body must contain the following sections in the order listed. Each section corresponds to a binding slot from the composition format. The Text Overlay section is conditional: it appears only if the composition includes the text binding (which is optional per COMPOSITION_FORMAT-02.md).

| Section Heading | Source Binding | Component Type | Condition |
|---|---|---|---|
| Opening (Hook) | opening | hook | Always present (required binding) |
| Voice Direction | voice | voice_style | Always present (required binding) |
| Visual Treatment | visuals | visual_direction | Always present (required binding) |
| Scene-by-Scene Breakdown | scenes + transitions | scene + transition | Always present (required binding) |
| Audio Direction | audio | audio_mood | Always present (required binding) |
| Text Overlay | text | text_style | Present only if text binding exists in composition |
| Production Notes | Generated | N/A | Always present (generated section) |

### Internal Section Structure

Each section presents the resolved component's properties in a consistent format:

1. **Section heading** matching the table above.
2. **Component metadata** displayed as a property list: name, version, component_type, duration_range (if present), platforms, tags.
3. **Resolved properties** displayed as a property list, with all type-specific properties shown. Override values replace the original component values. Unresolved placeholders appear as {UNRESOLVED: field_name}.
4. **Usage notes** from the component's markdown body, if available.

For the Scene-by-Scene Breakdown, scenes and transitions are interleaved: Scene 1, Transition 1, Scene 2, Transition 2, ..., Scene N. Each scene is a numbered subsection (### Scene 1: {scene_purpose}). Transitions are rendered as italicized notes between scene subsections.

## Resolution Rules

The resolution process transforms a composition (Layer 2) into an output (Layer 3). The following rules govern how each transformation occurs.

### Component Reference Expansion

Every component_id reference in the composition is replaced with the full content of the referenced component. The expansion process is:

1. **Look up** the component_id in the component library. Retrieve the component's complete property set (all common properties and all type-specific properties for its declared component_type).
2. **Apply overrides** from the composition's binding entry (see Override Application below).
3. **Render** the fully resolved property set into the appropriate output section using the Internal Section Structure defined above.

After expansion, no component_id references remain in the output. The output is self-contained: a reader never needs to consult the component library to understand any section.

### Override Application

When a composition binding includes an overrides block, the override values are merged with the component's base properties. The merge follows these rules:

1. **Override wins on conflict.** If the composition overrides a property, the override value replaces the component's base value for that property.
2. **Non-overridden properties retain their base values.** Properties not mentioned in the overrides block keep their original values from the component.
3. **Overrides must conform to the component type schema.** An override key must be a valid type-specific property for the declared component_type. An override value must match the property's data type (string, enum) and respect enum value restrictions.

The output section for each component clearly shows the final resolved values. If a property was overridden, the output shows the override value. The output does not annotate which values were overridden versus which were inherited from the base component -- it presents only the final resolved state.

### Placeholder Resolution

Placeholders ({placeholder_name} tokens) appear in component property values and override values. They are resolved from the composition's declared data sources. The resolution process is:

1. **Collect data source values.** Read all data source files declared in the composition's data_sources section. Build a unified field map: Product Master fields (product_name, product_category, brand_name, key_benefit, pain_point, target_audience), Campaign Input fields (campaign_name, call_to_action_url, seasonal_angle, campaign_tagline), and Platform Config fields (platform_defaults, aspect_ratios, duration_limits, trending_formats).
2. **Apply priority rules.** When multiple data sources provide the same field name, priority order is: Product Master (highest), Campaign Input (second), Platform Config (lowest).
3. **Replace each placeholder.** For every {field_name} encountered in any property value, replace it with the value of field_name from the unified field map.
4. **Flag unresolved placeholders.** If a field_name does not exist in any declared data source, replace the raw {field_name} with {UNRESOLVED: field_name}. This ensures no raw placeholder syntax remains in the output.

### Unresolved Placeholder Handling

When a placeholder cannot be resolved:

1. **Syntax:** The placeholder is rendered as `{UNRESOLVED: field_name}` in the output text. This exact syntax is used consistently throughout the output. Alternative syntaxes such as "TODO", "[MISSING]", or raw {field_name} without the UNRESOLVED prefix are not permitted.
2. **Visibility:** The {UNRESOLVED: field_name} flag is immediately visible to reviewers in the context where the placeholder appears.
3. **Metadata impact:** Each unresolved placeholder increments the unresolved_placeholder_count in the frontmatter.
4. **Lifecycle impact:** Any output with one or more unresolved placeholders must have lifecycle_status set to "draft" (not "final" or "review"). The output becomes eligible for "final" status only after all placeholders are resolved.
5. **Production Notes:** The Production Notes section includes a placeholder resolution summary listing each placeholder encountered, its expected data source, and its resolution status (RESOLVED or UNRESOLVED).

### Scene-Transition Interleaving

The Scene-by-Scene Breakdown section interleaves scenes and transitions in narrative order. The rendering process is:

1. Number scenes sequentially: Scene 1, Scene 2, ..., Scene N (where N is the number of scenes in the composition's scenes binding).
2. Number transitions sequentially: Transition 1, Transition 2, ..., Transition N-1.
3. Render in order: Scene 1, Transition 1, Scene 2, Transition 2, ..., Transition N-1, Scene N.
4. Each scene is rendered as a subsection heading (### Scene {i}: {scene_purpose}).
5. Each transition is rendered as an italicized line between scene subsections: *Transition: {transition_type}, {transition_duration}, {transition_energy}*.

The constraint that transitions count = scenes count - 1 is enforced during the planning phase. By the time the output is generated, the interleaving order is deterministic.

### Example of Resolution

Given a composition that references hook-question-001 with an override on hook_script:

**Composition binding:**
```yaml
opening:
  component_id: "hook-question-001"
  overrides:
    hook_script: "What if your {product_category} routine was missing one key ingredient?"
```

**Component base (from library):**
```
component_id: "hook-question-001"
component_type: "hook"
name: "Skincare Question Hook"
version: "1.0.0"
duration_range: "3-5s"
hook_style: "question_hook"
hook_script: "What if your {product_category} routine was missing one key ingredient?"
visual_cue: "Close-up of hand applying serum, soft focus background with warm lighting"
energy_level: "high"
```

**Data source (Product Master):**
```yaml
product_category: "skincare serum"
```

**Resolved output (Opening section):**
```
## Opening (Hook)

- Name: Skincare Question Hook
- Version: 1.0.0
- Duration Range: 3-5s
- Hook Style: question_hook
- Hook Script: "What if your skincare serum routine was missing one key ingredient?"
- Visual Cue: "Close-up of hand applying serum, soft focus background with warm lighting"
- Energy Level: high
```

The {product_category} placeholder was resolved from the Product Master data source to "skincare serum". The hook_script in the output shows the fully resolved value.

## Required Sections

This section defines each required output section in detail. For each section: the name, purpose, content description, and an example.

### Opening (Hook)

**Purpose:** Presents the fully resolved opening sequence of the video manuscript. The hook is the first creative element the viewer experiences and sets the tone for the entire video.

**Content:** The expanded hook component with all common properties and type-specific properties (hook_style, hook_script, visual_cue, energy_level). All placeholders in hook_script are resolved. Overrides from the composition are applied.

**Example:**
```markdown
## Opening (Hook)

- Name: Skincare Question Hook
- Version: 1.0.0
- Duration Range: 3-5s
- Platforms: tiktok, reels, shorts
- Hook Style: question_hook
- Hook Script: "What if your skincare serum routine was missing one key ingredient?"
- Visual Cue: "Close-up of hand applying serum, soft focus background with warm lighting"
- Energy Level: high
```

### Voice Direction

**Purpose:** Presents the voiceover delivery direction for the entire manuscript. This section governs how the script sounds across all scenes.

**Content:** The expanded voice_style component with all common properties and type-specific properties (voice_tone, pace, emphasis_pattern, voice_character). Overrides from the composition are applied.

**Example:**
```markdown
## Voice Direction

- Name: Conversational Expert Voice
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Voice Tone: conversational
- Pace: moderate
- Emphasis Pattern: "Stress product benefit words and ingredient names. Pause briefly before the call-to-action to let the message land."
- Voice Character: "Friendly expert in their late 20s, like a knowledgeable friend who happens to work in skincare research."
```

### Visual Treatment

**Purpose:** Presents the overall visual treatment and aesthetic for the manuscript. This section governs the visual style across all scenes.

**Content:** The expanded visual_direction component with all common properties and type-specific properties (visual_style, color_palette, lighting_mood, camera_work, aspect_ratio). Overrides from the composition are applied.

**Example:**
```markdown
## Visual Treatment

- Name: Minimalist Warm Aesthetic
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Visual Style: minimalist
- Color Palette: "Warm neutrals with gold accents. Primary: #F5F0E8, Accent: #C5A572, Text: #2C2C2C"
- Lighting Mood: soft
- Camera Work: "Mostly static shots with occasional slow push-in movements. Clean backgrounds with shallow depth of field to isolate subject."
- Aspect Ratio: "9:16 vertical (safe crop for all platforms, no critical elements in top/bottom 10%)"
```

### Scene-by-Scene Breakdown

**Purpose:** Presents the narrative content of the manuscript as an ordered sequence of scenes, with transitions interleaved between consecutive scenes. This is the largest section and the core of the creative direction.

**Content:** Each scene is rendered as a numbered subsection (### Scene {i}: {scene_purpose}) containing the expanded scene component with all common properties and type-specific properties (scene_purpose, scene_script, visual_direction, duration_target, camera_work). All placeholders in scene_script are resolved. Transitions are rendered as italicized lines between scene subsections showing the expanded transition component properties (transition_type, transition_duration, transition_energy).

**Example:**
```markdown
## Scene-by-Scene Breakdown

### Scene 1: Problem

- Name: Problem Statement Scene
- Version: 1.0.0
- Duration Range: 8-12s
- Scene Purpose: problem
- Scene Script: "Most skincare serum products promise visible radiance in 7 days, but most ingredients cannot penetrate deep enough to make a real difference."
- Visual Direction: "Split-screen composition: left side shows frustrated customer examining skin in mirror, right side shows generic product bottles with red X marks"
- Duration Target: "8-12s"
- Camera Work: "Medium shot on customer, slow pan across product collection"

*Transition: match_cut, 0.5s, moderate*

### Scene 2: Solution

- Name: Solution Introduction Scene
- Version: 1.0.0
- Duration Range: 10-15s
- Scene Purpose: solution
- Scene Script: "Introducing Lumiere Radiance Serum -- formulated with a proprietary delivery system for real visible radiance in 7 days."
- Visual Direction: "Product hero shot with warm backlight, serum droplet catching light"
- Duration Target: "10-15s"

*Transition: fade, 0.8s, subtle*

### Scene 3: Call to Action

- Name: Call to Action Scene
- Version: 1.0.0
- Duration Range: 5-8s
- Scene Purpose: CTA
- Scene Script: "Try Lumiere Radiance Serum today. Link in bio."
- Visual Direction: "Product centered on screen with brand logo, warm background"
- Duration Target: "5-8s"
```

### Audio Direction

**Purpose:** Presents the background music and audio direction for the manuscript. This section governs the musical mood, tempo, instrumentation, and volume balance across the entire video.

**Content:** The expanded audio_mood component with all common properties and type-specific properties (mood, tempo, instrumentation, volume_balance). Overrides from the composition are applied.

**Example:**
```markdown
## Audio Direction

- Name: Uplifting Acoustic Mood
- Version: 1.0.0
- Duration Range: 45-60s
- Platforms: tiktok, reels, shorts
- Mood: uplifting
- Tempo: moderate
- Instrumentation: "Acoustic guitar arpeggios with light shaker percussion, subtle strings pad building through the narrative arc, gentle piano accent on the CTA moment"
- Volume Balance: "Music at 20% volume under voiceover, swell to 35% during transitions, peak to 45% on final product reveal, fade out gently after CTA"
```

### Text Overlay

**Purpose:** Presents the on-screen text treatment for the manuscript. This section governs how captions, titles, and callout text appear on screen. This section is CONDITIONAL: it appears only if the composition includes the text binding. If the composition omits the text binding, this entire section is omitted from the output.

**Content:** The expanded text_style component with all common properties and type-specific properties (text_treatment, font_style, text_animation, text_color_scheme). Overrides from the composition are applied.

**Example:**
```markdown
## Text Overlay

- Name: Clean Subtitle Treatment
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Text Treatment: subtitles
- Font Style: "Clean sans-serif (Montserrat or Poppins), medium weight for body, bold for product names and key benefits. Minimum 24px equivalent on mobile."
- Text Animation: fade
- Text Color Scheme: "White text (#FFFFFF) with subtle dark drop shadow for readability against any background. Product names highlighted in brand gold (#C5A572)."
```

### Production Notes

**Purpose:** A generated section that provides meta-information about the resolved manuscript. This section is always present, regardless of which bindings are included in the composition.

**Content:** The Production Notes section includes the following subsections:

1. **Timing Summary:** Total estimated duration calculated from scene duration_targets and transition durations. Indicates whether the total falls within the metadata.duration_target range.
2. **Platform Considerations:** Platform-specific notes for each platform listed in metadata.target_platforms, covering aspect ratio safety, duration limits, and trending format considerations.
3. **Placeholder Resolution Summary:** A complete inventory of all placeholders encountered during resolution. Each entry shows: placeholder field name, the data source where the value was found (or "not found"), and the resolution status (RESOLVED or UNRESOLVED).
4. **Component Summary:** A count of components per type expanded in the output, confirming the component_count in the frontmatter.

**Example:**
```markdown
## Production Notes

### Timing Summary
- Hook duration: 3-5s
- Scene 1 duration: 8-12s
- Scene 2 duration: 10-15s
- Scene 3 duration: 5-8s
- Transition 1 duration: 0.5s
- Transition 2 duration: 0.8s
- Total estimated duration: 26.3-41.3s
- Duration target: 45-60s
- Status: BELOW TARGET (consider adding scenes or extending durations)

### Platform Considerations
- tiktok: Vertical 9:16 crop safe. First frame must be visually striking for feed preview. Max duration: 60s.
- reels: Vertical 9:16 crop safe. Ensure first frame works as grid preview thumbnail. Max duration: 90s.
- shorts: Vertical 9:16 crop safe. No critical elements in top/bottom 10%. Max duration: 60s.

### Placeholder Resolution Summary
| Placeholder | Data Source | Status |
|---|---|---|
| product_category | Product Master | RESOLVED |
| key_benefit | Product Master | RESOLVED |
| product_name | Product Master | RESOLVED |
| pain_point | Product Master | RESOLVED |

### Component Summary
- hook: 1
- scene: 3
- voice_style: 1
- visual_direction: 1
- audio_mood: 1
- text_style: 1
- transition: 2
- Total: 10
```

## Quality Requirements

Every resolved output must satisfy the following quality requirements. These requirements are enforced during the review phase and by the gatekeep_output_format step.

### No Dangling References

All component_id references from the composition must be fully expanded in the output. No component_id text may appear as an unresolved reference. Scanning the output for patterns like "component_id:" or "see component:" must yield zero results. Every component referenced in the composition is present in the output as fully expanded content with all properties resolved.

### No Unresolved Placeholders

All {placeholder} tokens must be either resolved to their data source values or flagged as {UNRESOLVED: field_name}. No raw {placeholder_name} syntax may appear in the output without the UNRESOLVED prefix. The {UNRESOLVED: field_name} syntax must be used consistently -- no alternative flagging formats are permitted. The unresolved_placeholder_count in the frontmatter must accurately reflect the count of flagged placeholders.

### Schema Conformance

All overrides applied in the output must conform to the referenced component's type schema. The output must show only valid property values: enum properties must contain valid enum values, string properties must contain strings, duration properties must match the duration format pattern. If the composition contained invalid overrides (which should have been caught during composition validation), the output must still present the override value but flag the conformance issue in the Production Notes section.

### Completeness

All required sections must be present in the output. The required sections are: Opening (Hook), Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, and Production Notes. The Text Overlay section is conditionally required (present only if the composition includes the text binding). The YAML frontmatter must contain all required fields. No section may be empty or contain only placeholder content.

### Consistency

No contradictions may exist between sections. For example:

- The Voice Direction section's pace must be compatible with the Opening section's energy_level (e.g., pace=slow with energy_level=high is a potential inconsistency).
- The total estimated duration in Production Notes must be consistent with the sum of individual scene and transition durations.
- The component_count in the frontmatter must match the actual number of distinct components expanded across all sections.
- The lifecycle_status must be consistent with the unresolved_placeholder_count (if count > 0, status must be "draft").
- Platform-specific notes must reference only the platforms listed in metadata.target_platforms.

## Downstream Extraction Contracts

The output is designed to be consumed by multiple downstream workflows, each extracting specific concerns. The output describes WHAT the deliverable is, not HOW to produce it. Downstream workflows determine their own production logic. This section defines extraction contracts for the primary downstream consumers.

### Contract 1: Voiceover Generation

**What it extracts:** The voiceover generation workflow extracts all scene_script fields from the Scene-by-Scene Breakdown section, in scene order, combined with the Voice Direction section properties for delivery guidance.

**How it uses the data:**
- Each scene_script provides the spoken text for that scene segment.
- Voice Direction's voice_tone determines the narrator's vocal quality.
- Voice Direction's pace determines the speaking speed.
- Voice Direction's emphasis_pattern guides where to place vocal stress.
- Voice Direction's voice_character informs the voice casting or TTS configuration.
- The hook_script from the Opening section provides the spoken text for the hook segment.

**Expected format:** Scene scripts are found under ### Scene {i}: {scene_purpose} subsections within ## Scene-by-Scene Breakdown, in the Scene Script property. The hook_script is found under ## Opening (Hook). All scripts must have placeholders resolved (no {UNRESOLVED: field_name} tokens in voiceover text).

**Error handling:** If any scene_script contains {UNRESOLVED: field_name} tokens, the voiceover generation workflow must halt and request that the placeholder be resolved before proceeding. Voiceover cannot be generated from partially resolved scripts.

### Contract 2: Visual Asset Creation

**What it extracts:** The visual asset creation workflow extracts the Visual Treatment section for global visual direction, combined with per-scene visual_direction properties from the Scene-by-Scene Breakdown, and per-scene camera_work specifications.

**How it uses the data:**
- Visual Treatment's visual_style determines the overall aesthetic approach.
- Visual Treatment's color_palette defines the color scheme (including hex codes).
- Visual Treatment's lighting_mood determines the lighting approach.
- Visual Treatment's camera_work provides the default camera approach.
- Visual Treatment's aspect_ratio determines the framing constraints.
- Each scene's visual_direction property provides scene-specific visual guidance.
- Each scene's camera_work property overrides the global camera approach for that scene (if present).
- The Visual Cue from the Opening section provides hook-specific visual direction.

**Expected format:** Visual Treatment properties are found under ## Visual Treatment. Scene-specific visual_direction and camera_work properties are found under each ### Scene {i}: {scene_purpose} subsection. All values are plain text descriptions.

### Contract 3: Platform Adaptation

**What it extracts:** The platform adaptation workflow extracts metadata from the frontmatter (target_platforms, duration_target) and Platform Considerations from the Production Notes section. It also references all other sections to verify compliance with platform-specific constraints.

**How it uses the data:**
- metadata.target_platforms lists the platforms to adapt for.
- metadata.duration_target defines the overall timing constraint.
- Platform Considerations in Production Notes provide per-platform constraints (aspect ratio, duration limits, format requirements).
- The adaptation workflow checks each scene's duration_target against platform duration limits.
- The adaptation workflow checks the Visual Treatment's aspect_ratio against platform-specific crop safety requirements.

**Expected format:** Frontmatter metadata is machine-parseable YAML. Platform Considerations are in the Production Notes section under ### Platform Considerations, with one bullet per platform. Duration information is available in each scene's Duration Target property and in the Timing Summary subsection.

### Platform-Specific Considerations

The output is not tied to any specific platform. Instead, it declares the target platforms in metadata and provides platform-specific guidance in the Production Notes. Downstream workflows use this information to make platform-specific decisions. The output itself remains platform-agnostic -- it describes a single canonical manuscript that may be adapted per platform by downstream workflows.

Key platform considerations include:

- **TikTok:** Vertical 9:16 format. First frame must be visually striking for feed preview. Trending sound references may be needed. Max duration varies (typically 60s).
- **Instagram Reels:** Vertical 9:16 format. First frame serves as grid preview thumbnail. Aspect ratio and crop safety critical. Max duration 90s.
- **YouTube Shorts:** Vertical 9:16 format. Safe crop zone excludes top and bottom 10% of frame. Max duration 60s.

## Example Outputs

This section provides a complete example output demonstrating the full resolution process. The example uses the composition from COMPOSITION_FORMAT-02.md Example 1 (Skincare Product Launch) with realistic data source values.

### Complete Example: Lumiere Serum Product Launch

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

- Name: Skincare Question Hook
- Version: 1.0.0
- Duration Range: 3-5s
- Platforms: tiktok, reels, shorts
- Tags: question, skincare, engagement
- Hook Style: question_hook
- Hook Script: "What if your skincare serum routine was missing one key ingredient?"
- Visual Cue: "Close-up of hand applying serum, soft focus background with warm lighting"
- Energy Level: high

## Voice Direction

- Name: Conversational Expert Voice
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Tags: conversational, friendly, expert, skincare
- Voice Tone: conversational
- Pace: moderate
- Emphasis Pattern: "Stress product benefit words and ingredient names. Pause briefly before the call-to-action to let the message land. Keep transitions between scenes smooth and natural."
- Voice Character: "Friendly expert in their late 20s, like a knowledgeable friend who happens to work in skincare research. Warm but credible."

## Visual Treatment

- Name: Minimalist Warm Aesthetic
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Tags: minimalist, warm, premium, skincare
- Visual Style: minimalist
- Color Palette: "Warm neutrals with gold accents. Primary: #F5F0E8, Accent: #C5A572, Text: #2C2C2C"
- Lighting Mood: soft
- Camera Work: "Mostly static shots with occasional slow push-in movements. Clean backgrounds with shallow depth of field to isolate subject."
- Aspect Ratio: "9:16 vertical (safe crop for all platforms, no critical elements in top/bottom 10%)"

## Scene-by-Scene Breakdown

### Scene 1: Problem

- Name: Problem Statement Scene
- Version: 1.0.0
- Duration Range: 8-12s
- Platforms: tiktok, reels, shorts
- Tags: problem, pain_point, relatable
- Scene Purpose: problem
- Scene Script: "Most skincare serum products promise visible radiance in 7 days, but most ingredients cannot penetrate deep enough to make a real difference."
- Visual Direction: "Split-screen composition: left side shows frustrated customer examining skin in mirror, right side shows generic product bottles with red X marks"
- Duration Target: "8-12s"
- Camera Work: "Medium shot on customer, slow pan across product collection"

*Transition: match_cut, 0.5s, moderate*

### Scene 2: Solution

- Name: Solution Introduction Scene
- Version: 1.0.0
- Duration Range: 10-15s
- Platforms: tiktok, reels, shorts
- Tags: solution, product, hero_shot
- Scene Purpose: solution
- Scene Script: "Introducing Lumiere Radiance Serum -- formulated with a proprietary delivery system for real visible radiance in 7 days."
- Visual Direction: "Product hero shot with warm backlight, serum droplet catching light against minimalist background"
- Duration Target: "10-15s"

*Transition: fade, 0.8s, subtle*

### Scene 3: Demo

- Name: Product Demonstration Scene
- Version: 1.0.0
- Duration Range: 10-15s
- Platforms: tiktok, reels, shorts
- Tags: demo, results, proof
- Scene Purpose: demo
- Scene Script: "In just 7 days, users reported visibly brighter, more even-toned skin."
- Visual Direction: "Before-and-after split comparison, warm lighting highlighting skin improvement"
- Duration Target: "10-15s"

*Transition: dissolve, 1.0s, subtle*

### Scene 4: CTA

- Name: Call to Action Scene
- Version: 1.0.0
- Duration Range: 5-8s
- Platforms: tiktok, reels, shorts
- Tags: CTA, conversion, urgency
- Scene Purpose: CTA
- Scene Script: "Try Lumiere Radiance Serum today. Link in bio."
- Visual Direction: "Product centered on screen with brand logo, warm background, call-to-action text overlay"
- Duration Target: "5-8s"

## Audio Direction

- Name: Uplifting Acoustic Mood
- Version: 1.0.0
- Duration Range: 45-60s
- Platforms: tiktok, reels, shorts
- Tags: uplifting, acoustic, positive, skincare
- Mood: uplifting
- Tempo: moderate
- Instrumentation: "Acoustic guitar arpeggios with light shaker percussion, subtle strings pad building through the narrative arc, gentle piano accent on the CTA moment"
- Volume Balance: "Music at 20% volume under voiceover, swell to 35% during transitions, peak to 45% on final product reveal, fade out gently after CTA"

## Text Overlay

- Name: Clean Subtitle Treatment
- Version: 1.0.0
- Platforms: tiktok, reels, shorts
- Tags: subtitles, accessible, clean, caption
- Text Treatment: subtitles
- Font Style: "Clean sans-serif (Montserrat or Poppins), medium weight for body, bold for product names and key benefits. Minimum 24px equivalent on mobile."
- Text Animation: fade
- Text Color Scheme: "White text (#FFFFFF) with subtle dark drop shadow for readability against any background. Product names highlighted in brand gold (#C5A572)."

## Production Notes

### Timing Summary
- Hook duration: 3-5s
- Scene 1 duration: 8-12s
- Scene 2 duration: 10-15s
- Scene 3 duration: 10-15s
- Scene 4 duration: 5-8s
- Transition 1 duration: 0.5s
- Transition 2 duration: 0.8s
- Transition 3 duration: 1.0s
- Total estimated duration: 38.3-57.3s
- Duration target: 45-60s
- Status: WITHIN TARGET RANGE (at moderate pace)

### Platform Considerations
- tiktok: Vertical 9:16 crop safe. First frame must be visually striking for feed preview. Max duration: 60s. Estimated duration 57.3s is within limit.
- reels: Vertical 9:16 crop safe. Ensure first frame works as grid preview thumbnail. Max duration: 90s. Estimated duration well within limit.
- shorts: Vertical 9:16 crop safe. No critical elements in top/bottom 10%. Max duration: 60s. Estimated duration 57.3s is within limit.

### Placeholder Resolution Summary
| Placeholder | Data Source | Status |
|---|---|---|
| product_category | Product Master | RESOLVED |
| key_benefit | Product Master | RESOLVED |
| product_name | Product Master | RESOLVED |

### Component Summary
- hook: 1
- scene: 4
- voice_style: 1
- visual_direction: 1
- audio_mood: 1
- text_style: 1
- transition: 3
- Total: 12
```

### Resolution Details for This Example

This example demonstrates the following resolution operations:

1. **Component reference expansion:** 12 component_id references from the composition were expanded into full component content. For instance, hook-question-001 was looked up in the component library and its full property set was rendered in the Opening section.

2. **Override application:** The composition overrode hook_script for the opening binding, scene_script for all four scene bindings, and color_palette for the visuals binding. In each case, the override value replaced the base component value in the output. Non-overridden properties retained their base values.

3. **Placeholder resolution:** Three placeholders were encountered: {product_category} (resolved to "skincare serum" from Product Master), {key_benefit} (resolved to "visible radiance in 7 days" from Product Master), and {product_name} (resolved to "Lumiere Radiance Serum" from Product Master). All were resolved successfully.

4. **Scene-transition interleaving:** Four scenes and three transitions were interleaved in narrative order: Scene 1, Transition 1, Scene 2, Transition 2, Scene 3, Transition 3, Scene 4.

5. **lifecycle_status set to "final":** Because unresolved_placeholder_count is 0 and all quality requirements are satisfied.

## Self-Validation Checklist

This section verifies that the output format definition satisfies all requirements from the source specification and the Composition System Standard.

### Section Coverage

| Required Section | Defined? | Section in This Document | Example Provided? |
|---|---|---|---|
| Opening (Hook) | YES | Required Sections - Opening (Hook) | YES |
| Voice Direction | YES | Required Sections - Voice Direction | YES |
| Visual Treatment | YES | Required Sections - Visual Treatment | YES |
| Scene-by-Scene Breakdown | YES | Required Sections - Scene-by-Scene Breakdown | YES |
| Audio Direction | YES | Required Sections - Audio Direction | YES |
| Text Overlay | YES | Required Sections - Text Overlay | YES |
| Production Notes | YES | Required Sections - Production Notes | YES |

### Resolution Rule Coverage

| Rule | Covered? | Section in This Document |
|---|---|---|
| Component reference expansion | YES | Resolution Rules - Component Reference Expansion |
| Override application (override wins) | YES | Resolution Rules - Override Application |
| Placeholder resolution from data sources | YES | Resolution Rules - Placeholder Resolution |
| Unresolved placeholder handling | YES | Resolution Rules - Unresolved Placeholder Handling |
| Scene-transition interleaving | YES | Resolution Rules - Scene-Transition Interleaving |
| Priority rules for data sources | YES | Resolution Rules - Placeholder Resolution (step 2) |

### Quality Requirement Coverage

| Requirement | Covered? | Section in This Document |
|---|---|---|
| No dangling references | YES | Quality Requirements - No Dangling References |
| No unresolved placeholders (unresolved flagged) | YES | Quality Requirements - No Unresolved Placeholders |
| Schema conformance | YES | Quality Requirements - Schema Conformance |
| Completeness (all required sections present) | YES | Quality Requirements - Completeness |
| Consistency (no contradictions) | YES | Quality Requirements - Consistency |

### Downstream Contract Coverage

| Contract | Covered? | Section in This Document |
|---|---|---|
| Voiceover generation | YES | Downstream Extraction Contracts - Contract 1 |
| Visual asset creation | YES | Downstream Extraction Contracts - Contract 2 |
| Platform adaptation | YES | Downstream Extraction Contracts - Contract 3 |

### Test Criteria Alignment (TC-OF-001 through TC-OF-N03)

| Criterion | Satisfied? | Evidence |
|---|---|---|
| TC-OF-001 (frontmatter fields) | YES | Output Structure - Frontmatter Fields table |
| TC-OF-002 (required sections) | YES | Output Structure - Required Sections table |
| TC-OF-003 (internal section structure) | YES | Output Structure - Internal Section Structure |
| TC-OF-004 (example skeleton) | YES | Example Outputs - Complete Example |
| TC-OF-005 (component_id expansion) | YES | Resolution Rules - Component Reference Expansion |
| TC-OF-006 (expansion process) | YES | Resolution Rules - Component Reference Expansion (3 steps) |
| TC-OF-007 (ordered list rendering) | YES | Resolution Rules - Scene-Transition Interleaving |
| TC-OF-008 (singleton rendering) | YES | Required Sections - individual section definitions |
| TC-OF-009 (placeholder replacement) | YES | Resolution Rules - Placeholder Resolution (step 3) |
| TC-OF-010 (unresolved flagging) | YES | Resolution Rules - Unresolved Placeholder Handling |
| TC-OF-011 (placeholder summary) | YES | Required Sections - Production Notes (Placeholder Resolution Summary) |
| TC-OF-012 (self-contained) | YES | Resolution Rules - Component Reference Expansion ("self-contained" statement) |
| TC-OF-013 (no residual references) | YES | Quality Requirements - No Dangling References |
| TC-OF-014 (downstream context) | YES | Downstream Extraction Contracts (3 contracts) |
| TC-OF-015 (extraction contracts) | YES | Downstream Extraction Contracts (3 contracts defined) |
| TC-OF-016 (downstream-agnostic) | YES | Downstream Extraction Contracts intro paragraph |
| TC-OF-017 (platform notes) | YES | Required Sections - Production Notes (Platform Considerations) |
| TC-OF-018 (unresolved syntax) | YES | Resolution Rules - Unresolved Placeholder Handling (exact syntax) |
| TC-OF-019 (lifecycle_status for draft) | YES | Resolution Rules - Unresolved Placeholder Handling (lifecycle impact) |
| TC-OF-020 (self-check) | YES | This Self-Validation Checklist |
| TC-OF-021 (example demonstrates all rules) | YES | Example Outputs - Resolution Details for This Example |
| TC-OF-N01 (no library dependency) | YES | Resolution Rules - Component Reference Expansion |
| TC-OF-N02 (no raw placeholders) | YES | Resolution Rules - Unresolved Placeholder Handling |
| TC-OF-N03 (no missing sections) | YES | Quality Requirements - Completeness |

### Component Type Coverage

| Component Type | Output Section | Example in Complete Output |
|---|---|---|
| hook | Opening (Hook) | YES - "Skincare Question Hook" |
| scene | Scene-by-Scene Breakdown | YES - 4 scenes (Problem, Solution, Demo, CTA) |
| voice_style | Voice Direction | YES - "Conversational Expert Voice" |
| visual_direction | Visual Treatment | YES - "Minimalist Warm Aesthetic" |
| audio_mood | Audio Direction | YES - "Uplifting Acoustic Mood" |
| text_style | Text Overlay | YES - "Clean Subtitle Treatment" |
| transition | Scene-by-Scene Breakdown (interleaved) | YES - 3 transitions (match_cut, fade, dissolve) |

### Completeness Summary

- All 7 required sections defined with purpose, content, and example: YES
- All frontmatter fields defined with type, required/optional, description: YES
- All resolution rules defined (expansion, override, placeholder, interleaving): YES
- All quality requirements defined (5 requirements): YES
- All downstream extraction contracts defined (3 contracts): YES
- At least one complete example output provided: YES (Lumiere Serum Product Launch)
- Example demonstrates all resolution rules: YES (verified in Resolution Details)
- All 7 component types have representation in output: YES
- Standard conformance (COMPOSITION_SYSTEM_STANDARD.md Section 5): YES
- Spec conformance (video_campaign_manuscript_v2.md Section 4): YES
- Test criteria alignment (TC-OF-001 through TC-OF-N03): YES (all 24 criteria satisfied)

---

**End of Output Format**
