---
doc_type: "component_schema"
lifecycle_status: "draft"
effective_version: "WBUILD2-dpxcr3x1"
domain: "video_campaign_manuscript"
component_type_count: 7
source_spec: "video_campaign_manuscript_v2.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
created_at: "2026-08-08"
---

# Component Schema: Video Campaign Manuscript Domain

## Overview

This document defines the Layer 1 component schema for the video_campaign_manuscript domain. The component library provides standardized, reusable building blocks (LEGO bricks) for assembling complete video production manuscripts. Each component encapsulates a distinct creative concern -- an opening hook, a content scene, voice direction, visual treatment, audio mood, text overlay styling, or scene transition -- that can be mixed, matched, and overridden across different campaign compositions.

The domain produces short-form video campaign manuscripts (15-90 seconds) for platforms including TikTok, Instagram Reels, and YouTube Shorts. A manuscript is the master creative document that coordinates all creative concerns into a unified production guide, which downstream workflows then use to generate voiceovers, visual assets, video edits, and platform-specific adaptations.

This schema defines exactly 7 component types, each with common properties shared across all types and type-specific properties unique to that type's creative concern. The schema follows the Universal Component Schema pattern defined in COMPOSITION_SYSTEM_STANDARD.md Section 3.

## Type Enumeration

The following component types are recognized in this domain. No other types are valid.

| Index | Component Type | Purpose | Cardinality | Required |
|---|---|---|---|---|
| 1 | hook | Opening sequence that captures attention | Singleton | Yes |
| 2 | scene | Content segment with narrative purpose | Ordered list (3-8) | Yes |
| 3 | voice_style | Voiceover delivery direction | Singleton | Yes |
| 4 | visual_direction | Visual treatment and aesthetic | Singleton | Yes |
| 5 | audio_mood | Background music and audio direction | Singleton | Yes |
| 6 | text_style | On-screen text treatment | Singleton | No |
| 7 | transition | Scene transition effect | Ordered list (N-1 for N scenes) | Yes |

## Common Properties

Every component, regardless of type, must declare the following common properties. These properties are domain-agnostic and remain stable across all current and future component types. Type-specific properties must not override or redefine these common property semantics.

| Property | Type | Required | Description | Validation |
|---|---|---|---|---|
| component_id | string | Yes | Unique identifier within the component library. Format: {type}-{descriptor}-{seq} (e.g., hook-dramatic-001). No two components in the library may share the same component_id. | Must match pattern: ^[a-z]+-[a-z0-9]+-[0-9]{3}$ |
| component_type | enum | Yes | The component type. Must be one of the 7 types defined in the Type Enumeration table above. | Must be one of: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition |
| name | string | Yes | Human-readable display name for the component. Used in output section headings and human review. | Non-empty string, max 100 characters |
| version | string | Yes | Semantic version indicating the component's schema evolution. Format: MAJOR.MINOR.PATCH. | Must match pattern: ^\d+\.\d+\.\d+$ |
| description | string | Yes | Creative intent and usage guidance. Describes what this component does and when to use it. | Non-empty string, max 500 characters |
| duration_range | string | No | Applicable duration for this component. Domain-specific (e.g., "3-5s" for hooks, "10-15s" for scenes). | If present, must match pattern: ^\d+(-\d+)?s$ |
| platforms | array | No | Target platforms this component is designed for. Valid values: tiktok, reels, shorts. | If present, must be a non-empty array of valid platform identifiers |
| tags | array | No | Classification tags for search and filtering within the component library. | If present, must be a non-empty array of non-empty strings |

## Component Types

### Type: hook

#### Type Overview

A hook component defines the opening sequence of a video manuscript. Its purpose is to capture viewer attention within the first 3-5 seconds, establishing curiosity or urgency that compels continued viewing. Every manuscript requires exactly one hook (singleton, required). The hook sets the tone for the entire video and must align with the voice_style and visual_direction components.

**When to use:** Always required. Select a hook based on the campaign's opening strategy -- dramatic reveals for product launches, question hooks for engagement, statistic hooks for authority positioning.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| hook_style | enum | Yes | The opening technique used to capture attention. Determines the narrative approach of the first seconds. Valid values: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook | dramatic_reveal |
| hook_script | string | Yes | The spoken or displayed text during the hook. This is the first words the viewer hears. May contain {placeholder} references resolved from data sources at generation time. Maximum 50 words to fit within the 3-5 second duration window. | "What if everything you knew about skincare was wrong?" |
| visual_cue | string | Yes | Description of the visual element shown during the hook. Guides the visual production team on what the viewer sees in the opening moments. | "Extreme close-up of cracked serum bottle, dark background" |
| energy_level | enum | Yes | The intensity and pace of the opening. Determines how aggressively the hook grabs attention. Valid values: low, medium, high | high |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| HOOK-VR-001 | hook_style value | Must be one of: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook | "Invalid hook_style value '{value}'. Must be one of: dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook" |
| HOOK-VR-002 | hook_script word count | Must not exceed 50 words | "hook_script exceeds maximum 50 words (found {count} words)" |
| HOOK-VR-003 | hook_script placeholder syntax | If placeholders present, must use {placeholder_name} syntax with valid field names from data sources | "Invalid placeholder syntax in hook_script: '{raw}'. Expected format: {field_name}" |
| HOOK-VR-004 | energy_level value | Must be one of: low, medium, high | "Invalid energy_level value '{value}'. Must be one of: low, medium, high" |
| HOOK-VR-005 | duration_range | If present, must match pattern \d+(-\d+)?s and value must be within 1-10s range | "hook duration_range '{value}' is invalid or outside the 1-10s acceptable range" |
| HOOK-VR-006 | Cross-property: hook_style=visual_reveal and visual_cue | If hook_style is visual_reveal, visual_cue is mandatory and must be at least 20 characters | "hook_style=visual_reveal requires a detailed visual_cue (minimum 20 characters)" |

#### Example Component

```yaml
---
component_id: "hook-question-001"
component_type: "hook"
name: "Skincare Question Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["question", "skincare", "engagement"]
description: "Opens with a provocative question about skincare routines, creating immediate curiosity and relatability for viewers who suspect their routine may be incomplete."

hook_style: "question_hook"
hook_script: "What if your {product_category} routine was missing one key ingredient?"
visual_cue: "Close-up of hand applying serum, soft focus background with warm lighting"
energy_level: "high"
---

# Skincare Question Hook

Usage notes: Best for product launches where the key differentiator is a novel
ingredient or formulation. Pair with conversational or authoritative voice_tone.
Works well across all three short-form platforms. The question format drives
comment engagement on TikTok and Reels.
```

### Type: scene

#### Type Overview

A scene component defines a content segment within the video manuscript. Each scene serves a specific narrative purpose -- presenting a problem, introducing a solution, demonstrating features, providing testimonials, or driving a call to action. Scenes are assembled as an ordered list of 3 to 8 scenes per manuscript, forming the narrative arc of the video. Each scene is required.

**When to use:** Always required. A manuscript must contain at least 3 and at most 8 scenes. Scenes should follow a logical narrative progression (problem, solution, demo, CTA being the most common arc).

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| scene_purpose | enum | Yes | The narrative role this scene plays in the overall story arc. Determines where in the sequence this scene belongs. Valid values: problem, solution, demo, testimonial, CTA, education, comparison | problem |
| scene_script | string | Yes | The spoken text for this scene. May contain {placeholder} references resolved from data sources. Word count should be proportional to duration_target (approximately 2.5 words per second of target duration). | "Most products promise results but deliver disappointment." |
| visual_direction | string | Yes | Description of what the viewer sees during this scene. Guides camera work, set design, and visual effects. | "Split-screen: left shows frustrated customer, right shows product" |
| duration_target | string | Yes | Target duration for this scene. Must match duration format. | "8-12s" |
| camera_work | string | No | Specific camera movement or angle guidance for this scene. If omitted, the visual_direction component's general camera approach applies. | "Slow push-in on customer face" |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| SCENE-VR-001 | scene_purpose value | Must be one of: problem, solution, demo, testimonial, CTA, education, comparison | "Invalid scene_purpose value '{value}'. Must be one of: problem, solution, demo, testimonial, CTA, education, comparison" |
| SCENE-VR-002 | duration_target format | Must match pattern \d+(-\d+)?s | "duration_target '{value}' does not match required format. Expected: Ns or N-Ns (e.g., '10s' or '8-12s')" |
| SCENE-VR-003 | duration_target range | Duration must be between 3s and 30s | "duration_target '{value}' is outside the acceptable 3-30s range for a single scene" |
| SCENE-VR-004 | scene_script placeholder syntax | If placeholders present, must use {placeholder_name} syntax | "Invalid placeholder syntax in scene_script: '{raw}'. Expected format: {field_name}" |
| SCENE-VR-005 | scene_script word count vs duration | If duration_target specifies a range, word count should be approximately 2.5 words per second of the midpoint duration (allow +/-30% tolerance) | "scene_script word count ({count}) is not proportional to duration_target '{duration}'. Expected approximately {expected} words." |
| SCENE-VR-006 | Cross-property: scene_purpose=CTA and scene_script | If scene_purpose is CTA, scene_script must contain an actionable directive (at least one imperative verb) | "scene_purpose=CTA requires an actionable call-to-action in scene_script" |

#### Example Component

```yaml
---
component_id: "scene-problem-001"
component_type: "scene"
name: "Problem Statement Scene"
version: "1.0.0"
duration_range: "8-12s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["problem", "pain_point", "relatable"]
description: "Establishes the viewer's pain point by presenting a common frustration. Creates empathy and sets up the need for the product solution that follows."

scene_purpose: "problem"
scene_script: "Most {product_category} products promise {key_benefit}, but most ingredients can't penetrate deep enough to make a real difference."
visual_direction: "Split-screen composition: left side shows frustrated customer examining skin in mirror, right side shows generic product bottles with red X marks"
duration_target: "8-12s"
camera_work: "Medium shot on customer, slow pan across product collection"
---

# Problem Statement Scene

Usage notes: This scene establishes the emotional hook after the opening. It
should feel relatable, not accusatory. The split-screen visual creates contrast
between the problem and the failed solutions. Pair with empathetic voice_tone
for maximum resonance. This scene typically positions second in the narrative
arc, immediately after the hook.
```

### Type: voice_style

#### Type Overview

A voice_style component defines the voiceover delivery direction for the manuscript. It governs how the script sounds -- the tone, pacing, emphasis patterns, and character of the narrator's voice. Every manuscript requires exactly one voice_style (singleton, required). This component ensures vocal consistency across all scenes.

**When to use:** Always required. Select a voice_style that matches the campaign's brand personality and target audience. Authoritative tones work for educational or professional products; conversational tones work for lifestyle and consumer products.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| voice_tone | enum | Yes | The overall vocal quality and personality of the narrator. Sets the emotional register for the entire manuscript. Valid values: authoritative, conversational, energetic, empathetic, playful | conversational |
| pace | enum | Yes | The speaking speed throughout the manuscript. Determines how much content fits within the duration target. Valid values: slow, moderate, fast, varied | moderate |
| emphasis_pattern | string | No | Guidance on how key words and phrases should be stressed. Describes where to place vocal weight for maximum impact. | "Stress product benefits, pause before CTA" |
| voice_character | string | No | A description of the voice persona. Helps voice talent understand the character they are performing. | "Friendly expert, like a knowledgeable friend" |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| VOICE-VR-001 | voice_tone value | Must be one of: authoritative, conversational, energetic, empathetic, playful | "Invalid voice_tone value '{value}'. Must be one of: authoritative, conversational, energetic, empathetic, playful" |
| VOICE-VR-002 | pace value | Must be one of: slow, moderate, fast, varied | "Invalid pace value '{value}'. Must be one of: slow, moderate, fast, varied" |
| VOICE-VR-003 | Cross-property: pace=fast and duration_target | If pace is fast, total manuscript word count should be higher than moderate pace for the same duration | "pace=fast suggests higher word density; verify scene_script word counts align with duration targets" |

#### Example Component

```yaml
---
component_id: "voice-conversational-001"
component_type: "voice_style"
name: "Conversational Expert Voice"
version: "1.0.0"
platforms: ["tiktok", "reels", "shorts"]
tags: ["conversational", "friendly", "expert", "skincare"]
description: "A warm, approachable narrator who speaks like a knowledgeable friend sharing insider secrets. Builds trust through familiarity rather than authority. Ideal for consumer skincare and beauty products targeting millennials and Gen Z."

voice_tone: "conversational"
pace: "moderate"
emphasis_pattern: "Stress product benefit words and ingredient names. Pause briefly before the call-to-action to let the message land. Keep transitions between scenes smooth and natural."
voice_character: "Friendly expert in their late 20s, like a knowledgeable friend who happens to work in skincare research. Warm but credible."
---

# Conversational Expert Voice

Usage notes: This voice style works best for products that benefit from personal
recommendation rather than clinical authority. The moderate pace allows
viewers to absorb product details without feeling rushed. Pair with
energy_level=medium or high hooks to balance warmth with engagement.
Best with visual_style=minimalist or vibrant aesthetics.
```

### Type: visual_direction

#### Type Overview

A visual_direction component defines the overall visual treatment and aesthetic for the manuscript. It governs the visual style, color palette, lighting mood, camera approach, and aspect ratio considerations. Every manuscript requires exactly one visual_direction (singleton, required). This component ensures visual consistency across all scenes.

**When to use:** Always required. Select a visual_style that aligns with the brand identity and campaign objectives. Cinematic styles suit premium products; vibrant styles suit lifestyle and youth-targeted campaigns.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| visual_style | enum | Yes | The overall aesthetic approach for the video. Determines the production design language. Valid values: cinematic, minimalist, vibrant, documentary, animated, mixed_media | minimalist |
| color_palette | string | Yes | The color scheme for the video. Should reference brand colors when available. Include hex codes for precision. | "Warm neutrals with gold accents. Brand hex: #C5A572" |
| lighting_mood | enum | Yes | The quality and mood of lighting throughout the video. Affects the emotional tone of the visual production. Valid values: bright, moody, natural, dramatic, soft | soft |
| camera_work | string | No | General camera approach for the manuscript. Specific scenes may override with their own camera_work property. | "Mostly static shots with occasional slow movement" |
| aspect_ratio | string | No | Video dimensions and crop safety guidance. Should account for platform-specific requirements. | "9:16 vertical (safe crop for all platforms)" |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| VISUAL-VR-001 | visual_style value | Must be one of: cinematic, minimalist, vibrant, documentary, animated, mixed_media | "Invalid visual_style value '{value}'. Must be one of: cinematic, minimalist, vibrant, documentary, animated, mixed_media" |
| VISUAL-VR-002 | lighting_mood value | Must be one of: bright, moody, natural, dramatic, soft | "Invalid lighting_mood value '{value}'. Must be one of: bright, moody, natural, dramatic, soft" |
| VISUAL-VR-003 | color_palette content | Must be a non-empty string. If brand hex codes are referenced, they must be valid 6-digit hex format (#RRGGBB). | "color_palette references invalid hex format. Expected #RRGGBB format (e.g., #C5A572)" |
| VISUAL-VR-004 | aspect_ratio format | If present, must specify dimensions in standard format (e.g., "9:16", "16:9", "1:1") | "aspect_ratio '{value}' is not in a recognized format. Expected standard ratio format like '9:16' or '16:9'" |

#### Example Component

```yaml
---
component_id: "visual-minimalist-warm-001"
component_type: "visual_direction"
name: "Minimalist Warm Aesthetic"
version: "1.0.0"
platforms: ["tiktok", "reels", "shorts"]
tags: ["minimalist", "warm", "premium", "skincare"]
description: "Clean, uncluttered visual style with warm color tones. Uses negative space effectively to draw attention to product and subject. Ideal for premium skincare and beauty brands that want to convey sophistication without intimidation."

visual_style: "minimalist"
color_palette: "Warm neutrals with gold accents. Primary: #F5F0E8, Accent: #C5A572, Text: #2C2C2C"
lighting_mood: "soft"
camera_work: "Mostly static shots with occasional slow push-in movements. Clean backgrounds with shallow depth of field to isolate subject."
aspect_ratio: "9:16 vertical (safe crop for all platforms, no critical elements in top/bottom 10%)"
---

# Minimalist Warm Aesthetic

Usage notes: This visual direction creates a premium, approachable feel. The warm
neutrals work exceptionally well for skincare and beauty content where the product
itself should be the visual hero. The soft lighting flatters skin tones and creates
an aspirational but attainable mood. Ensure all product shots maintain the warm
color temperature -- avoid cool blue lighting that conflicts with the palette.
```

### Type: audio_mood

#### Type Overview

An audio_mood component defines the background music and audio direction for the manuscript. It governs the musical mood, tempo, instrumentation preferences, and volume balance between music and voiceover. Every manuscript requires exactly one audio_mood (singleton, required). This component ensures audio consistency that supports the emotional arc.

**When to use:** Always required. Select an audio_mood that complements the voice_tone and reinforces the campaign's emotional message. Uplifting moods suit product launches; tense moods suit problem-focused narratives.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| mood | enum | Yes | The emotional feel of the background music. Should complement the overall campaign tone. Valid values: uplifting, tense, inspirational, playful, calm, dramatic | uplifting |
| tempo | enum | Yes | The speed of the background music. Should align with the voice pace and scene energy. Valid values: slow, moderate, fast, dynamic | moderate |
| instrumentation | string | No | Preferred instruments and sound design elements. Guides the music selection or composition. | "Acoustic guitar with light percussion" |
| volume_balance | string | No | Guidance on the balance between background music and voiceover. Specifies how music should duck and swell relative to speech. | "Music at 20% under voiceover, swell to 40% in transitions" |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| AUDIO-VR-001 | mood value | Must be one of: uplifting, tense, inspirational, playful, calm, dramatic | "Invalid mood value '{value}'. Must be one of: uplifting, tense, inspirational, playful, calm, dramatic" |
| AUDIO-VR-002 | tempo value | Must be one of: slow, moderate, fast, dynamic | "Invalid tempo value '{value}'. Must be one of: slow, moderate, fast, dynamic" |
| AUDIO-VR-003 | Cross-property: mood and voice_tone compatibility | If voice_tone is empathetic, mood should not be dramatic or tense (emotional mismatch) | "Potential mismatch: voice_tone={voice_tone} with audio mood={mood}. Review for emotional coherence." |

#### Example Component

```yaml
---
component_id: "audio-uplifting-001"
component_type: "audio_mood"
name: "Uplifting Acoustic Mood"
version: "1.0.0"
duration_range: "45-60s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["uplifting", "acoustic", "positive", "skincare"]
description: "Warm, optimistic background music with acoustic guitar foundation and light rhythmic elements. Creates a positive, aspirational atmosphere that supports product-focused content without competing with the voiceover."

mood: "uplifting"
tempo: "moderate"
instrumentation: "Acoustic guitar arpeggios with light shaker percussion, subtle strings pad building through the narrative arc, gentle piano accent on the CTA moment"
volume_balance: "Music at 20% volume under voiceover, swell to 35% during transitions, peak to 45% on final product reveal, fade out gently after CTA"
---

# Uplifting Acoustic Mood

Usage notes: This audio mood creates a warm, trustworthy atmosphere ideal for
skincare and lifestyle content. The moderate tempo pairs well with conversational
or empathetic voice tones. The acoustic instrumentation avoids sounding overly
produced, which aligns with the authentic, relatable brand voice typical of
DTC beauty brands. Ensure the music bed does not have vocal elements that would
compete with the voiceover.
```

### Type: text_style

#### Type Overview

A text_style component defines the on-screen text treatment for the manuscript. It governs how captions, titles, lower thirds, and callout text appear -- including font style, animation behavior, and color scheme. This component is optional (singleton, not required). Not all manuscripts need on-screen text treatment, but when used, it ensures consistency across all text elements.

**When to use:** Optional. Include when the campaign requires on-screen text for accessibility (captions), emphasis (callouts), or branding (lower thirds, title cards). Particularly important for TikTok and Reels where auto-captions and kinetic typography drive engagement.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| text_treatment | enum | Yes | The primary text display approach. Determines how text content is presented on screen. Valid values: subtitles, kinetic_typography, lower_thirds, title_cards, callouts | subtitles |
| font_style | string | No | Font family and weight guidance. Should be legible on mobile screens. | "Clean sans-serif, bold for emphasis" |
| text_animation | enum | No | How text appears on screen. If omitted, defaults to platform-native caption styling. Valid values: none, fade, slide, typewriter, bounce | fade |
| text_color_scheme | string | No | Color guidance for text elements. Must ensure sufficient contrast against the visual_direction color palette for readability. | "White text with dark shadow for readability" |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| TEXT-VR-001 | text_treatment value | Must be one of: subtitles, kinetic_typography, lower_thirds, title_cards, callouts | "Invalid text_treatment value '{value}'. Must be one of: subtitles, kinetic_typography, lower_thirds, title_cards, callouts" |
| TEXT-VR-002 | text_animation value | If present, must be one of: none, fade, slide, typewriter, bounce | "Invalid text_animation value '{value}'. Must be one of: none, fade, slide, typewriter, bounce" |
| TEXT-VR-003 | Cross-property: text_color_scheme and visual_direction | If both are specified, text_color_scheme should describe sufficient contrast against the visual_direction color_palette | "text_color_scheme may have insufficient contrast against visual_direction color_palette. Verify readability on mobile screens." |

#### Example Component

```yaml
---
component_id: "text-subtitles-001"
component_type: "text_style"
name: "Clean Subtitle Treatment"
version: "1.0.0"
platforms: ["tiktok", "reels", "shorts"]
tags: ["subtitles", "accessible", "clean", "caption"]
description: "Standard subtitle treatment with clean typography and subtle animation. Ensures accessibility compliance and supports viewers watching without sound. Designed for legibility on mobile screens with varying background content."

text_treatment: "subtitles"
font_style: "Clean sans-serif (Montserrat or Poppins), medium weight for body, bold for product names and key benefits. Minimum 24px equivalent on mobile."
text_animation: "fade"
text_color_scheme: "White text (#FFFFFF) with subtle dark drop shadow for readability against any background. Product names highlighted in brand gold (#C5A572)."
---

# Clean Subtitle Treatment

Usage notes: This text style prioritizes readability and accessibility. The fade
animation is subtle enough not to distract from the visual content. The white
text with shadow ensures legibility against both light and dark backgrounds in
the minimalist warm aesthetic. Use this as the default text treatment when the
campaign does not specifically require kinetic typography or title cards.
```

### Type: transition

#### Type Overview

A transition component defines how the video moves between consecutive scenes. It governs the visual effect, duration, and energy of the scene change. Transitions are assembled as an ordered list, with exactly N-1 transitions for N scenes (e.g., 3 scenes require 2 transitions). Every manuscript requires transitions (required).

**When to use:** Always required when the manuscript has 2 or more scenes. The number of transitions must always equal the number of scenes minus one. Select transitions that maintain the narrative flow -- match cuts for thematic connections, fades for temporal shifts, whip pans for energy.

#### Type-Specific Properties

| Property | Type | Required | Description | Example Value |
|---|---|---|---|---|
| transition_type | enum | Yes | The visual effect used to move between scenes. Determines the mechanical approach to the scene change. Valid values: cut, fade, dissolve, wipe, zoom, match_cut, whip_pan | match_cut |
| transition_duration | string | Yes | How long the transition effect lasts. Must match duration format. Typical range: 0.3s to 2.0s. | "0.5s" |
| transition_energy | enum | Yes | The intensity of the transition effect. Should align with the surrounding scene energy levels and overall manuscript pacing. Valid values: subtle, moderate, dramatic | moderate |

#### Validation Rules

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| TRANS-VR-001 | transition_type value | Must be one of: cut, fade, dissolve, wipe, zoom, match_cut, whip_pan | "Invalid transition_type value '{value}'. Must be one of: cut, fade, dissolve, wipe, zoom, match_cut, whip_pan" |
| TRANS-VR-002 | transition_duration format | Must match pattern \d+(-\d+)?s or \d+\.\d+s | "transition_duration '{value}' does not match required format. Expected: Ns, N.Ns, or N-Ns (e.g., '0.5s' or '1s')" |
| TRANS-VR-003 | transition_duration range | Duration must be between 0.1s and 3.0s | "transition_duration '{value}' is outside the acceptable 0.1-3.0s range" |
| TRANS-VR-004 | transition_energy value | Must be one of: subtle, moderate, dramatic | "Invalid transition_energy value '{value}'. Must be one of: subtle, moderate, dramatic" |
| TRANS-VR-005 | Cross-property: transition_type=whip_pan and transition_energy | If transition_type is whip_pan, transition_energy must be moderate or dramatic (whip_pan is inherently energetic) | "transition_type=whip_pan requires transition_energy of moderate or dramatic. 'subtle' is not compatible with whip_pan." |
| TRANS-VR-006 | Cross-property: transition_type=cut and transition_duration | If transition_type is cut, transition_duration should be 0.1s or less (cuts are instant) | "transition_type=cut with transition_duration='{value}' is contradictory. Cuts should be 0.1s or less." |

#### Example Component

```yaml
---
component_id: "transition-match-cut-001"
component_type: "transition"
name: "Match Cut Transition"
version: "1.0.0"
duration_range: "0.5s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["match_cut", "thematic", "smooth", "professional"]
description: "A thematic transition that connects two scenes through visual or conceptual similarity. Creates a sense of narrative continuity by linking related visual elements across the cut. Ideal for connecting problem-to-solution or before-to-after sequences."

transition_type: "match_cut"
transition_duration: "0.5s"
transition_energy: "moderate"
---

# Match Cut Transition

Usage notes: Match cuts are most effective when the two scenes share a visual
element (shape, color, movement direction) that can bridge the transition.
For example, a close-up of a product bottle can match-cut to a close-up of
the product being applied. This transition type works well for problem-to-
solution scene sequences. Avoid using between scenes with no visual connection,
as the match cut will feel forced. Pair with moderate energy_level scenes.
```

## Validation Rules (Global)

The following validation rules apply to all components regardless of type. They are enforced in addition to the type-specific validation rules defined in each component type section above.

### Required Fields Validation

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-001 | component_id present | Must be present and non-empty | "Missing required field: component_id" |
| GLOBAL-VR-002 | component_type present | Must be present and non-empty | "Missing required field: component_type" |
| GLOBAL-VR-003 | name present | Must be present and non-empty | "Missing required field: name" |
| GLOBAL-VR-004 | version present | Must be present and non-empty | "Missing required field: version" |
| GLOBAL-VR-005 | description present | Must be present and non-empty | "Missing required field: description" |

### Type Validity

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-006 | component_type value | Must be exactly one of: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition | "Invalid component_type '{value}'. Must be one of: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition" |

### Uniqueness

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-007 | component_id uniqueness | No two components in the library may share the same component_id | "Duplicate component_id '{id}' found. Each component must have a unique identifier within the library." |
| GLOBAL-VR-008 | component_id naming convention | Must match format: {type}-{descriptor}-{seq} where type is lowercase, descriptor is alphanumeric lowercase with hyphens, seq is 3-digit zero-padded number | "component_id '{id}' does not follow naming convention. Expected format: {type}-{descriptor}-{seq} (e.g., hook-dramatic-001)" |

### Schema Conformance

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-009 | Type-specific properties present | All required type-specific properties for the declared component_type must be present | "Missing required type-specific property '{property}' for component_type '{type}'" |
| GLOBAL-VR-010 | Type-specific property types | Each type-specific property value must match its declared data type (string, enum, array) | "Property '{property}' expected type {expected_type} but found {actual_type}" |
| GLOBAL-VR-011 | No property name conflicts | Type-specific properties must not use reserved common property names: component_id, component_type, name, version, description, duration_range, platforms, tags | "Type-specific property '{property}' conflicts with reserved common property name" |

### Semantic Version Format

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-012 | version format | Must match MAJOR.MINOR.PATCH where each is a non-negative integer | "version '{value}' does not match semantic versioning format. Expected: MAJOR.MINOR.PATCH (e.g., 1.0.0)" |
| GLOBAL-VR-013 | version non-negative | Each version component (MAJOR, MINOR, PATCH) must be >= 0 | "version '{value}' contains negative version components" |

### Duration Format

| Rule ID | Condition | Expected Result | Error Message |
|---|---|---|---|
| GLOBAL-VR-014 | duration_range format (common property) | If present, must match pattern: \d+(-\d+)?s (e.g., "3s", "3-5s", "45-60s") | "duration_range '{value}' does not match required format. Expected: Ns or N-Ns" |

## Extensibility Model

This section defines how the component schema can evolve over time without breaking existing compositions or invalidating existing components.

### Adding New Component Types

New component types can be added to the domain without breaking existing compositions. The process is:

1. Define the new type's type-specific properties (name, type, required/optional, description, example values for enums).
2. Add the new type to the Type Enumeration table in this schema.
3. Define type-specific validation rules for the new type.
4. Provide at least one example component of the new type.
5. Existing compositions continue to work unchanged because they reference components by component_id, not by type. A composition that does not reference the new type is unaffected.
6. New compositions can reference the new type by including component bindings for it.

### Common Property Stability

The common property set (component_id, component_type, name, version, description, duration_range, platforms, tags) is stable. Adding a new component type does not require changes to the common properties. Common properties may only be extended by adding new optional properties (MINOR version change to the schema standard itself). Existing common properties must not be removed or have their semantics changed incompatibly.

### Type-Specific Property Evolution

Type-specific properties for each component type can evolve independently:

| Change Type | Semver Impact | Example |
|---|---|---|
| Add a new optional type-specific property | MINOR (backward compatible) | Adding camera_angle as an optional property to the scene type |
| Remove or rename a type-specific property | MAJOR (breaking change) | Removing energy_level from hook type |
| Change a property from optional to required | MAJOR (breaking change) | Making voice_character required in voice_style |
| Add new values to an existing enum | MINOR (backward compatible) | Adding "whispered" to voice_tone enum |
| Remove values from an existing enum | MAJOR (breaking change) | Removing "playful" from voice_tone enum |
| Documentation clarification, typo fix | PATCH (no schema change) | Fixing description text for a property |

### Backward Compatibility Rules

1. Existing components remain valid after schema evolution (unless a MAJOR version change is explicitly made).
2. Existing compositions remain valid after new types are added (they reference by component_id, not type).
3. Type-specific property additions (optional) do not invalidate existing components of that type.
4. Type-specific property removals or semantic changes require a MAJOR version bump to the schema, and existing components using the old schema must be migrated.

### Forward Compatibility

Compositions may reference component_ids that do not yet exist in the library. The workflow flags these as gaps in the output (missing components noted but not blocking). This allows compositions to be designed before all components are created.

## Component File Format

Components are stored as individual markdown files with YAML frontmatter. The file format follows the pattern defined in COMPOSITION_SYSTEM_STANDARD.md Section 3.3.

### File Structure

```
library/
  hooks/
    hook-question-001.md
    hook-dramatic-001.md
  scenes/
    scene-problem-001.md
    scene-solution-001.md
  voice_styles/
    voice-conversational-001.md
  visual_directions/
    visual-minimalist-warm-001.md
  audio_moods/
    audio-uplifting-001.md
  text_styles/
    text-subtitles-001.md
  transitions/
    transition-match-cut-001.md
    transition-fade-001.md
```

### File Template

```markdown
---
component_id: "{type}-{descriptor}-{seq}"
component_type: "{type}"
name: "{Human-readable name}"
version: "{MAJOR.MINOR.PATCH}"
duration_range: "{optional duration}"
platforms: ["{platform1}", "{platform2}"]
tags: ["{tag1}", "{tag2}"]
description: "{Creative intent and usage guidance}"

# Type-specific properties follow
{property_1}: "{value}"
{property_2}: "{value}"
---

# {Component Name}

Usage notes, pairing guidance, and additional documentation...
```

### Complete Example

```markdown
---
component_id: "hook-statistic-001"
component_type: "hook"
name: "Statistic Authority Hook"
version: "1.0.0"
duration_range: "3-5s"
platforms: ["tiktok", "reels", "shorts"]
tags: ["statistic", "authority", "data", "skincare"]
description: "Opens with a surprising statistic that establishes authority and creates urgency. Positions the narrator as knowledgeable and data-informed."

hook_style: "statistic_hook"
hook_script: "92% of {product_category} users are making this one mistake every single day."
visual_cue: "Bold statistic text overlay on screen with animated counter, product blurred in background"
energy_level: "high"
---

# Statistic Authority Hook

Usage notes: Best for campaigns targeting analytical or research-oriented
audiences. The statistic creates immediate credibility and FOMO (fear of
missing out). Ensure the statistic is defensible or sourced. Pair with
authoritative voice_tone for maximum impact. Works well on TikTok where
data-driven content performs strongly in the algorithm.
```

## Self-Validation Checklist

This section verifies that the schema covers all component types declared in the domain specification (video_campaign_manuscript_v2.md Section 2).

### Type Coverage Matrix

| Spec Type (Section 2.1) | Defined in Schema | Schema Section | Properties Defined | Example Provided |
|---|---|---|---|---|
| hook | YES | Type: hook | hook_style, hook_script, visual_cue, energy_level | hook-question-001 |
| scene | YES | Type: scene | scene_purpose, scene_script, visual_direction, duration_target, camera_work | scene-problem-001 |
| voice_style | YES | Type: voice_style | voice_tone, pace, emphasis_pattern, voice_character | voice-conversational-001 |
| visual_direction | YES | Type: visual_direction | visual_style, color_palette, lighting_mood, camera_work, aspect_ratio | visual-minimalist-warm-001 |
| audio_mood | YES | Type: audio_mood | mood, tempo, instrumentation, volume_balance | audio-uplifting-001 |
| text_style | YES | Type: text_style | text_treatment, font_style, text_animation, text_color_scheme | text-subtitles-001 |
| transition | YES | Type: transition | transition_type, transition_duration, transition_energy | transition-match-cut-001 |

### Coverage Summary

- Total types in spec: 7
- Total types in schema: 7
- Missing types: 0
- Extra types not in spec: 0
- All types have complete type-specific property definitions: YES
- All types have at least one example component: YES
- All enum values explicitly listed: YES
- All validation rules in implementable form: YES
- Common properties match COMPOSITION_SYSTEM_STANDARD.md Section 3.1: YES
- Extensibility model documented: YES
- Component file format defined: YES

### Verification Notes

All 7 component types from video_campaign_manuscript_v2.md Section 2.1 are defined in this schema with their exact type-specific properties as specified. No types have been added or omitted. Property names, types, required/optional markers, and enum values match the spec exactly. The common properties follow the Universal Component Schema from COMPOSITION_SYSTEM_STANDARD.md Section 3.1.

---

**End of Component Schema**
