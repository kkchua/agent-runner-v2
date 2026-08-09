---
doc_type: "component_schema"
lifecycle_status: "draft"
effective_version: "WBUILD2-paqdd825"
domain: "video_campaign_manuscript"
component_type_count: 7
created_at: "2026-08-08"
source_spec: "creative_workflow_builder_v1.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
spec_type_source: "COMPOSITION_SYSTEM_STANDARD.md Section 7.1"
---

# Component Schema: Video Campaign Manuscript Domain

## 1. Overview

This document defines the Layer 1 component schema for the video campaign manuscript domain. A video campaign manuscript is a structured production document that guides the end-to-end creation of short-form video advertisements and branded content across platforms such as TikTok, Instagram Reels, YouTube Shorts, and similar. The composition system decomposes a manuscript into standardized, reusable building blocks (components) that can be assembled declaratively into complete production documents. This schema defines the standardized building blocks -- the LEGO bricks -- that compositions reference. Each component encapsulates a distinct creative concern (opening sequence, content segment, voice direction, visual treatment, audio direction, on-screen text treatment, or scene transition) so that production teams can mix, match, and override them without rewriting entire manuscripts.

**Domain context:** Short-form video campaign production for digital advertising and branded content. The end deliverable is a production manuscript that downstream workflows consume to generate voiceovers, visual assets, video edits, and platform-specific adaptations.

**Number of component types defined:** 7

**Source of type enumeration:** COMPOSITION_SYSTEM_STANDARD.md Section 7.1 (Video Campaign Manuscripts).

---

## 2. Common Properties

All component types share the following common properties. These properties are stable and domain-agnostic. They MUST NOT be redefined, overridden, or removed by type-specific property extensions.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier within the component library. Format: "{type}-{descriptor}-{sequence}" (e.g., hook-dramatic-001). Must be unique across all components in the library. |
| component_type | enum | Yes | The component type. Must be one of the seven recognized types: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition. |
| name | string | Yes | Human-readable display name for the component. Used in composition documentation and output section headers. |
| version | string | Yes | Semantic version following MAJOR.MINOR.PATCH format (e.g., 1.0.0). See Section 5 for versioning rules. |
| description | string | Yes | A clear statement of what this component does, its creative intent, and when to use it in a composition. |
| duration_range | string | No | The applicable duration range for this component (e.g., "3-5s", "10-15s"). Domain-specific. Not all types require this. |
| platforms | array | No | List of target platform identifiers where this component is applicable (e.g., ["tiktok", "reels", "shorts"]). |
| tags | array | No | Classification tags for search, filter, and categorization (e.g., ["dramatic", "product", "suspense"]). |

---

## 3. Component Types

### 3.1 Type Enumeration

The following enum lists all recognized component types for the video campaign manuscript domain:

```yaml
valid_component_types:
  - hook
  - scene
  - voice_style
  - visual_direction
  - audio_mood
  - text_style
  - transition
```

No other component_type values are valid. A component declaring an unrecognized type fails validation.

---

### 3.2 Type: hook

#### 3.2.1 Type Overview

- **Name:** hook
- **Purpose:** Defines the opening sequence of a video. The hook captures viewer attention in the first few seconds and establishes the creative premise.
- **When to use:** Every video campaign manuscript requires exactly one hook component. It is the first element in the viewing experience.

#### 3.2.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| hook_style | enum | Yes | The opening technique used to capture attention. Valid values: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook. | dramatic_reveal |
| hook_script | string | Yes | The spoken or displayed text of the opening. Maximum 50 words. May contain {placeholder} syntax for data source resolution. | "What if everything you knew about skincare was wrong?" |
| visual_cue | string | Yes | Description of the visual element shown during the hook. Must be specific enough for a video editor to execute. | "Extreme close-up of a cracked serum bottle, dark background, single spotlight from above" |
| energy_level | enum | Yes | The intensity and pace of the opening. Valid values: low, medium, high. | high |

#### 3.2.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| HOOK-VR-001 | hook_style is present | Value must be one of: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook | "Invalid hook_style '{value}'. Must be one of the recognized hook styles." |
| HOOK-VR-002 | hook_script word count | Word count must not exceed 50 | "hook_script exceeds 50-word limit ({count} words found)." |
| HOOK-VR-003 | hook_script is present | Must be a non-empty string | "hook_script is required and must not be empty." |
| HOOK-VR-004 | visual_cue is present | Must be a non-empty string with at least 10 characters | "visual_cue must be a descriptive string of at least 10 characters." |
| HOOK-VR-005 | energy_level is present | Value must be one of: low, medium, high | "Invalid energy_level '{value}'. Must be low, medium, or high." |
| HOOK-VR-006 | Cross-property: if hook_style is visual_reveal | visual_cue must reference a specific visual object or scene | "When hook_style is 'visual_reveal', visual_cue must describe a specific visual element." |

#### 3.2.4 Example Component

```yaml
---
component_id: "hook-dramatic-reveal-001"
component_type: "hook"
name: "Dramatic Reveal Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["dramatic", "suspense", "product"]
description: "Opens with a mysterious product silhouette in darkness, building curiosity before the reveal. Effective for beauty and tech products."

hook_style: "dramatic_reveal"
hook_script: "What if everything you knew about {product_name} was wrong?"
visual_cue: "Extreme close-up of product silhouette in darkness, single spotlight from above, slow pull-back"
energy_level: "high"
---

# Dramatic Reveal Hook

Usage notes: Best paired with a high-energy voice_style and dramatic lighting in visual_direction.
Works well with transition_type "dissolve" into the first scene.
```

---

### 3.3 Type: scene

#### 3.3.1 Type Overview

- **Name:** scene
- **Purpose:** Defines a content segment within the video. Each scene delivers a specific narrative beat (problem setup, solution demo, social proof, etc.).
- **When to use:** A manuscript typically contains 3-8 scenes arranged in sequence. Scenes are the primary content carriers.

#### 3.3.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| scene_purpose | enum | Yes | The narrative function of this scene. Valid values: problem_setup, solution_demo, social_proof, call_to_action, product_intro, education, emotional_appeal. | problem_setup |
| scene_script | string | Yes | The spoken narration or dialogue for this scene. May contain {placeholder} syntax. | "Most people spend hours researching products that end up disappointing them." |
| visual_direction | string | Yes | Detailed description of what the viewer sees during this scene. Must be actionable for a video editor or motion designer. | "Split screen: left side shows frustrated person scrolling phone, right side shows product packaging rotating slowly" |
| duration_target | number | Yes | Target duration for this scene in seconds. Must be a positive number. | 12 |

#### 3.3.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| SCENE-VR-001 | scene_purpose is present | Value must be one of: problem_setup, solution_demo, social_proof, call_to_action, product_intro, education, emotional_appeal | "Invalid scene_purpose '{value}'. Must be a recognized narrative function." |
| SCENE-VR-002 | scene_script is present | Must be a non-empty string | "scene_script is required and must not be empty." |
| SCENE-VR-003 | visual_direction is present | Must be a non-empty string with at least 15 characters | "visual_direction must be a descriptive string of at least 15 characters." |
| SCENE-VR-004 | duration_target is present | Must be a positive number greater than 0 | "duration_target must be a positive number (got {value})." |
| SCENE-VR-005 | Cross-property: if duration_target > 30 | scene_script must have word count greater than 75 | "Scenes longer than 30 seconds must have a scene_script exceeding 75 words (current: {count})." |
| SCENE-VR-006 | Cross-property: if scene_purpose is call_to_action | scene_script must contain an actionable directive (imperative verb) | "call_to_action scenes must include a clear directive in scene_script." |

#### 3.3.4 Example Component

```yaml
---
component_id: "scene-problem-setup-001"
component_type: "scene"
name: "Problem Setup Scene"
version: "1.0.0"
duration_range: "10-15s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["problem", "pain_point", "relatable"]
description: "Establishes the viewer's pain point or problem. Creates empathy and sets up the need for the solution."

scene_purpose: "problem_setup"
scene_script: "Most people spend hours researching {product_category} that end up disappointing them. You read reviews, watch videos, and still end up with something that does not work."
visual_direction: "Split screen: left side shows frustrated person scrolling phone in dim room, right side shows pile of discarded product packaging. Text overlay: 'There is a better way.'"
duration_target: 12
---

# Problem Setup Scene

Usage notes: Pair with empathetic voice_tone. Transition into solution_demo scene using dissolve or match_cut.
Works well with low-to-medium energy audio_mood to build tension before the solution reveal.
```

---

### 3.4 Type: voice_style

#### 3.4.1 Type Overview

- **Name:** voice_style
- **Purpose:** Defines the voiceover direction for the entire video. Controls tone, pace, emphasis, and vocal character.
- **When to use:** Each manuscript binds exactly one voice_style component. It applies globally across all scenes.

#### 3.4.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| voice_tone | enum | Yes | The overall vocal attitude and emotion. Valid values: authoritative, conversational, enthusiastic, empathetic, dramatic. | enthusiastic |
| pace | enum | Yes | The speaking speed. Valid values: slow, moderate, fast, varied. | moderate |
| emphasis_pattern | string | No | Description of which words or phrases receive vocal emphasis. | "Emphasize product benefits and emotional triggers. Pause before the key revelation." |
| voice_character | string | No | Description of the ideal voice persona (age range, gender, accent, register). | "Young female, mid-20s, warm American accent, relatable peer tone" |

#### 3.4.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| VOICE-VR-001 | voice_tone is present | Value must be one of: authoritative, conversational, enthusiastic, empathetic, dramatic | "Invalid voice_tone '{value}'. Must be a recognized vocal tone." |
| VOICE-VR-002 | pace is present | Value must be one of: slow, moderate, fast, varied | "Invalid pace '{value}'. Must be slow, moderate, fast, or varied." |
| VOICE-VR-003 | Cross-property: if voice_tone is dramatic | pace should not be fast (warning, not hard failure) | "Warning: dramatic voice_tone paired with fast pace may reduce emotional impact." |
| VOICE-VR-004 | Cross-property: if voice_tone is empathetic | voice_character should describe a warm or relatable persona | "empathetic voice_tone works best with warm, relatable voice_character descriptions." |

#### 3.4.4 Example Component

```yaml
---
component_id: "voice-enthusiastic-peer-001"
component_type: "voice_style"
name: "Enthusiastic Peer Voice"
version: "1.0.0"
tags: ["enthusiastic", "peer", "relatable", "young_audience"]
description: "A warm, enthusiastic peer-to-peer voice that feels like a friend sharing a discovery. Effective for lifestyle and beauty products targeting Gen Z and Millennials."

voice_tone: "enthusiastic"
pace: "moderate"
emphasis_pattern: "Emphasize product benefits and transformation language. Pause briefly before the call to action to build anticipation."
voice_character: "Young female, mid-20s, warm American accent, conversational and relatable, slight excitement in delivery"
---

# Enthusiastic Peer Voice

Usage notes: Pairs well with high-energy hook components and upbeat audio_mood.
Avoid pairing with dramatic lighting -- the tone mismatch can feel dissonant.
```

---

### 3.5 Type: visual_direction

#### 3.5.1 Type Overview

- **Name:** visual_direction
- **Purpose:** Defines the overall visual treatment for the video. Establishes style, color, lighting, camera work, and framing.
- **When to use:** Each manuscript binds exactly one visual_direction component. It applies globally to all scenes.

#### 3.5.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| visual_style | enum | Yes | The overarching visual aesthetic. Valid values: cinematic, documentary, lifestyle, motion_graphics, mixed. | lifestyle |
| color_palette | string | Yes | Description of the color scheme used throughout the video. | "Warm earth tones: terracotta, cream, sage green, with gold accent highlights" |
| lighting_mood | enum | Yes | The lighting atmosphere. Valid values: bright, dramatic, natural, neon, warm. | natural |
| camera_work | string | No | Description of camera movement, angles, and framing style. | "Handheld close-ups with slow push-ins. Occasional drone overhead for establishing shots. No shaky cam." |
| aspect_ratio | enum | No | The target aspect ratio. Valid values: 16:9, 9:16, 1:1, 4:5. Default is 9:16 for vertical video. | 9:16 |

#### 3.5.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| VISDIR-VR-001 | visual_style is present | Value must be one of: cinematic, documentary, lifestyle, motion_graphics, mixed | "Invalid visual_style '{value}'. Must be a recognized visual aesthetic." |
| VISDIR-VR-002 | color_palette is present | Must be a non-empty string with at least 10 characters | "color_palette must describe the color scheme in at least 10 characters." |
| VISDIR-VR-003 | lighting_mood is present | Value must be one of: bright, dramatic, natural, neon, warm | "Invalid lighting_mood '{value}'. Must be a recognized lighting atmosphere." |
| VISDIR-VR-004 | aspect_ratio is present (if provided) | Value must be one of: 16:9, 9:16, 1:1, 4:5 | "Invalid aspect_ratio '{value}'. Must be 16:9, 9:16, 1:1, or 4:5." |
| VISDIR-VR-005 | Cross-property: if visual_style is cinematic | lighting_mood should be dramatic or warm (warning) | "Warning: cinematic visual_style pairs best with dramatic or warm lighting_mood." |

#### 3.5.4 Example Component

```yaml
---
component_id: "visdir-lifestyle-natural-001"
component_type: "visual_direction"
name: "Natural Lifestyle Visual Treatment"
version: "1.0.0"
platforms: ["tiktok", "reels", "shorts"]
tags: ["lifestyle", "natural", "warm", "authentic"]
description: "Authentic lifestyle visual treatment with natural lighting and warm tones. Creates an approachable, real-life feel ideal for beauty, wellness, and home products."

visual_style: "lifestyle"
color_palette: "Warm earth tones: terracotta, cream, sage green, with gold accent highlights"
lighting_mood: "natural"
camera_work: "Handheld medium shots with gentle push-ins. Close-ups for product details. Natural movement, no tripod stiffness. Shoot in golden hour when possible."
aspect_ratio: "9:16"
---

# Natural Lifestyle Visual Treatment

Usage notes: Works with empathetic or conversational voice_tone. Pair with warm audio_mood.
Ensure all scene visual_direction descriptions stay within this palette for visual consistency.
```

---

### 3.6 Type: audio_mood

#### 3.6.1 Type Overview

- **Name:** audio_mood
- **Purpose:** Defines the background music and audio atmosphere for the video. Controls mood, tempo, instrumentation, and balance with voiceover.
- **When to use:** Each manuscript binds exactly one audio_mood component. It applies globally to the audio mix.

#### 3.6.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| mood | enum | Yes | The emotional tone of the background music. Valid values: energetic, calm, tense, uplifting, mysterious. | uplifting |
| tempo | enum | Yes | The speed of the music. Valid values: slow, moderate, fast. | moderate |
| instrumentation | string | No | Description of the primary instruments and sound elements. | "Acoustic guitar, light percussion, soft synth pads, occasional finger snaps" |
| volume_balance | string | No | Description of how music volume relates to voiceover and sound effects. | "Music at 30% under voiceover, swell to 60% during transitions, drop to 15% during key dialogue moments" |

#### 3.6.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| AUDIO-VR-001 | mood is present | Value must be one of: energetic, calm, tense, uplifting, mysterious | "Invalid mood '{value}'. Must be a recognized audio mood." |
| AUDIO-VR-002 | tempo is present | Value must be one of: slow, moderate, fast | "Invalid tempo '{value}'. Must be slow, moderate, or fast." |
| AUDIO-VR-003 | Cross-property: if mood is tense | tempo should not be slow (warning) | "Warning: tense mood with slow tempo may feel dull rather than suspenseful." |
| AUDIO-VR-004 | Cross-property: if mood is energetic | tempo should be fast or moderate (not slow) | "Warning: energetic mood paired with slow tempo creates a mismatch." |

#### 3.6.4 Example Component

```yaml
---
component_id: "audio-uplifting-mod-001"
component_type: "audio_mood"
name: "Uplifting Moderate Tempo"
version: "1.0.0"
duration_range: "30-60s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["uplifting", "positive", "acoustic", "brand"]
description: "Warm, uplifting background music with moderate tempo. Builds positivity and forward momentum without overpowering voiceover."

mood: "uplifting"
tempo: "moderate"
instrumentation: "Acoustic guitar fingerpicking, light shaker percussion, warm synth pad underneath, occasional piano notes for emphasis"
volume_balance: "Music at 25-30% under voiceover, swell to 50% during transitions and scene changes, peak at 60% during the final call to action moment"
---

# Uplifting Moderate Tempo

Usage notes: Versatile mood that works with most voice tones. Avoid pairing with tense scene_purpose scenes.
Best with natural or warm lighting_mood for a cohesive feel.
```

---

### 3.7 Type: text_style

#### 3.7.1 Type Overview

- **Name:** text_style
- **Purpose:** Defines the on-screen text treatment including typography, animation, placement, and color scheme.
- **When to use:** Each manuscript binds one text_style component. It applies globally to all text overlays.

#### 3.7.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| text_treatment | enum | Yes | The style of on-screen text presentation. Valid values: kinetic_typography, lower_thirds, full_screen, overlay, subtitles. | kinetic_typography |
| font_style | string | Yes | Description of the typography including font family, weight, and sizing guidance. | "Bold sans-serif (Montserrat Bold), 48px for headlines, 28px for body. All caps for emphasis words." |
| text_animation | enum | Yes | The animation style for text appearance. Valid values: fade_in, slide_in, bounce, typewriter, pop, none. | pop |
| text_color_scheme | string | Yes | Description of text colors including primary, secondary, and background treatment. | "White text with black drop shadow on busy backgrounds. Gold accent for key phrases. Semi-transparent black bar behind lower thirds." |

#### 3.7.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| TEXT-VR-001 | text_treatment is present | Value must be one of: kinetic_typography, lower_thirds, full_screen, overlay, subtitles | "Invalid text_treatment '{value}'. Must be a recognized text presentation style." |
| TEXT-VR-002 | font_style is present | Must be a non-empty string | "font_style is required and must not be empty." |
| TEXT-VR-003 | text_animation is present | Value must be one of: fade_in, slide_in, bounce, typewriter, pop, none | "Invalid text_animation '{value}'. Must be a recognized animation style." |
| TEXT-VR-004 | text_color_scheme is present | Must be a non-empty string describing colors | "text_color_scheme must describe the color treatment for on-screen text." |
| TEXT-VR-005 | Cross-property: if text_treatment is kinetic_typography | text_animation must not be none (kinetic text requires animation) | "kinetic_typography requires a text_animation value other than none." |

#### 3.7.4 Example Component

```yaml
---
component_id: "text-kinetic-pop-001"
component_type: "text_style"
name: "Kinetic Pop Text Treatment"
version: "1.0.0"
platforms: ["tiktok", "reels"]
tags: ["kinetic", "dynamic", "bold", "modern"]
description: "Dynamic kinetic typography with pop-in animations. Creates energy and draws attention to key phrases. Ideal for fast-paced product demos and lifestyle content."

text_treatment: "kinetic_typography"
font_style: "Bold sans-serif (Montserrat Bold), 48px for headlines, 28px for body text. All caps for emphasis words. Letter spacing slightly tight for impact."
text_animation: "pop"
text_color_scheme: "White text with black drop shadow on busy backgrounds. Gold accent color (#D4A84B) for key phrases. Semi-transparent black bar behind lower thirds for readability."
---

# Kinetic Pop Text Treatment

Usage notes: Pairs well with high-energy hook styles and fast-paced scenes.
Ensure text color scheme has sufficient contrast against the visual_direction color palette.
```

---

### 3.8 Type: transition

#### 3.8.1 Type Overview

- **Name:** transition
- **Purpose:** Defines the visual transition between scenes. Controls the type, duration, and energy of scene-to-scene movement.
- **When to use:** Compositions reference transitions between scene pairs. A composition may use one or more transition components.

#### 3.8.2 Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| transition_type | enum | Yes | The visual transition effect. Valid values: cut, dissolve, wipe, zoom, glitch, match_cut. | dissolve |
| transition_duration | number | Yes | Duration of the transition in seconds. Must be a positive number, typically between 0.3 and 2.0. | 0.8 |
| transition_energy | enum | Yes | The intensity of the transition. Valid values: low, medium, high. | medium |

#### 3.8.3 Type-Specific Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| TRANS-VR-001 | transition_type is present | Value must be one of: cut, dissolve, wipe, zoom, glitch, match_cut | "Invalid transition_type '{value}'. Must be a recognized transition effect." |
| TRANS-VR-002 | transition_duration is present | Must be a positive number between 0.1 and 5.0 | "transition_duration must be between 0.1 and 5.0 seconds (got {value})." |
| TRANS-VR-003 | transition_energy is present | Value must be one of: low, medium, high | "Invalid transition_energy '{value}'. Must be low, medium, or high." |
| TRANS-VR-004 | Cross-property: if transition_type is cut | transition_duration should be 0.1-0.3 (cuts are instantaneous) | "Warning: cut transitions should have duration under 0.3 seconds (got {value})." |
| TRANS-VR-005 | Cross-property: if transition_energy is high | transition_duration should be under 1.0 second | "High-energy transitions should be quick (under 1.0s) to maintain momentum." |

#### 3.8.4 Example Component

```yaml
---
component_id: "transition-dissolve-smooth-001"
component_type: "transition"
name: "Smooth Dissolve Transition"
version: "1.0.0"
duration_range: "0.5-1.0s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["dissolve", "smooth", "professional", "versatile"]
description: "A clean dissolve transition that smoothly blends two scenes. Professional and versatile, suitable for most content types and moods."

transition_type: "dissolve"
transition_duration: 0.8
transition_energy: "medium"
---

# Smooth Dissolve Transition

Usage notes: The most versatile transition. Works between any scene types.
Pair with moderate or uplifting audio_mood for a cohesive flow.
Avoid pairing with high-energy glitch transitions in the same manuscript -- choose one energy level.
```

---

## 4. Validation Rules (Global)

These validation rules apply to all components regardless of type. They are enforced in addition to type-specific validation rules defined in Section 3.

### 4.1 Required Fields Validation

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-001 | component_id is present | Must be a non-empty string | "Component is missing required field 'component_id'." |
| GLOBAL-VR-002 | component_type is present | Must be a non-empty string | "Component is missing required field 'component_type'." |
| GLOBAL-VR-003 | name is present | Must be a non-empty string | "Component is missing required field 'name'." |
| GLOBAL-VR-004 | version is present | Must be a non-empty string | "Component is missing required field 'version'." |
| GLOBAL-VR-005 | description is present | Must be a non-empty string with at least 10 characters | "Component is missing required field 'description' or description is too short." |

### 4.2 Type Enumeration Validation

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-006 | component_type value | Must be one of: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition | "Unrecognized component_type '{value}'. Must be one of the seven defined types." |

### 4.3 Unique Identifier Validation

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-007 | component_id uniqueness | No two components in the library may share the same component_id | "Duplicate component_id '{id}' found. Each component must have a unique identifier." |
| GLOBAL-VR-008 | component_id format | Must match pattern "{type}-{descriptor}-{sequence}" where type is the component_type, descriptor is lowercase-hyphenated words, and sequence is a numeric suffix | "component_id '{id}' does not follow the naming convention '{type}-{descriptor}-{sequence}'." |

### 4.4 Semantic Version Validation

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-009 | version format | Must match MAJOR.MINOR.PATCH where each is a non-negative integer | "version '{value}' does not follow semantic versioning format (MAJOR.MINOR.PATCH)." |

### 4.5 Type-Specific Schema Conformance

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-010 | Type-specific properties | All required properties for the declared component_type must be present | "Component of type '{type}' is missing required type-specific property '{property}'." |
| GLOBAL-VR-011 | Property data types | All property values must conform to their declared data types | "Property '{property}' has invalid type. Expected {expected_type}, got {actual_type}." |
| GLOBAL-VR-012 | Enum value conformance | All enum-typed properties must use values from their defined valid value lists | "Property '{property}' value '{value}' is not in the valid set: {valid_values}." |

### 4.6 No-Override Rule

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-013 | Type-specific properties must not override common properties | No type-specific property may be named component_id, component_type, name, version, description, duration_range, platforms, or tags | "Type-specific property '{property}' conflicts with a common property. Common properties cannot be overridden." |

---

## 5. Extensibility Model

### 5.1 Adding New Component Types

New component types can be added to the domain without breaking existing compositions. The process is:

1. **Define the new type's specific properties** following the pattern in Section 3. Each property must have: name, data type, required/optional status, description, and example value.
2. **Add the new type to the type enumeration** in Section 3.1 (valid_component_types list).
3. **Define type-specific validation rules** for the new type following the pattern in the relevant type section.
4. **Provide at least one example component** for the new type that passes all validation rules.
5. **Document the new type** in this schema document with its own subsection under Section 3.

Existing compositions continue to work because they reference components by component_id, not by type. Adding a new type does not invalidate any existing component_id reference.

### 5.2 Backward Compatibility Rules

- **Common properties are stable.** The eight common properties (component_id, component_type, name, version, description, duration_range, platforms, tags) MUST NOT be removed, renamed, or have their semantics changed.
- **Existing type definitions are stable.** Type-specific properties that exist today cannot be removed or have their data types changed in a backward-incompatible way without a MAJOR version increment.
- **Optional properties can be added freely.** Adding a new optional type-specific property is a backward-compatible change. Existing components that lack the property remain valid.
- **Enum values can be added freely.** Adding new valid values to an enum property is backward-compatible. Existing components using old values remain valid.
- **Enum values cannot be removed without MAJOR version bump.** Removing a valid enum value is a breaking change if existing components use that value.

### 5.3 Versioning Rules

Component type schema changes follow semantic versioning at the schema level:

| Change Type | Version Impact | Example |
|---|---|---|
| Add a new optional type-specific property | MINOR (e.g., 1.0.0 to 1.1.0) | Adding "subtext_overlay" as optional to text_style |
| Add a new valid enum value | MINOR (e.g., 1.0.0 to 1.1.0) | Adding "whip_pan" to transition_type enum |
| Remove a type-specific property | MAJOR (e.g., 1.x.x to 2.0.0) | Removing "energy_level" from hook |
| Change a property's data type | MAJOR (e.g., 1.x.x to 2.0.0) | Changing duration_target from number to string |
| Make an optional property required | MAJOR (e.g., 1.x.x to 2.0.0) | Making voice_character required in voice_style |
| Make a required property optional | MAJOR (e.g., 1.x.x to 2.0.0) | Making hook_script optional in hook |
| Fix documentation typos, clarify descriptions | PATCH (e.g., 1.0.0 to 1.0.1) | Clarifying what "energy_level: high" means |
| Add a new component type entirely | MINOR at schema level | Adding "caption_style" type |

### 5.4 Schema Stability Guarantee

The common property set (Section 2) is governed by the Composition System Standard. Changes to common properties require a standard version increment and are not made at the domain schema level. Domain schema changes affect only type-specific properties and the type enumeration.

---

## 6. Component File Format

Components are stored as markdown files with YAML frontmatter. The frontmatter contains all common properties and type-specific properties. The markdown body contains additional documentation, usage notes, and examples.

### 6.1 File Structure

```
components/
  hooks/
    hook-dramatic-reveal-001.md
    hook-question-painpoint-001.md
  scenes/
    scene-problem-setup-001.md
    scene-solution-demo-001.md
  voice_styles/
    voice-enthusiastic-peer-001.md
  visual_directions/
    visdir-lifestyle-natural-001.md
  audio_moods/
    audio-uplifting-mod-001.md
  text_styles/
    text-kinetic-pop-001.md
  transitions/
    transition-dissolve-smooth-001.md
```

### 6.2 Complete Example Component File

```markdown
---
component_id: "hook-question-painpoint-001"
component_type: "hook"
name: "Pain Point Question Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: ["tiktok", "reels"]
tags: ["question", "pain_point", "relatable", "skincare"]
description: "Opens with a relatable question that highlights the viewer's pain point. Creates immediate identification and stops the scroll."

hook_style: "question_hook"
hook_script: "Tired of buying {product_category} that never delivers on its promises?"
visual_cue: "Close-up of person looking frustrated at bathroom shelf full of half-used products, soft morning light"
energy_level: "medium"
---

# Pain Point Question Hook

## Usage Notes

- Best paired with empathetic voice_style for authenticity.
- Works well as an opener for problem-solution structured manuscripts.
- The {product_category} placeholder should resolve from the Product Master data source.
- Transition into a problem_setup scene using dissolve or match_cut.

## Platform Adaptations

- TikTok: Add trending sound underneath the question delivery.
- Reels: Ensure the first frame shows the frustrated expression clearly for grid preview.
- Shorts: Vertical crop safe -- face centered in frame.
```

---

## 7. Self-Check: Spec-to-Schema Coverage

This section verifies that all component types declared in the domain specification are covered by this schema.

### 7.1 Cross-Reference Table

| Spec Source | Type Declared | Schema Section | Status |
|---|---|---|---|
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | hook | Section 3.2 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | scene | Section 3.3 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | voice_style | Section 3.4 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | visual_direction | Section 3.5 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | audio_mood | Section 3.6 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | text_style | Section 3.7 | COVERED |
| COMPOSITION_SYSTEM_STANDARD.md Section 7.1 | transition | Section 3.8 | COVERED |

### 7.2 Coverage Summary

- **Total types in spec:** 7
- **Total types in schema:** 7
- **Missing types:** 0
- **Extra types (not in spec):** 0

All component types from COMPOSITION_SYSTEM_STANDARD.md Section 7.1 are defined in this schema. No types are missing and no invented types have been added.

### 7.3 Test Criteria Traceability

| Test Criteria ID | Requirement | Schema Section | Status |
|---|---|---|---|
| TC-CS-001 | All spec types defined | Section 7.1 | SATISFIED |
| TC-CS-002 | Type enumeration present | Section 3.1 | SATISFIED |
| TC-CS-003 | All 7 types from Section 7.1 defined | Sections 3.2-3.8 | SATISFIED |
| TC-CS-004 | All six common properties included | Section 2 | SATISFIED |
| TC-CS-005 | Each common property has type, required/optional, description | Section 2 | SATISFIED |
| TC-CS-006 | component_id specifies uniqueness and naming convention | Section 2, Section 4 | SATISFIED |
| TC-CS-007 | version specifies semantic versioning | Section 2, Section 4 | SATISFIED |
| TC-CS-008 | Type-specific properties per type | Sections 3.2-3.8 | SATISFIED |
| TC-CS-009 | Each property has name, type, required/optional, description | Sections 3.2-3.8 | SATISFIED |
| TC-CS-010 | Enum values explicitly listed | Sections 3.2-3.8 | SATISFIED |
| TC-CS-011 | No type-specific property duplicates common properties | Section 4, GLOBAL-VR-013 | SATISFIED |
| TC-CS-012 | Type-specific validation rules | Sections 3.2-3.8 | SATISFIED |
| TC-CS-013 | Implementable validation rules | Sections 3.2-3.8, Section 4 | SATISFIED |
| TC-CS-014 | Cross-property validation rules | Sections 3.2-3.8 | SATISFIED |
| TC-CS-015 | Extensibility documented | Section 5 | SATISFIED |
| TC-CS-016 | Versioning rules specified | Section 5.3 | SATISFIED |
| TC-CS-017 | Common properties stable | Section 5.2, Section 5.4 | SATISFIED |
| TC-CS-018 | Example per type | Sections 3.2-3.8 | SATISFIED |
| TC-CS-019 | Examples use file format | Section 6 | SATISFIED |
| TC-CS-020 | Realistic example values | Sections 3.2-3.8 | SATISFIED |
| TC-CS-021 | Self-check section | Section 7 | SATISFIED |
| TC-CS-022 | Missing type flagging | Section 7.2 | SATISFIED |
| TC-CS-N01 | No invented types | Section 7.1 | SATISFIED |
| TC-CS-N02 | Common properties domain-agnostic | Section 2 | SATISFIED |
| TC-CS-N03 | No type-specific override of common properties | Section 4, GLOBAL-VR-013 | SATISFIED |

---

**End of Component Schema**
