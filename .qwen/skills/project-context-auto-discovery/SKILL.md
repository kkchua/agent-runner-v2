---
name: project-context-auto-discovery
description: Procedure for auto-discovering project context files in the delivery scaffold workflow - scanning for AI context, project metadata, architecture docs, and existing delivery docs
source: auto-skill
extracted_at: '2026-06-04T17:25:20.252Z'
---

# Project Context Auto-Discovery Procedure

## When to use
This skill applies when executing the `project_analysis` step in `delivery_scaffold_v1` — the first step of the delivery scaffold workflow. The step must auto-discover project context files without waiting for a seed file.

## Discovery sequence

### Step 0: Create the output directory structure
- Create the directory path `{step_dir}` ensuring all parent directories exist
- Use shell commands to create the directory structure: `mkdir -p {step_dir}`

### Step 1: Scan for AI Coder Context Files (highest priority)
Use glob patterns to search for these files in the project root:
- `QWEN.md` — Qwen Code project context
- `AGENTS.md` — Agent configuration (not docs/delivery/08_agents/)
- `CLAUDE.md` — Claude Code instructions
- `.cursorrules` — Cursor AI rules
- `.github/copilot-instructions.md` — GitHub Copilot instructions
- `.windsurfrules` — Windsurf rules

### Step 2: Scan for Project Metadata Files
Look for these common project configuration files:
- `README.md` or `README` — project overview
- `pyproject.toml` — Python project config (name, description, dependencies)
- `package.json` — Node.js project config (name, description, dependencies)
- `Cargo.toml` — Rust project config
- `go.mod` — Go module info
- `Gemfile` — Ruby dependencies

### Step 3: Scan for Architecture & Design Docs
Search in these locations for documentation:
- `docs/architecture/*.md` — architecture documents
- `docs/specs/*.md` — specification documents
- `docs/design/*.md` — design documents
- `ARCHITECTURE.md` — root-level architecture overview
- `DESIGN.md` — root-level design overview

### Step 4: Scan for Existing Delivery Docs
Check for any partially scaffolded delivery documentation:
- `docs/delivery/00_templates/*.md` — any existing templates
- `docs/delivery/08_agents/AGENTS.md` — existing agent registry
- Any files under `docs/delivery/` that already exist

## File discovery technique

Use the `glob` tool to search for each file pattern individually:
```
glob(pattern="QWEN.md", path="/workspace/projects/project-name")
```

For directories, use `list_directory` to enumerate contents:
```
list_directory(path="/workspace/projects/project-name/docs/delivery")
```

## Reading discovered files

After discovering files, read each one using the `read_file` tool:
```
read_file(file_path="/workspace/projects/project-name/QWEN.md")
```

## Handling missing files

If none of the expected files exist, the analysis should return `REJECTED` with the message "No project context files found".

## Recording discovered files

Maintain a list of all discovered files to include in the "Discovered Files Summary" section of the project analysis. This provides traceability for the analysis.

## Anti-patterns to avoid
- Waiting for a seed file — auto-discovery is mandatory
- Skipping any discovered file — read ALL of them
- Assuming files exist without verifying with glob/list_directory first
- Hardcoding project-specific file paths that won't generalize to other projects
- Failing to include all discovered files in the "Discovered Files Summary" section of the analysis
- Not reading files that exist to extract their content for the analysis
- Failing to handle cases where some files exist but others don't
- Not organizing the discovered files by category (AI context, project metadata, etc.) for the analysis
- Not properly handling the absolute path requirement for file operations
- Not properly calling the create_todos and mark_complete functions to track progress
- Forgetting to verify the correct job ID is used in tracking functions