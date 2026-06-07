---
name: project-analysis-gate-with-todo-tracking
description: Complete procedure for the project_analysis step in delivery_scaffold_v1 with proper todo tracking — auto-discovery of project context files, structured analysis output, meta.json sidecar contract, and progress tracking
source: auto-skill
extracted_at: '2026-06-05T15:25:25.111Z'
---

# Project Analysis Gate with Todo Tracking Procedure

## When to use
This skill applies when executing the `project_analysis` step in `delivery_scaffold_v1` — the first step of the delivery scaffold workflow. No prior workflow gating is required. The coder MUST auto-discover project context files — do NOT wait for a seed file. This procedure includes proper todo tracking with create_todos and mark_complete functions.

## Required tracking sequence

### Step 1: Create todos at the beginning of the task
Call the create_todos function immediately after starting the workflow step using the shell command:
```
python3 -c "from agent_runner_v2.agent_tools import create_todos; create_todos('JOB_ID', ['Scan project root for AI context files', 'Scan project root for project metadata files', 'Scan project root for architecture/design docs', 'Scan project root for existing delivery docs', 'Read all discovered files', 'Analyze project domain and tech stack', 'Assess project complexity and workflow scope', 'Determine suggested agent roles', 'Identify project-specific considerations', 'Write PROJECT_ANALYSIS markdown file', 'Write meta.json sidecar', 'Verify all files exist and are correctly formatted'])"
```

Where JOB_ID is the specific job identifier provided by the runner (e.g., SCAFFOLD-GEN-20260605-015).

### Step 2: Execute each step and mark complete
After completing each step, call the mark_complete function using the shell command:
```
python3 -c "from agent_runner_v2.agent_tools import mark_complete; mark_complete('JOB_ID', STEP_NUMBER, notes='Specific notes about what was done for this step')"
```

Where STEP_NUMBER is the 1-based index of the step being marked complete, and notes should be unique for each step describing what was accomplished.

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

## Execution sequence with todo tracking

### Step 1: Create the output directory structure
- Create the directory path `{step_dir}` ensuring all parent directories exist
- Use shell commands to create the directory structure: `mkdir -p {step_dir}`
- Mark this step as complete with appropriate notes
- Verify the directory was created successfully before proceeding with file operations

### Step 2: Auto-discover files
- Use the `list_directory` tool and `read_file` tool to scan for all four categories of files listed above.
- Use glob patterns if available, or systematically check for each file using read_file to see if it exists.
- Build a complete list of discovered files.
- Mark this step as complete with appropriate notes

### Step 3: Read ALL discovered files
- Read every file that exists. Do not skip any.
- Use the content to inform the analysis.
- Mark this step as complete with appropriate notes

### Step 4: Analyze project characteristics
- Determine domain area based on discovered files
- Summarize tech stack
- Assess complexity level (simple/standard/advanced)
- Determine suggested workflow scope and agent roles
- Identify project-specific SOP considerations
- Mark each analysis component as complete with appropriate notes

### Step 5: Write the PROJECT_ANALYSIS file
- Follow the required compact format with all 8 sections.
- Write to `{step_dir}/project_analysis.json`.
- Mark this step as complete with appropriate notes

### Step 6: Verify the analysis file exists on disk
- Confirm all 8 sections are present before writing the sidecar.
- Mark this step as complete with appropriate notes

### Step 7: Write the meta.json sidecar
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
- Mark this step as complete with appropriate notes

### Step 8: Verify both files exist on disk
- Read both the analysis file and the sidecar back to confirm they exist and have correct content before returning.
- Mark this step as complete with appropriate notes

### Step 9: Return final JSON
- Return only valid JSON matching:
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "<short summary>",
    "artifacts": {
      "PROJECT_ANALYSIS": "<path if created>"
    },
    "recorded_at": "2026-06-05T00:00:00"
  }
}
```
- No markdown, no explanation, no text before or after the JSON.
- Ensure the JSON follows the exact schema with schema_version and coder_result fields.
- Mark this step as complete with appropriate notes

## Complexity classification guide

| Rating | Indicators |
|---|---|
| simple | Single CLI tool, <5 source files, no external dependencies, solo developer |
| standard | Multi-component system, 5-20 source files, moderate integrations, needs review process |
| advanced | Large codebase, 20+ files, multiple services or teams, compliance requirements, complex dependency graph, CI/CD pipeline, structured delivery docs already in place, sophisticated architecture patterns, multiple integrated systems |

## Handling existing delivery scaffolds

When `docs/delivery/` already contains mature artifacts (templates, SOP, reviews, active initiatives):
- The PROJECT_ANALYSIS should explicitly note this under "Project-Specific SOP Considerations"
- The scaffold should **respect and extend existing artifacts rather than overwrite** them
- Count the number of existing files to gauge maturity (e.g., "35+ files under docs/delivery/")
- Reference existing templates by name in the "Discovered Files Summary"
- This affects downstream steps (generate_sop, generate_templates) — they should merge, not replace

## Available tools for this procedure
- `list_directory`: To list files and directories in a specific path
- `read_file`: To read the content of specific files
- `write_file`: To create or update files with content
- `edit`: To modify existing files by replacing text
- `run_shell_command`: To execute shell commands including the create_todos and mark_complete functions

## Anti-patterns to avoid
- Waiting for a seed file — auto-discovery is mandatory
- Skipping any discovered file — read ALL of them
- Writing the meta.json sidecar before the analysis file exists on disk
- Omitting any of the 8 required sections (especially "Discovered Files")
- Using relative paths in the meta.json artifacts map
- Returning markdown-wrapped JSON or explanatory text
- Failing to verify that both the analysis file and sidecar exist on disk before completing the step
- Creating the output directory structure without ensuring all parent directories exist first
- Not checking if files actually exist before including them in the discovered files list
- Assuming specific file paths without verifying them exist in the target project
- Failing to create the output directory before attempting to write the analysis file
- Not properly handling the absolute path requirement for file operations
- Forgetting to call the create_todos and mark_complete functions to track progress
- Not marking each step as complete after performing it
- Failing to verify the correct job ID is used in tracking functions
- Not properly structuring the JSON response to match the required schema
- Using unavailable tools like glob when list_directory and read_file are the appropriate tools
- Not using the proper JSON schema with schema_version and coder_result fields in the final output
- Not properly tracking each step with unique notes in the mark_complete function