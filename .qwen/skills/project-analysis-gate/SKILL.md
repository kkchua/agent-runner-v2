---
name: project-analysis-gate
description: Procedure for the project_analysis step in delivery_scaffold_v1 — auto-discovery of project context files, structured analysis output, and meta.json sidecar contract
source: auto-skill
extracted_at: '2026-06-03T23:18:56.360Z'
---

# Project Analysis Gate Procedure

## When to use
This skill applies when executing the `project_analysis` step in `delivery_scaffold_v1` — the first step of the delivery scaffold workflow. No prior workflow gating is required. The coder MUST auto-discover project context files — do NOT wait for a seed file.

## Auto-discovery rules (MANDATORY)

Scan the project root for the following files. Read EVERY file that exists — do not skip any discovered file. Use ALL discovered content to build the analysis.

### 1. AI Coder Context Files (highest priority)
- `QWEN.md` — Qwen Code project context
- `AGENTS.md` — Agent configuration (not docs/delivery/08_agents/)
- `CLAUDE.md` — Claude Code instructions
- `.cursorrules` — Cursor AI rules
- `.github/copilot-instructions.md` — GitHub Copilot instructions
- `.windsurfrules` — Windsurf rules

### 2. Project Metadata Files
- `README.md` or `README` — project overview
- `pyproject.toml` — Python project config
- `package.json` — Node.js project config
- `Cargo.toml` — Rust project config
- `go.mod` — Go module info
- `Gemfile` — Ruby dependencies

### 3. Architecture & Design Docs (if present)
- `docs/architecture/*.md`
- `docs/specs/*.md`
- `docs/design/*.md`
- `ARCHITECTURE.md`
- `DESIGN.md`

### 4. Existing Delivery Docs (if partially scaffolded)
- `docs/delivery/00_templates/*.md` — any existing templates
- `docs/delivery/08_agents/AGENTS.md` — existing agent registry
- Any files under `docs/delivery/` that already exist

**If none of these files exist**, return `REJECTED` with "No project context files found".

## Required PROJECT_ANALYSIS sections (all 8 mandatory)

The analysis document must include these sections in order:

1. **Domain Area** — What domain does this project belong to?
2. **Tech Stack Summary** — Technologies mentioned or implied (languages, frameworks, databases)
3. **Complexity Assessment** — Rate as `simple`, `standard`, or `advanced`
   - Simple: single-purpose tool, small team, minimal integrations
   - Standard: multi-component system, moderate integrations, review process needed
   - Advanced: large system, multiple services/teams, compliance requirements, complex dependencies
4. **Suggested Workflow Scope** — Which delivery layers are needed based on complexity
   - Always: SOP, status rules, initiative/planning/task templates
   - Standard adds: task graph template, implementation plan template, review template
   - Advanced adds: memory template, full agent system (AGENTS.md + agent contracts)
5. **Suggested Agent Roles** — Which agent roles make sense
   - Always: Planner, Reviewer
   - Standard adds: Task Decomposer, Implementation Planner, Executor
   - Advanced adds: Memory Manager
6. **Delivery Folder Customization** — Usually "no — keep standard docs/delivery/"
7. **Project-Specific SOP Considerations** — Special rules, constraints, conventions
8. **Discovered Files Summary** — List which files were found and read (for traceability)

## Output paths

The PROJECT_ANALYSIS file is written to the step's artifact directory:
- Analysis file: `{step_dir}/project_analysis.json`
- Sidecar: `{step_dir}/meta.json`

The step_dir is provided by the runner context (e.g., `delivery_scaffold_v1/SCAFFOLD-GEN-YYYYMMDD-NNN/00_project_analysis/`).

## Execution sequence

### Step 1: Auto-discover files
- Use glob patterns to scan for all four categories of files listed above.
- Build a complete list of discovered files.

### Step 2: Read ALL discovered files
- Read every file that exists. Do not skip any.
- Use the content to inform the analysis.

### Step 3: Write the PROJECT_ANALYSIS file
- Follow the required compact format with all 8 sections.
- Write to `{step_dir}/project_analysis.json`.

### Step 4: Verify the analysis file exists on disk
- Confirm all 8 sections are present before writing the sidecar.

### Step 5: Write the meta.json sidecar
- Path: `{step_dir}/meta.json`
- Structure (exact):
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary",
    "artifacts": {
      "PROJECT_ANALYSIS": "<path of the analysis file>"
    },
    "recorded_at": "ISO-8601 timestamp"
  }
}
```

### Step 6: Verify the sidecar exists on disk
- Read it back to confirm before returning.

### Step 7: Return final JSON
- Return only valid JSON matching:
```json
{
  "status": "APPROVED" | "REJECTED",
  "remark": "<short summary>",
  "artifacts": {
    "PROJECT_ANALYSIS": "<path if created>"
  }
}
```
- No markdown, no explanation, no text before or after the JSON.

## Complexity classification guide

| Rating | Indicators |
|---|---|
| simple | Single CLI tool, <5 source files, no external dependencies, solo developer |
| standard | Multi-component system, 5-20 source files, moderate integrations, needs review process |
| advanced | Large codebase, 20+ files, multiple services or teams, compliance requirements, complex dependency graph, CI/CD pipeline, structured delivery docs already in place |

## Handling existing delivery scaffolds

When `docs/delivery/` already contains mature artifacts (templates, SOP, reviews, active initiatives):
- The PROJECT_ANALYSIS should explicitly note this under "Project-Specific SOP Considerations"
- The scaffold should **respect and extend existing artifacts rather than overwrite** them
- Count the number of existing files to gauge maturity (e.g., "35+ files under docs/delivery/")
- Reference existing templates by name in the "Discovered Files Summary"
- This affects downstream steps (generate_sop, generate_templates) — they should merge, not replace

## Anti-patterns to avoid
- Waiting for a seed file — auto-discovery is mandatory
- Skipping any discovered file — read ALL of them
- Writing the meta.json sidecar before the analysis file exists on disk
- Omitting any of the 8 required sections (especially "Discovered Files")
- Using relative paths in the meta.json artifacts map
- Returning markdown-wrapped JSON or explanatory text
