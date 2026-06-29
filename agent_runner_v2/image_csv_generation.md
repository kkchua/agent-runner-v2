# Execution Plan: Image-to-CSV Prompt Generation

**Document version:** 1.0
**Related template:** `bootstrap/workflows/default/prompts/image_csv_gen_v1/02_gen_prompts.txt`

---

## Overview

Process images from `source_images/` folder, generate T2I/I2V prompt CSVs via LLM in-session, and save to `source_csv/` folder.

---

## Workflow

### Step 1: Image Analysis
- Qwen Code reads each image in `source_images/` using the `read_file` tool
- Produces a structured visual description covering:
  - **Subject** — main visual elements and focal points
  - **Mood** — emotional tone and atmosphere
  - **Composition** — framing, depth layers, spatial arrangement
  - **Lighting** — quality, direction, and color temperature of light
  - **Style** — artistic style, texture, rendering approach
  - **Color palette** — dominant and accent colors
  - **Animatable elements** — objects or effects that could move in video (e.g., butterflies, mist, foliage)

### Step 2: Prompt Construction
- Combine the image description with the rules from the runtime workflow prompt into a single prompt
- The prompt instructs generation of exactly 6 JSON rows with:
  - `image_filename` — zero-padded, lowercase, unique per row (format: `image_NN_theme_style.png`)
  - `t2i_prompt1` — single-sentence vertical T2I prompt (Midjourney/SDXL/DALL·E optimized)
  - `t2i_prompt2` — WAN 2.2 I2V prompt with mandatory camera motion phrase + parallax cues
  - `negative_prompt` — comma-separated negative keywords

### Step 3: JSON Generation
- Qwen Code generates the JSON array in-session following all template rules
- Mode defaults to **VARIATION** (styles differ per row, theme may repeat)
- Each `t2i_prompt2` must begin with an approved camera motion phrase:
  - `Slow dolly in` | `Slow push in` | `Gentle pull back` | `Smooth pan left` | `Smooth pan right` | `Slow tilt up` | `Slow tilt down` | `Subtle handheld drift` | `Gentle arc shot` | `Cinematic tracking shot`

### Step 4: Validation
Before saving, verify:
- Exactly 6 items in the array
- All filenames are unique and follow the naming convention
- `t2i_prompt2` starts with an approved camera motion phrase
- `t2i_prompt2` contains parallax cues (foreground/midground/background depth movement)
- No markdown, no extra keys, no negative words in positive prompts

### Step 5: CSV Output
- Convert validated JSON to CSV format
- Save to `source_csv/{image_name}.csv`
- CSV columns: `image_filename`, `t2i_prompt1`, `t2i_prompt2`, `negative_prompt`

---

## Inputs

| Path | Description |
|------|-------------|
| `source_images/*.png` | Source images to process |
| `%USERPROFILE%/.ukbe-runner/workflows/<workflow>/prompts/image_csv_gen_v1/02_gen_prompts.txt` | Runtime prompt template with generation rules |

## Outputs

| Path | Description |
|------|-------------|
| `source_csv/YYYYMMDD-NNN/{image_name}.json` | Raw JSON (6 prompt variations) in date-stamped run folder |
| `source_csv/YYYYMMDD-NNN/{image_name}.csv` | CSV conversion of the JSON, same run folder |

**Output folder structure:**
```
source_csv/
├── 20260423-001/
│   ├── image1.json
│   ├── image1.csv
│   └── meta.json
├── 20260423-002/
│   ├── image2.json
│   ├── image2.csv
│   └── meta.json
└── 20260424-001/
    ├── image3.json
    ├── image3.csv
    └── meta.json
```

**Folder naming:** `YYYYMMDD-NNN` where `NNN` is a zero-padded running number that increments per run on the same day. Resets each day.

---

## Execution Method

All generation happens **in-session** using Qwen Code's own LLM capabilities:

1. Qwen Code reads the image → produces description
2. Qwen Code applies template rules → generates JSON
3. Qwen Code validates → converts to CSV → saves file

**No external API calls required.** No curl, no DashScope API, no extra scripts or dependencies.

---

## Per-Image Process Summary

```
image in source_images/
  → read_file (visual analysis)
  → structured description
  → apply template rules from the runtime workflow prompt
  → generate JSON array (6 rows)
  → validate schema
  → convert to CSV
  → save to source_csv/{image_name}.csv
```
