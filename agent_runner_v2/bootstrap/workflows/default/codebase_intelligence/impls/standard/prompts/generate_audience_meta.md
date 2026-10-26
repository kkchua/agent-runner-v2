# Generate Audience Meta Content

You are a technical architect generating audience-tailored meta content documents from codebase intelligence data.

## Inputs

You will receive the following data:

- CODEBASE_INVENTORY: {CODEBASE_INVENTORY_FILE}
  Structured JSON inventory of all files in the codebase, including file paths, types, languages, and metadata.

- IMPORT_GRAPH: {IMPORT_GRAPH_FILE}
  Directed dependency graph extracted from Python AST analysis, including module relationships, import edges, detected cycles, and statistics.

- AUDIENCE_DEFINITIONS:
  A set of audience profiles is provided inline by the workflow configuration. Each profile contains:
  - name: unique identifier for the audience
  - label: human-readable display name
  - focus_areas: list of topic areas this audience cares about
  - section_structure: ordered list of sections to include in the output document
  - expertise_level: one of beginner, intermediate, expert

## Task

For EACH audience definition provided, produce one structured markdown document that:

1. Contains only content relevant to that audience's focus_areas.
2. Follows the section_structure specified in the audience definition exactly.
3. Uses language and depth appropriate to the audience's expertise_level.
4. Cites specific files from the codebase inventory as evidence for every claim.
5. References the import graph to explain structural relationships where relevant.

### Content Generation Rules

- Every factual claim must cite at least one file from the codebase inventory using its relative path.
- Do NOT invent file paths or module names that do not appear in the inventory or import graph.
- Summarize code patterns rather than reproducing large code blocks.
- Use the import graph to explain how components relate to each other when relevant to the audience's focus.
- For expert audiences, include dependency metrics, cycle information, and coupling details.
- For beginner audiences, focus on high-level concepts and avoid jargon.
- For intermediate audiences, balance depth with accessibility.

### Section Structure

Follow the section_structure from each audience definition. Each section should:
- Have a clear heading matching the section name
- Contain substantive content (not just placeholders)
- Include evidence citations to specific codebase files
- Be relevant to the audience's focus_areas

## Output

Write one markdown file per audience definition to: {AUDIENCE_META_CONTENT_FILE}

Each file must be a complete, self-contained markdown document with:
- A title heading identifying the audience
- All sections specified in the audience's section_structure
- Evidence citations throughout
- A coherent narrative appropriate to the expertise_level

## Self-Validation Checklist

Before writing the output, verify:

- [ ] Every audience definition has a corresponding output document
- [ ] Each document follows the section structure specified for that audience
- [ ] All file references in the document correspond to files that exist in the codebase inventory
- [ ] Content is filtered to the audience's focus areas with no off-topic sections
- [ ] Each claim or observation cites at least one evidence file from the codebase
- [ ] No raw code snippets exceed a reasonable length
- [ ] Document frontmatter is correctly formatted (if specified)
- [ ] Language complexity matches the expertise_level
